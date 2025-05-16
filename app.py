import streamlit as st
import pandas as pd
import plotly.express as px
import os

# === Configuración general ===
st.set_page_config(page_title="Análisis de Mortalidad 2019 🇨🇴", layout="wide")

# === Encabezado ===
col1, col2 = st.columns([1, 10])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4474/4474364.png", width=60)
with col2:
    st.title("Análisis Interactivo de Mortalidad en Colombia - 2019")
    st.markdown(
        "<span style='color: gray;'>🗓️ Datos filtrados por año, agrupados y visualizados para comprender tendencias demográficas y geográficas.</span>",
        unsafe_allow_html=True
    )

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

# === KPIs visuales con estilo personalizado ===
st.markdown("### 📌 Indicadores principales")

kpi1 = len(df)
kpi2 = df["MANERA_MUERTE"].nunique()
kpi3 = df["SEXO"].replace({1: "Hombre", 2: "Mujer", 3: "Sin identificar"}).value_counts().idxmax()
kpi4 = df["DEPARTAMENTO"].value_counts().idxmax()
kpi5 = df["DEPARTAMENTO"].value_counts().idxmin()

col1, col2, col3, col4, col5 = st.columns(5)

kpi_style = """
    <div style="
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.05);
        height: 100px;
    ">
        <div style="font-size: 16px; color: #666;">{titulo}</div>
        <div style="font-size: 28px; font-weight: bold; color: #333;">{valor}</div>
    </div>
"""

with col1:
    st.markdown(kpi_style.format(titulo="👥 Personas registradas", valor=f"{kpi1:,}"), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_style.format(titulo="🧬 Tipos de muerte", valor=kpi2), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_style.format(titulo="🛋️ Sexo con más muertes", valor=kpi3), unsafe_allow_html=True)
with col4:
    st.markdown(kpi_style.format(titulo="📍 Dpto. con más muertes", valor=kpi4), unsafe_allow_html=True)
with col5:
    st.markdown(kpi_style.format(titulo="📉 Dpto. con menos muertes", valor=kpi5), unsafe_allow_html=True)

# === Menú de navegación ===
menu = st.radio("📊 Ir a sección:", [
    "📽️ Mapa de burbujas",
    "📈 Muertes por mes",
    "🔫 Ciudades más violentas",
    "🥧 Ciudades con menor mortalidad",
    "📋 Causas de muerte",
    "📊 Histograma por edad",
    "🚻 Sexo por departamento"
], horizontal=True)

# === Visualizaciones ===
if menu == "📽️ Mapa de burbujas":
    st.subheader("📽️ Mapa de burbujas: Muertes por departamento")
    deptos_coords = {
        "ANTIOQUIA": [6.25184, -75.56359], "CUNDINAMARCA": [4.711, -74.0721], "VALLE DEL CAUCA": [3.4516, -76.532],
        "ATLANTICO": [10.9685, -74.7813], "BOLIVAR": [10.3997, -75.5144], "NARIÑO": [1.2136, -77.2811],
        "SANTANDER": [7.1193, -73.1227], "NORTE DE SANTANDER": [7.8833, -72.5078], "TOLIMA": [4.4389, -75.2322],
        "CESAR": [10.4753, -73.2436], "META": [3.9906, -73.7639], "CORDOBA": [8.74798, -75.8814],
        "MAGDALENA": [10.5911, -74.1864], "CAUCA": [2.44, -76.61]
    }
    burbujas = df.groupby("DEPARTAMENTO").size().reset_index(name="Total Muertes")
    burbujas[["LAT", "LON"]] = burbujas["DEPARTAMENTO"].apply(lambda d: pd.Series(deptos_coords.get(d, [None, None])))
    burbujas = burbujas.dropna()
    fig_burbujas = px.scatter_mapbox(
        burbujas, lat="LAT", lon="LON", size="Total Muertes", hover_name="DEPARTAMENTO",
        zoom=4, size_max=40, mapbox_style="open-street-map")
    st.plotly_chart(fig_burbujas, use_container_width=True)

