import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "

# ================= SESSION =================
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""

# ================= FUNCIONES =================
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# ================= UI =================
st.set_page_config(page_title='Tablero Inteligente', layout="wide")

st.title('🧠 Tablero Inteligente')

# 👉 Imagen que elegiste
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Writing_on_the_whiteboard.jpg/960px-Writing_on_the_whiteboard.jpg",
    caption="Imagen ilustrativa de tablero",
    width=600
)

st.subheader("Dibuja un boceto y analízalo con IA")

# ================= SIDEBAR =================
st.sidebar.title("⚙️ Configuración")

stroke_width = st.sidebar.slider('Ancho de línea', 1, 30, 5)

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 API Key")
ke = st.sidebar.text_input('Ingresa tu clave', type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Acerca de")
st.sidebar.info(
    "Esta aplicación demuestra la capacidad de una IA para interpretar bocetos."
)

# ================= CANVAS =================
st.markdown("### ✏️ Área de dibujo")

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color="#000000",
    background_color='#FFFFFF',
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas",
)

# ================= API =================
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# ================= BOTONES =================
col1, col2 = st.columns([1,1])

with col1:
    analyze_button = st.button("🔍 Analizar imagen", use_container_width=True)

with col2:
    clear_button = st.button("🧹 Limpiar", use_container_width=True)

if clear_button:
    st.session_state.analysis_done = False
    st.session_state.full_response = ""
    st.experimental_rerun()

# ================= ANÁLISIS =================
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando imagen... ⏳"):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')
        
        base64_image = encode_image_to_base64("img.png")
        st.session_state.base64_image = base64_image
            
        prompt_text = "Describe en español brevemente la imagen"
    
        try:
            message_placeholder = st.empty()
            full_response = ""

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )
            
            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown("### 🧾 Resultado")
                st.success(full_response)

            st.session_state.full_response = full_response
            st.session_state.analysis_done = True
            
            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = full_response
    
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# ================= HISTORIA =================
if st.session_state.analysis_done:
    st.divider()
    st.subheader("📚 Crear historia")

    if st.button("✨ Generar historia infantil"):
        with st.spinner("Creando historia... 📖"):
            story_prompt = f"Basándote en esta descripción: '{st.session_state.full_response}', crea una historia infantil breve y entretenida."

            story_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=500,
            )

            st.markdown("### 📖 Tu historia:")
            st.info(story_response.choices[0].message.content)

# ================= VALIDACIONES =================
if not api_key:
    st.warning("⚠️ Por favor ingresa tu API key.")
elif canvas_result.image_data is None:
    st.info("✏️ Dibuja algo en el tablero para analizarlo.")
