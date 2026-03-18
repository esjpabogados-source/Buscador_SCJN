import streamlit as st
import pandas as pd
from scjn_api import SJFAPI
import ia_helper
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generar_pdf_tesis(registro, rubro, instancia, epoca, tipo_tesis, texto):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    Story = []
    
    Story.append(Paragraph(f"<b>Registro Digital:</b> {registro}", styles['Normal']))
    Story.append(Paragraph(f"<b>Tipo:</b> {tipo_tesis}", styles['Normal']))
    Story.append(Paragraph(f"<b>Instancia:</b> {instancia}", styles['Normal']))
    Story.append(Paragraph(f"<b>Época:</b> {epoca}", styles['Normal']))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("<b>Rubro:</b>", styles['Heading3']))
    Story.append(Paragraph(rubro, styles['Normal']))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("<b>Texto:</b>", styles['Heading3']))
    for p in str(texto).split('\n'):
        if p.strip():
            # Handle standard XML characters avoiding reportlab errors
            p_clean = p.strip().replace('<', '&lt;').replace('>', '&gt;')
            Story.append(Paragraph(p_clean, styles['Normal']))
            Story.append(Spacer(1, 6))
            
    doc.build(Story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

st.set_page_config(page_title="Buscador de Jurisprudencia SCJN", layout="wide", page_icon="⚖️")

# Custom CSS for aesthetics
st.markdown("""
<style>
    .main-header {
        font-family: 'Inter', sans-serif;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-family: 'Inter', sans-serif;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .result-card {
        background-color: #F8FAFC;
        border-right: 4px solid #3B82F6;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    .rubro-text {
        color: #0F172A;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .metadata-tag {
        display: inline-block;
        background-color: #DBEAFE;
        color: #1D4ED8;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: 600;
        background-color: #3B82F6;
        color: white;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_api():
    return SJFAPI()

api = get_api()

st.markdown('<h1 class="main-header">🏛️ Buscador Interactivo SCJN</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Accede al Semanario Judicial de la Federación y consulta criterios, tesis y jurisprudencias en tiempo real.</p>', unsafe_allow_html=True)

# Sidebar for filters
with st.sidebar:
    st.header("🔍 Filtros de Búsqueda")
    termino = st.text_input("Palabras Clave o Pregunta", placeholder="Ej. jurisprudencias de pensión alimenticia en oaxaca", help="Ingresa términos exactos o haz una búsqueda con IA.")
    
    st.subheader("Búsqueda Inteligente (IA)")
    usar_ia = st.toggle("Activar Búsqueda con IA", help="Traduce lenguaje natural a términos de búsqueda óptimos para la SCJN.")
    api_key_gemini = ""
    if usar_ia:
        api_key_gemini = st.text_input("API Key de Gemini", type="password", help="Obtén tu clave gratuita en Google AI Studio.")
    
    st.subheader("Configuración")
    resultados_por_pagina = st.slider("Resultados a mostrar", min_value=10, max_value=50, value=20, step=10)
    
    buscar_btn = st.button("Buscar en la SCJN", use_container_width=True)

# Main content area
if buscar_btn:
    if not termino:
        st.warning("⚠️ Por favor, introduce al menos una palabra clave o pregunta para realizar la búsqueda.")
    elif usar_ia and not api_key_gemini:
        st.error("🔑 Necesitas ingresar una API Key de Gemini para usar la Búsqueda Inteligente.")
    else:
        with st.spinner("Analizando y buscando en la SCJN..."):
            termino_busqueda = termino
            
            # Si el usuario quiere usar IA
            if usar_ia and api_key_gemini:
                ia_helper.configurar_gemini(api_key_gemini)
                st.info("🧠 **Procesando lenguaje natural con Gemini...**")
                resultado_ia = ia_helper.procesar_busqueda_ia(termino)
                if resultado_ia and "error" in resultado_ia:
                    st.error(f"❌ Error al procesar la IA: {resultado_ia['error']}")
                    st.info("Revisa que tu API Key sea correcta o intenta de nuevo más tarde.")
                elif resultado_ia:
                    termino_busqueda = resultado_ia.get('terminos_optimizados', termino)
                    with st.expander("🤖 Análisis de la IA sobre tu búsqueda", expanded=True):
                        st.markdown(f"**Intención detectada y términos generados:** `{termino_busqueda}`")
                        st.write(resultado_ia.get('explicacion', ''))
                else:
                    st.error("Hubo un problema desconocido al procesar la IA. Cayendo de vuelta a búsqueda normal.")
            
            resultados = api.buscar_tesis(termino_busqueda, page=0, size=resultados_por_pagina)
            
            if resultados and 'documents' in resultados and len(resultados['documents']) > 0:
                total_encontrados = resultados.get('total', 0)
                st.success(f"✅ Se encontraron **{total_encontrados}** resultados para '{termino}'. Mostrando los primeros {len(resultados['documents'])}.")
                
                for item in resultados['documents']:
                    registro = item.get('ius', item.get('id', 'N/A'))
                    rubro = item.get('rubro', 'Sin rubro')
                    instancia = item.get('instanciaAbr', 'Instancia no especificada')
                    epoca = item.get('epocaAbr', 'Época no especificada')
                    tipo_tesis = 'Jurisprudencia' if item.get('tipoTesis') == '1' else 'Tesis Aislada'
                    
                    # Highlight terms in text if present
                    texto = item.get('texto', 'Texto no disponible en vista previa corta.')
                    if not texto:
                        texto = item.get('textoPublicacion', 'Texto no disponible.')
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="rubro-text">{rubro}</div>
                            <div>
                                <span class="metadata-tag">#{registro}</span>
                                <span class="metadata-tag">Tipo: {tipo_tesis}</span>
                                <span class="metadata-tag">🏛️ {instancia}</span>
                                <span class="metadata-tag">📅 {epoca}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("📄 Ver texto completo de la Tesis/Jurisprudencia"):
                            st.write(texto)
                            
                            pdf_bytes = generar_pdf_tesis(registro, rubro, instancia, epoca, tipo_tesis, texto)
                            
                            st.download_button(
                                label="📥 Descargar Documento (PDF)",
                                data=pdf_bytes,
                                file_name=f"SCJN_{registro}.pdf",
                                mime="application/pdf",
                                key=f"dl_{registro}"
                            )
            else:
                st.info(f"No se encontraron resultados en el SJF para '{termino}'. Intenta con otros términos.")
else:
    st.info("👈 Ingresa tus palabras clave en el panel izquierdo y haz clic en 'Buscar' para comenzar.")
