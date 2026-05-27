import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_workspace_access
from app.database import get_db
from app.models.models import ApiToken

router = APIRouter(prefix="/workspaces/{workspace_id}/tokens", tags=["tokens"])


class TokenCreate(BaseModel):
    descricao: str


class TokenOut(BaseModel):
    id: int
    descricao: str | None
    created_at: str
    expires_at: str | None


@router.get("", response_model=list[TokenOut])
async def list_tokens(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_workspace_access),
):
    result = await db.execute(
        select(ApiToken)
        .where(ApiToken.workspace_id == workspace_id)
        .order_by(ApiToken.created_at.desc())
    )
    tokens = result.scalars().all()
    return [
        TokenOut(
            id=t.id,
            descricao=t.descricao,
            created_at=t.created_at.isoformat(),
            expires_at=t.expires_at.isoformat() if t.expires_at else None,
        )
        for t in tokens
    ]


@router.post("", status_code=201)
async def create_token(
    workspace_id: int,
    payload: TokenCreate,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_workspace_access),
):
    raw_token = secrets.token_hex(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    token = ApiToken(
        workspace_id=workspace_id,
        token_hash=token_hash,
        descricao=payload.descricao,
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)

    return {
        "id": token.id,
        "token": raw_token,
        "descricao": token.descricao,
        "created_at": token.created_at.isoformat(),
        "warning": "Guarde este token agora. Ele não será exibido novamente.",
    }


@router.delete("/{token_id}", status_code=204)
async def delete_token(
    workspace_id: int,
    token_id: int,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_workspace_access),
):
    result = await db.execute(
        select(ApiToken).where(
            ApiToken.id == token_id,
            ApiToken.workspace_id == workspace_id,
        )
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Token não encontrado")

    count_result = await db.execute(
        select(ApiToken).where(ApiToken.workspace_id == workspace_id)
    )
    total = len(count_result.scalars().all())
    if total <= 1:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir o último token do workspace"
        )

    await db.delete(token)
    await db.commit()
