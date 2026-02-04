# RAG Application - Chat con PDFs Privados

## 📋 Descripción Simple

Esta aplicación permite hacer preguntas sobre documentos PDF privados usando inteligencia artificial. Funciona como un chatbot que:

- **Carga documentos PDF** desde tu computadora
- **Procesa y almacena** el contenido de los PDFs en una base de datos vectorial
- **Responde preguntas** sobre el contenido de los documentos usando un modelo de lenguaje (GPT-4)
- **Mantiene el historial** de la conversación para entender el contexto
- **Muestra las fuentes** de donde obtuvo la información para cada respuesta

Es una aplicación de **RAG (Retrieval-Augmented Generation)**, que combina búsqueda de información con generación de texto para dar respuestas precisas basadas en tus documentos.

---

## 🏗️ Arquitectura del Proyecto

La aplicación está dividida en dos componentes principales:

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │◄────────┤    Backend      │
│   (React)       │  HTTP   │   (FastAPI)     │
│   Puerto 3000   │         │   Puerto 8000   │
└─────────────────┘         └─────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │   PostgreSQL    │
                            │  + pgvector     │
                            │  (Vector Store) │
                            └─────────────────┘
```

---

## 🔧 Backend - Descripción Detallada

### Tecnologías Utilizadas

- **Python 3.11**: Lenguaje de programación principal
- **FastAPI**: Framework web moderno y rápido para construir APIs
- **LangChain**: Framework para construir aplicaciones con modelos de lenguaje
- **LangServe**: Extensión de LangChain para servir cadenas como APIs REST
- **OpenAI API**: Para embeddings (text-embedding-ada-002) y modelo de chat (GPT-4)
- **PostgreSQL + pgvector**: Base de datos para almacenar vectores de embeddings
- **Uvicorn**: Servidor ASGI para ejecutar FastAPI
- **Poetry**: Gestor de dependencias y entornos virtuales

### Arquitectura del Backend

El backend está estructurado en los siguientes módulos:

#### 1. **`app/server.py`** - Servidor FastAPI Principal

Este archivo configura el servidor web y define los endpoints:

- **`GET /`**: Redirige a la documentación de la API (`/docs`)
- **`POST /upload`**: Permite subir archivos PDF al servidor
- **`POST /load-and-process-pdfs`**: Ejecuta el script que procesa los PDFs y los carga en la base de datos
- **`POST /rag/stream`**: Endpoint principal para hacer preguntas (streaming de respuestas)
- **`GET /rag/static/{filename}`**: Sirve archivos PDF estáticos para descarga

**Características importantes:**
- CORS configurado para permitir conexiones desde `http://localhost:3000` (frontend)
- Montaje de archivos estáticos para servir PDFs
- Integración con LangServe para exponer la cadena RAG como API REST

#### 2. **`app/rag_chain.py`** - Cadena RAG Principal

Este es el corazón de la aplicación. Define cómo funciona el sistema RAG:

**Componentes principales:**

1. **Vector Store (PGVector)**:
   - Almacena los embeddings de los documentos PDF
   - Permite búsqueda semántica usando similitud de vectores
   - Collection name: `collection164`
   - Base de datos: `database164`

2. **MultiQueryRetriever**:
   - Técnica avanzada que genera múltiples versiones de la pregunta del usuario
   - Esto mejora la recuperación de documentos relevantes
   - Usa el LLM para reescribir la pregunta desde diferentes perspectivas

3. **Chat History (SQLChatMessageHistory)**:
   - Almacena el historial de conversaciones en PostgreSQL
   - Base de datos: `pdf_rag_history`
   - Permite mantener contexto entre mensajes

4. **Standalone Question Chain**:
   - Convierte preguntas de seguimiento en preguntas independientes
   - Ejemplo: Si el usuario pregunta "¿Y cuántos años tenía?" después de preguntar sobre una persona, convierte esto en "¿Cuántos años tenía [nombre de la persona]?"
   - Usa el historial de chat para entender el contexto

5. **Final Chain (RunnableWithMessageHistory)**:
   - Combina todos los componentes anteriores
   - Flujo completo:
     ```
     Pregunta del usuario
         ↓
     Standalone Question Chain (convierte a pregunta independiente)
         ↓
     MultiQueryRetriever (busca documentos relevantes)
         ↓
     LLM (genera respuesta basada en contexto)
         ↓
     Respuesta al usuario + documentos fuente
     ```

**Modelos utilizados:**
- **Embeddings**: `text-embedding-ada-002` (OpenAI)
- **LLM**: `gpt-4-1106-preview` (OpenAI) con streaming habilitado

#### 3. **`rag-data-loader/rag_load_and_process.py`** - Procesador de PDFs

Script que procesa los PDFs y los carga en la base de datos:

1. **Carga de documentos**:
   - Usa `DirectoryLoader` con `UnstructuredPDFLoader`
   - Carga todos los PDFs de la carpeta `pdf-documents`
   - Soporta procesamiento multihilo

2. **División de texto (Chunking)**:
   - Usa `SemanticChunker` para dividir documentos en chunks semánticos
   - Esto es mejor que dividir por caracteres porque mantiene el significado

