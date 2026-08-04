# rag/schemas.py

from pydantic import BaseModel, Field
from typing import Literal


class ResumenContrato(BaseModel):
    partes: list[str] = Field(description="Nombres de las partes involucradas en el contrato")
    objeto: str = Field(description="Objeto o propósito principal del contrato")
    duracion: str = Field(description="Duración o vigencia del contrato")
    obligaciones_principales: list[str] = Field(description="Obligaciones más importantes de las partes")
    resumen_ejecutivo: str = Field(description="Resumen general del contrato en 3-5 oraciones")


class ClausulaImportante(BaseModel):
    tipo: str = Field(description="Categoría: Pago, Terminación, Confidencialidad, Penalizaciones, Jurisdicción, Propiedad Intelectual, etc.")
    resumen: str = Field(description="Resumen breve de qué establece la cláusula")
    pagina: int = Field(description="Número de página donde se encuentra")
    texto_original: str = Field(description="Fragmento textual original de la cláusula")


class ClausulasDetectadas(BaseModel):
    clausulas: list[ClausulaImportante]


class RiesgoDetectado(BaseModel):
    descripcion: str = Field(description="Descripción del riesgo identificado")
    severidad: Literal["alto", "medio", "bajo"] = Field(description="Nivel de severidad")
    clausula_relacionada: str = Field(description="Cláusula o fragmento relacionado con el riesgo")
    pagina: int = Field(description="Número de página donde se encuentra")
    recomendacion: str = Field(description="Recomendación breve y accionable")


class RiesgosDetectados(BaseModel):
    riesgos: list[RiesgoDetectado]


class ExplicacionSimple(BaseModel):
    texto_original: str = Field(description="El texto original de la cláusula consultada")
    explicacion_simple: str = Field(description="Explicación en lenguaje sencillo, sin jerga legal")