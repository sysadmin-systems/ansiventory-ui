#!/bin/bash
# ==============================================================
#  Ansiventory UI — setup da estrutura de pastas
#  Rode na raiz do repositório clonado
# ==============================================================

set -e

ROOT=$(pwd)

echo "🗂  Criando estrutura em: $ROOT"

# Backend FastAPI
mkdir -p backend/app/{models,routers,schemas}

# Frontend Nuxt3
mkdir -p frontend/{components,pages,composables,layouts,assets}

# Plugin Ansible
mkdir -p plugin

# Infraestrutura (já existe parte, completa o restante)
mkdir -p docker/postgres/{init,conf}
mkdir -p infra/{k8s,scripts}

# SQL
mkdir -p sql

# Arquivos __init__.py do backend
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/app/routers/__init__.py
touch backend/app/schemas/__init__.py

echo ""
echo "✅  Estrutura criada:"
echo ""
find . \
  -not -path '*/.git/*' \
  -not -path '*/node_modules/*' \
  -not -name '.gitkeep' \
  | sort \
  | sed 's|[^/]*/|  |g'

echo ""
echo "Próximo passo: copie os arquivos gerados para cada pasta e rode:"
echo "  docker compose up -d"
