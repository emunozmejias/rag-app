# 🏗️ Arquitectura de la Aplicación RAG

## 📋 Descripción General

Esta aplicación es un sistema de **RAG (Retrieval-Augmented Generation)** que permite hacer preguntas sobre documentos PDF privados usando inteligencia artificial. La aplicación funciona como un chatbot inteligente que:

- **Carga y procesa documentos PDF** desde el sistema de archivos
- **Extrae y almacena el contenido** de los PDFs en una base de datos vectorial
- **Responde preguntas** sobre el contenido de los documentos usando modelos de lenguaje (GPT-4)
- **Mantiene el historial** de conversaciones para entender el contexto
- **Muestra las fuentes** de donde obtuvo la información para cada respuesta

### Casos de Uso

- Consultar información de documentos técnicos
- Analizar contratos o documentos legales
- Extraer información de reportes o informes
- Crear un asistente de conocimiento basado en documentos privados

---

## 🎯 Cómo se Usa

### Modo de Operación

1. **Subir PDFs**: El usuario sube archivos PDF a través de la interfaz web
2. **Procesar Documentos**: Los PDFs se procesan, dividen en chunks semánticos y se generan embeddings
3. **Hacer Preguntas**: El usuario hace preguntas en lenguaje natural sobre el contenido de los documentos
4. **Obtener Respuestas**: El sistema busca información relevante y genera respuestas contextualizadas

### Interfaz de Usuario

- **Chat Interface**: Área de conversación donde se muestran preguntas y respuestas
- **Upload de Archivos**: Botón para subir PDFs al servidor
- **Procesamiento**: Botón para procesar los PDFs cargados
- **Fuentes**: Enlaces a los documentos fuente utilizados para cada respuesta

---

## 🏛️ Arquitectura del Sistema

### Arquitectura General

La aplicación sigue una arquitectura de **microservicios** con tres componentes principales:

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                               │
│                    (Navegador Web)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/HTTPS
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌────────▼────────┐
│   Frontend     │            │    Backend       │
│   (React)      │◄───────────┤   (FastAPI)     │
│   Puerto 3001  │   REST API │   Puerto 8000   │
└────────────────┘            └────────┬────────┘
                                        │
                        ┌───────────────┼───────────────┐
                        │               │               │
                ┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
                │  PostgreSQL  │ │  PostgreSQL │ │   OpenAI    │
                │  (Vector DB) │ │  (History)  │ │     API     │
                │  database164 │ │pdf_rag_hist │ │             │
                └──────────────┘ └──────────────┘ └─────────────┘
```

### Componentes Principales

#### 1. **Frontend (React + TypeScript)**
- **Ubicación**: `frontend/`
- **Puerto**: 3001 (host) → 80 (contenedor)
- **Tecnología**: React 18 con TypeScript
- **Servidor Web**: Nginx (en producción Docker)

**Responsabilidades**:
- Interfaz de usuario interactiva
- Gestión de estado de la conversación
- Streaming de respuestas en tiempo real
- Upload y gestión de archivos PDF
- Visualización de fuentes de información

#### 2. **Backend (FastAPI + Python)**
- **Ubicación**: `app/`
- **Puerto**: 8000
- **Tecnología**: FastAPI con Python 3.11

**Responsabilidades**:
- API REST para comunicación con el frontend
- Procesamiento de documentos PDF
- Gestión de la cadena RAG
- Integración con servicios externos (OpenAI, PostgreSQL)
- Servicio de archivos estáticos

#### 3. **Base de Datos (PostgreSQL + pgvector)**
- **Puerto**: 5432
- **Tecnología**: PostgreSQL 16 con extensión pgvector

**Bases de Datos**:
- **`database164`**: Almacena embeddings y documentos (vector store)
- **`pdf_rag_history`**: Almacena historial de conversaciones

---

## 🔄 Flujo de Datos

### Flujo de Procesamiento de PDFs

```
1. Usuario sube PDFs
   ↓
2. Frontend → POST /upload → Backend
   ↓
3. Backend guarda PDFs en ./pdf-documents/
   ↓
4. Usuario ejecuta procesamiento
   ↓
5. Frontend → POST /load-and-process-pdfs → Backend
   ↓