3. **Generación de embeddings**:
   - Crea embeddings para cada chunk usando OpenAI
   - Los embeddings son representaciones vectoriales del texto

4. **Almacenamiento**:
   - Guarda los chunks y sus embeddings en PostgreSQL con pgvector
   - `pre_delete_collection=True` elimina la colección anterior antes de crear una nueva

### Flujo de Datos en el Backend

```
1. Usuario sube PDFs → /upload endpoint
2. Usuario ejecuta procesamiento → /load-and-process-pdfs
   ↓
3. Script procesa PDFs:
   - Extrae texto
   - Divide en chunks semánticos
   - Genera embeddings
   - Almacena en PostgreSQL
   ↓
4. Usuario hace pregunta → /rag/stream
   ↓
5. Backend procesa:
   - Convierte pregunta a standalone (si es necesario)
   - Genera múltiples versiones de la pregunta
   - Busca documentos relevantes en vector store
   - Genera respuesta con GPT-4
   - Stream de respuesta al frontend
```

---

## 🎨 Frontend - Descripción Detallada

### Tecnologías Utilizadas

- **React 18**: Biblioteca de JavaScript para construir interfaces de usuario
- **TypeScript**: Superset de JavaScript con tipado estático
- **Tailwind CSS**: Framework de CSS utility-first para estilos
- **@microsoft/fetch-event-source**: Para recibir respuestas en streaming (Server-Sent Events)
- **React Scripts**: Herramientas de configuración para React
- **UUID**: Para generar IDs únicos de sesión

### Arquitectura del Frontend

#### **`src/App.tsx`** - Componente Principal

**Estado de la aplicación:**
- `messages`: Array de mensajes (usuario y asistente)
- `inputValue`: Valor del campo de texto
- `selectedFiles`: Archivos PDF seleccionados para subir
- `sessionIdRef`: ID único de sesión (generado con UUID)

**Funcionalidades principales:**

1. **Manejo de Mensajes**:
   - `handleSendMessage`: Envía pregunta al backend usando Server-Sent Events
   - `setPartialMessage`: Actualiza mensajes parciales durante el streaming
   - `handleReceiveMessage`: Procesa chunks de datos recibidos del servidor

2. **Streaming de Respuestas**:
   - Usa `fetchEventSource` para recibir respuestas en tiempo real
   - El backend envía chunks de texto que se van mostrando progresivamente
   - Esto crea una experiencia más fluida (como ChatGPT)

3. **Gestión de Archivos**:
   - `handleUploadFiles`: Sube PDFs al servidor
   - `loadAndProcessPDFs`: Ejecuta el procesamiento de PDFs en el backend

4. **Interfaz de Usuario**:
   - Chat interface con mensajes del usuario y asistente
   - Área de texto para escribir preguntas
   - Botones para subir y procesar PDFs
   - Enlaces para descargar documentos fuente

**Flujo de comunicación Frontend-Backend:**

```
Frontend (React)
    ↓ POST /rag/stream
Backend (FastAPI)
    ↓ Procesa con RAG Chain
    ↓ Stream de respuesta
Frontend recibe chunks
    ↓ Actualiza UI en tiempo real
Usuario ve respuesta progresiva
```

### Estructura de la UI

```
┌─────────────────────────────────────┐
│         Header (Título)             │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Mensajes del Chat            │ │
│  │  - Usuario (azul)             │ │
│  │  - Asistente (gris)           │ │
│  │  - Fuentes (enlaces)          │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Textarea (pregunta)          │ │
│  │  Botón "Send"                 │ │
│  │  Input file (PDFs)            │ │
│  │  Botón "Upload PDFs"          │ │
│  │  Botón "Load and Process"     │ │
│  └───────────────────────────────┘ │
├─────────────────────────────────────┤
│         Footer                      │
└─────────────────────────────────────┘
```

---

## 🚀 Cómo Ejecutar la Aplicación

### Prerrequisitos

1. **Python 3.11** (no 3.12)
2. **Node.js y npm** (para el frontend)
3. **PostgreSQL** con extensión **pgvector** instalada
4. **Poetry** instalado (`pip install poetry`)
5. **OpenAI API Key**

### Configuración Inicial

1. **Clonar el repositorio** (si aplica)

2. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   ```
   Edita el archivo `.env` y configura:
   - `OPENAI_API_KEY`: Tu clave de API de OpenAI
   - Variables de PostgreSQL si usas credenciales diferentes

3. **Configurar PostgreSQL**:
   ```sql
   -- Crear base de datos para vector store
   CREATE DATABASE database164;
   
   -- Crear base de datos para historial de chat
   CREATE DATABASE pdf_rag_history;
   
   -- Conectar a cada base de datos y ejecutar:
   CREATE EXTENSION vector;
   ```

---

## 🖥️ Ejecución SIN Docker

### Paso 1: Instalar Dependencias del Backend

```bash
# Instalar Poetry si no lo tienes
pip install poetry

