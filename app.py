import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis de Mortalidad 2019", layout="wide")
st.title("📊 Análisis de Mortalidad en Colombia - Año 2019")

# Cargar base unificada
archivo = "Base_Unificada_Limpia_Completa.xlsx"

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

# Filtrar año
df = df[df["AÑO"] == 2019]

# Mapa de burbujas: muertes por departamento con lat/long aproximadas
st.header("🗺️ Mapa de burbujas: Muertes por departamento")
deptos_coords = {
    "ANTIOQUIA": [6.25184, -75.56359], "CUNDINAMARCA": [4.711, -74.0721], "VALLE DEL CAUCA": [3.4516, -76.532],
    "ATLANTICO": [10.9685, -74.7813], "BOLIVAR": [10.3997, -75.5144], "NARIÑO": [1.2136, -77.2811],
    "SANTANDER": [7.1193, -73.1227], "NORTE DE SANTANDER": [7.8833, -72.5078], "TOLIMA": [4.4389, -75.2322],
    "CESAR": [10.4753, -73.2436], "META": [3.9906, -73.7639], "CORDOBA": [8.74798, -75.8814],
    "MAGDALENA": [10.5911, -74.1864], "CAUCA": [2.44, -76.61]
}
burbujas = df.groupby("DEPARTAMENTO").size().reset_index(name="Total Muertes")
burbujas[["LAT", "LON"]] = burbujas["DEPARTAMENTO"].map(deptos_coords).apply(pd.Series)
fig_burbujas = px.scatter_mapbox(
    burbujas,
    lat="LAT",
    lon="LON",
    size="Total Muertes",
    hover_name="DEPARTAMENTO",
    size_max=40,
    zoom=4,
    mapbox_style="carto-positron",
    title="Muertes por departamento (tamaño de burbuja proporcional)"
)
st.plotly_chart(fig_burbujas, use_container_width=True)

# Gráfico de líneas: muertes por mes
st.header("📈 Muertes por mes")
muertes_mes = df.groupby("MES").size().reset_index(name="Total")
fig_line = px.line(muertes_mes, x="MES", y="Total", markers=True, title="Muertes por mes en 2019")
st.plotly_chart(fig_line, use_container_width=True)

# Gráfico de barras: ciudades más violentas (filtro por texto)
st.header("🔫 Top 5 ciudades más violentas (mención textual 'arma de fuego')")
violentas = df[df["Detalle"].str.contains("arma de fuego", case=False, na=False)]
top5 = violentas["MUNICIPIO"].value_counts().nlargest(5).reset_index()
top5.columns = ["MUNICIPIO", "Total"]
fig_violentas = px.bar(top5, x="MUNICIPIO", y="Total", title="Top 5 ciudades más violentas")
st.plotly_chart(fig_violentas, use_container_width=True)

# Gráfico circular: ciudades con menor mortalidad
st.header("🥧 10 ciudades con menor mortalidad")
menores = df["MUNICIPIO"].value_counts().nsmallest(10).reset_index()
menores.columns = ["MUNICIPIO", "Total"]
fig_pie = px.pie(menores, names="MUNICIPIO", values="Total", title="10 ciudades con menor mortalidad")
st.plotly_chart(fig_pie, use_container_width=True)

# Tabla: principales causas de muerte
st.header("📋 Top 10 causas de muerte")
if "Nombre_capitulo" in df.columns:
    causas = df.groupby("Nombre_capitulo").size().reset_index(name="Total")
    top_causas = causas.sort_values("Total", ascending=False).head(10)
    st.dataframe(top_causas)
else:
    st.warning("⚠️ La columna 'Nombre_capitulo' no está disponible para mostrar causas.")

# Histograma: distribución por grupo de edad
st.header("📊 Histograma de edad (quinquenal)")
edad_map = {
    "0 a 4": "0-4", "5 a 9": "5-9", "10 a 14": "10-14", "15 a 19": "15-19",
    "20 a 24": "20-24", "25 a 29": "25-29", "30 a 34": "30-34", "35 a 39": "35-39",
    "40 a 44": "40-44", "45 a 49": "45-49", "50 a 54": "50-54", "55 a 59": "55-59",
    "60 a 64": "60-64", "65 a 69": "65-69", "70 a 74": "70-74", "75 a 79": "75-79",
    "80 a 84": "80-84", "85 y más": "85+"
}
df["GRUPO_EDAD1"] = df["GRUPO_EDAD1"].replace(edad_map)
edad_data = df["GRUPO_EDAD1"].value_counts().sort_index().reset_index()
edad_data.columns = ["Grupo Edad", "Muertes"]
fig_hist = px.bar(edad_data, x="Grupo Edad", y="Muertes", title="Distribución de muertes por edad")
st.plotly_chart(fig_hist, use_container_width=True)

# Barras apiladas: muertes por sexo y departamento
st.header("🚻 Comparación por sexo y departamento")
sexo_dep = df.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="Total")
fig_apiladas = px.bar(sexo_dep, x="DEPARTAMENTO", y="Total", color="SEXO",
                      title="Muertes por sexo en cada departamento")
st.plotly_chart(fig_apiladas, use_container_width=True)

# Gráfico de dispersión: muertes por hora y minutos
st.header("⏰ Muertes por hora y minutos")
df_hora = df.dropna(subset=["HORA", "MINUTOS"])
df_hora = df_hora[(df_hora["HORA"] >= 0) & (df_hora["HORA"] <= 23)]
df_hora = df_hora[(df_hora["MINUTOS"] >= 0) & (df_hora["MINUTOS"] <= 59)]
fig_dispersion = px.scatter(
    df_hora,
    x="HORA",
    y="MINUTOS",
    title="Distribución de muertes por hora y minutos",
    labels={"HORA": "Hora del día", "MINUTOS": "Minutos"},
    opacity=0.5
)
fig_dispersion.update_traces(marker=dict(size=5))
st.plotly_chart(fig_dispersion, use_container_width=True)
