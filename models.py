import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("=== MODELOS DISPONIBLES EN TU API KEY ===")
for model in genai.list_models():
    # Filtramos solo los modelos que soportan generación de contenido (Chat/LLM)
    if "generateContent" in model.supported_generation_methods:
        print(f"- {model.name}")