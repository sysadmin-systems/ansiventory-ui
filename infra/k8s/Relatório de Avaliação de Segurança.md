# Relatório de Avaliação de Segurança (Read-Only)
## Projeto: Ansiventory UI (`/home/sysadmin/dev/ansiventory-ui`)

**Data da análise:** 27/05/2026  
**Modo:** somente leitura (análise estática de código e configuração; sem alterações, sem testes dinâmicos de penetração)

---

## 1. Resumo executivo

O Ansiventory UI é uma aplicação de inventário Ansible com **backend FastAPI**, **frontend Nuxt 3**, **PostgreSQL** e deploy previsto em **AKS/ArgoCD** com TLS e **External Secrets (OpenBao)**.

**Pontos positivos observados:**
- Tokens de API armazenados como hash SHA-256 (não em texto claro no banco).
- Sessão web via cookie `httpOnly` (token não exposto ao `localStorage` no frontend).
- Consultas SQL majoritariamente parametrizadas (SQLAlchemy/`text()` com bind params).
- Segredos de DB em K8s via External Secrets; TLS no Ingress de produção.
- `.env` está no `.gitignore`.

**Riscos principais (ação imediata):**
1. **Autorização ausente ou incompleta** em múltiplos endpoints — inventário, hosts e grupos acessíveis **sem autenticação**, permitindo leitura e escrita não autorizada.
2. **Falta de isolamento por workspace (IDOR)** — mesmo endpoints “protegidos” não validam se a sessão pertence ao `workspace_id` da URL.
3. **Documentação promete Bearer token**, mas o backend **não implementa** `Authorization: Bearer`; o inventário público contradiz o modelo documentado.
4. **Exposição de infraestrutura** em `docker-compose` (PostgreSQL na porta do host, `network_mode: host`, pgAdmin fraco).
5. **Superfície de ataque ampliada**: `/docs` OpenAPI, vault via `subprocess`, senhas em arquivos temporários, sem rate limiting.

**Classificação geral:** risco **alto** em ambiente exposto à rede; adequado apenas para desenvolvimento local isolado até correções de autorização.

---

## 2. Metodologia e escopo

### O que foi analisado
| Área | Artefatos |
|------|-----------|
| Autenticação/autorização | `backend/app/auth.py`, routers, `frontend/stores/auth.ts`, `frontend/middleware/auth.ts` |
| Segredos | `.env.example`, `.gitignore`, `infra/k8s/external-secret.yaml`, `docker-compose.yml` |
| Validação / injeção | Routers, `schemas.py`, `migrate_inventory.py` |
| CORS e headers | `backend/app/main.py`, `frontend/nuxt.config.ts` |
| Dependências | `backend/requirements.txt`, `pyproject.toml`, `frontend/package.json`, `uv.lock`, `package-lock.json` |
| Logs/erros/API | Respostas HTTPException, `/auth/me`, inventário |
| Docker/K8s | `docker-compose.yml`, Dockerfiles, `infra/k8s/*` |
| Migração | `migrate_inventory.py` |
| Frontend | Páginas, `useApi.ts`, `localStorage` (logo) |
| OWASP Top 10 | Mapeamento por achado |

### O que **não** foi verificado estaticamente
- Varredura automatizada de CVEs (`npm audit`, `pip-audit`, Trivy) — **não executada**.
- Comportamento em runtime (cookies reais, Traefik, pg_hba, políticas de rede K8s).
- Testes de penetração, fuzzing, ou configuração do cluster fora dos manifests do repositório.
- Schema SQL completo (`sql/ansiventory_schema.sql` referenciado no README **não está** no repositório atual).

---

## 3. Achados por severidade

### Crítico

---

#### C-01 — Endpoints de inventário e workspaces públicos (sem autenticação)

**Descrição:** Qualquer cliente pode listar workspaces e obter o inventário Ansible completo (hosts, grupos, `hostvars` mescladas), incluindo variáveis potencialmente sensíveis (senhas em vault cifrado, chaves, `ansible_host`, etc.).

**Evidência:**

```14:17:backend/app/routers/inventory.py
@router.get("/workspaces", response_model=list[WorkspaceOut])
async def list_workspaces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).order_by(Workspace.name))
```

```20:21:backend/app/routers/inventory.py
@router.get("/inventory/{workspace_slug}")
async def get_inventory(workspace_slug: str, db: AsyncSession = Depends(get_db)):
```

`require_session` é importado mas **não usado** neste router.

**Impacto:** Exfiltração massiva de inventário de infraestrutura; violação de confidencialidade (OWASP A01 Broken Access Control, A02 Cryptographic Failures se vars contiverem segredos).

