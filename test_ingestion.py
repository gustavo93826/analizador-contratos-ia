from ingestion.pdf_reader import process_pdf, get_full_text

pdf_nativo = "data/uploads/contrato_nativo.pdf"
pdf_escaneado = "data/uploads/contrato_escaneado.pdf"

print("=== PDF NATIVO ===")
pages = process_pdf(pdf_nativo)
for p in pages:
    print(f"Página {p['page_number']} | fuente: {p['source']} | caracteres: {len(p['text'])}")

print("\n=== PDF ESCANEADO ===")
pages_ocr = process_pdf(pdf_escaneado)
for p in pages_ocr:
    print(f"Página {p['page_number']} | fuente: {p['source']} | caracteres: {len(p['text'])}")

print("\n--- Vista previa del texto completo (nativo) ---")
print(get_full_text(pages)[:500])