elif menu == "📈 Muertes por mes":
    st.subheader("📈 Distribución mensual de muertes")
    if "MES" in df.columns:
        muertes_mes = df.groupby("MES").size().reset_index(name="Total")
        muertes_mes["MES"] = pd.Categorical(muertes_mes["MES"], categories=range(1, 13), ordered=True)
        muertes_mes = muertes_mes.sort_values("MES")
        fig_line = px.line(muertes_mes, x="MES", y="Total", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("⚠️ La columna 'MES' no está disponible.")

elif menu == "🔫 Ciudades más violentas":
    st.subheader("🔫 Top 5 ciudades más violentas")
    if all(col in df.columns for col in ["MANERA_MUERTE", "Detalle", "MUNICIPIO"]):
        violentas = df[df["MANERA_MUERTE"].str.contains("homicidio", case=False, na=False) |
                       df["Detalle"].str.contains("arma de fuego", case=False, na=False)]
        top5 = violentas["MUNICIPIO"].value_counts().nlargest(5).reset_index()
        top5.columns = ["MUNICIPIO", "Total"]
        fig_violentas = px.bar(top5, x="MUNICIPIO", y="Total", color="Total", color_continuous_scale="Reds")
        st.plotly_chart(fig_violentas, use_container_width=True)
    else:
        st.warning("⚠️ Datos insuficientes para esta sección.")

elif menu == "🥧 Ciudades con menor mortalidad":
    st.subheader("🥧 10 ciudades con menor mortalidad")
    if "MUNICIPIO" in df.columns:
        menores = df["MUNICIPIO"].value_counts().nsmallest(10).reset_index()
        menores.columns = ["MUNICIPIO", "Total"]
        fig_pie = px.pie(menores, names="MUNICIPIO", values="Total", hole=0.4)
        fig_pie.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("⚠️ La columna 'MUNICIPIO' no está disponible.")

elif menu == "📋 Causas de muerte":
    st.subheader("📋 Top 10 causas de muerte")
    if "Nombre_capitulo" in df.columns:
        causas = df["Nombre_capitulo"].value_counts().nlargest(10).reset_index()
        causas.columns = ["Causa", "Total"]
        st.dataframe(causas)
    else:
        st.warning("⚠️ La columna 'Nombre_capitulo' no está disponible.")

elif menu == "📊 Histograma por edad":
    st.subheader("📊 Histograma de edad (quinquenal)")
    if "GRUPO_EDAD1" in df.columns:
        edad_map = {i: f"{5*(i//5)}-{5*(i//5)+4}" for i in range(30)}
        df["EDAD_QUINQUENAL"] = df["GRUPO_EDAD1"].map(edad_map)
        edad_data = df["EDAD_QUINQUENAL"].value_counts().sort_index().reset_index()
        edad_data.columns = ["Rango de Edad", "Muertes"]
        fig_hist = px.bar(edad_data, x="Rango de Edad", y="Muertes", color="Muertes",
                          color_continuous_scale="Blues")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("⚠️ La columna 'GRUPO_EDAD1' no está disponible.")

elif menu == "🚻 Sexo por departamento":
    st.subheader("🚻 Comparación por sexo y departamento")
    if "DEPARTAMENTO" in df.columns and "SEXO" in df.columns:
        df["SEXO"] = df["SEXO"].astype(str).replace({"1": "Hombre", "2": "Mujer", "3": "Sin identificar"})
        sexo_dep = df.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="Total")
        fig_apiladas = px.bar(
            sexo_dep, x="DEPARTAMENTO", y="Total", color="SEXO", barmode="group",
            title="Distribución de muertes por sexo y departamento",
            labels={"DEPARTAMENTO": "Departamento", "Total": "Cantidad de muertes"},
            color_discrete_sequence=px.colors.qualitative.Set2)
        fig_apiladas.update_layout(xaxis_tickangle=45, height=600, bargap=0.25)
        st.plotly_chart(fig_apiladas, use_container_width=True)
    else:
        st.warning("⚠️ No se pueden mostrar los datos por sexo y departamento.")
