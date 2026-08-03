from ingestion.pdf_reader import process_pdf
from rag.indexing import index_contract, query_contract

#1 y 2 estan comentadas para que no se ejecute la ingesta y la indexación cada vez que se corre el test. 

# 1. Ingesta (Fase 1)
#pages = process_pdf("data/uploads/contrato_nativo.pdf")

# 2. Indexación (Fase 2)
#index_contract(pages, contract_id="contrato_nativo")
#print(f"✅ Contrato indexado: {len(pages)} páginas procesadas")

# 3. Prueba de recuperación semántica
query = "¿El bien tiene embargos o pleitos pendientes?"
resultados = query_contract("contrato_nativo", query, k=4)

print(f"\n=== Resultados para: '{query}' ===")
for r in resultados:
    print(f"\n[Página {r.metadata['page_number']} | chunk {r.metadata['chunk_index']}]")
    print(r.page_content)