**Sugestão de correção:**
- Exigir autenticação em `/workspaces` e `/inventory/*` (cookie de sessão **ou** Bearer token documentado).
- Para Ansible, usar token de serviço com escopo mínimo (somente leitura de inventário do workspace).
- Não expor inventário na Internet sem mTLS ou rede privada.

---

#### C-02 — CRUD de hosts e grupos majoritariamente sem autenticação

**Descrição:** Operações de leitura, criação e exclusão em hosts e grupos não declaram `Depends(require_session)`.

**Evidência (exemplos):**

```65:66:backend/app/routers/hosts.py
@router.get("/{host_id}", response_model=HostOut)
async def get_host(workspace_id: int, host_id: int, db: AsyncSession = Depends(get_db)):
```

```94:95:backend/app/routers/hosts.py
@router.post("", response_model=HostOut, status_code=201)
async def create_host(workspace_id: int, payload: HostCreate, db: AsyncSession = Depends(get_db)):
```

```175:176:backend/app/routers/hosts.py
@router.delete("/{host_id}", status_code=204)
async def delete_host(workspace_id: int, host_id: int, db: AsyncSession = Depends(get_db)):
```

```13:14:backend/app/routers/grupos.py
@router.get("", response_model=list[GrupoOut])
async def list_grupos(workspace_id: int, db: AsyncSession = Depends(get_db)):
```

```34:35:backend/app/routers/grupos.py
@router.post("", response_model=GrupoOut, status_code=201)
async def create_grupo(workspace_id: int, payload: GrupoCreate, db: AsyncSession = Depends(get_db)):
```

Endpoints **com** auth: `list_hosts`, `update_host` (parcial); `update_grupo` (parcial); `tokens/*`; `vault/*`.

**Impacto:** Qualquer atacante pode criar, alterar (onde não há auth), excluir hosts/grupos e ler vars/audit — comprometimento de integridade e disponibilidade do inventário.

**Sugestão de correção:**
- Aplicar `require_session` (ou dependency central) em **todos** os handlers.
- Middleware global de autenticação com lista de rotas públicas explícita (`/health`, `/auth/login`).

---

#### C-03 — IDOR entre workspaces (sem vínculo sessão ↔ `workspace_id`)

**Descrição:** Mesmo com sessão válida, **não há verificação** de que `session["workspace_id"] == workspace_id` da rota. Um token do workspace A pode operar no workspace B alterando o ID na URL.

**Evidência:** Busca por validação cruzada — **nenhuma ocorrência** de `session["workspace_id"]` comparado ao path nos routers.

Exemplo de endpoint “protegido” sem isolamento:

```27:32:backend/app/routers/tokens.py
@router.get("", response_model=list[TokenOut])
async def list_tokens(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    _session: dict = Depends(require_session),
):
```

**Impacto:** Escalação horizontal entre tenants/workspaces; gestão de tokens e dados de outros clientes.

**Sugestão de correção:**
- Dependency `require_workspace_access(workspace_id, session)` usada em todos os routers prefixados por `/workspaces/{workspace_id}`.
- Retornar `403` quando o workspace não corresponder à sessão.

---

### Alto

---

#### A-01 — Documentação/README promete Bearer; backend só valida cookie

**Descrição:** README e `migrate_inventory.py` usam `Authorization: Bearer`, mas `require_session` lê apenas cookie `ansiventory_session`.

**Evidência:**

```55:65:backend/app/auth.py
async def require_session(
    ansiventory_session: str | None = Cookie(default=None),
    ...
):
```

```64:64:migrate_inventory.py
AUTH_HEADERS = {"Authorization": f"Bearer {TOKEN}"}
```

```117:119:README.md
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
```

**Impacto:** Falsa sensação de segurança; scripts podem “funcionar” apenas porque endpoints estão **públicos** (C-01/C-02), não por Bearer válido.

**Sugestão:** Implementar `HTTPBearer` opcional **ou** corrigir documentação; unificar modelo de auth para automação (Ansible) vs UI (cookie).

---

#### A-02 — Cookie de sessão armazena o token API em texto claro

**Descrição:** Após login, o valor do cookie é o token bruto, não um ID de sessão opaco.

**Evidência:**

```78:86:backend/app/auth.py
    response.set_cookie(
        key=SESSION_COOKIE,
        value=payload.token,
        httponly=True,
        secure=IS_PROD,
        ...
    )
```

**Impacto:** Roubo de cookie = roubo direto do token de API; logout não revoga o token no servidor (apenas remove cookie).

