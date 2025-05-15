import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Análisis de Mortalidad 2019", layout="wide")
st.title("📊 Análisis de Mortalidad en Colombia - Año 2019")

# === Cargar base unificada ===
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

# === Filtrar solo año 2019 ===
if "AÑO" not in df.columns:
    st.error("❌ La columna 'AÑO' no está en los datos.")
    st.stop()
df = df[df["AÑO"] == 2019]

# === Mapa de burbujas ===
st.header("🗺️ Mapa de burbujas: Muertes por departamento")
deptos_coords = {
    "ANTIOQUIA": [6.25184, -75.56359], "CUNDINAMARCA": [4.711, -74.0721], "VALLE DEL CAUCA": [3.4516, -76.532],
    "ATLANTICO": [10.9685, -74.7813], "BOLIVAR": [10.3997, -75.5144], "NARIÑO": [1.2136, -77.2811],
    "SANTANDER": [7.1193, -73.1227], "NORTE DE SANTANDER": [7.8833, -72.5078], "TOLIMA": [4.4389, -75.2322],
    "CESAR": [10.4753, -73.2436], "META": [3.9906, -73.7639], "CORDOBA": [8.74798, -75.8814],
    "MAGDALENA": [10.5911, -74.1864], "CAUCA": [2.44, -76.61]
}
burbujas = df.groupby("DEPARTAMENTO").size().reset_index(name="Total Muertes")
burbujas[["LAT", "LON"]] = burbujas["DEPARTAMENTO"].apply(
    lambda d: pd.Series(deptos_coords.get(d, [None, None]))
)
burbujas = burbujas.dropna(subset=["LAT", "LON"])
fig_burbujas = px.scatter_mapbox(
    burbujas, lat="LAT", lon="LON", size="Total Muertes", hover_name="DEPARTAMENTO",
    size_max=40, zoom=4, mapbox_style="carto-positron",
    title="Muertes por departamento (tamaño de burbuja proporcional)"
)
st.plotly_chart(fig_burbujas, use_container_width=True, key="mapa_burbujas")

# === Muertes por mes ===
st.header("📈 Muertes por mes")
if "MES" in df.columns:
    muertes_mes = df.groupby("MES").size().reset_index(name="Total")
    fig_line = px.line(muertes_mes, x="MES", y="Total", markers=True, title="Muertes por mes en 2019")
    st.plotly_chart(fig_line, use_container_width=True, key="line_mes")
else:
    st.warning("⚠️ La columna 'MES' no está disponible.")

# === Ciudades más violentas ===
st.header("🔫 Top 5 ciudades más violentas (homicidios o arma de fuego)")
if "MANERA_MUERTE" in df.columns and "Detalle" in df.columns and "MUNICIPIO" in df.columns:
    violentas = df[
        df["MANERA_MUERTE"].str.contains("homicidio", case=False, na=False) |
        df["Detalle"].str.contains("arma de fuego", case=False, na=False)
    ]
    top5 = violentas["MUNICIPIO"].value_counts().nlargest(5).reset_index()
    top5.columns = ["MUNICIPIO", "Total"]
    fig_violentas = px.bar(top5, x="MUNICIPIO", y="Total", title="Top 5 ciudades más violentas")
    st.plotly_chart(fig_violentas, use_container_width=True, key="violentas")
else:
    st.warning("⚠️ Faltan columnas para calcular ciudades más violentas.")

# === Ciudades con menor mortalidad ===
st.header("🥧 10 ciudades con menor mortalidad")
if "MUNICIPIO" in df.columns:
    menores = df["MUNICIPIO"].value_counts().nsmallest(10).reset_index()
    menores.columns = ["MUNICIPIO", "Total"]
    fig_pie = px.pie(menores, names="MUNICIPIO", values="Total", title="10 ciudades con menor mortalidad")
    st.plotly_chart(fig_pie, use_container_width=True, key="pie_menor")
else:
    st.warning("⚠️ La columna 'MUNICIPIO' no está disponible.")

# === Principales causas de muerte ===
st.header("📋 Top 10 causas de muerte")
if "Nombre_capitulo" in df.columns:
    causas = df.groupby("Nombre_capitulo").size().reset_index(name="Total")
    top_causas = causas.sort_values("Total", ascending=False).head(10)
    st.dataframe(top_causas)
else:
    st.warning("⚠️ La columna 'Nombre_capitulo' no está disponible.")

# === Histograma por edad (quinquenal, hasta 29 años) ===
st.header("📊 Histograma de edad (quinquenal)")
if "GRUPO_EDAD1" in df.columns:
    def map_edad(grupo):
        if pd.isna(grupo):
            return np.nan
        grupo = grupo.lower()
        if "0" in grupo and "4" in grupo:
            return "0-4"
        elif "5" in grupo and "9" in grupo:
            return "5-9"
        elif "10" in grupo and "14" in grupo:
            return "10-14"
        elif "15" in grupo and "19" in grupo:
            return "15-19"
        elif "20" in grupo and "24" in grupo:
            return "20-24"
        elif "25" in grupo and "29" in grupo:
            return "25-29"
        else:
            return np.nan

    df["GRUPO_EDAD_Q"] = df["GRUPO_EDAD1"].apply(map_edad)
    edad_orden = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29"]
    edad_data = df["GRUPO_EDAD_Q"].value_counts().reindex(edad_orden).dropna().reset_index()
    edad_data.columns = ["Rango de Edad", "Número de Muertes"]

    if not edad_data.empty:
        fig_hist = px.bar(
            edad_data, x="Rango de Edad", y="Número de Muertes",
            title="Distribución de muertes según grupos quinquenales de edad",
            color="Número de Muertes", color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_hist, use_container_width=True, key="hist_edad")
    else:
        st.info("ℹ️ No hay datos disponibles para los rangos de edad definidos.")
else:
    st.warning("⚠️ La columna 'GRUPO_EDAD1' no está disponible.")

# === Comparación por sexo y departamento ===
st.header("🚻 Comparación por sexo y departamento")
if "DEPARTAMENTO" in df.columns and "SEXO" in df.columns:
    sexo_dep = df.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="Total")
    fig_apiladas = px.bar(
        sexo_dep, x="DEPARTAMENTO", y="Total", color="SEXO",
        title="Muertes por sexo en cada departamento"
    )
    st.plotly_chart(fig_apiladas, use_container_width=True, key="sexo_dep")
else:
    st.warning("⚠️ Faltan columnas para mostrar muertes por sexo y departamento.")

# === Dispersión de hora y minutos ===
st.header("⏰ Muertes por hora y minutos")
if "HORA" in df.columns and "MINUTOS" in df.columns:
    df_hora = df.dropna(subset=["HORA", "MINUTOS"])
    df_hora = df_hora[(df_hora["HORA"].between(0, 23)) & (df_hora["MINUTOS"].between(0, 59))]
    fig_dispersion = px.scatter(
        df_hora, x="HORA", y="MINUTOS",
        title="Distribución de muertes por hora y minutos",
        labels={"HORA": "Hora del día", "MINUTOS": "Minutos"},
        opacity=0.5
    )
    fig_dispersion.update_traces(marker=dict(size=5))
    st.plotly_chart(fig_dispersion, use_container_width=True, key="hora_min")
else:
    st.warning("⚠️ No se pueden mostrar las muertes por hora y minutos.")
