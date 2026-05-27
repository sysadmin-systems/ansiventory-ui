from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import require_session
from app.models.models import Workspace, Host, Grupo, HostGrupo
from app.schemas.schemas import WorkspaceOut

router = APIRouter(tags=["inventory"])


@router.get("/workspaces", response_model=list[WorkspaceOut])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_session),
):
    # retorna apenas o workspace da sessão
    result = await db.execute(
        select(Workspace)
        .where(Workspace.id == _session["workspace_id"])
        .order_by(Workspace.name)
    )
    return result.scalars().all()


@router.get("/inventory/{workspace_slug}")
async def get_inventory(
    workspace_slug: str,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_session),
):
    """
    Retorna o inventário Ansible completo no formato JSON esperado pelo plugin.
    Aceita Bearer token (para scripts/AWX) ou cookie (para UI).
    """
    # valida que o slug pertence ao workspace da sessão
    ws_result = await db.execute(
        select(Workspace).where(
            Workspace.slug == workspace_slug,
            Workspace.id == _session["workspace_id"],
        )
    )
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_slug}' não encontrado")

    hosts_result = await db.execute(
        select(Host)
        .where(Host.workspace_id == workspace.id, Host.ativo == True)
        .order_by(Host.hostname)
    )
    hosts = hosts_result.scalars().all()

    if not hosts:
        return {"_meta": {"hostvars": {}}}

    inventory: dict = {"_meta": {"hostvars": {}}}

    for host in hosts:
        vars_result = await db.execute(
            text("SELECT fn_hostvars(:host_id)"),
            {"host_id": host.id}
        )
        hostvars = vars_result.scalar() or {}
        if "ansible_host" not in hostvars:
            hostvars["ansible_host"] = str(host.ip_address) if host.ip_address else host.hostname
        inventory["_meta"]["hostvars"][host.hostname] = hostvars

    grupos_result = await db.execute(
        select(Grupo, Host.hostname)
        .join(HostGrupo, HostGrupo.grupo_id == Grupo.id)
        .join(Host, Host.id == HostGrupo.host_id)
        .where(Grupo.workspace_id == workspace.id, Host.ativo == True)
        .order_by(Grupo.nome, Host.hostname)
    )

    for grupo, hostname in grupos_result.all():
        if grupo.nome not in inventory:
            inventory[grupo.nome] = {
                "hosts": [],
                "vars": grupo.vars or {},
            }
        inventory[grupo.nome]["hosts"].append(hostname)

    return inventory
