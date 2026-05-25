from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

bearer_scheme = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Valida o Bearer token contra a tabela api_tokens.
    O token é armazenado como SHA-256 — nunca o valor plaintext.
    """
    token = credentials.credentials

    result = await db.execute(
        text("""
            SELECT t.id, t.descricao, t.workspace_id, t.expires_at
            FROM api_tokens t
            WHERE t.token_hash = encode(digest(:token, 'sha256'), 'hex')
              AND (t.expires_at IS NULL OR t.expires_at > NOW())
        """),
        {"token": token}
    )
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return dict(row)
