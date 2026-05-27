from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import require_workspace_access
from app.models.models import Grupo
from app.schemas.schemas import GrupoCreate, GrupoOut, GrupoUpdate

router = APIRouter(prefix="/workspaces/{workspace_id}/grupos", tags=["grupos"])


@router.get("", response_model=list[GrupoOut])
async def list_grupos(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_workspace_access),
):
    result = await db.execute(
        select(Grupo)
        .where(Grupo.workspace_id == workspace_id)
        .order_by(Grupo.nome)
    )
    return result.scalars().all()


@router.get("/{grupo_id}", response_model=GrupoOut)
async def get_grupo(
    workspace_id: int,
    grupo_id: int,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_workspace_access),
):
    result = await db.execute(
        select(Grupo).where(Grupo.id == grupo_id, Grupo.workspace_id == workspace_id)
    )
    grupo = result.scalar_one_or_none()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return grupo


@router.post("", response_model=GrupoOut, status_code=201)
async def create_grupo(
    workspace_id: int,
    payload: GrupoCreate,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_workspace_access),
):
    grupo = Grupo(workspace_id=workspace_id, nome=payload.nome, vars=payload.vars)
    db.add(grupo)
    await db.commit()
    await db.refresh(grupo)
    return grupo


@router.patch("/{grupo_id}", response_model=GrupoOut)
async def update_grupo(
    workspace_id: int,
    grupo_id: int,
    payload: GrupoUpdate,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_workspace_access),
):
    result = await db.execute(
        select(Grupo).where(Grupo.id == grupo_id, Grupo.workspace_id == workspace_id)
    )
    grupo = result.scalar_one_or_none()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(grupo, field, value)

    await db.commit()
    await db.refresh(grupo)
    return grupo


@router.delete("/{grupo_id}", status_code=204)
async def delete_grupo(
    workspace_id: int,
    grupo_id: int,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_workspace_access),
):
    result = await db.execute(
        select(Grupo).where(Grupo.id == grupo_id, Grupo.workspace_id == workspace_id)
    )
    grupo = result.scalar_one_or_none()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    await db.delete(grupo)
    await db.commit()
