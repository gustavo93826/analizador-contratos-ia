# backend/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion.pdf_reader import process_pdf, get_full_text
from rag.indexing import index_contract
from rag.chains import (
    generar_resumen,
    detectar_clausulas,
    identificar_riesgos,
    explicar_en_simple,
)
from backend import storage

app = FastAPI(
    title="Analizador de Contratos con IA",
    description="API para resumir contratos, detectar cláusulas, identificar riesgos y explicarlos en lenguaje sencillo.",
    version="0.1.0",
)

# Habilitado para desarrollo local (Streamlit corre en otro puerto).
# En producción, restringir allow_origins a dominios específicos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE_MB = 15
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class ExplicarRequest(BaseModel):
    pregunta: str


def _require_contract(contract_id: str) -> None:
    if not storage.contract_exists(contract_id):
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")


@app.post("/contratos/subir")
async def subir_contrato(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")

    contenido = await file.read()
    if len(contenido) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo excede el límite de {MAX_FILE_SIZE_MB}MB."
        )

    contract_id = storage.generate_contract_id()
    upload_path = storage.get_upload_path(contract_id, file.filename)
    with open(upload_path, "wb") as f:
        f.write(contenido)

    try:
        pages = process_pdf(str(upload_path))
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="No se pudo leer el PDF. Puede estar corrupto o dañado."
        )

    if not pages:
        raise HTTPException(status_code=422, detail="El PDF no contiene páginas procesables.")

    storage.save_processed_pages(contract_id, pages)
    storage.register_contract(contract_id, file.filename, len(pages))

    try:
        index_contract(pages, contract_id=contract_id)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Error al generar los embeddings. Verifica tu API Key o inténtalo de nuevo."
        )

    return {
        "contract_id": contract_id,
        "filename": file.filename,
        "num_paginas": len(pages),
    }


@app.get("/contratos/{contract_id}/resumen")
def obtener_resumen(contract_id: str):
    _require_contract(contract_id)
    full_text = get_full_text(storage.load_processed_pages(contract_id))
    try:
        return generar_resumen(full_text)
    except Exception:
        raise HTTPException(status_code=502, detail="Error al generar el resumen con el LLM.")


@app.get("/contratos/{contract_id}/clausulas")
def obtener_clausulas(contract_id: str):
    _require_contract(contract_id)
    full_text = get_full_text(storage.load_processed_pages(contract_id))
    try:
        return detectar_clausulas(full_text)
    except Exception:
        raise HTTPException(status_code=502, detail="Error al detectar cláusulas con el LLM.")


@app.get("/contratos/{contract_id}/riesgos")
def obtener_riesgos(contract_id: str):
    _require_contract(contract_id)
    full_text = get_full_text(storage.load_processed_pages(contract_id))
    try:
        return identificar_riesgos(full_text)
    except Exception:
        raise HTTPException(status_code=502, detail="Error al identificar riesgos con el LLM.")


@app.post("/contratos/{contract_id}/explicar")
def explicar_clausula(contract_id: str, body: ExplicarRequest):
    _require_contract(contract_id)
    try:
        return explicar_en_simple(contract_id, body.pregunta)
    except Exception:
        raise HTTPException(status_code=502, detail="Error al generar la explicación con el LLM.")