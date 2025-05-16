import streamlit as st
import pandas as pd
import plotly.express as px
import os
from streamlit_extras.emoji_rain import rain

# === Configuración general ===
st.set_page_config(page_title="Análisis de Mortalidad 2019 🇨🇴", layout="wide")

# === Encabezado visual llamativo ===
col1, col2 = st.columns([1, 10])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4474/4474364.png", width=60)
with col2:
    st.title("Análisis Interactivo de Mortalidad en Colombia - 2019")
    st.markdown("""
    <span style='color: gray;'>📅 Datos filtrados por año, agrupados y visualizados para comprender tendencias demográficas y geográficas.</span>
    """, unsafe_allow_html=True)

# === Decoración animada (opcional) ===
rain(emoji="💀", font_size=20, falling_speed=5, animation_length="infinite")

# === Menú de navegación con emojis ===
menu = st.radio("📊 Ir a sección:", [
    "🗺️ Mapa de burbujas",
    "📈 Muertes por mes",
    "🔫 Ciudades más violentas",
    "🥧 Ciudades con menor mortalidad",
    "📋 Causas de muerte",
    "📊 Histograma por edad",
    "🚻 Sexo por departamento"
], horizontal=True)

# === Cargar base de datos ===
archivo = os.path.join(os.getcwd(), "Base_Unificada_Limpia_Completa.xlsx")

@st.cache_data
def cargar_datos():
    try:
        return pd.read_excel(archivo)
    except FileNotFoundError:
        st.error("❌ No se encuentra el archivo Base_Unificada_Limpia_Completa.xlsx")
        return pd.DataFrame()

df = cargar_datos()
if df.empty:
    st.stop()

# === Filtrar por año 2019 ===
if "AÑO" not in df.columns:
    st.error("❌ La columna 'AÑO' no está en los datos.")
    st.stop()
df = df[df["AÑO"] == 2019]