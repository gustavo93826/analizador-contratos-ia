# rag/chains.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from rag.schemas import ResumenContrato, ClausulasDetectadas, RiesgosDetectados, ExplicacionSimple
from rag.indexing import query_contract

load_dotenv()

LLM_MODEL = "gemini-3.5-flash-lite"  # modelo de LLM a usar para todas las tareas. Cambiar aquí si se quiere otro modelo.


def get_llm():
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1,  # baja: buscamos precisión y consistencia, no creatividad
    )


# ---------------------------------------------------------------
# 1. RESUMEN AUTOMÁTICO — contexto completo, sin retrieval
# ---------------------------------------------------------------
RESUMEN_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente legal experto en análisis de contratos. "
     "Analiza el contrato completo proporcionado y genera un resumen "
     "estructurado, preciso y objetivo. No inventes información que no "
     "esté explícitamente en el texto."),
    ("human", "Contrato completo:\n\n{contrato}")
])

def generar_resumen(full_text: str) -> ResumenContrato:
    llm = get_llm().with_structured_output(ResumenContrato)
    chain = RESUMEN_PROMPT | llm
    return chain.invoke({"contrato": full_text})


# ---------------------------------------------------------------
# 2. DETECCIÓN DE CLÁUSULAS IMPORTANTES — contexto completo
# ---------------------------------------------------------------
CLAUSULAS_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente legal experto en análisis de contratos. "
     "Recorre el contrato completo e identifica TODAS las cláusulas "
     "relevantes (pago, terminación, confidencialidad, penalizaciones, "
     "jurisdicción, propiedad intelectual, renovación, garantías, etc.). "
     "Indica en qué página aparece cada una, según las marcas [Página N] "
     "presentes en el texto. No inventes cláusulas inexistentes."),
    ("human", "Contrato completo:\n\n{contrato}")
])

def detectar_clausulas(full_text: str) -> ClausulasDetectadas:
    llm = get_llm().with_structured_output(ClausulasDetectadas)
    chain = CLAUSULAS_PROMPT | llm
    return chain.invoke({"contrato": full_text})


# ---------------------------------------------------------------
# 3. IDENTIFICACIÓN DE RIESGOS — contexto completo
# ---------------------------------------------------------------
RIESGOS_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un abogado especializado en revisión de riesgos contractuales. "
     "Analiza el contrato completo y detecta cláusulas potencialmente "
     "desfavorables, ambiguas, unilaterales o de alto impacto económico o "
     "legal para alguna de las partes. Clasifica cada riesgo por severidad "
     "(alto, medio, bajo) y da una recomendación breve y accionable. "
     "Basa tu análisis únicamente en el texto proporcionado."),
    ("human", "Contrato completo:\n\n{contrato}")
])

def identificar_riesgos(full_text: str) -> RiesgosDetectados:
    llm = get_llm().with_structured_output(RiesgosDetectados)
    chain = RIESGOS_PROMPT | llm
    return chain.invoke({"contrato": full_text})


# ---------------------------------------------------------------
# 4. EXPLICACIÓN EN LENGUAJE SENCILLO — RAG real (retrieval + LLM)
# ---------------------------------------------------------------
EXPLICACION_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente que traduce lenguaje legal a español sencillo, "
     "como si le explicaras el contrato a alguien sin formación jurídica. "
     "Usa SOLO el fragmento de contrato proporcionado como contexto. "
     "No agregues opiniones legales ni inventes cláusulas."),
    ("human",
     "Fragmento del contrato relevante:\n\n{contexto}\n\n"
     "Pregunta del usuario: {pregunta}")
])

def explicar_en_simple(contract_id: str, pregunta: str) -> ExplicacionSimple:
    # Aquí SÍ usamos retrieval real: recuperamos solo los chunks
    # relevantes a la pregunta, en vez de mandar todo el contrato.
    docs = query_contract(contract_id, pregunta, k=4)
    contexto = "\n\n".join(
        f"[Página {d.metadata['page_number']}]\n{d.page_content}" for d in docs
    )

    llm = get_llm().with_structured_output(ExplicacionSimple)
    chain = EXPLICACION_PROMPT | llm
    return chain.invoke({"contexto": contexto, "pregunta": pregunta})