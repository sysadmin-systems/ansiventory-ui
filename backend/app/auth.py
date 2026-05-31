import hashlib
import os
from datetime import datetime, timezone

from fastapi import Cookie, Depends, Header, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

SESSION_COOKIE = "ansiventory_session"
COOKIE_MAX_AGE = 60 * 60 * 8  # 8 horas
IS_PROD = os.getenv("APP_ENV", "development") == "production"


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ------------------------------------------------------------------
# Schema de login
# ------------------------------------------------------------------
class LoginRequest(BaseModel):
    workspace: str
    token: str


# ------------------------------------------------------------------
# Validação interna do token
# ------------------------------------------------------------------
async def _validate_token(token: str, db: AsyncSession) -> dict:
    token_hash = _hash_token(token)
    result = await db.execute(
        text("""
            SELECT t.id, t.workspace_id, t.descricao, t.expires_at,
                   w.slug AS workspace_slug
            FROM api_tokens t
            JOIN workspaces w ON w.id = t.workspace_id
            WHERE t.token_hash = :token_hash
              AND (t.expires_at IS NULL OR t.expires_at > NOW())
        """),
        {"token_hash": token_hash},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return dict(row)


# ------------------------------------------------------------------
# Dependency principal — aceita cookie httpOnly OU Bearer token
# Usado por TODOS os endpoints protegidos
# ------------------------------------------------------------------
async def require_session(
    ansiventory_session: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    token = None

    # 1. tenta cookie (UI)
    if ansiventory_session:
        token = ansiventory_session

    # 2. tenta Bearer token (API, scripts, AWX)
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Autenticação necessária",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await _validate_token(token, db)


# ------------------------------------------------------------------
# Dependency de workspace — valida auth + pertencimento ao workspace
# ------------------------------------------------------------------
async def require_workspace_access(
    workspace_id: int,
    session: dict = Depends(require_session),
) -> dict:
    if session["workspace_id"] != workspace_id:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado a este workspace",
        )
    return session


# ------------------------------------------------------------------
# Endpoint de login — seta o cookie httpOnly
# ------------------------------------------------------------------
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    token_data = await _validate_token(payload.token, db)

    if token_data["workspace_slug"] != payload.workspace:
        raise HTTPException(status_code=401, detail="Token não pertence a este workspace")

    response.set_cookie(
        key=SESSION_COOKIE,
        value=payload.token,
        httponly=True,
        secure=IS_PROD,
        samesite="strict" if IS_PROD else "lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )

    return {
        "workspace": payload.workspace,
        "workspace_id": token_data["workspace_id"],
        "message": "autenticado com sucesso",
    }


# ------------------------------------------------------------------
# Endpoint de logout
# ------------------------------------------------------------------
async def logout(response: Response) -> dict:
    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
        httponly=True,
        secure=IS_PROD,
        samesite="strict" if IS_PROD else "lax",
    )
    return {"message": "sessão encerrada"}
