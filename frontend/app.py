# frontend/app.py

import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Analizador de Contratos con IA", layout="wide")


# ---------------------------------------------------------------
# Helpers de estado y llamadas al backend
# ---------------------------------------------------------------

def init_session_state():
    defaults = {
        "contract_id": None,
        "filename": None,
        "resumen": None,
        "clausulas": None,
        "riesgos": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def subir_contrato(file) -> dict | None:
    try:
        response = requests.post(
            f"{BACKEND_URL}/contratos/subir",
            files={"file": (file.name, file.getvalue(), "application/pdf")},
            timeout=120,
        )
        if response.status_code != 200:
            st.error(f"Error al subir el contrato: {response.json().get('detail', 'Error desconocido')}")
            return None
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("No se pudo conectar con el backend. ¿Está corriendo `uvicorn backend.main:app --reload`?")
        return None


def obtener_analisis(endpoint: str) -> dict | None:
    contract_id = st.session_state.contract_id
    try:
        response = requests.get(f"{BACKEND_URL}/contratos/{contract_id}/{endpoint}", timeout=120)
        if response.status_code != 200:
            st.error(f"Error al obtener {endpoint}: {response.json().get('detail', 'Error desconocido')}")
            return None
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("No se pudo conectar con el backend.")
        return None


def pedir_explicacion(pregunta: str) -> dict | None:
    contract_id = st.session_state.contract_id
    try:
        response = requests.post(
            f"{BACKEND_URL}/contratos/{contract_id}/explicar",
            json={"pregunta": pregunta},
            timeout=120,
        )
        if response.status_code != 200:
            st.error(f"Error al generar la explicación: {response.json().get('detail', 'Error desconocido')}")
            return None
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("No se pudo conectar con el backend.")
        return None


# ---------------------------------------------------------------
# Componentes visuales
# ---------------------------------------------------------------

SEVERIDAD_COLOR = {"alto": "🔴", "medio": "🟠", "bajo": "🟢"}


def render_resumen(data: dict):
    st.subheader("Resumen ejecutivo")
    st.write(data["resumen_ejecutivo"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Partes involucradas**")
        for p in data["partes"]:
            st.markdown(f"- {p}")
        st.markdown(f"**Duración:** {data['duracion']}")
    with col2:
        st.markdown("**Objeto del contrato**")
        st.write(data["objeto"])

    st.markdown("**Obligaciones principales**")
    for o in data["obligaciones_principales"]:
        st.markdown(f"- {o}")


def render_clausulas(data: dict):
    st.subheader(f"Cláusulas importantes detectadas ({len(data['clausulas'])})")
    for c in data["clausulas"]:
        with st.expander(f"[{c['tipo']}] — Página {c['pagina']}"):
            st.markdown(f"**Resumen:** {c['resumen']}")
            st.markdown("**Texto original:**")
            st.caption(c["texto_original"])


def render_riesgos(data: dict):
    st.subheader(f"Riesgos identificados ({len(data['riesgos'])})")

    orden = {"alto": 0, "medio": 1, "bajo": 2}
    riesgos_ordenados = sorted(data["riesgos"], key=lambda r: orden.get(r["severidad"], 3))

    for r in riesgos_ordenados:
        icono = SEVERIDAD_COLOR.get(r["severidad"], "⚪")
        with st.expander(f"{icono} [{r['severidad'].upper()}] — Página {r['pagina']}"):
            st.markdown(f"**Descripción:** {r['descripcion']}")
            st.markdown(f"**Cláusula relacionada:** {r['clausula_relacionada']}")
            st.markdown(f"**Recomendación:** {r['recomendacion']}")


def render_explicacion():
    st.subheader("Explica una cláusula en lenguaje sencillo")
    pregunta = st.text_input(
        "Escribe tu duda sobre el contrato",
        placeholder="Ej. ¿Qué pasa si termino el contrato antes de tiempo?"
    )
    if st.button("Explícame esto en simple", disabled=not pregunta):
        with st.spinner("Buscando la cláusula relevante y generando la explicación..."):
            resultado = pedir_explicacion(pregunta)
        if resultado:
            st.markdown("**Texto original relevante:**")
            st.caption(resultado["texto_original"])
            st.markdown("**Explicación en lenguaje sencillo:**")
            st.info(resultado["explicacion_simple"])


# ---------------------------------------------------------------
# Layout principal
# ---------------------------------------------------------------

init_session_state()

st.title("📄 Analizador de Contratos con IA")
st.caption("Sube un contrato en PDF y obtén resumen, cláusulas clave, riesgos y explicaciones en lenguaje sencillo.")

uploaded_file = st.file_uploader("Sube tu contrato (PDF)", type=["pdf"])

if uploaded_file is not None and uploaded_file.name != st.session_state.filename:
    with st.spinner("Procesando el documento (lectura, OCR si aplica, e indexación)..."):
        resultado = subir_contrato(uploaded_file)
    if resultado:
        st.session_state.contract_id = resultado["contract_id"]
        st.session_state.filename = uploaded_file.name
        # Limpiar análisis previos al subir un contrato nuevo
        st.session_state.resumen = None
        st.session_state.clausulas = None
        st.session_state.riesgos = None
        st.success(f"Contrato procesado: {resultado['num_paginas']} páginas.")

if st.session_state.contract_id:
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Resumen", "📌 Cláusulas Importantes", "⚠️ Riesgos", "💬 Explicación en Lenguaje Sencillo"
    ])

    with tab1:
        if st.session_state.resumen is None:
            with st.spinner("Generando resumen..."):
                st.session_state.resumen = obtener_analisis("resumen")
        if st.session_state.resumen:
            render_resumen(st.session_state.resumen)

    with tab2:
        if st.session_state.clausulas is None:
            with st.spinner("Detectando cláusulas importantes..."):
                st.session_state.clausulas = obtener_analisis("clausulas")
        if st.session_state.clausulas:
            render_clausulas(st.session_state.clausulas)

    with tab3:
        if st.session_state.riesgos is None:
            with st.spinner("Identificando riesgos..."):
                st.session_state.riesgos = obtener_analisis("riesgos")
        if st.session_state.riesgos:
            render_riesgos(st.session_state.riesgos)

    with tab4:
        render_explicacion()
else:
    st.info("Sube un contrato en PDF para comenzar el análisis.")