FROM python:3.11-slim

# Instalar dependencias del sistema necesarias (paquetes básicos)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    poppler-utils \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar libGL para OpenCV (intentar diferentes variantes)
RUN apt-get update && \
    (apt-get install -y --no-install-recommends libgl1-mesa-glx || \
     apt-get install -y --no-install-recommends libgl1 || \
     echo "Warning: Could not install libGL, OpenCV may have limited functionality") && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install poetry==1.6.1

RUN poetry config virtualenvs.create false

WORKDIR /code

# Copiar archivos de dependencias
COPY ./pyproject.toml ./README.md ./poetry.lock* ./

# Copiar packages si existe (el directorio existe según la estructura del proyecto)
COPY ./packages ./packages

# Instalar dependencias
RUN poetry install --no-interaction --no-ansi --no-root

# Copiar código de la aplicación
COPY ./app ./app
COPY ./rag-data-loader ./rag-data-loader
COPY ./pdf-documents ./pdf-documents

# Instalar dependencias de la aplicación
RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

# Usar variables de entorno para la configuración
ENV PYTHONUNBUFFERED=1

CMD exec uvicorn app.server:app --host 0.0.0.0 --port 8000
