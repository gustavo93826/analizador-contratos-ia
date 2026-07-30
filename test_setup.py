import os
from dotenv import load_dotenv
import pytesseract
import fitz  # PyMuPDF
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# 1. Verificar que la API Key se está leyendo
api_key = os.getenv("GOOGLE_API_KEY")
assert api_key, "❌ No se encontró GOOGLE_API_KEY en el .env"
print("✅ API Key cargada correctamente")

# 2. Verificar Tesseract
print("✅ Versión de Tesseract:", pytesseract.get_tesseract_version())

# 3. Verificar PyMuPDF
print("✅ PyMuPDF importado correctamente, versión:", fitz.__version__)

# 4. Verificar conexión real con Gemini
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=api_key)
respuesta = llm.invoke("Responde solo con la palabra: funciona")
# En lugar de print(respuesta.content)
if isinstance(respuesta.content, list):
    print("✅ Respuesta de Gemini:", respuesta.content[0]['text'])
else:
    print("✅ Respuesta de Gemini:", respuesta.content)