# 📊 Cómo Consultar las Bases de Datos PostgreSQL

Este proyecto utiliza dos bases de datos PostgreSQL:

1. **`database164`** - Almacena los embeddings de los documentos PDF (vector store)
2. **`pdf_rag_history`** - Almacena el historial de conversaciones del chat

## 🚀 Método 1: Usando el Script Python (Recomendado)

El script `query_database.py` te permite consultar las bases de datos de forma fácil y estructurada.

### Instalación

Asegúrate de tener las dependencias instaladas:

```bash
poetry install
```

### Uso Básico

```bash
# Consultar ambas bases de datos
poetry run python query_database.py

# Solo consultar la base de datos del vector store
poetry run python query_database.py --database vector

# Solo consultar la base de datos del historial de chat
poetry run python query_database.py --database history

# Consultar una tabla específica
poetry run python query_database.py --database vector --table langchain_pg_embedding
poetry run python query_database.py --database history --table message_store
```

### Ejemplos de Salida

El script mostrará:
- ✅ Lista de todas las tablas
- 📊 Estructura de cada tabla (columnas, tipos de datos)
- 📈 Conteo de filas
- 🔍 Muestra de datos (limitada para evitar mostrar vectores completos)

## 🗄️ Método 2: Usando psql (Línea de Comandos)

### Conectar a las Bases de Datos

```bash
# Conectar a la base de datos del vector store
psql -U postgres -d database164

# Conectar a la base de datos del historial
psql -U postgres -d pdf_rag_history
```

### Consultas Útiles

Puedes usar el archivo `database_queries.sql` que contiene consultas predefinidas:

```bash
# Ejecutar consultas desde un archivo
psql -U postgres -d database164 -f database_queries.sql
```

O ejecutar consultas directamente:

```sql
-- Listar todas las tablas
\dt

-- Ver estructura de una tabla
\d langchain_pg_embedding

-- Contar documentos
SELECT COUNT(*) FROM langchain_pg_embedding;

-- Ver documentos con sus metadatos
SELECT id, cmetadata->>'source' as source_file 
FROM langchain_pg_embedding 
LIMIT 10;
```

## 📋 Tablas Principales

### Base de Datos: `database164` (Vector Store)

**Tabla: `langchain_pg_embedding`**
- `id`: ID único del chunk
- `collection_id`: ID de la colección (ej: "collection164")
- `embedding`: Vector de embedding (tipo `vector`)
- `document`: Texto del chunk
- `cmetadata`: Metadatos en formato JSON (incluye `source`, `page`, etc.)
- `custom_id`: ID personalizado
- `uuid`: UUID del documento

### Base de Datos: `pdf_rag_history` (Chat History)

**Tabla: `message_store`**
- `id`: ID único del mensaje
- `session_id`: ID de la sesión de chat
- `message`: Contenido del mensaje (formato JSON)
- `created_at`: Fecha y hora de creación

## 🔍 Consultas Comunes

### Ver cuántos documentos están almacenados

```sql
-- En database164
SELECT COUNT(*) as total_chunks FROM langchain_pg_embedding;
```

### Ver documentos por archivo fuente

```sql
-- En database164
SELECT 
    cmetadata->>'source' as source_file,
    COUNT(*) as chunk_count
FROM langchain_pg_embedding
GROUP BY cmetadata->>'source'
ORDER BY chunk_count DESC;
```

### Ver sesiones de chat

```sql
-- En pdf_rag_history
SELECT DISTINCT session_id FROM message_store;
```

### Ver mensajes de una sesión específica

```sql
-- En pdf_rag_history
SELECT 
    id,
    message,
    created_at
FROM message_store
WHERE session_id = 'TU_SESSION_ID'
ORDER BY created_at;
```

## ⚙️ Configuración de Credenciales

Si tus credenciales de PostgreSQL son diferentes a las predeterminadas, puedes modificar el script `query_database.py`:

```python
VECTOR_DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "database164",
    "user": "postgres",
    "password": "tu_password"  # Cambiar aquí
}

HISTORY_DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pdf_rag_history",
    "user": "postgres",
    "password": "tu_password"  # Cambiar aquí
}
```

O usar variables de entorno:

```bash
export PGPASSWORD=tu_password
psql -U postgres -d database164
```

## 🐳 Si usas Docker

Si PostgreSQL está corriendo en Docker, necesitarás ajustar el host:

```python
VECTOR_DB_CONFIG = {
    "host": "localhost",  # O la IP del contenedor
    # ... resto de la configuración
}
```

O usar `host.docker.internal` si estás conectando desde dentro de un contenedor.

## 📚 Recursos Adicionales

- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación de pgvector](https://github.com/pgvector/pgvector)
- [Documentación de LangChain PGVector](https://python.langchain.com/docs/integrations/vectorstores/pgvector)

## ❓ Troubleshooting

### Error: "No se puede conectar a la base de datos"

1. Verifica que PostgreSQL esté corriendo:
   ```bash
   # macOS
   brew services list
   
   # Linux
   sudo systemctl status postgresql
   ```

2. Verifica que las bases de datos existan:
   ```sql
   \l  -- Listar todas las bases de datos
   ```

3. Verifica las credenciales en el script

### Error: "La tabla no existe"

1. Asegúrate de haber ejecutado el script de procesamiento de PDFs:
   ```bash
   poetry run python rag-data-loader/rag_load_and_process.py
   ```

2. Verifica que la extensión `vector` esté instalada:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Error: "No module named 'psycopg'"

Instala las dependencias:
```bash
poetry install
```
