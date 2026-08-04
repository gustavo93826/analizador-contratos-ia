from ingestion.pdf_reader import process_pdf, get_full_text
from rag.indexing import index_contract
from rag.chains import generar_resumen, detectar_clausulas, identificar_riesgos, explicar_en_simple

contract_id = "contrato_nativo"
pdf_path = "data/uploads/contrato_nativo.pdf"

# 1. Ingesta (Fase 1)
pages = process_pdf(pdf_path)
full_text = get_full_text(pages)

# 2. Indexación — necesaria solo para la función 4 (RAG real)
index_contract(pages, contract_id=contract_id)

# 3. Resumen
print("=== RESUMEN ===")
resumen = generar_resumen(full_text)
print(resumen.model_dump_json(indent=2))

# 4. Cláusulas importantes
print("\n=== CLÁUSULAS IMPORTANTES ===")
clausulas = detectar_clausulas(full_text)
for c in clausulas.clausulas:
    print(f"- [{c.tipo}] (pág. {c.pagina}): {c.resumen}")

# 5. Riesgos
print("\n=== RIESGOS ===")
riesgos = identificar_riesgos(full_text)
for r in riesgos.riesgos:
    print(f"- [{r.severidad.upper()}] (pág. {r.pagina}): {r.descripcion}")
    print(f"  Recomendación: {r.recomendacion}")

# 6. Explicación en lenguaje sencillo (RAG real)
print("\n=== EXPLICACIÓN EN LENGUAJE SENCILLO ===")
explicacion = explicar_en_simple(contract_id,  "¿A quién le corresponde pagar las obligaciones fiscales del bien?")
print(explicacion.model_dump_json(indent=2))