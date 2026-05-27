#!/usr/bin/env python3
"""
Ansiventory UI — Migração de inventário existente
Lê hosts.yml + host_vars/ e popula o banco via API

Uso:
    python3 migrate_inventory.py \
        --inventory /home/sysadmin/development/infra-ansible-navigator/inventory \
        --api http://localhost:8000 \
        --workspace 1

Dependências:
    pip install pyyaml requests
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
import yaml


# ------------------------------------------------------------------
# Suporte ao !vault do Ansible — preserva como string "__vault__:..."
# em vez de explodir o parser
# ------------------------------------------------------------------
class VaultString(str):
    pass

def vault_constructor(loader, node):
    value = loader.construct_scalar(node)
    # retorna dict com __ansible_vault — formato que o Ansible reconhece para descriptografar
    return {"__ansible_vault": value.strip()}

yaml.add_constructor("!vault", vault_constructor, Loader=yaml.SafeLoader)


# ------------------------------------------------------------------
# Argumentos
# ------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Migra inventário Ansible para Ansiventory UI")
parser.add_argument("--inventory", required=True, help="Caminho para a pasta inventory/")
parser.add_argument("--api", default="http://localhost:8000", help="URL base da API")
parser.add_argument("--workspace", type=int, default=1, help="ID do workspace no banco")
parser.add_argument("--token", default=os.environ.get("ANSIVENTORY_TOKEN", ""), help="Bearer token da API")
parser.add_argument("--dry-run", action="store_true", help="Apenas mostra o que seria feito, sem chamar a API")
parser.add_argument("--update", action="store_true", help="Atualiza hosts existentes com vars do arquivo")
args = parser.parse_args()

INVENTORY_DIR = Path(args.inventory)
API_BASE = args.api.rstrip("/")
WORKSPACE_ID = args.workspace
DRY_RUN = args.dry_run
UPDATE = args.update
TOKEN = args.token

if not TOKEN and not DRY_RUN:
    print("ERRO: defina ANSIVENTORY_TOKEN ou use --token", file=sys.stderr)
    sys.exit(1)

AUTH_HEADERS = {"Authorization": f"Bearer {TOKEN}"}

HOST_VARS_DIR = INVENTORY_DIR / "host_vars"
HOSTS_YML = INVENTORY_DIR / "hosts.yml"
GROUP_VARS_DIR = INVENTORY_DIR / "group_vars"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def log(msg):
    print(msg)

def log_ok(msg):
    print(f"  ✓ {msg}")

def log_skip(msg):
    print(f"  ~ {msg}")

def log_err(msg):
    print(f"  ✗ {msg}", file=sys.stderr)

def api_post(path, payload):
    if DRY_RUN:
        print(f"  [DRY-RUN] POST {path}")
        print(f"            {json.dumps(payload, ensure_ascii=False)[:120]}...")
        return {"id": 0}
    r = requests.post(f"{API_BASE}{path}", json=payload, headers=AUTH_HEADERS, timeout=10)
    if r.status_code in (200, 201):
        return r.json()
    # duplicate key — trata como skip
    if r.status_code in (409, 422, 500) and any(w in r.text.lower() for w in ("duplicate", "unique", "already")):
        return "__exists__"
    log_err(f"POST {path} -> {r.status_code}: {r.text[:200]}")
    return None

def api_patch(path, payload):
    if DRY_RUN:
        print(f"  [DRY-RUN] PATCH {path}")
        return {"id": 0}
    r = requests.patch(f"{API_BASE}{path}", json=payload, headers=AUTH_HEADERS, timeout=10)
    if r.status_code in (200, 201):
        return r.json()
    log_err(f"PATCH {path} -> {r.status_code}: {r.text[:200]}")
    return None

def api_get(path):
    r = requests.get(f"{API_BASE}{path}", headers=AUTH_HEADERS, timeout=10)
    if r.status_code != 200:
        return None
    return r.json()


# ------------------------------------------------------------------
# 1. Lê hosts.yml
# ------------------------------------------------------------------
log("\n📄 Lendo hosts.yml...")

with open(HOSTS_YML) as f:
    hosts_data = yaml.safe_load(f)

# Extrai grupos e seus hosts
# Estrutura: all.children.{grupo}.hosts.{hostname}: {}
all_children = hosts_data.get("all", {}).get("children", {})

grupos_hosts: dict[str, list[str]] = {}

def extract_groups(children: dict, parent: str = None):
    for group_name, group_data in children.items():
        if group_data is None:
            group_data = {}
        hosts = list((group_data.get("hosts") or {}).keys())
        # filtra hosts comentados (já removidos pelo yaml parser)
        grupos_hosts[group_name] = hosts
        # recursivo para subgrupos
        sub = group_data.get("children") or {}
        if sub:
            extract_groups(sub, group_name)

extract_groups(all_children)

# Todos os hostnames únicos
all_hostnames = set()
for hosts in grupos_hosts.values():
    all_hostnames.update(hosts)

# garante grupo 'all' com todos os hosts e suas vars
grupos_hosts["all"] = list(all_hostnames)

log(f"  Grupos encontrados: {list(grupos_hosts.keys())}")
log(f"  Total de hosts únicos: {len(all_hostnames)}")


# ------------------------------------------------------------------
# 2. Lê group_vars/all.yml (vars globais)
# ------------------------------------------------------------------
group_vars_all = {}
group_vars_files = {}

if GROUP_VARS_DIR.exists():
    all_yml = GROUP_VARS_DIR / "all.yml"
    if all_yml.exists():
        with open(all_yml) as f:
            group_vars_all = yaml.safe_load(f) or {}
        log(f"\n📦 group_vars/all.yml: {len(group_vars_all)} variáveis")

    # outros group_vars
    for f in GROUP_VARS_DIR.glob("*.yml"):
        if f.stem == "all":
            continue
        with open(f) as fp:
            group_vars_files[f.stem] = yaml.safe_load(fp) or {}
        log(f"  group_vars/{f.name}: {len(group_vars_files[f.stem])} variáveis")


# ------------------------------------------------------------------
# 3. Lê host_vars/
# ------------------------------------------------------------------
log(f"\n📂 Lendo host_vars/ ...")

host_vars: dict[str, dict] = {}

for hostname in all_hostnames:
    # tenta todas as extensões e estruturas possíveis
    candidates = [
        HOST_VARS_DIR / f"{hostname}.yml",
        HOST_VARS_DIR / f"{hostname}.yaml",
        HOST_VARS_DIR / hostname / "vars.yml",
        HOST_VARS_DIR / hostname / "vars.yaml",
        HOST_VARS_DIR / hostname / "main.yml",
        HOST_VARS_DIR / hostname / "main.yaml",
    ]

    found = next((p for p in candidates if p.exists()), None)
    if found:
        with open(found) as f:
            host_vars[hostname] = yaml.safe_load(f) or {}
    else:
        host_vars[hostname] = {}

hosts_with_vars = sum(1 for v in host_vars.values() if v)
log(f"  {hosts_with_vars}/{len(all_hostnames)} hosts com host_vars")


# ------------------------------------------------------------------
# 4. Cria grupos no banco
# ------------------------------------------------------------------
log(f"\n🗂  Criando grupos...")

# Busca grupos existentes
existing_grupos = api_get(f"/workspaces/{WORKSPACE_ID}/grupos") or []
existing_grupo_names = {g["nome"]: g["id"] for g in existing_grupos}

grupo_ids: dict[str, int] = dict(existing_grupo_names)

for grupo_nome, hosts in grupos_hosts.items():
    # vars do grupo
    vars_grupo = {}
    if grupo_nome == "all":
        vars_grupo = group_vars_all
    elif grupo_nome in group_vars_files:
        vars_grupo = group_vars_files[grupo_nome]

    if grupo_nome in existing_grupo_names:
        if UPDATE:
            grupo_id = existing_grupo_names[grupo_nome]
            result = api_patch(f"/workspaces/{WORKSPACE_ID}/grupos/{grupo_id}", {"vars": vars_grupo})
            if result:
                log_ok(f"Grupo '{grupo_nome}' atualizado (id={grupo_id}, {len(vars_grupo)} vars)")
            else:
                log_err(f"Grupo '{grupo_nome}' falhou ao atualizar")
        else:
            log_skip(f"Grupo '{grupo_nome}' já existe (use --update para sobrescrever)")
        continue

    payload = {"nome": grupo_nome, "vars": vars_grupo}
    result = api_post(f"/workspaces/{WORKSPACE_ID}/grupos", payload)
    if result == "__exists__":
        log_skip(f"Grupo '{grupo_nome}' duplicado, pulando")
    elif result:
        grupo_ids[grupo_nome] = result.get("id", 0)
        log_ok(f"Grupo '{grupo_nome}' criado (id={result.get('id')}, {len(hosts)} hosts)")


# ------------------------------------------------------------------
# 5. Detecta IP e ambiente de cada host a partir das host_vars
# ------------------------------------------------------------------
def detect_ip(hvars: dict, hostname: str):
    """Retorna IP real se existir, senão None. ansible_host fica nas vars."""
    import re
    ip_pattern = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
    for key in ["ip_address", "ansible_host"]:
        val = str(hvars.get(key, ""))
        if ip_pattern.match(val):
            return val
    return None

def detect_ambiente(hvars: dict, grupos: list[str]) -> str:
    if hvars.get("ambiente"):
        return hvars["ambiente"]
    if "linux_cloud_main_servers" in grupos:
        return "azure"
    hostname_lower = str(list(hvars.get("ansible_host", ""))).lower()
    if "azure" in hostname_lower:
        return "azure"
    return "onprem"

def detect_municipio(hvars: dict, hostname: str) -> str:
    for key in ["municipio", "ds_municipio", "php_city_name"]:
        val = hvars.get(key)
        if val:
            return str(val)
    return None


# ------------------------------------------------------------------
# 6. Cria hosts no banco
# ------------------------------------------------------------------
log(f"\n🖥  Criando hosts...")

# Busca hosts existentes
existing_hosts = api_get(f"/workspaces/{WORKSPACE_ID}/hosts") or []
existing_host_names = {h["hostname"] for h in existing_hosts}

criados = 0
pulados = 0
erros = 0

# mapa hostname -> id para updates
existing_host_map = {h["hostname"]: h["id"] for h in (api_get(f"/workspaces/{WORKSPACE_ID}/hosts") or [])}

atualizados = 0

for hostname in sorted(all_hostnames):
    hvars = host_vars.get(hostname, {})
    meus_grupos = [g for g, hosts in grupos_hosts.items() if hostname in hosts]
    meus_grupo_ids = [grupo_ids[g] for g in meus_grupos if g in grupo_ids and grupo_ids[g] != 0]
    ip = detect_ip(hvars, hostname)
    ambiente = detect_ambiente(hvars, meus_grupos)
    municipio = detect_municipio(hvars, hostname)
    vars_clean = {k: v for k, v in hvars.items() if k not in ("municipio", "ambiente")}

    if hostname in existing_host_map:
        if UPDATE:
            host_id = existing_host_map[hostname]
            patch_payload = {
                "ip_address": ip,
                "municipio": municipio,
                "ambiente": ambiente,
                "vars": vars_clean,
                "grupo_ids": meus_grupo_ids,
            }
            result = api_patch(f"/workspaces/{WORKSPACE_ID}/hosts/{host_id}", patch_payload)
            if result:
                log_ok(f"{hostname} -> atualizado")
                atualizados += 1
            else:
                log_err(f"{hostname} -> falhou ao atualizar")
                erros += 1
        else:
            log_skip(f"{hostname} já existe (use --update para sobrescrever)")
            pulados += 1
        continue

    payload = {
        "hostname": hostname,
        "ip_address": ip,
        "municipio": municipio,
        "ambiente": ambiente,
        "ativo": True,
        "vars": vars_clean,
        "grupo_ids": meus_grupo_ids,
    }

    result = api_post(f"/workspaces/{WORKSPACE_ID}/hosts", payload)
    if result == "__exists__":
        log_skip(f"{hostname} duplicado, pulando")
        pulados += 1
    elif result:
        log_ok(f"{hostname} -> ip={ip}, ambiente={ambiente}, grupos={meus_grupos}")
        criados += 1
    else:
        log_err(f"{hostname} -> falhou")
        erros += 1


# ------------------------------------------------------------------
# Resumo
# ------------------------------------------------------------------
log(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Migração {'(DRY-RUN) ' if DRY_RUN else ''}concluída
  Grupos  : {len(grupo_ids)}
  Hosts criados    : {criados}
  Hosts atualizados: {atualizados}
  Hosts pulados    : {pulados}
  Erros            : {erros}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")