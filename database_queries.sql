-- ============================================================================
-- CONSULTAS SQL PARA LA BASE DE DATOS POSTGRESQL DEL PROYECTO RAG
-- ============================================================================
-- 
-- Este archivo contiene consultas SQL útiles para explorar las bases de datos
-- del proyecto RAG.
--
-- USO:
--   psql -U postgres -d database164        # Para vector store
--   psql -U postgres -d pdf_rag_history    # Para historial de chat
-- ============================================================================

-- ============================================================================
-- BASE DE DATOS: database164 (Vector Store)
-- ============================================================================

-- 1. Listar todas las tablas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 2. Ver estructura de la tabla de embeddings (PGVector)
-- Nota: El nombre de la tabla puede variar, comúnmente es 'langchain_pg_embedding'
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'langchain_pg_embedding'
ORDER BY ordinal_position;

-- 3. Contar documentos/chunks almacenados
SELECT COUNT(*) as total_chunks 
FROM langchain_pg_embedding;

-- 4. Ver información de los documentos (sin los vectores completos)
SELECT 
    id,
    collection_id,
    cmetadata,
    uuid
FROM langchain_pg_embedding
LIMIT 10;

-- 5. Ver los metadatos de los documentos
SELECT 
    id,
    cmetadata->>'source' as source_file,
    cmetadata->>'page' as page_number,
    cmetadata->>'chunk' as chunk_info
FROM langchain_pg_embedding
LIMIT 20;

-- 6. Contar documentos por archivo fuente
SELECT 
    cmetadata->>'source' as source_file,
    COUNT(*) as chunk_count
FROM langchain_pg_embedding
GROUP BY cmetadata->>'source'
ORDER BY chunk_count DESC;

-- 7. Ver el tamaño de los vectores (dimensión del embedding)
SELECT 
    id,
    LENGTH(embedding::text) as vector_length,
    array_length(embedding, 1) as vector_dimension
FROM langchain_pg_embedding
LIMIT 5;

-- 8. Ver información sobre las colecciones
SELECT DISTINCT collection_id 
FROM langchain_pg_embedding;

-- 9. Verificar que la extensión pgvector está instalada
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 10. Ver el tamaño total de la tabla
SELECT 
    pg_size_pretty(pg_total_relation_size('langchain_pg_embedding')) as total_size,
    pg_size_pretty(pg_relation_size('langchain_pg_embedding')) as table_size,
    pg_size_pretty(pg_indexes_size('langchain_pg_embedding')) as indexes_size;

-- ============================================================================
-- BASE DE DATOS: pdf_rag_history (Chat History)
-- ============================================================================

-- 1. Listar todas las tablas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 2. Ver estructura de la tabla de historial de mensajes
-- Nota: El nombre puede variar, comúnmente es 'message_store'
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'message_store'
ORDER BY ordinal_position;

-- 3. Contar mensajes totales
SELECT COUNT(*) as total_messages 
FROM message_store;

-- 4. Ver todas las sesiones únicas
SELECT DISTINCT session_id 
FROM message_store
ORDER BY session_id;

-- 5. Contar mensajes por sesión
SELECT 
    session_id,
    COUNT(*) as message_count
FROM message_store
GROUP BY session_id
ORDER BY message_count DESC;

-- 6. Ver los últimos mensajes de una sesión específica
SELECT 
    id,
    session_id,
    message,
    created_at
FROM message_store
WHERE session_id = 'TU_SESSION_ID_AQUI'
ORDER BY created_at DESC
LIMIT 20;

-- 7. Ver todos los mensajes recientes (últimas 24 horas)
SELECT 
    id,
    session_id,
    message,
    created_at
FROM message_store
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- 8. Ver el tamaño total de la tabla
SELECT 
    pg_size_pretty(pg_total_relation_size('message_store')) as total_size,
    pg_size_pretty(pg_relation_size('message_store')) as table_size;

-- ============================================================================
-- CONSULTAS AVANZADAS
-- ============================================================================

-- Búsqueda de similitud vectorial (ejemplo)
-- Nota: Necesitas un vector de embedding para comparar
-- SELECT 
--     id,
--     cmetadata,
--     1 - (embedding <=> '[TU_VECTOR_AQUI]'::vector) as similarity
-- FROM langchain_pg_embedding
-- ORDER BY embedding <=> '[TU_VECTOR_AQUI]'::vector
-- LIMIT 5;

-- Ver estadísticas de uso
SELECT 
    'Vector Store' as database_name,
    (SELECT COUNT(*) FROM langchain_pg_embedding) as total_chunks,
    (SELECT COUNT(DISTINCT cmetadata->>'source') FROM langchain_pg_embedding) as unique_files
UNION ALL
SELECT 
    'Chat History' as database_name,
    (SELECT COUNT(*) FROM message_store) as total_messages,
    (SELECT COUNT(DISTINCT session_id) FROM message_store) as unique_sessions;
