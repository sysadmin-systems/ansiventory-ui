from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer,
    String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    hosts: Mapped[list["Host"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    grupos: Mapped[list["Grupo"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    api_tokens: Mapped[list["ApiToken"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")


class Grupo(Base):
    __tablename__ = "grupos"
    __table_args__ = (UniqueConstraint("workspace_id", "nome"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    vars: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace: Mapped["Workspace"] = relationship(back_populates="grupos")
    host_grupos: Mapped[list["HostGrupo"]] = relationship(back_populates="grupo", cascade="all, delete-orphan")


class Host(Base):
    __tablename__ = "hosts"
    __table_args__ = (
        UniqueConstraint("workspace_id", "hostname"),
        Index("idx_hosts_workspace", "workspace_id"),
        Index("idx_hosts_ambiente", "ambiente"),
        Index("idx_hosts_ativo", "ativo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    hostname: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[str] = mapped_column(INET, nullable=False)
    municipio: Mapped[Optional[str]] = mapped_column(Text)
    ambiente: Mapped[Optional[str]] = mapped_column(String(20))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    vars: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace: Mapped["Workspace"] = relationship(back_populates="hosts")
    host_grupos: Mapped[list["HostGrupo"]] = relationship(back_populates="host", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="host")


class HostGrupo(Base):
    __tablename__ = "host_grupos"

    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), primary_key=True)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupos.id", ondelete="CASCADE"), primary_key=True)

    host: Mapped["Host"] = relationship(back_populates="host_grupos")
    grupo: Mapped["Grupo"] = relationship(back_populates="host_grupos")


class ApiToken(Base):
    __tablename__ = "api_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    workspace: Mapped["Workspace"] = relationship(back_populates="api_tokens")


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index("idx_audit_host", "host_id"),
        Index("idx_audit_changed_at", "changed_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    host_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hosts.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(Text, nullable=False)
    diff: Mapped[Optional[dict]] = mapped_column(JSONB)
    changed_by: Mapped[str] = mapped_column(Text, nullable=False, server_default="system")
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    host: Mapped[Optional["Host"]] = relationship(back_populates="audit_logs")
