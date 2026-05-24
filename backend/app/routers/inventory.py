from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import Workspace, Host, Grupo, HostGrupo
from app.schemas.schemas import WorkspaceOut

router = APIRouter(tags=["inventory"])


@router.get("/workspaces", response_model=list[WorkspaceOut])
async def list_workspaces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).order_by(Workspace.name))
    return result.scalars().all()


@router.get("/inventory/{workspace_slug}")
async def get_inventory(workspace_slug: str, db: AsyncSession = Depends(get_db)):
    """
    Retorna o inventário Ansible completo no formato JSON esperado pelo plugin.

    Estrutura de saída:
    {
        "grupo1": { "hosts": ["host1", "host2"] },
        "grupo2": { "hosts": ["host1"] },
        "_meta": {
            "hostvars": {
                "host1": { ...vars merged... }
            }
        }
    }
    """
    ws_result = await db.execute(
        select(Workspace).where(Workspace.slug == workspace_slug)
    )
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_slug}' não encontrado")

    # Busca todos os hosts ativos com seus grupos
    hosts_result = await db.execute(
        select(Host)
        .where(Host.workspace_id == workspace.id, Host.ativo == True)
        .order_by(Host.hostname)
    )
    hosts = hosts_result.scalars().all()

    if not hosts:
        return {"_meta": {"hostvars": {}}}

    # Monta o inventário
    inventory: dict = {"_meta": {"hostvars": {}}}

    for host in hosts:
        # vars efetivas via fn_hostvars (merge group_vars + host_vars)
        vars_result = await db.execute(
            text("SELECT fn_hostvars(:host_id)"),
            {"host_id": host.id}
        )
        hostvars = vars_result.scalar() or {}

        # garante ansible_host se não vier nas vars
        if "ansible_host" not in hostvars:
            hostvars["ansible_host"] = str(host.ip_address)

        inventory["_meta"]["hostvars"][host.hostname] = hostvars

    # Busca grupos e monta listas de hosts
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


@router.get("/inventory/{workspace_slug}.yml", response_class=PlainTextResponse)
async def get_inventory_plugin_config(workspace_slug: str, db: AsyncSession = Depends(get_db)):
    """
    Retorna o arquivo .yml de configuração do plugin Ansible.
    Salve como `inventory.ansiventory.yml` e use com:
    ansible-playbook -i inventory.ansiventory.yml playbook.yml
    """
    ws_result = await db.execute(
        select(Workspace).where(Workspace.slug == workspace_slug)
    )
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_slug}' não encontrado")

    from app.config import settings
    base_url = f"http://{settings.postgres_host}:8000"

    yaml_content = f"""# Ansiventory UI — Plugin de inventário dinâmico
# Gerado automaticamente para workspace: {workspace.name}
# Uso: ansible-playbook -i inventory.ansiventory.yml playbook.yml

plugin: community.general.url
url: {base_url}/inventory/{workspace_slug}
"""
    return yaml_content
