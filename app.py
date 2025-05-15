import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis de Mortalidad 2019", layout="wide")
st.title("📊 Análisis de Mortalidad en Colombia - Año 2019")

# === Cargar base de datos ===
@st.cache_data

def cargar_datos():
    archivo = "Base_Unificada_Limpia_Completa.xlsx"
    try:
        return pd.read_excel(archivo)
    except FileNotFoundError:
        st.error("❌ No se encuentra el archivo Base_Unificada_Limpia_Completa.xlsx")
        return pd.DataFrame()

df = cargar_datos()

if df.empty or "AÑO" not in df.columns:
    st.error("❌ Datos no disponibles o falta la columna 'AÑO'.")
    st.stop()

# === Filtrar por año 2019 ===
df = df[df["AÑO"] == 2019]

# === Secciones en tabs ===
tabs = st.tabs([
    "🗺️ Mapa de burbujas",
    "📈 Muertes por mes",
    "🔫 Ciudades violentas",
    "🥧 Menor mortalidad",
    "📋 Causas de muerte",
    "📊 Histograma edad",
    "🚻 Sexo y departamento",
    "⏰ Hora y minutos"
])

# === Mapa de burbujas ===
with tabs[0]:
    st.header("🗺️ Mapa de burbujas: Muertes por departamento")
    deptos_coords = {
        "ANTIOQUIA": [6.25184, -75.56359], "CUNDINAMARCA": [4.711, -74.0721],
        "VALLE DEL CAUCA": [3.4516, -76.532], "ATLANTICO": [10.9685, -74.7813],
        "BOLIVAR": [10.3997, -75.5144], "NARIÑO": [1.2136, -77.2811],
        "SANTANDER": [7.1193, -73.1227], "NORTE DE SANTANDER": [7.8833, -72.5078],
        "TOLIMA": [4.4389, -75.2322], "CESAR": [10.4753, -73.2436],
        "META": [3.9906, -73.7639], "CORDOBA": [8.74798, -75.8814],
        "MAGDALENA": [10.5911, -74.1864], "CAUCA": [2.44, -76.61]
    }
    burbujas = df.groupby("DEPARTAMENTO").size().reset_index(name="Total Muertes")
    burbujas[["LAT", "LON"]] = burbujas["DEPARTAMENTO"].apply(lambda d: pd.Series(deptos_coords.get(d, [None, None])))
    burbujas = burbujas.dropna(subset=["LAT", "LON"])
    fig = px.scatter_mapbox(
        burbujas, lat="LAT", lon="LON", size="Total Muertes", hover_name="DEPARTAMENTO",
        size_max=40, zoom=4, mapbox_style="carto-positron",
        title="Muertes por departamento (tamaño de burbuja proporcional)"
    )
    st.plotly_chart(fig, use_container_width=True, key="mapa_burbujas")

# === Muertes por mes ===
with tabs[1]:
    st.header("📈 Muertes por mes")
    if "MES" in df.columns:
        data = df.groupby("MES").size().reset_index(name="Total")
        fig = px.line(data, x="MES", y="Total", markers=True, title="Muertes por mes en 2019")
        st.plotly_chart(fig, use_container_width=True, key="muertes_mes")
    else:
        st.warning("⚠️ La columna 'MES' no está disponible.")

# === Ciudades violentas ===
with tabs[2]:
    st.header("🔫 Top 5 ciudades más violentas")
    if all(col in df.columns for col in ["MANERA_MUERTE", "Detalle", "MUNICIPIO"]):
        violentas = df[
            df["MANERA_MUERTE"].str.contains("homicidio", case=False, na=False) |
            df["Detalle"].str.contains("arma de fuego", case=False, na=False)
        ]
        top5 = violentas["MUNICIPIO"].value_counts().nlargest(5).reset_index()
        top5.columns = ["MUNICIPIO", "Total"]
        fig = px.bar(top5, x="MUNICIPIO", y="Total", title="Top 5 ciudades más violentas")
        st.plotly_chart(fig, use_container_width=True, key="top_violentas")
    else:
        st.warning("⚠️ Columnas necesarias no disponibles.")

# === Menor mortalidad ===
with tabs[3]:
    st.header("🥧 10 ciudades con menor mortalidad")
    if "MUNICIPIO" in df.columns:
        menores = df["MUNICIPIO"].value_counts().nsmallest(10).reset_index()
        menores.columns = ["MUNICIPIO", "Total"]
        fig = px.pie(menores, names="MUNICIPIO", values="Total", title="10 ciudades con menor mortalidad")
        st.plotly_chart(fig, use_container_width=True, key="menor_mortalidad")
    else:
        st.warning("⚠️ Falta la columna 'MUNICIPIO'.")

# === Causas de muerte ===
with tabs[4]:
    st.header("📋 Top 10 causas de muerte")
    if "Nombre_capitulo" in df.columns:
        causas = df.groupby("Nombre_capitulo").size().reset_index(name="Total")
        top = causas.sort_values("Total", ascending=False).head(10)
        st.dataframe(top)
    else:
        st.warning("⚠️ Columna 'Nombre_capitulo' no disponible.")

# === Histograma por edad ===
with tabs[5]:
    st.header("📊 Histograma de edad (quinquenal)")
    if "GRUPO_EDAD1" in df.columns:
        edad_map = {
            "0 a 4": "0-4", "5 a 9": "5-9", "10 a 14": "10-14",
            "15 a 19": "15-19", "20 a 24": "20-24", "25 a 29": "25-29"
        }
        df["GRUPO_EDAD1"] = df["GRUPO_EDAD1"].replace(edad_map)
        orden = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29"]
        edad = df["GRUPO_EDAD1"].value_counts().reindex(orden).dropna().reset_index()
        edad.columns = ["Grupo Edad", "Muertes"]
        fig = px.bar(edad, x="Grupo Edad", y="Muertes", color="Muertes",
                     color_continuous_scale="Blues",
                     title="Muertes por grupos quinquenales de edad")
        st.plotly_chart(fig, use_container_width=True, key="hist_edad")
    else:
        st.warning("⚠️ Falta la columna 'GRUPO_EDAD1'.")

# === Comparación por sexo y departamento ===
with tabs[6]:
    st.header("🚻 Comparación por sexo y departamento")
    if all(col in df.columns for col in ["DEPARTAMENTO", "SEXO"]):
        sexo_dep = df.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="Total")
        fig = px.bar(sexo_dep, x="DEPARTAMENTO", y="Total", color="SEXO",
                     title="Muertes por sexo en cada departamento")
        st.plotly_chart(fig, use_container_width=True, key="sexo_departamento")
    else:
        st.warning("⚠️ Faltan columnas para comparar por sexo.")

# === Muertes por hora y minutos ===
with tabs[7]:
    st.header("⏰ Muertes por hora y minutos")
    if all(col in df.columns for col in ["HORA", "MINUTOS"]):
        df_hora = df.dropna(subset=["HORA", "MINUTOS"])
        df_hora = df_hora[(df_hora["HORA"].between(0, 23)) & (df_hora["MINUTOS"].between(0, 59))]
        fig = px.scatter(df_hora, x="HORA", y="MINUTOS",
                         title="Distribución de muertes por hora y minutos",
                         labels={"HORA": "Hora del día", "MINUTOS": "Minutos"}, opacity=0.5)
        fig.update_traces(marker=dict(size=5))
        st.plotly_chart(fig, use_container_width=True, key="muertes_hora")
    else:
        st.warning("⚠️ Faltan columnas de hora o minutos.")