6. Backend ejecuta rag_load_and_process.py
   ↓
7. Script carga PDFs con UnstructuredPDFLoader
   ↓
8. Divide documentos en chunks semánticos (SemanticChunker)
   ↓
9. Genera embeddings con OpenAI (text-embedding-ada-002)
   ↓
10. Almacena en PostgreSQL con pgvector
```

### Flujo de Pregunta y Respuesta

```
1. Usuario escribe pregunta
   ↓
2. Frontend → POST /rag/stream → Backend
   ↓
3. Backend recibe pregunta
   ↓
4. Standalone Question Chain convierte pregunta de seguimiento
   ↓
5. MultiQueryRetriever genera múltiples versiones de la pregunta
   ↓
6. Búsqueda semántica en vector store (PostgreSQL + pgvector)
   ↓
7. Recupera documentos relevantes
   ↓
8. LLM (GPT-4) genera respuesta basada en contexto
   ↓
9. Backend → Stream de respuesta → Frontend
   ↓
10. Frontend muestra respuesta en tiempo real
```

---

## 🧩 Componentes Detallados

### Backend Components

#### `app/server.py` - Servidor FastAPI
- **Framework**: FastAPI
- **Endpoints**:
  - `GET /` → Redirige a `/docs` (documentación API)
  - `POST /upload` → Sube archivos PDF
  - `POST /load-and-process-pdfs` → Procesa PDFs
  - `POST /rag/stream` → Endpoint principal RAG (streaming)
  - `GET /rag/static/{filename}` → Sirve PDFs estáticos
- **Middleware**: CORS configurado para permitir frontend

#### `app/rag_chain.py` - Cadena RAG Principal
- **Componentes**:
  1. **PGVector**: Vector store para embeddings
  2. **MultiQueryRetriever**: Genera múltiples versiones de preguntas
  3. **Standalone Question Chain**: Convierte preguntas de seguimiento
  4. **Chat History**: Mantiene contexto de conversación
  5. **Final Chain**: Orquesta todo el flujo

#### `rag-data-loader/rag_load_and_process.py` - Procesador de PDFs
- **Carga**: DirectoryLoader con UnstructuredPDFLoader
- **Chunking**: SemanticChunker (división semántica)
- **Embeddings**: OpenAIEmbeddings (text-embedding-ada-002)
- **Almacenamiento**: PGVector.from_documents()

### Frontend Components

#### `frontend/src/App.tsx` - Componente Principal
- **Estado**:
  - `messages`: Array de mensajes (usuario/asistente)
  - `inputValue`: Texto del input
  - `selectedFiles`: Archivos seleccionados
  - `sessionIdRef`: ID único de sesión
- **Funcionalidades**:
  - Streaming de respuestas (Server-Sent Events)
  - Upload de archivos
  - Procesamiento de PDFs
  - Visualización de fuentes

---

## 🔗 Relaciones entre Componentes

### Comunicación Frontend ↔ Backend

```
Frontend (React)          Backend (FastAPI)
     │                           │
     │  HTTP POST /rag/stream    │
     ├──────────────────────────>│
     │                           │
     │  Server-Sent Events       │
     │<──────────────────────────┤
     │  (Streaming de respuesta) │
```

### Comunicación Backend ↔ Base de Datos

```
Backend (FastAPI)         PostgreSQL
     │                           │
     │  Búsqueda semántica       │
     ├──────────────────────────>│
     │  (pgvector)               │
     │                           │
     │  Documentos relevantes    │
     │<──────────────────────────┤
     │                           │
     │  Guardar historial        │
     ├──────────────────────────>│
     │  (SQLChatMessageHistory)  │
```

### Comunicación Backend ↔ OpenAI

```
Backend (FastAPI)         OpenAI API
     │                           │
     │  Generar embeddings       │
     ├──────────────────────────>│
     │  (text-embedding-ada-002) │
     │                           │
     │  Generar respuesta        │
     ├──────────────────────────>│
     │  (gpt-4-1106-preview)    │
     │                           │
     │  Respuesta stream         │
     │<──────────────────────────┤
