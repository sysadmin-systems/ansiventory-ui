from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth import verify_token
from app.models.models import Host, HostGrupo, Grupo, AuditLog
from app.schemas.schemas import HostCreate, HostOut, HostUpdate, HostVarsOut, AuditLogOut

router = APIRouter(prefix="/workspaces/{workspace_id}/hosts", tags=["hosts"])


def _host_to_out(host: Host) -> HostOut:
    grupos = [hg.grupo.nome for hg in host.host_grupos if hg.grupo]
    # converte IPv4Address -> str antes de validar
    host_dict = {
        "id": host.id,
        "workspace_id": host.workspace_id,
        "hostname": host.hostname,
        "ip_address": str(host.ip_address),
        "municipio": host.municipio,
        "ambiente": host.ambiente,
        "ativo": host.ativo,
        "vars": host.vars,
        "updated_at": host.updated_at,
        "grupos": grupos,
    }
    return HostOut.model_validate(host_dict)


@router.get("", response_model=list[HostOut])
async def list_hosts(
    workspace_id: int,
    ambiente: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    municipio: Optional[str] = Query(None),
    grupo: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _token: dict = Depends(verify_token),
):
    q = (
        select(Host)
        .where(Host.workspace_id == workspace_id)
        .options(selectinload(Host.host_grupos).selectinload(HostGrupo.grupo))
        .order_by(Host.hostname)
    )
    if ambiente:
        q = q.where(Host.ambiente == ambiente)
    if ativo is not None:
        q = q.where(Host.ativo == ativo)
    if municipio:
        q = q.where(Host.municipio.ilike(f"%{municipio}%"))
    if grupo:
        q = q.join(HostGrupo).join(Grupo).where(Grupo.nome == grupo)

    result = await db.execute(q)
    hosts = result.scalars().unique().all()
    return [_host_to_out(h) for h in hosts]


@router.get("/{host_id}", response_model=HostOut)
async def get_host(workspace_id: int, host_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Host)
        .where(Host.id == host_id, Host.workspace_id == workspace_id)
        .options(selectinload(Host.host_grupos).selectinload(HostGrupo.grupo))
    )
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host não encontrado")
    return _host_to_out(host)


@router.get("/{host_id}/vars", response_model=HostVarsOut)
async def get_host_vars(workspace_id: int, host_id: int, db: AsyncSession = Depends(get_db)):
    """Retorna as vars efetivas do host — merge de group_vars + host_vars."""
    result = await db.execute(
        select(Host.hostname)
        .where(Host.id == host_id, Host.workspace_id == workspace_id)
    )
    hostname = result.scalar_one_or_none()
    if not hostname:
        raise HTTPException(status_code=404, detail="Host não encontrado")

    vars_result = await db.execute(text("SELECT fn_hostvars(:host_id)"), {"host_id": host_id})
    vars_final = vars_result.scalar()
    return HostVarsOut(hostname=hostname, vars_final=vars_final or {})


@router.post("", response_model=HostOut, status_code=201)
async def create_host(workspace_id: int, payload: HostCreate, db: AsyncSession = Depends(get_db)):
    host = Host(
        workspace_id=workspace_id,
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        municipio=payload.municipio,
        ambiente=payload.ambiente,
        ativo=payload.ativo,
        vars=payload.vars,
    )
    db.add(host)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Host '{payload.hostname}' já existe neste workspace")

    for grupo_id in payload.grupo_ids:
        db.add(HostGrupo(host_id=host.id, grupo_id=grupo_id))

    db.add(AuditLog(
        workspace_id=workspace_id,
        host_id=host.id,
        action="create",
        diff={"hostname": host.hostname, "ip_address": str(host.ip_address)},
        changed_by="api",
    ))

    await db.commit()
    await db.refresh(host)

    result = await db.execute(
        select(Host)
        .where(Host.id == host.id)
        .options(selectinload(Host.host_grupos).selectinload(HostGrupo.grupo))
    )
    return _host_to_out(result.scalar_one())


@router.patch("/{host_id}", response_model=HostOut)
async def update_host(
    workspace_id: int, host_id: int, payload: HostUpdate, db: AsyncSession = Depends(get_db),
    _token: dict = Depends(verify_token),
):
    result = await db.execute(
        select(Host)
        .where(Host.id == host_id, Host.workspace_id == workspace_id)
        .options(selectinload(Host.host_grupos).selectinload(HostGrupo.grupo))
    )
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host não encontrado")

    before = {"vars": host.vars, "ativo": host.ativo}
    update_data = payload.model_dump(exclude_unset=True, exclude={"grupo_ids"})
    for field, value in update_data.items():
        setattr(host, field, value)

    if payload.grupo_ids is not None:
        await db.execute(delete(HostGrupo).where(HostGrupo.host_id == host_id))
        for grupo_id in payload.grupo_ids:
            db.add(HostGrupo(host_id=host_id, grupo_id=grupo_id))

    db.add(AuditLog(
        workspace_id=workspace_id,
        host_id=host_id,
        action="update",
        diff={"before": before, "after": update_data},
        changed_by="api",
    ))

    await db.commit()
    result = await db.execute(
        select(Host)
        .where(Host.id == host_id)
        .options(selectinload(Host.host_grupos).selectinload(HostGrupo.grupo))
    )
    return _host_to_out(result.scalar_one())


@router.delete("/{host_id}", status_code=204)
async def delete_host(workspace_id: int, host_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Host).where(Host.id == host_id, Host.workspace_id == workspace_id)
    )
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host não encontrado")

    db.add(AuditLog(
        workspace_id=workspace_id,
        host_id=host_id,
        action="delete",
        diff={"hostname": host.hostname},
        changed_by="api",
    ))
    await db.delete(host)
    await db.commit()


@router.get("/{host_id}/audit", response_model=list[AuditLogOut])
async def get_host_audit(workspace_id: int, host_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.host_id == host_id, AuditLog.workspace_id == workspace_id)
        .order_by(AuditLog.changed_at.desc())
        .limit(50)
    )
    return result.scalars().all()
