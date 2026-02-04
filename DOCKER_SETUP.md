# 🐳 Guía de Configuración Docker

Esta guía te ayudará a ejecutar la aplicación RAG completamente en contenedores Docker.

## 📋 Prerrequisitos

1. **Docker** instalado (versión 20.10 o superior)
2. **Docker Compose** instalado (versión 1.29 o superior)
3. **OpenAI API Key** (obligatorio)

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Edita el archivo `.env` y configura:

```env
# OpenAI API Key (requerido)
OPENAI_API_KEY=tu_clave_api_openai_aqui

# PostgreSQL Configuration (opcional, defaults funcionan)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_VECTOR_DB=database164
POSTGRES_HISTORY_DB=pdf_rag_history

# CORS Origins
CORS_ORIGINS=http://localhost:3001,http://localhost:80

# PDF Documents Directory
PDF_DOCUMENTS_DIR=./pdf-documents
```

### 2. Construir y Ejecutar los Contenedores

```bash
# Construir todas las imágenes
docker compose build

# Iniciar todos los servicios
docker compose up -d

# Ver los logs
docker compose logs -f
```

### 3. Verificar que Todo Esté Funcionando

```bash
# Verificar estado de los contenedores
docker compose ps

# Verificar logs de un servicio específico
docker compose logs backend
docker compose logs frontend
docker compose logs postgres
```

## 📁 Estructura de Servicios

### PostgreSQL (puerto 5432)
- **Imagen**: `pgvector/pgvector:pg16`
- **Bases de datos**:
  - `database164` - Vector store (embeddings)
  - `pdf_rag_history` - Historial de chat
- **Volumen**: `postgres_data` (persistente)

### Backend (puerto 8000)
- **Imagen**: Construida desde `Dockerfile`
- **Endpoints**:
  - `http://localhost:8000/docs` - Documentación API
  - `http://localhost:8000/rag/stream` - Endpoint RAG
  - `http://localhost:8000/upload` - Subir PDFs
  - `http://localhost:8000/load-and-process-pdfs` - Procesar PDFs

### Frontend (puerto 3001)
- **Imagen**: Construida desde `frontend/Dockerfile`
- **URL**: `http://localhost:3001`
- **Servido por**: Nginx

## 🔧 Comandos Útiles

### Gestión de Contenedores

```bash
# Iniciar servicios
docker compose up -d

# Detener servicios
docker compose down

# Detener y eliminar volúmenes (⚠️ elimina datos de BD)
docker compose down -v

# Reiniciar un servicio específico
docker compose restart backend

# Reconstruir un servicio específico
docker compose build backend
docker compose up -d backend
```

### Ver Logs

```bash
# Todos los servicios
docker compose logs -f

# Servicio específico
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres

# Últimas 100 líneas
docker compose logs --tail=100 backend
```

### Acceder a Contenedores

```bash
# Acceder al contenedor del backend
docker compose exec backend bash

# Acceder a PostgreSQL
docker compose exec postgres psql -U postgres -d database164

# Ejecutar comandos en el backend
docker compose exec backend poetry run python rag-data-loader/rag_load_and_process.py
```

## 📝 Procesar PDFs

### Opción 1: Desde la Interfaz Web

1. Abre `http://localhost:3001`
2. Haz clic en "Upload PDFs" para subir archivos
3. Haz clic en "Load and Process PDFs" para procesarlos

### Opción 2: Desde la Línea de Comandos

```bash
# Copiar PDFs al directorio
cp tus_archivos.pdf pdf-documents/

# Ejecutar el script de procesamiento
docker compose exec backend poetry run python rag-data-loader/rag_load_and_process.py
```

## 🔍 Verificar Base de Datos

```bash
# Conectar a PostgreSQL
docker compose exec postgres psql -U postgres

# Listar bases de datos
\l

# Conectar a database164
\c database164

# Ver tablas
\dt

# Ver datos
SELECT COUNT(*) FROM langchain_pg_embedding;
```

## 🛠️ Troubleshooting

### Error: "No se puede conectar a PostgreSQL"

1. Verifica que el contenedor esté corriendo:
   ```bash
   docker compose ps
   ```

2. Verifica los logs:
   ```bash
   docker compose logs postgres
   ```

3. Espera a que PostgreSQL esté listo (healthcheck):
   ```bash
   docker compose up -d postgres
   # Espera unos segundos
   docker compose up -d backend
   ```

### Error: "OPENAI_API_KEY no está configurada"

1. Verifica que el archivo `.env` exista
2. Verifica que contenga `OPENAI_API_KEY=tu_clave`
3. Reinicia los contenedores:
   ```bash
   docker compose down
   docker compose up -d
   ```

### Error: "Frontend no se conecta al backend"

1. Verifica que ambos contenedores estén corriendo:
   ```bash
   docker compose ps
   ```

2. Verifica la variable `REACT_APP_API_URL` en `docker-compose.yml`
3. Reconstruye el frontend:
   ```bash
   docker compose build frontend
   docker compose up -d frontend
   ```

### Error: "No se encuentran PDFs"

1. Verifica que los PDFs estén en `pdf-documents/`
2. Verifica que el volumen esté montado correctamente
3. Lista archivos en el contenedor:
   ```bash
   docker compose exec backend ls -la pdf-documents/
   ```

### Limpiar Todo y Empezar de Nuevo

```bash
# ⚠️ ADVERTENCIA: Esto elimina todos los datos
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## 🔄 Actualizar la Aplicación

```bash
# Detener contenedores
docker compose down

# Reconstruir imágenes
docker compose build --no-cache

# Iniciar de nuevo
docker compose up -d
```

## 📊 Monitoreo

### Ver uso de recursos

```bash
docker stats
```

### Ver estado de salud

```bash
docker compose ps
```

## 🌐 Acceso desde Otros Dispositivos

Si quieres acceder desde otros dispositivos en tu red:

1. Actualiza `CORS_ORIGINS` en `.env`:
   ```env
   CORS_ORIGINS=http://localhost:3001,http://TU_IP:3001
   ```

2. Actualiza `REACT_APP_API_URL` en `docker-compose.yml`:
   ```yaml
   args:
     - REACT_APP_API_URL=http://TU_IP:8000
   ```

3. Reconstruye y reinicia:
   ```bash
   docker compose build frontend
   docker compose up -d
   ```

## 📚 Archivos Importantes

- `docker-compose.yml` - Configuración de todos los servicios
- `Dockerfile` - Imagen del backend
- `frontend/Dockerfile` - Imagen del frontend
- `init-db.sh` - Script de inicialización de la base de datos
- `.env` - Variables de entorno (no está en git)

## ✅ Verificación Final

Una vez que todo esté corriendo, deberías poder:

1. ✅ Acceder a `http://localhost:3001` y ver la interfaz
2. ✅ Acceder a `http://localhost:8000/docs` y ver la documentación de la API
3. ✅ Subir PDFs desde la interfaz web
4. ✅ Procesar PDFs y hacer preguntas

¡Listo! Tu aplicación RAG está completamente dockerizada. 🎉
