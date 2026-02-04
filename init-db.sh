#!/bin/bash
set -e

echo "Creating databases..."

# Crear base de datos para vector store
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE database164;
EOSQL

# Crear base de datos para historial de chat
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE pdf_rag_history;
EOSQL

# Instalar extensión pgvector en ambas bases de datos
echo "Installing pgvector extension..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "database164" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "pdf_rag_history" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

echo "Databases created and extensions installed successfully!"
