# rag/indexing.py

import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
PERSIST_DIR = "data/vectorstore"
COLLECTION_NAME = "contratos"
EMBEDDING_MODEL = "models/gemini-embedding-001"


def build_documents(pages_data: list[dict], contract_id: str) -> list[Document]:
    """
    Convierte las páginas extraídas en la Fase 1 en fragmentos (chunks)
    listos para ser embebidos, conservando metadata clave para trazabilidad.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    documents = []
    for page in pages_data:
        chunks = splitter.split_text(page["text"])
        for i, chunk in enumerate(chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "contract_id": contract_id,
                        "page_number": page["page_number"],
                        "source": page["source"],
                        "chunk_index": i,
                    }
                )
            )
    return documents


def get_embedding_function() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )


def index_contract(pages_data: list[dict], contract_id: str) -> Chroma:
    """
    Genera embeddings para todos los chunks de un contrato
    y los persiste en la base vectorial ChromaDB.
    """
    documents = build_documents(pages_data, contract_id)
    embeddings = get_embedding_function()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR
    )
    return vectorstore


def get_vectorstore() -> Chroma:
    """Reabre la base vectorial ya existente en disco (sin reindexar)."""
    embeddings = get_embedding_function()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )


def query_contract(contract_id: str, query: str, k: int = 4) -> list[Document]:
    """
    Recupera los k fragmentos más relevantes de UN contrato específico
    para una consulta dada, usando similitud semántica.
    """
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search(
        query,
        k=k,
        filter={"contract_id": contract_id}
    )