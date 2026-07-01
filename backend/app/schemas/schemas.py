from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


# ------------------------------------------------------------------
# Workspace
# ------------------------------------------------------------------
class WorkspaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    created_at: datetime


# ------------------------------------------------------------------
# Grupo
# ------------------------------------------------------------------
class GrupoCreate(BaseModel):
    nome: str
    vars: dict[str, Any] = {}


class GrupoUpdate(BaseModel):
    nome: Optional[str] = None
    vars: Optional[dict[str, Any]] = None


class GrupoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    nome: str
    vars: dict[str, Any]
    updated_at: datetime


# ------------------------------------------------------------------
# Host
# ------------------------------------------------------------------
class HostCreate(BaseModel):
    hostname: str
    ip_address: Optional[str]
    municipio: Optional[str] = None
    ambiente: Optional[str] = None
    ativo: bool = True
    vars: dict[str, Any] = {}
    grupo_ids: list[int] = []


class HostUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    municipio: Optional[str] = None
    ambiente: Optional[str] = None
    ativo: Optional[bool] = None
    vars: Optional[dict[str, Any]] = None
    grupo_ids: Optional[list[int]] = None


class HostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    hostname: str
    ip_address: Optional[str]
    municipio: Optional[str]
    ambiente: Optional[str]
    ativo: bool
    vars: dict[str, Any]
    updated_at: datetime
    grupos: list[str] = []


class VarDetail(BaseModel):
    value: Any
    source: str           # "host" | "group"
    group: Optional[str] = None      # nome do grupo de origem
    overrides: Optional[str] = None  # nome do grupo que está sendo sobrescrito


class HostVarsOut(BaseModel):
    hostname: str
    vars_final: dict[str, Any]
    vars_detail: dict[str, VarDetail] = {}


# ------------------------------------------------------------------
# Audit
# ------------------------------------------------------------------
class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    host_id: Optional[int]
    action: str
    diff: Optional[dict[str, Any]]
    changed_by: str
    changed_at: datetime