```

---

## 💻 Lenguajes y Frameworks

### Backend

#### Lenguaje
- **Python**: 3.11 (>=3.11,<3.12)

#### Frameworks y Librerías

| Framework/Librería | Versión | Propósito |
|-------------------|---------|-----------|
| **FastAPI** | (implícito via uvicorn) | Framework web asíncrono |
| **Uvicorn** | ^0.23.2 | Servidor ASGI |
| **LangChain** | (vía langchain-*) | Framework para aplicaciones LLM |
| **LangServe** | >=0.0.30 | Servir cadenas LangChain como API |
| **LangChain Community** | ^0.0.31 | Integraciones comunitarias |
| **LangChain Experimental** | ^0.0.55 | Funcionalidades experimentales |
| **LangChain OpenAI** | ^0.1.1 | Integración con OpenAI |
| **Pydantic** | <2 | Validación de datos |
| **python-dotenv** | ^1.0.1 | Gestión de variables de entorno |
| **psycopg** | ^3.1.18 | Driver PostgreSQL |
| **pgvector** | ^0.2.5 | Extensión vectorial para PostgreSQL |
| **unstructured** | ^0.12.6 (all-docs) | Procesamiento de documentos |
| **tiktoken** | ^0.6.0 | Tokenización para LLMs |
| **tqdm** | ^4.66.2 | Barras de progreso |

#### Gestión de Dependencias
- **Poetry**: 1.6.1

### Frontend

#### Lenguaje
- **TypeScript**: ^4.9.5

#### Frameworks y Librerías

| Framework/Librería | Versión | Propósito |
|-------------------|---------|-----------|
| **React** | ^18.2.0 | Biblioteca UI |
| **React DOM** | ^18.2.0 | Renderizado React |
| **React Scripts** | 5.0.1 | Scripts de configuración |
| **@microsoft/fetch-event-source** | ^2.0.1 | Server-Sent Events |
| **Tailwind CSS** | ^3.4.3 | Framework CSS utility-first |
| **UUID** | (vía @types/uuid ^9.0.8) | Generación de IDs únicos |

#### Herramientas de Desarrollo
- **TypeScript**: ^4.9.5
- **@types/react**: ^18.2.74
- **@types/react-dom**: ^18.2.24
- **@types/node**: ^16.18.95
- **@types/jest**: ^27.5.2

### Base de Datos

#### Sistema de Base de Datos
- **PostgreSQL**: 16 (pgvector/pgvector:pg16)
- **pgvector**: Extensión para almacenamiento vectorial

### Infraestructura

#### Contenedores
- **Docker**: Para containerización
- **Docker Compose**: Para orquestación

#### Servidores Web
- **Nginx**: Alpine (para frontend en producción)
- **Uvicorn**: Para backend FastAPI

---

## 🗄️ Estructura de Base de Datos

### Base de Datos: `database164` (Vector Store)

**Tabla**: `langchain_pg_embedding`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | UUID | ID único del chunk |
| `collection_id` | UUID | ID de la colección |
| `embedding` | vector | Vector de embedding (1536 dimensiones) |
| `document` | text | Texto del chunk |
| `cmetadata` | jsonb | Metadatos (source, page, etc.) |
| `custom_id` | text | ID personalizado |
| `uuid` | UUID | UUID del documento |

### Base de Datos: `pdf_rag_history` (Chat History)

**Tabla**: `message_store`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | UUID | ID único del mensaje |
| `session_id` | text | ID de la sesión de chat |
| `message` | jsonb | Contenido del mensaje |
| `created_at` | timestamp | Fecha y hora de creación |

---

## 🔐 Seguridad y Configuración

### Variables de Entorno

#### Backend
- `OPENAI_API_KEY`: Clave de API de OpenAI (requerido)
- `POSTGRES_HOST`: Host de PostgreSQL (default: localhost)
- `POSTGRES_PORT`: Puerto de PostgreSQL (default: 5432)
- `POSTGRES_USER`: Usuario de PostgreSQL (default: postgres)
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL
- `POSTGRES_VECTOR_DB`: Base de datos vectorial (default: database164)
- `POSTGRES_HISTORY_DB`: Base de datos de historial (default: pdf_rag_history)
- `CORS_ORIGINS`: Orígenes permitidos para CORS (default: http://localhost:3001)
- `PDF_DOCUMENTS_DIR`: Directorio de documentos PDF

#### Frontend
- `REACT_APP_API_URL`: URL del backend (default: http://localhost:8000)

---

## 📊 Modelos de IA Utilizados

### OpenAI

| Modelo | Versión | Uso |
|--------|---------|-----|
| **GPT-4** | gpt-4-1106-preview | Generación de respuestas |
| **text-embedding-ada-002** | - | Generación de embeddings |

### Configuración
- **Temperature**: 0 (determinístico)
- **Streaming**: Habilitado
- **Dimensión de embeddings**: 1536

---

## 🚀 Despliegue

### Opción 1: Docker Compose (Recomendado)

```bash
docker compose up -d
```

**Servicios**:
- PostgreSQL: puerto 5432
- Backend: puerto 8000
- Frontend: puerto 3001

### Opción 2: Desarrollo Local

**Backend**:
```bash
poetry install
poetry run uvicorn app.server:app --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm start
```

---

## 🔄 Flujo Completo de la Aplicación

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       │ 1. Sube PDFs
       ▼
┌─────────────────┐
│  Frontend React │
└──────┬──────────┘
       │
       │ 2. POST /upload
       ▼
┌─────────────────┐
│  Backend FastAPI│
└──────┬──────────┘
       │
       │ 3. Guarda PDFs
       ▼
┌─────────────────┐
│ pdf-documents/  │
└─────────────────┘

       │ 4. POST /load-and-process-pdfs
       ▼
┌─────────────────┐
│ Procesador PDFs │
└──────┬──────────┘
       │
       │ 5. Carga y divide
       │ 6. Genera embeddings
       ▼
┌─────────────────┐
│  OpenAI API     │
└──────┬──────────┘
       │
       │ 7. Almacena vectores
       ▼
┌─────────────────┐
│  PostgreSQL     │
│  (database164)  │
└─────────────────┘

       │ 8. Usuario hace pregunta
       ▼
┌─────────────────┐
│  Frontend React │
└──────┬──────────┘
       │
       │ 9. POST /rag/stream
       ▼
┌─────────────────┐
│  Backend FastAPI│
│  (RAG Chain)    │
└──────┬──────────┘
       │
       │ 10. Búsqueda semántica
       ▼
┌─────────────────┐
│  PostgreSQL     │
│  (database164)  │
└──────┬──────────┘
       │
       │ 11. Genera respuesta
       ▼
┌─────────────────┐
│  OpenAI API     │
│  (GPT-4)        │
└──────┬──────────┘
       │
       │ 12. Stream de respuesta
       ▼
┌─────────────────┐
│  Frontend React │
└──────┬──────────┘
       │
       │ 13. Muestra respuesta
       ▼
┌─────────────┐
│   Usuario   │
└─────────────┘
```

