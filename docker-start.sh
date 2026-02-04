#!/bin/bash

# Script de ayuda para iniciar la aplicación RAG con Docker

set -e

echo "🚀 Iniciando aplicación RAG con Docker..."
echo ""

# Verificar que existe .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "📝 Creando .env desde .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Archivo .env creado. Por favor, edítalo y configura tu OPENAI_API_KEY"
        echo "   nano .env"
        exit 1
    else
        echo "❌ Error: No se encontró .env.example"
        exit 1
    fi
fi

# Verificar que OPENAI_API_KEY esté configurada
if ! grep -q "OPENAI_API_KEY=.*[^=]$" .env 2>/dev/null || grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env 2>/dev/null; then
    echo "⚠️  OPENAI_API_KEY no está configurada en .env"
    echo "   Por favor, edita .env y configura tu clave de API de OpenAI"
    exit 1
fi

echo "✅ Configuración verificada"
echo ""

# Construir imágenes
echo "🔨 Construyendo imágenes Docker..."
docker compose build

echo ""
echo "🚀 Iniciando contenedores..."
docker compose up -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 5

echo ""
echo "✅ Aplicación iniciada!"
echo ""
echo "📊 Servicios disponibles:"
echo "   - Frontend:  http://localhost:3001"
echo "   - Backend:   http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/docs"
echo ""
echo "📝 Para ver los logs:"
echo "   docker compose logs -f"
echo ""
echo "🛑 Para detener:"
echo "   docker compose down"
echo ""
