import os

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, UnstructuredPDFLoader
from langchain_community.vectorstores.pgvector import PGVector
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Obtener configuración de PostgreSQL desde variables de entorno
postgres_host = os.getenv("POSTGRES_HOST", "localhost")
postgres_port = os.getenv("POSTGRES_PORT", "5432")
postgres_user = os.getenv("POSTGRES_USER", "postgres")
postgres_password = os.getenv("POSTGRES_PASSWORD", "")
postgres_vector_db = os.getenv("POSTGRES_VECTOR_DB", "database164")

# Obtener ruta de documentos desde variable de entorno o usar ruta relativa
pdf_directory = os.getenv("PDF_DOCUMENTS_DIR", os.path.abspath("./pdf-documents"))

loader = DirectoryLoader(
    pdf_directory,
    glob="**/*.pdf",
    use_multithreading=True,
    show_progress=True,
    max_concurrency=50,
    loader_cls=UnstructuredPDFLoader,
)
docs = loader.load()

embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', )

text_splitter = SemanticChunker(
    embeddings=embeddings
)

flattened_docs = [doc[0] for doc in docs if doc]
chunks = text_splitter.split_documents(flattened_docs)

# Construir connection string
if postgres_password:
    connection_string = f"postgresql+psycopg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_vector_db}"
else:
    connection_string = f"postgresql+psycopg://{postgres_user}@{postgres_host}:{postgres_port}/{postgres_vector_db}"

PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="collection164",
    connection_string=connection_string,
    pre_delete_collection=True,
)