**Sugestão:** Sessão server-side (session ID aleatório + store Redis/DB) ou JWT de curta duração; rotação no login; opção de revogação.

---

#### A-03 — Tokens API sem expiração por padrão

**Descrição:** Criação de token não define `expires_at`.

**Evidência:**

```60:64:backend/app/routers/tokens.py
    token = ApiToken(
        workspace_id=workspace_id,
        token_hash=token_hash,
        descricao=payload.descricao,
    )
```

Validação aceita `expires_at IS NULL`:

```41:42:backend/app/auth.py
              AND (t.expires_at IS NULL OR t.expires_at > NOW())
```

**Impacto:** Comprometimento permanente até revogação manual.

**Sugestão:** TTL obrigatório, rotação, auditoria de uso.

---

#### A-04 — Ingress expõe rotas sensíveis do backend no mesmo host

**Evidência:**

```58:71:infra/k8s/ingress.yaml
    - match: Host(`ansiventory.bauhaus.systems`) && PathPrefix(`/inventory`)
    ...
    - match: Host(`ansiventory.bauhaus.systems`) && PathPrefix(`/workspaces`)
    ...
    - match: Host(`ansiventory.bauhaus.systems`) && PathPrefix(`/vault`)
```

Combinado com C-01/C-02, inventário e vault ficam acessíveis na borda pública se o backend estiver alcançável.

**Sugestão:** Exigir auth em todas as rotas; WAF/rate limit no Ingress; restringir `/vault` a rede interna.

---

#### A-05 — Endpoint vault executa `ansible-vault` com dados do usuário

**Descrição:** `subprocess.run` com senhas em arquivos temporários no filesystem do container.

**Evidência:**

```24:30:backend/app/routers/vault.py
def _write_password_file(password: str) -> str:
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.pass', delete=False)
    tmp.write(password.strip() + '\n')
```

```41:50:backend/app/routers/vault.py
        result = subprocess.run(
            [
                "ansible-vault", "encrypt_string",
                "--vault-password-file", pass_file,
```

**Impacto:** Risco de vazamento via `/tmp`, side-channel, DoS por subprocess; plaintext de segredos em memória/logs se stderr vazar.

**Sugestão:** Isolar em worker dedicado; limites de tamanho/rate; biblioteca Python de vault em vez de CLI; garantir `chmod 0600` nos temporários.

---

#### A-06 — PostgreSQL exposto no host via Docker Compose

**Evidência:**

```30:31:docker-compose.yml
    ports:
      - "${POSTGRES_HOST_PORT:-5432}:5432"
```

```50:50:docker-compose.yml
    network_mode: host
```

**Impacto:** Ataque direto ao banco se credenciais fracas ou rede acessível.

**Sugestão:** Remover publish de porta em produção; usar rede bridge interna; não usar `network_mode: host` sem necessidade.

---

### Médio

---

#### M-01 — CORS restrito a localhost; produção pode estar mal configurada

**Evidência:**

```22:28:backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Impacto:** Em produção com outro domínio, UI pode falhar **ou** alguém pode ampliar `allow_origins` para `*` com credentials (erro grave). Não verificado estaticamente o proxy Traefik.

**Sugestão:** `allow_origins` via variável de ambiente com domínio de produção; nunca `*` com `allow_credentials=True`.

---

#### M-02 — `ENVIRONMENT` vs `APP_ENV` — flag de cookie `Secure` pode não ativar

**Evidência:**

```14:14:backend/app/auth.py
IS_PROD = os.getenv("ENVIRONMENT", "development") == "production"
```

```122:122:docker-compose.yml
      APP_ENV:           ${APP_ENV:-development}
```

Compose define `APP_ENV`, não `ENVIRONMENT`. K8s define `ENVIRONMENT=production` corretamente.

**Impacto:** Cookies sem `Secure` em deploy Docker “produção”; session hijack em HTTP.

**Sugestão:** Unificar variável; falhar startup se produção sem HTTPS.

---

#### M-03 — Sem rate limiting no login e APIs

**Evidência:** Nenhum `slowapi`, middleware ou limite em `auth.login` ou routers.

**Impacto:** Brute force de tokens; DoS em vault/subprocess.

**Sugestão:** Rate limit por IP no Ingress ou FastAPI; backoff exponencial; CAPTCHA opcional.

---

#### M-04 — OpenAPI/Swagger provavelmente exposto (padrão FastAPI)

**Evidência:** `FastAPI()` sem `docs_url=None` em `main.py`.

**Impacto:** Enumeração de API (OWASP A05 Security Misconfiguration).

**Sugestão:** Desabilitar `/docs` e `/redoc` em produção ou proteger com auth.

---

#### M-05 — `/auth/me` retorna metadados da sessão sem filtrar

**Evidência:**

```37:39:backend/app/main.py
@app.get("/auth/me", tags=["auth"])
async def me(session: dict = Depends(require_session)):
    return session
