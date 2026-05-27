from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.auth import LoginRequest, login, logout, require_session
from app.routers import grupos, hosts, inventory, vault, tokens


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Ansiventory UI",
    description="Inventário dinâmico Ansible com backend PostgreSQL",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # frontend Nuxt3
    allow_credentials=True,                   # necessário para cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Auth — público (sem cookie)
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


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ansiventory-ui"}
