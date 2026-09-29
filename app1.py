import io
import cv2
from gtts import gTTS
import numpy as np
from PIL import Image
import pytesseract
import streamlit as st

# Configuración de la interfaz
st.set_page_config(
    page_title="LectoKids - Ayudante de Lectura",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- ESTILOS CSS TEMÁTICOS PARA NIÑOS ---
st.markdown(
    """
    <style>
    /* Importación de fuente infantil redondeada */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Fredoka', sans-serif;
    }

    /* Fondo de la app con gradiente suave */
    .stApp {
        background: linear-gradient(180deg, #FFF9E6 0%, #E8F5E9 100%);
    }

    /* Encabezado animado e infantil */
    .kids-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #FFD93D 100%);
        padding: 2rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
        margin-bottom: 1.5rem;
        border: 4px solid #FFFFFF;
    }
    .kids-header h1 {
        color: white !important;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .kids-header p {
        font-size: 1.3rem;
        margin: 0;
        opacity: 0.95;
    }

    /* Tarjetas para contenido */
    .kids-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 6px 15px rgba(0,0,0,0.06);
        border: 3px solid #6C5CE7;
        margin-bottom: 1.5rem;
    }

    /* Personalización de la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #E3F2FD;
        border-right: 3px dashed #90CAF9;
    }

    /* Botones y radio buttons con estilo divertido */
    .stRadio > label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #2D3436;
    }
    
    /* Cajas de alerta estilizadas */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- CABECERA DE LA APP ---
st.markdown(
    """
    <div class="kids-header">
        <h1>📚 LectoKids</h1>
        <p>¡Aprende a leer y a escuchar de forma divertida! 🎈</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "✨ **Toma una foto** o **sube una imagen** con texto para escuchar cómo se lee."
)

# --- IMAGEN DECORATIVA ---
try:
    # Opción 1: Imagen local cargada en tu repositorio
    imagen_banner = Image.open("Niños_leyendo_con_profe.jpg")
    st.image(
        imagen_banner,
        use_container_width=True,
        caption="¡Aprender a leer nunca fue tan fácil!",
    )
except FileNotFoundError:
    # Opción 2: Imagen de respaldo desde internet si no se encuentra 'banner.jpg'
    st.image(
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=800&auto=format&fit=crop",
        use_container_width=True,
        caption="¡Explora y aprende escuchando!",
    )

st.divider()

# --- SELECCIÓN DEL MÉTODO DE ENTRADA ---
opcion_entrada = st.radio(
    "📸 ¿Cómo quieres cargar tu texto?",
    ("Usar Cámara 📸", "Subir Imagen 📁"),
    horizontal=True,
)

img_file_buffer = None

if opcion_entrada == "Usar Cámara 📸":
    img_file_buffer = st.camera_input("Toma una foto del libro o texto")
else:
    img_file_buffer = st.file_uploader(
        "Sube una foto del texto", type=["jpg", "jpeg", "png"]
    )

with st.sidebar:
    st.header("⚙️ Configuración")
    filtro = st.radio("Aplicar Filtro", ("Sin Filtro", "Con Filtro"))

    # Mapeo de idioma para OCR y para Audio
    idioma_opcion = st.selectbox("Idioma del texto", ("Español", "Inglés"))

# Definición de códigos por separado
if idioma_opcion == "Español":
    ocr_lang = "spa"
    tts_lang = "es"
else:
    ocr_lang = "eng"
    tts_lang = "en"

if img_file_buffer is not None:
    # Decodificación de la imagen a OpenCV
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(
        np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR
    )

    # Aplicación de filtro opcional
    if filtro == "Con Filtro":
        cv2_img = cv2.bitwise_not(cv2_img)

    # Procesamiento para OCR
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    texto_detectado = pytesseract.image_to_string(img_rgb, lang=ocr_lang)

    st.divider()
    st.subheader("📝 Texto detectado:")

    texto_limpio = texto_detectado.strip()

    if texto_limpio:
        st.info(f"📖 {texto_limpio}")

        st.subheader("🔊 Audio de lectura:")
        with st.spinner("✨ Generando lectura en voz alta..."):
            try:
                # Usamos tts_lang ("es" o "en") para el sintetizador de voz
                tts = gTTS(text=texto_limpio, lang=tts_lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)

                # Reproducción directa
                st.audio(fp, format="audio/mp3")
                st.balloons()  # Efecto de globos al completar la lectura
            except Exception as e:
                st.error(f"Error al generar el audio: {e}")
    else:
        st.warning(
            "🔍 No se detectó ningún texto claro en la imagen. Intenta enfocar mejor o usar otro ángulo."
        )