---

## 📝 Notas Técnicas

### Características Clave

1. **Streaming de Respuestas**: Las respuestas se envían en tiempo real usando Server-Sent Events
2. **Búsqueda Semántica**: Usa embeddings vectoriales para encontrar información relevante
3. **Multi-Query Retrieval**: Genera múltiples versiones de la pregunta para mejorar la recuperación
4. **Historial de Conversación**: Mantiene contexto entre mensajes
5. **Deduplicación de Fuentes**: Evita mostrar archivos fuente duplicados

### Optimizaciones

- **Chunking Semántico**: Divide documentos manteniendo el significado
- **Búsqueda Vectorial**: Búsqueda eficiente usando pgvector
- **Streaming**: Respuestas en tiempo real sin esperar completitud
- **Caché de Archivos**: Nginx sirve archivos estáticos eficientemente

---

## 🔍 Troubleshooting

### Problemas Comunes

1. **Error de CORS**: Verificar `CORS_ORIGINS` en variables de entorno
2. **Error de conexión a BD**: Verificar credenciales de PostgreSQL
3. **Error de OpenAI**: Verificar `OPENAI_API_KEY`
4. **PDFs no se procesan**: Verificar dependencias del sistema (libGL, etc.)

---

## 📚 Referencias

- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [React Documentation](https://react.dev/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**Última actualización**: Febrero 2025
