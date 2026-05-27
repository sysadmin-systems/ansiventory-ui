import subprocess
import tempfile
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import require_session

router = APIRouter(prefix="/vault", tags=["vault"])


class EncryptRequest(BaseModel):
    value: str
    vault_id: str = "default"
    password: str


class DecryptRequest(BaseModel):
    encrypted: str
    password: str


def _write_password_file(password: str) -> str:
    """Cria arquivo temporário com a senha do vault."""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.pass', delete=False)
    tmp.write(password.strip() + '\n')  # ansible-vault exige newline no final
    tmp.flush()
    tmp.close()
    return tmp.name


@router.post("/encrypt")
async def encrypt_value(
    payload: EncryptRequest,
    _session: dict = Depends(require_session),
):
    """Criptografa um valor usando ansible-vault encrypt_string."""
    pass_file = _write_password_file(payload.password)
    try:
        result = subprocess.run(
            [
                "ansible-vault", "encrypt_string",
                "--vault-password-file", pass_file,
                "--stdin-name", "value",
            ],
            input=payload.value,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao criptografar: {result.stderr.strip()}"
            )

        # extrai só o bloco vault da saída
        output = result.stdout
        # remove a linha "value: !vault |" e retorna só o bloco AES
        lines = output.split('\n')
        vault_lines = []
        capturing = False
        for line in lines:
            if '$ANSIBLE_VAULT' in line:
                capturing = True
            if capturing and line.strip():
                vault_lines.append(line.strip())

        vault_block = '\n'.join(vault_lines)
        if not vault_block:
            vault_block = output.strip()

        return {"result": vault_block}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout ao criptografar")
    finally:
        os.unlink(pass_file)


@router.post("/decrypt")
async def decrypt_value(
    payload: DecryptRequest,
    _session: dict = Depends(require_session),
):
    """Descriptografa um valor usando ansible-vault decrypt."""
    pass_file = _write_password_file(payload.password)

    # normaliza o input — remove prefixos e espaços extras
    encrypted = payload.encrypted.strip()
    if not encrypted.startswith('$ANSIBLE_VAULT'):
        raise HTTPException(
            status_code=400,
            detail="O valor não parece ser um Ansible Vault válido"
        )

    # cria arquivo temporário com o conteúdo vault
    vault_file = tempfile.NamedTemporaryFile(
        mode='w', suffix='.vault', delete=False
    )
    vault_file.write(encrypted)
    vault_file.flush()
    vault_file.close()

    try:
        result = subprocess.run(
            [
                "ansible-vault", "decrypt",
                "--vault-password-file", pass_file,
                "--output", "-",
                vault_file.name,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            err = result.stderr.strip()
            if "ERROR! Decryption failed" in err or "bad decrypt" in err.lower():
                raise HTTPException(status_code=401, detail="Senha incorreta")
            raise HTTPException(status_code=400, detail=f"Erro ao descriptografar: {err}")

        return {"result": result.stdout.strip()}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout ao descriptografar")
    finally:
        os.unlink(pass_file)
        os.unlink(vault_file.name)
