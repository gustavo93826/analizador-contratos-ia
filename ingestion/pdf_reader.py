# ingestion/pdf_reader.py

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

MIN_CHARS_THRESHOLD = 20   # Si una página tiene menos caracteres que esto, se asume escaneada
OCR_LANG = "spa"           # Idioma para Tesseract (instalado en la Fase 0)
OCR_DPI = 300               # Resolución de renderizado antes del OCR


def extract_native_text(page: fitz.Page) -> str:
    """Extrae el texto nativo (ya digital) de una página de PDF."""
    return page.get_text("text").strip()


def is_scanned_page(text: str) -> bool:
    """
    Heurística: si el texto extraído es muy corto o vacío,
    asumimos que la página es una imagen escaneada sin capa de texto.
    """
    return len(text) < MIN_CHARS_THRESHOLD


def render_page_as_image(page: fitz.Page, dpi: int = OCR_DPI) -> Image.Image:
    """Convierte una página del PDF en una imagen PIL para poder aplicarle OCR."""
    zoom = dpi / 72  # 72 DPI es la resolución base interna de un PDF
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix)
    img_bytes = pix.tobytes("png")
    return Image.open(io.BytesIO(img_bytes))


def ocr_page(page: fitz.Page) -> str:
    """Aplica OCR a una página renderizada como imagen."""
    image = render_page_as_image(page)
    text = pytesseract.image_to_string(image, lang=OCR_LANG)
    return text.strip()


def process_pdf(file_path: str) -> list[dict]:
    """
    Procesa un PDF completo y devuelve una lista de diccionarios,
    uno por página, indicando el texto extraído y su origen (native u ocr).
    """
    doc = fitz.open(file_path)
    pages_data = []

    for page_number, page in enumerate(doc, start=1):
        native_text = extract_native_text(page)

        if is_scanned_page(native_text):
            text = ocr_page(page)
            source = "ocr"
        else:
            text = native_text
            source = "native"

        pages_data.append({
            "page_number": page_number,
            "text": text,
            "source": source
        })

    doc.close()
    return pages_data


def get_full_text(pages_data: list[dict]) -> str:
    """
    Une el texto de todas las páginas en un solo string,
    conservando el número de página (clave para citar la fuente en fases futuras).
    """
    parts = [f"[Página {p['page_number']}]\n{p['text']}" for p in pages_data]
    return "\n\n".join(parts)