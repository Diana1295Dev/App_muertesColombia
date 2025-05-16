import streamlit as st
import pandas as pd
import plotly.express as px
import os

# === Configuración general ===
st.set_page_config(page_title="Análisis de Mortalidad 2019", layout="wide")
st.title("📊 Análisis de Mortalidad en Colombia - Año 2019")

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

# === Mapa de burbujas: muertes por departamento ===
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
    size_max=40, zoom=4, mapbox_style="open-street-map",
    title="Muertes por departamento (tamaño de burbuja proporcional)"
)
fig_burbujas.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
st.plotly_chart(fig_burbujas, use_container_width=True, key="mapa_burbujas")

# === Gráfico de líneas: muertes por mes ===
st.header("📈 Muertes por mes")
if "MES" in df.columns and not df["MES"].isnull().all():
    muertes_mes = df.groupby("MES").size().reset_index(name="Total")
    muertes_mes["MES"] = pd.Categorical(muertes_mes["MES"], categories=range(1,13), ordered=True)
    muertes_mes = muertes_mes.sort_values("MES")
    fig_line = px.line(muertes_mes, x="MES", y="Total", markers=True, title="Muertes por mes en 2019",
                       labels={"MES": "Mes", "Total": "Número de Muertes"})
    fig_line.update_traces(line=dict(color="#636EFA", width=3), marker=dict(size=8))
    fig_line.update_layout(xaxis=dict(tickmode='linear'))
    st.plotly_chart(fig_line, use_container_width=True, key="linea_mes")
else:
    st.warning("⚠️ La columna 'MES' no está disponible.")

# === Gráfico de barras: ciudades más violentas ===
st.header("🔫 Top 5 ciudades más violentas (homicidios o arma de fuego)")
if all(col in df.columns for col in ["MANERA_MUERTE", "Detalle", "MUNICIPIO"]):
    violentas = df[
        df["MANERA_MUERTE"].str.contains("homicidio", case=False, na=False) |
        df["Detalle"].str.contains("arma de fuego", case=False, na=False)
    ]
    top5 = violentas["MUNICIPIO"].value_counts().nlargest(5).reset_index()
    top5.columns = ["MUNICIPIO", "Total"]
    fig_violentas = px.bar(top5, x="MUNICIPIO", y="Total", title="Top 5 ciudades más violentas",
                           color="Total", color_continuous_scale="Reds")
    fig_violentas.update_layout(xaxis_title="Municipio", yaxis_title="Muertes")
    st.plotly_chart(fig_violentas, use_container_width=True, key="top_violentas")
else:
    st.warning("⚠️ Faltan columnas necesarias para calcular ciudades más violentas.")

# === Gráfico circular: ciudades con menor mortalidad ===
st.header("🥧 10 ciudades con menor mortalidad")
if "MUNICIPIO" in df.columns:
    menores = df["MUNICIPIO"].value_counts().nsmallest(10).reset_index()
    menores.columns = ["MUNICIPIO", "Total"]
    fig_pie = px.pie(menores, names="MUNICIPIO", values="Total", title="10 ciudades con menor mortalidad",
                     hole=0.4)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True, key="menor_mortalidad")
else:
    st.warning("⚠️ La columna 'MUNICIPIO' no está disponible.")

# === Tabla: principales causas de muerte ===
st.header("📋 Top 10 causas de muerte")
if "Nombre_capitulo" in df.columns:
    causas = df.groupby("Nombre_capitulo").size().reset_index(name="Total")
    top_causas = causas.sort_values("Total", ascending=False).head(10)
    st.dataframe(top_causas)
else:
    st.warning("⚠️ La columna 'Nombre_capitulo' no está disponible.")

# === Histograma por edad (quinquenal) ===
st.header("📊 Histograma de edad (quinquenal)")
if "GRUPO_EDAD1" in df.columns:
    edad_map = {
        0: "0-4", 1: "0-4", 2: "0-4", 3: "0-4", 4: "0-4",
        5: "5-9", 6: "5-9", 7: "5-9", 8: "5-9", 9: "5-9",
        10: "10-14", 11: "10-14", 12: "10-14", 13: "10-14", 14: "10-14",
        15: "15-19", 16: "15-19", 17: "15-19", 18: "15-19", 19: "15-19",
        20: "20-24", 21: "20-24", 22: "20-24", 23: "20-24", 24: "20-24",
        25: "25-29", 26: "25-29", 27: "25-29", 28: "25-29", 29: "25-29"
    }
    df["EDAD_QUINQUENAL"] = df["GRUPO_EDAD1"].map(edad_map)
    edad_orden = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29"]
    edad_data = df["EDAD_QUINQUENAL"].value_counts().reindex(edad_orden, fill_value=0).reset_index()
    edad_data.columns = ["Rango de Edad", "Número de Muertes"]
    fig_hist = px.bar(
        edad_data, x="Rango de Edad", y="Número de Muertes",
        title="Distribución de muertes según grupos quinquenales de edad",
        color="Número de Muertes", color_continuous_scale="Blues"
    )
    fig_hist.update_layout(xaxis_title="Edad", yaxis_title="Muertes")
    st.plotly_chart(fig_hist, use_container_width=True, key="hist_edad")
else:
    st.warning("⚠️ La columna 'GRUPO_EDAD1' no está disponible.")

# === Barras apiladas por sexo ===
st.header("🚻 Comparación por sexo y departamento")
if "DEPARTAMENTO" in df.columns and "SEXO" in df.columns:
    df["SEXO"] = df["SEXO"].astype(str).replace({"1": "Hombre", "2": "Mujer", "3": "Sin identificar"})
    sexo_dep = df.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="Total")

    fig_apiladas = px.bar(
        sexo_dep, x="DEPARTAMENTO", y="Total", color="SEXO",
        title="Muertes por sexo en cada departamento",
        barmode="stack",
        labels={"Total": "Número de Muertes", "DEPARTAMENTO": "Departamento"}
    )

    fig_apiladas.update_layout(
        xaxis_title="Departamento",
        yaxis_title="Número de Muertes",
        xaxis_tickangle=45,
        legend_title="Sexo",
        margin=dict(t=40, b=120),
        height=550
    )

    fig_apiladas.update_traces(marker_line_width=0.5)
    st.plotly_chart(fig_apiladas, use_container_width=True, key="sexo_departamento")
else:
    st.warning("⚠️ No se pueden mostrar los datos por sexo y departamento.")