```

Retorno inclui campos do `_validate_token` (`id`, `workspace_id`, `descricao`, `expires_at`, `workspace_slug`).

**Impacto:** Exposição desnecessária de metadados; facilita reconhecimento.

**Sugestão:** DTO mínimo (`workspace`, `workspace_id`).

---

#### M-06 — Hash SHA-256 simples para tokens (sem trabalho adaptativo)

**Evidência:**

```17:18:backend/app/auth.py
def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

**Impacto:** Tokens têm alta entropia (`secrets.token_hex(32)`), mitigando brute force offline; porém, vazamento de DB + tokens fracos futuros seria problemático. Não é bcrypt/argon2.

**Sugestão:** HMAC com pepper em KMS **ou** Argon2id para hashes de API key.

---

#### M-07 — pgAdmin com configuração fraca (profile opcional)

**Evidência:**

```83:84:docker-compose.yml
      PGADMIN_CONFIG_SERVER_MODE: "False"
      PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED: "False"
```

**Impacto:** Interface admin de DB com superfície extra se profile ativado em rede exposta.

**Sugestão:** Não usar em produção; VPN apenas.

---

#### M-08 — Volume bind `./backend:/app` no compose

**Evidência:**

```128:129:docker-compose.yml
    volumes:
      - ./backend:/app
```

**Impacto:** Risco em ambiente compartilhado (hot-reload); não padrão para produção.

---

#### M-09 — Dockerfile backend com `--reload`

**Evidência:**