# Instalar dependencias del proyecto
poetry install
```

### Paso 2: Procesar PDFs (Primera Vez)

Antes de usar la aplicación, necesitas procesar los PDFs:

```bash
# Asegúrate de tener PDFs en la carpeta pdf-documents/
# Edita la ruta en rag-data-loader/rag_load_and_process.py si es necesario

poetry run python rag-data-loader/rag_load_and_process.py
```

Este script:
- Carga todos los PDFs de `pdf-documents/`
- Los divide en chunks semánticos
- Genera embeddings
- Los almacena en PostgreSQL

### Paso 3: Iniciar el Backend

En una terminal:

```bash
# Opción 1: Usando LangChain CLI
poetry run langchain serve

# Opción 2: Directamente con uvicorn
poetry run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
```

El backend estará disponible en:
- **API**: `http://localhost:8000`
- **Documentación**: `http://localhost:8000/docs`
- **Endpoint RAG**: `http://localhost:8000/rag/stream`

### Paso 4: Iniciar el Frontend

En otra terminal:

```bash
cd frontend

# Instalar dependencias (solo la primera vez)
npm install

# Iniciar servidor de desarrollo
npm start
```

El frontend se abrirá automáticamente en `http://localhost:3000`

### Paso 5: Usar la Aplicación

1. Abre `http://localhost:3000` en tu navegador
2. (Opcional) Sube PDFs usando el botón "Upload PDFs"
3. (Opcional) Haz clic en "Load and Process PDFs" para procesarlos
4. Escribe una pregunta en el área de texto
5. Presiona Enter o haz clic en "Send"
6. La respuesta aparecerá en tiempo real con las fuentes

---

## 🐳 Ejecución CON Docker

### Construir la Imagen Docker

```bash
# Desde la raíz del proyecto
docker build -t rag-app-backend .
```

Este comando:
- Usa Python 3.11 como base
- Instala Poetry
- Copia e instala dependencias
- Configura el servidor para ejecutarse en el puerto 8080

### Ejecutar el Contenedor del Backend

```bash
docker run -d \
  --name rag-backend \
  -p 8080:8080 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e POSTGRES_VECTOR_DB_URL="postgresql+psycopg://postgres@host.docker.internal:5432/database164" \
  -e POSTGRES_CHAT_HISTORY_URL="postgresql+psycopg://postgres:postgres@host.docker.internal:5432/pdf_rag_history" \
  rag-app-backend
```

**Notas importantes:**
- `host.docker.internal` permite que el contenedor acceda a PostgreSQL en tu máquina local
- Si PostgreSQL está en otro host, cambia la URL
- El puerto 8080 se mapea al puerto 8080 del contenedor

### Ejecutar el Frontend (sin Docker)

El frontend se ejecuta mejor sin Docker para desarrollo:

```bash
cd frontend
npm install
npm start
```

**Nota**: Si ejecutas el backend en Docker en el puerto 8080, necesitarás actualizar las URLs en `App.tsx` de `localhost:8000` a `localhost:8080`, o mapear el puerto 8000 en Docker.

### Docker Compose (Opcional)

Para una solución más completa, puedes crear un `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - POSTGRES_VECTOR_DB_URL=postgresql+psycopg://postgres@db:5432/database164
      - POSTGRES_CHAT_HISTORY_URL=postgresql+psycopg://postgres:postgres@db:5432/pdf_rag_history
    depends_on:
      - db
  
  db:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Ejecutar con:
```bash
docker compose up -d
```

---

## 📝 Notas Adicionales

### Variables de Entorno

Consulta el archivo `.env.example` para ver todas las variables de entorno disponibles.

### Estructura de Carpetas

```
.
├── app/                    # Código del backend
│   ├── __init__.py
│   ├── rag_chain.py       # Cadena RAG principal
│   └── server.py          # Servidor FastAPI
├── frontend/              # Aplicación React
│   ├── src/
│   │   └── App.tsx        # Componente principal
│   └── package.json
├── pdf-documents/         # PDFs a procesar
├── rag-data-loader/       # Script de procesamiento
├── pyproject.toml         # Dependencias Python
├── Dockerfile            # Configuración Docker
└── .env.example          # Plantilla de variables de entorno
```

### Troubleshooting

1. **Error de conexión a PostgreSQL**:
   - Verifica que PostgreSQL esté corriendo
   - Verifica las credenciales en `.env`
   - Asegúrate de que la extensión `vector` esté instalada

2. **Error de OpenAI API**:
   - Verifica que `OPENAI_API_KEY` esté configurada correctamente
   - Verifica que tengas créditos disponibles

3. **Frontend no se conecta al backend**:
   - Verifica que el backend esté corriendo en el puerto correcto
   - Verifica la configuración de CORS en `server.py`

4. **PDFs no se procesan**:
   - Verifica que los PDFs estén en `pdf-documents/`
   - Verifica la ruta en `rag_load_and_process.py`
   - Revisa los logs del script

---

## 🔗 Recursos Adicionales

- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [React Documentation](https://react.dev/)

---

## 📄 Licencia

[Especificar licencia si aplica]
