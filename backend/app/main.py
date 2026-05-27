import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.auth import LoginRequest, login, logout, require_session
from app.routers import grupos, hosts, inventory, vault, tokens

IS_PROD = os.getenv("ENVIRONMENT", "development") == "production"

# desabilita /docs e /redoc em produção
docs_url = None if IS_PROD else "/docs"
redoc_url = None if IS_PROD else "/redoc"
openapi_url = None if IS_PROD else "/openapi.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Ansiventory UI",
    description="Inventário dinâmico Ansible com backend PostgreSQL",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

# CORS — origins explícitos em produção
allowed_origins = (
    [os.getenv("FRONTEND_URL", "https://ansiventory.bauhaus.systems")]
    if IS_PROD
    else ["http://localhost:3000", "http://localhost:3001"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if IS_PROD:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# ------------------------------------------------------------------
# Auth — rotas públicas
# ------------------------------------------------------------------
app.post("/auth/login", tags=["auth"])(login)
app.post("/auth/logout", tags=["auth"])(logout)


@app.get("/auth/me", tags=["auth"])
async def me(session: dict = Depends(require_session)):
    return session


# ------------------------------------------------------------------
# Routers protegidos
# ------------------------------------------------------------------
app.include_router(inventory.router)
app.include_router(hosts.router)
app.include_router(grupos.router)
app.include_router(vault.router)
app.include_router(tokens.router)


# Health — público (para probes k8s)
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ansiventory-ui"}