```20:20:backend/Dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

K8s sobrescreve o comando (sem reload). Imagem Docker local ainda arriscada.

---

#### M-10 — CSRF em endpoints autenticados por cookie

**Descrição:** Mutações via cookie `SameSite=lax` (dev) ou `strict` (prod) reduzem CSRF, mas POST/PATCH/DELETE autenticados permanecem vulneráveis a cenários cross-site em `lax` ou bugs de browser.

**Evidência:** Cookie auth + `useApi` sem token CSRF:

```3:7:frontend/composables/useApi.ts
    const res = await fetch(`/api${path}`, {
      ...options,
      credentials: 'include',
```

**Impacto:** Médio enquanto C-02 existir (ataque nem precisa de CSRF); após correção de auth, CSRF volta a ser relevante para UI.

**Sugestão:** `SameSite=Strict`, token CSRF double-submit, ou usar apenas Bearer para mutações.

---

#### M-11 — Middleware frontend ignora SSR

**Evidência:**

```4:5:frontend/middleware/auth.ts
  if (import.meta.server) return
```

**Impacto:** Páginas podem renderizar no servidor sem checagem de auth (dados sensíveis no HTML inicial — **não verificado** se páginas buscam dados no SSR).

**Sugestão:** Guard server-side no Nitro ou `useFetch` com credenciais apenas client-side + rotas sem dados sensíveis no SSR.

---

### Baixo

---

#### B-01 — Logo em `localStorage` (data URL)

**Evidência:**

```298:298:frontend/pages/settings.vue
    localStorage.setItem('ansiventory_logo', result)
```

**Impacto:** XSS futuro poderia ler logo; SVG malicioso em `<img src>` tem risco limitado. Não armazena token de API.

**Sugestão:** Validar MIME magic bytes; preferir PNG; CSP restritiva.

---

#### B-02 — Script de migração envia payloads para API sem TLS enforcement

**Evidência:** `--api http://localhost:8000` padrão; token em header se endpoints exigirem auth no futuro.

**Sugestão:** Exigir HTTPS fora de localhost; usar variáveis de ambiente para secrets.

---

#### B-03 — `get_inventory_plugin_config` gera URL incorreta

**Evidência:**

```105:113:backend/app/routers/inventory.py
    base_url = f"http://{settings.postgres_host}:8000"
    ...
url: {base_url}/inventory/{workspace_slug}
```

**Impacto:** Misconfiguration operacional, não exploit direto.

---

#### B-04 — Container provavelmente roda como root

**Evidência:** Dockerfiles sem `USER` não privilegiado.

**Sugestão:** Usuário não-root no backend/frontend.

---

#### B-05 — Devtools Nuxt habilitado

**Evidência:**

```2:2:frontend/nuxt.config.ts
  devtools: { enabled: true },
```

**Impacto:** Possível exposição de ferramentas em build se não desabilitado por ambiente — **não verificado** no artefato `.output` de produção.

---

### Informativo

---

#### I-01 — Boas práticas já presentes
- `.env` no `.gitignore`; External Secrets no K8s; TLS via cert-manager; roles PostgreSQL separadas em `02_roles.sql`; tokens gerados com `secrets.token_hex(32)`.

#### I-02 — SQL injection
- Uso de parâmetros nomeados; `ilike` com valor bound em `list_hosts` — baixo risco de SQLi clássico.

#### I-03 — XSS no frontend
- Interpolação Vue `{{ }}` em `VarsTable.vue` — escape padrão; sem `v-html` nas páginas da aplicação (exceto artefatos gerados `.nuxt`).

#### I-04 — Dependências (versões fixadas, CVEs não auditadas)

| Pacote | Versão |
|--------|--------|
| fastapi | 0.115.0 |
| uvicorn | 0.30.6 |
| sqlalchemy | 2.0.35 |
| nuxt | ^3.15.0 |
| vue | ^3.5.0 |

**Recomendação:** executar `pip-audit`, `npm audit`, Trivy nas imagens — **não verificado estaticamente**.

#### I-05 — RBAC
- Não há papéis (admin/read-only); um token = acesso total ao workspace (quando auth funcionar).

#### I-06 — HTTPS/TLS
- Produção: Ingress `websecure` + cert-manager — **assumido correto se cluster configurado**.
- Dev: HTTP explícito — aceitável localmente.

#### I-07 — Auditoria
- `changed_by` fixo como `"api"` — sem identificação do token/usuário.

---

## 4. Mapeamento OWASP Top 10 (2021) — resumo

| OWASP | Relevância no projeto |
|-------|------------------------|
| A01 Broken Access Control | **Crítica** (C-01, C-02, C-03) |
| A02 Cryptographic Failures | Inventário público; SHA-256; cookies |
| A03 Injection | Baixa em SQL; subprocess vault |
| A04 Insecure Design | Auth dual inconsistente; sem RBAC |
| A05 Security Misconfiguration | Docker, CORS, docs, pgAdmin |
| A06 Vulnerable Components | Auditar dependências |
| A07 Auth Failures | Sem rate limit; tokens eternos |
| A08 Software/Data Integrity | Não avaliado (supply chain) |
| A09 Logging/Monitoring | Sem evidência de SIEM/alertas |
| A10 SSRF | Não identificado |

---

## 5. Checklist de prioridades recomendadas

| Prioridade | Ação |
|------------|------|
| P0 | Adicionar autenticação obrigatória em **todos** os endpoints exceto `/health` e `/auth/login` |
| P0 | Implementar verificação `session.workspace_id == workspace_id` em todas as rotas de workspace |
| P0 | Proteger `/inventory/*` com token (Bearer ou header dedicado) + bloquear acesso anônimo |
| P1 | Implementar Bearer token conforme documentação **ou** corrigir README/scripts |
| P1 | Substituir cookie com token bruto por sessão opaca server-side |
| P1 | Definir `expires_at` padrão nos tokens; revogação e auditoria |
| P1 | Desabilitar `/docs` em produção; adicionar security headers (HSTS, CSP, X-Frame-Options) no Traefik ou app |
| P2 | Rate limiting (login, vault, inventário) |
| P2 | Corrigir `ENVIRONMENT`/`APP_ENV`; garantir `Secure` + `SameSite=Strict` em produção |
| P2 | Fechar porta PostgreSQL no host; remover `network_mode: host` onde possível |
| P2 | Endurecer endpoint vault (limites, worker isolado) |
| P3 | `pip-audit` / `npm audit` / scan de imagens no CI |
| P3 | Usuário não-root nos containers; desabilitar Nuxt devtools em prod |
| P3 | RBAC (leitura vs escrita) e atribuição em audit log |

---

## 6. Conclusão

O projeto demonstra **intenção** de segurança (hash de tokens, cookies `httpOnly`, External Secrets, TLS no K8s), mas a implementação atual apresenta **falhas graves de controle de acesso** que anulam esses controles em qualquer ambiente acessível na rede. A discrepância entre documentação (Bearer + inventário “seguro”) e código (endpoints públicos, só cookie) agrava o risco operacional.

**Recomendação:** tratar correções P0 como bloqueante para qualquer exposição além de `localhost` isolado; em seguida validar com testes automatizados de autorização (matriz endpoint × auth × workspace).

---

*Relatório gerado por análise estática read-only. Para validação dinâmica (pentest, scans de CVE, configuração efetiva do cluster), é necessário ambiente de teste e ferramentas de scanning em pipeline.*