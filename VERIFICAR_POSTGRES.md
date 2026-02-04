# ✅ Verificar si PostgreSQL está Corriendo en macOS

## 🔍 Métodos para Verificar

### Método 1: Verificar el Puerto (Más Confiable)

```bash
lsof -i :5432
```

**Resultado esperado si está corriendo:**
```
COMMAND     PID           USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
postgres   1516 elizabethmunoz    7u  IPv6 ...      0t0  TCP localhost:postgresql (LISTEN)
postgres   1516 elizabethmunoz    8u  IPv4 ...      0t0  TCP localhost:postgresql (LISTEN)
```

✅ **Tu PostgreSQL está corriendo** - Se detectó el proceso en el puerto 5432

### Método 2: Verificar con Homebrew (si instalaste con Homebrew)

```bash
brew services list | grep postgres
```

**Resultado esperado:**
```
postgresql@17  started  elizabethmunoz  ~/Library/LaunchAgents/homebrew.mxcl.postgresql@17.plist
```

### Método 3: Intentar Conectarse

```bash
psql -U postgres -c "SELECT version();"
```

Si funciona, verás la versión de PostgreSQL.

### Método 4: Verificar Procesos

```bash
ps aux | grep postgres | grep -v grep
```

Deberías ver procesos como:
- `postgres: checkpointer`
- `postgres: background writer`
- `postgres: walwriter`
- etc.

## 🚀 Iniciar PostgreSQL (si no está corriendo)

### Si instalaste con Homebrew:

```bash
# Iniciar PostgreSQL
brew services start postgresql@17

# O para una versión específica
brew services start postgresql@16
```

### Si instalaste con Postgres.app:

1. Abre la aplicación Postgres.app
2. Haz clic en "Start" si está detenido

### Si instalaste manualmente:

```bash
# Buscar el directorio de datos (varía según instalación)
pg_ctl -D /usr/local/var/postgres start

# O si está en otra ubicación
pg_ctl -D /opt/homebrew/var/postgresql@17 start
```

## 📊 Verificar las Bases de Datos del Proyecto

Una vez que PostgreSQL esté corriendo, verifica que las bases de datos existan:

```bash
# Listar todas las bases de datos
psql -U postgres -l

# O verificar específicamente las del proyecto
psql -U postgres -c "\l" | grep -E "(database164|pdf_rag_history)"
```

**Bases de datos esperadas:**
- `database164` - Vector store (embeddings)
- `pdf_rag_history` - Historial de chat

## 🔧 Crear las Bases de Datos (si no existen)

Si las bases de datos no existen, créalas:

```bash
# Crear base de datos para vector store
psql -U postgres -c "CREATE DATABASE database164;"

# Crear base de datos para historial
psql -U postgres -c "CREATE DATABASE pdf_rag_history;"

# Instalar extensión pgvector en ambas bases de datos
psql -U postgres -d database164 -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -U postgres -d pdf_rag_history -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 🛑 Detener PostgreSQL

Si necesitas detener PostgreSQL:

```bash
# Con Homebrew
brew services stop postgresql@17

# Con pg_ctl
pg_ctl -D /opt/homebrew/var/postgresql@17 stop
```

## 📝 Notas Importantes

1. **Puerto por defecto**: PostgreSQL usa el puerto `5432`
2. **Usuario por defecto**: `postgres`
3. **Socket Unix**: En macOS, PostgreSQL también usa sockets Unix en `/tmp/.s.PGSQL.5432`

## ❓ Troubleshooting

### Error: "No se puede conectar al servidor"

1. Verifica que PostgreSQL esté corriendo (Método 1)
2. Verifica que el puerto 5432 no esté bloqueado
3. Verifica las credenciales

### Error: "base de datos no existe"

Ejecuta los comandos de creación de bases de datos arriba.

### Error: "extensión vector no existe"

Instala pgvector:
```bash
# Si usas Homebrew
brew install pgvector

# Luego crea la extensión en las bases de datos
psql -U postgres -d database164 -c "CREATE EXTENSION vector;"
```

## ✅ Estado Actual de tu Sistema

Basado en la verificación realizada:
- ✅ **PostgreSQL está corriendo** (proceso detectado en puerto 5432)
- ✅ **psql está instalado** (versión 17.7 de Homebrew)
- ✅ **Hay conexiones activas** (python3 conectado a postgres)

Ahora puedes usar el script `query_database.py` para consultar tus bases de datos.
