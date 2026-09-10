import io
import cv2
from gtts import gTTS
import numpy as np
from PIL import Image
import pytesseract
import streamlit as st

# Configuración de la interfaz
st.set_page_config(
    page_title="LectoKids - Ayudante de Lectura", layout="centered"
)

st.title("📚 LectoKids: ¡Aprende a Leer!")
st.write(
    "Toma una foto o sube una imagen con texto para escuchar cómo se lee."
)

# --- IMAGEN DECORATIVA ---
# Puedes guardar una imagen llamada "banner.jpg" en la carpeta del repositorio,
# o usar una imagen desde una URL pública.
try:
    # Opción 1: Imagen local cargada en tu repositorio
    imagen_banner = Image.open("banner.jpg")
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
    "Selecciona la fuente de la imagen:",
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
        st.info(texto_limpio)

        st.subheader("🔊 Audio de lectura:")
        with st.spinner("Generando lectura en voz alta..."):
            try:
                # Usamos tts_lang ("es" o "en") para el sintetizador de voz
                tts = gTTS(text=texto_limpio, lang=tts_lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)

                # Reproducción directa
                st.audio(fp, format="audio/mp3")
            except Exception as e:
                st.error(f"Error al generar el audio: {e}")
    else:
        st.warning(
            "No se detectó ningún texto claro en la imagen. Intenta enfocar mejor o usar otro ángulo."
        )
