# Ansiventory UI

Inventário dinâmico Ansible com backend PostgreSQL e interface web.

## O problema que resolve

Gerenciar inventário Ansible em arquivos YAML estáticos (`hosts.yml`, `host_vars/`) não escala quando você tem dezenas de hosts em múltiplos ambientes e clientes. Qualquer mudança exige editar arquivos manualmente, sem histórico, sem interface, sem fonte de verdade centralizada.

O Ansiventory substitui esses arquivos por um banco PostgreSQL acessível de qualquer lugar, com uma UI para gerenciar hosts e variáveis, e um endpoint HTTP que o Ansible consome como inventário dinâmico.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + SQLAlchemy async + asyncpg |
| Banco | PostgreSQL (CloudNativePG em produção) |
| Frontend | Nuxt 3 + Tailwind CSS |
| Auth | httpOnly cookie + Bearer token |
| Deploy | AKS + ArgoCD + Traefik + cert-manager |
| Secrets | External Secrets Operator + OpenBao |

---

## Desenvolvimento local

### Pré-requisitos

- Docker + Docker Compose
- Node.js 20+
- Python 3.12+

### Subir o ambiente

```bash
# clone o repo
git clone https://github.com/sysadmin-systems/ansiventory-ui
cd ansiventory-ui

# copia e edita as variáveis de ambiente
cp .env.example .env

# sobe o banco e o backend
docker compose up -d

# instala e sobe o frontend
cd frontend
npm install
npm run dev
```

A UI estará disponível em `http://localhost:3001`.
A API estará disponível em `http://localhost:8000`.
Documentação da API: `http://localhost:8000/docs`.

### Inicializar o banco

```bash
# aplica o schema e dados de exemplo
docker exec -i ansiventory_db psql -U ansiventory -d ansiventory < sql/ansiventory_schema.sql
```

### Criar o primeiro token de acesso

```bash
# gera um token seguro
TOKEN=$(openssl rand -hex 32)
echo "Token: $TOKEN"

# insere no banco
docker exec ansiventory_db psql -U ansiventory -d ansiventory -c \
  "INSERT INTO api_tokens (workspace_id, token_hash, descricao)
   VALUES (1, encode(digest('$TOKEN', 'sha256'), 'hex'), 'admin');"
```

Acesse `http://localhost:3001/login` com o workspace `tecnologica` e o token gerado.

---

## Migração do inventário existente

Se você já tem um inventário Ansible (`hosts.yml` + `host_vars/`), use o script de migração:

```bash
pip install pyyaml requests

# dry-run primeiro
python3 sql/migrate_inventory.py \
  --inventory /caminho/para/inventory \
  --api http://localhost:8000 \
  --workspace 1 \
  --dry-run

# migração real
ANSIVENTORY_TOKEN=seu-token python3 sql/migrate_inventory.py \
  --inventory /caminho/para/inventory \
  --api http://localhost:8000 \
  --workspace 1
```

---

## Inventário dinâmico no Ansible

Crie o arquivo `inventario.py` no seu projeto Ansible:

```python
#!/usr/bin/env python3
import urllib.request, os, sys

url = os.environ.get("ANSIVENTORY_URL", "http://localhost:8000/inventory/tecnologica")
token = os.environ.get("ANSIVENTORY_TOKEN")

if not token:
    print("ERRO: variável ANSIVENTORY_TOKEN não definida", file=sys.stderr)
    sys.exit(1)

req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req) as r:
    print(r.read().decode())
```

```bash
chmod +x inventario.py
```

No `ansible.cfg`:

```ini
[defaults]
inventory = inventario.py
```

Uso:

```bash
ANSIVENTORY_TOKEN=seu-token ansible-playbook playbook.yml --limit=tubarao-sc
ANSIVENTORY_TOKEN=seu-token ansible-playbook playbook.yml --limit=linux_cloud_main_servers
```

---

## Deploy em produção (AKS + ArgoCD)

### Pré-requisitos no cluster

- Traefik como Ingress Controller
- cert-manager com ClusterIssuer configurado para Cloudflare
- External Secrets Operator conectado ao OpenBao
- CloudNativePG operator instalado
- ArgoCD

### Secrets no OpenBao

Crie os secrets no caminho `secret/ansiventory/database`:

```bash
bao kv put secret/ansiventory/database \
  username=ansiventory \
  password=sua-senha-segura \
  dbname=ansiventory
```

### Deploy via ArgoCD

```bash
# aplica o ArgoCD Application — ele cuida do resto
kubectl apply -f infra/k8s/argocd-app.yaml
```

O ArgoCD vai sincronizar automaticamente todos os manifests de `infra/k8s/` e manter o cluster em sync com o repositório.

### Ajustes necessários antes do deploy

Edite os seguintes valores nos manifests:

| Arquivo | Campo | Valor padrão | Ajuste para |
|---|---|---|---|
| `k8s/ingress.yaml` | `dnsNames` | `ansiventory.bauhaus.systems` | seu domínio |
| `k8s/ingress.yaml` | `issuerRef.name` | `letsencrypt-prod` | nome do seu ClusterIssuer |
| `k8s/backend/deployment.yaml` | `image` | `bauhaussistemas/ansiventory-backend:latest` | seu registry |
| `k8s/frontend/deployment.yaml` | `image` | `bauhaussistemas/ansiventory-frontend:latest` | seu registry |
| `k8s/database/cluster.yaml` | `storageClass` | `managed-csi` | storageClass do seu AKS |
| `k8s/external-secret.yaml` | `server` | `https://bao.bauhaus.cloud:8200` | URL do seu OpenBao |

### Build e push das imagens

```bash
# backend
docker build -t seu-registry/ansiventory-backend:latest ./backend
docker push seu-registry/ansiventory-backend:latest

# frontend
docker build -t seu-registry/ansiventory-frontend:latest ./frontend
docker push seu-registry/ansiventory-frontend:latest
```

---

## Estrutura do projeto

```
ansiventory-ui/
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── routers/
│   │   │   ├── hosts.py
│   │   │   ├── grupos.py
│   │   │   ├── inventory.py
│   │   │   ├── vault.py
│   │   │   └── tokens.py
│   │   └── schemas/
│   └── Dockerfile
├── frontend/                 # Nuxt 3
│   ├── pages/
│   │   ├── login.vue
│   │   ├── hosts/
│   │   ├── grupos.vue
│   │   ├── vault.vue
│   │   └── settings.vue
│   ├── components/
│   ├── composables/
│   ├── stores/
│   └── Dockerfile
├── infra/
│   └── k8s/                  # Manifests Kubernetes
│       ├── argocd-app.yaml
│       ├── namespace.yaml
│       ├── ingress.yaml
│       ├── external-secret.yaml
│       ├── backend/
│       ├── frontend/
│       └── database/
├── sql/
│   ├── ansiventory_schema.sql
│   └── migrate_inventory.py
└── docker-compose.yml
```

---

## Funcionalidades

- **Hosts** — CRUD completo com busca, filtros por ambiente e grupo
- **Variáveis** — edição inline, suporte a `!vault` (Ansible Vault)
- **Grupos** — gerenciamento de group_vars com membros
- **Vault Tool** — criptografar e descriptografar valores via ansible-vault
- **Inventário dinâmico** — endpoint HTTP consumido pelo Ansible como script
- **Audit log** — histórico de alterações por host
- **Settings** — gerenciamento de tokens de API e upload de logo

---

## Licença

Proprietário — Tecnológica Sistemas
