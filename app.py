import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# --- Configuración de rutas y carga de datos ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "src", "Base_Unificada_Limpia_Completa.xlsx")

def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    return pd.read_excel(path)

def compute_kpis(df: pd.DataFrame) -> dict:
    sexo_map = {1: "Hombre", 2: "Mujer", 3: "Sin identificar"}
    df_sexo = df.replace({"SEXO": sexo_map})
    return {
        "total_registros": len(df),
        "tipos_muerte": df["MANERA_MUERTE"].nunique(),
        "sexo_max": df_sexo["SEXO"].value_counts().idxmax(),
        "dpto_max": df["DEPARTAMENTO"].value_counts().idxmax(),
        "dpto_min": df["DEPARTAMENTO"].value_counts().idxmin(),
    }

# Coordenadas de departamentos de Colombia
DEPT_COORDS = {
    "AMAZONAS": (-1.4419, -70.1449), "ANTIOQUIA": (6.2518, -75.5636), "ARAUCA": (7.0856, -70.7591),
    "ATLÁNTICO": (10.9685, -74.7813), "BOLÍVAR": (10.3910, -75.4794), "BOYACÁ": (5.4545, -73.3620),
    "CALDAS": (5.0703, -75.5138), "CAQUETÁ": (0.8699, -73.8419), "CASANARE": (5.3548, -71.9269),
    "CAUCA": (2.4411, -76.6063), "CESAR": (9.3373, -73.6536), "CHOCÓ": (5.6947, -76.6612),
    "CÓRDOBA": (8.7470, -75.8814), "CUNDINAMARCA": (4.6486, -74.2479), "GUAINÍA": (2.5854, -68.5247),
    "GUAVIARE": (2.0439, -72.3311), "HUILA": (2.5359, -75.5277), "LA GUAJIRA": (11.3548, -72.5203),
    "MAGDALENA": (10.5929, -74.1860), "META": (3.6438, -73.6137), "NARIÑO": (1.2136, -77.2811),
    "NORTE DE SANTANDER": (7.9073, -72.5046), "PUTUMAYO": (0.4350, -76.6469), "QUINDÍO": (4.4610, -75.6674),
    "RISARALDA": (5.2468, -75.7366), "SAN ANDRÉS": (12.5847, -81.7006), "SANTANDER": (7.1254, -73.1198),
    "SUCRE": (9.3047, -75.3978), "TOLIMA": (4.4389, -75.2322), "VALLE DEL CAUCA": (3.4516, -76.5320),
    "VAUPÉS": (0.8550, -70.8116), "VICHADA": (5.0702, -69.3040), "BOGOTÁ, D.C.": (4.7110, -74.0721)
}

df_raw = load_data(DATA_FILE)
kpis = compute_kpis(df_raw)

dpto_options = [{"label": d, "value": d} for d in sorted(df_raw["DEPARTAMENTO"].dropna().astype(str).unique())]
causa_options = [{"label": c, "value": c} for c in sorted(df_raw.get("Nombre_capitulo", pd.Series(dtype=str)).dropna().unique())]

app = Dash(__name__)
server = app.server
app.title = "Análisis de Mortalidad 2019 🇨🇴"

def kpi_card(title: str, value: str) -> html.Div:
    return html.Div([
        html.Div(title, style={"fontSize": "16px", "color": "#666"}),
        html.Div(value, style={"fontSize": "28px", "fontWeight": "bold"}),
    ], style={
        "backgroundColor": "#f0f2f6", "padding": "20px", "borderRadius": "15px",
        "textAlign": "center", "boxShadow": "2px 2px 6px rgba(0,0,0,0.05)",
        "flex": "1 1 18%", "minWidth": "180px"
    })

app.layout = html.Div([
    html.Header([
        html.Img(src="https://cdn-icons-png.flaticon.com/512/4474/4474364.png", style={"width": "60px"}),
        html.H1("Análisis Interactivo de Mortalidad en Colombia - 2019", style={"marginLeft": "10px"}),
    ], style={"display": "flex", "alignItems": "center", "padding": "20px"}),

    html.Div([
        html.H3("📌 Indicadores principales"),
        html.Div([
            kpi_card("👥 Personas registradas", f"{kpis['total_registros']:,}"),
            kpi_card("🧬 Tipos de muerte", str(kpis['tipos_muerte'])),
            kpi_card("🛌 Sexo con más muertes", kpis['sexo_max']),
            kpi_card("📍 Dpto. con más muertes", kpis['dpto_max']),
            kpi_card("📉 Dpto. con menos muertes", kpis['dpto_min']),
        ], style={"display": "flex", "justifyContent": "space-around", "gap": "40px", "padding": "10px 20px", "flexWrap": "nowrap", "overflowX": "auto"})
    ], style={"padding": "0 20px"}),

    html.Div([
        html.Div([
            html.Label("Filtrar por Departamento:"),
            dcc.Dropdown(id="filter-depto", options=dpto_options, placeholder="Selecciona departamento", clearable=True)
        ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),
        html.Div([
            html.Label("Filtrar por Causa:"),
            dcc.Dropdown(id="filter-causa", options=causa_options, placeholder="Selecciona causa", clearable=True)
        ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),
    ], style={"padding": "0 20px"}),

    dcc.Tabs(id="tabs", value="mapa", children=[
        dcc.Tab(label="🎮 Mapa de burbujas", value="mapa"),
        dcc.Tab(label="📈 Muertes por mes", value="mes"),
        dcc.Tab(label="🔫 Ciudades más violentas", value="violentas"),
        dcc.Tab(label="🥧 Ciudades con menor mortalidad", value="menor"),
        dcc.Tab(label="📋 Causas de muerte", value="causas"),
        dcc.Tab(label="📊 Histograma por edad", value="edad"),
        dcc.Tab(label="🛋 Sexo por departamento", value="sexo"),
    ], style={"padding": "20px"}),

    html.Div(id="contenido", style={"padding": "0 20px 20px 20px"})
])

def filter_df(depto, causa):
    df = df_raw.copy()
    if depto:
        df = df[df["DEPARTAMENTO"] == depto]
    if causa:
        df = df[df["Nombre_capitulo"] == causa]
    return df

def render_map(df):
    data = (
        df.groupby("DEPARTAMENTO").size().reset_index(name="Total Muertes")
        .assign(
            LAT=lambda d: d["DEPARTAMENTO"].map(lambda x: DEPT_COORDS.get(x, (None, None))[0]),
            LON=lambda d: d["DEPARTAMENTO"].map(lambda x: DEPT_COORDS.get(x, (None, None))[1])
        )
        .dropna()
    )
    fig = px.scatter_map(
        data, lat="LAT", lon="LON", size="Total Muertes",
        hover_name="DEPARTAMENTO", zoom=4, size_max=40,
        map_style="open-street-map"
    )
    return dcc.Graph(figure=fig)

def render_mes(df):
    df_fecha = df.copy()
    df_fecha["FECHA"] = pd.to_datetime(dict(year=df_fecha["AÑO"], month=df_fecha["MES"], day=1))
    df_mes = df_fecha.groupby("FECHA").size().reset_index(name="Total Muertes")
    fig = px.line(df_mes, x="FECHA", y="Total Muertes", markers=True,
                  title="Muertes por mes en Colombia - 2019")
    return dcc.Graph(figure=fig)

def render_violentas(df):
    df_homicidio = df[df["MANERA_MUERTE"] == "Homicidio"]
    df_homicidio = df_homicidio[df_homicidio["MUNICIPIO"].notna()]

    if df_homicidio.empty:
        return html.Div("No hay datos disponibles para mostrar homicidios.")

    data = df_homicidio["MUNICIPIO"].value_counts().nlargest(10).reset_index()
    data.columns = ["Municipio", "Muertes"]
    fig = px.bar(data, x="Municipio", y="Muertes", title="10 municipios más violentos (HOMICIDIO)")
    return dcc.Graph(figure=fig)

def render_menor(df):
    df_filtered = df[df["MUNICIPIO"].notna()]

    if df_filtered.empty:
        return html.Div("No hay datos disponibles para mostrar.")

    conteo = df_filtered["MUNICIPIO"].value_counts().reset_index()
    conteo.columns = ["Municipio", "Muertes"]
    conteo = conteo.sort_values("Muertes", ascending=True).head(10)

    fig = px.pie(
        conteo,
        names="Municipio",
        values="Muertes",
        title="🕊️ Municipios con menor mortalidad (todas las causas)",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Tealgrn
    )

    fig.update_traces(
        textinfo="none",  # No mostrar ninguna etiqueta
        pull=[0.03]*len(conteo),
        marker=dict(line=dict(color='white', width=2))
    )

    fig.update_layout(
        title_font_size=22,
        showlegend=True,
        legend_title_text="Municipio",
        legend_font_size=14,
        margin=dict(t=60, b=20, l=0, r=0),
        height=500
    )

    return dcc.Graph(figure=fig)


def render_causas(df):
    data = df["Nombre_capitulo"].value_counts().reset_index()
    data.columns = ["Causa", "Cantidad"]
    return html.Table([
        html.Thead([
            html.Tr([html.Th("Causa"), html.Th("Cantidad")])
        ]),
        html.Tbody([
            html.Tr([html.Td(row["Causa"]), html.Td(f"{row['Cantidad']:,}")]) for _, row in data.iterrows()
        ])
    ], style={"width": "100%", "borderCollapse": "collapse", "border": "1px solid #ddd"})

def render_edad(df):
    fig = px.histogram(
        df, 
        x="GRUPO_EDAD1", 
        title="Distribución de muertes por grupos de edad",
        color_discrete_sequence=["#636EFA"],  # Color azul agradable
        nbins=20,  # Controlamos la cantidad de barras (puedes ajustar según tus datos)
        opacity=0.8,
    )
    fig.update_layout(
        xaxis_title="Grupo de Edad",
        yaxis_title="Número de Muertes",
        title_font_size=24,
        title_x=0.5,  # Centrar el título
        bargap=0.2,   # Separación entre barras
        plot_bgcolor='white',
        font=dict(family="Arial", size=14, color="#222"),
        xaxis=dict(tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor="LightGray"),
        margin=dict(t=60, b=120, l=60, r=40),
    )
    return dcc.Graph(figure=fig)


def render_sexo(df):
    df_sexo = df.copy()
    df_sexo["SEXO"] = df_sexo["SEXO"].replace({1: "Hombre", 2: "Mujer", 3: "Sin identificar"})
    data = df_sexo.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="Cantidad")

    colors = {
        "Hombre": "#1f77b4",          # azul
        "Mujer": "#ff69b4",           # rosa
        "Sin identificar": "#7f7f7f"  # gris
    }

    fig = px.bar(
        data,
        y="DEPARTAMENTO",
        x="Cantidad",
        color="SEXO",
        title="Distribución de muertes por sexo y departamento",
        color_discrete_map=colors,
        labels={"Cantidad": "Número de Muertes", "DEPARTAMENTO": "Departamento"},
        orientation='h'  # Barra horizontal
    )
    fig.update_layout(
        barmode="stack",
        yaxis=dict(
            autorange="reversed",  # Para que el primer departamento aparezca arriba
            tickangle=0
        ),
        plot_bgcolor="white",
        font=dict(family="Arial", size=14, color="#222"),
        title_x=0.5,
        margin=dict(t=60, b=50, l=180, r=40),
        xaxis=dict(showgrid=True, gridcolor="LightGray"),
    )

    # Etiquetado de las barras
    fig.update_traces(texttemplate="%{x}", textposition="inside", textfont_color="white", textfont_size=16)

    return dcc.Graph(figure=fig)


@app.callback(
    Output("contenido", "children"),
    Input("tabs", "value"),
    Input("filter-depto", "value"),
    Input("filter-causa", "value"),
)
def update_content(tab, depto, causa):
    df = filter_df(depto, causa)
    if tab == "mapa":
        return render_map(df)
    elif tab == "mes":
        return render_mes(df)
    elif tab == "violentas":
        return render_violentas(df)
    elif tab == "menor":
        return render_menor(df)
    elif tab == "causas":
        return render_causas(df)
    elif tab == "edad":
        return render_edad(df)
    elif tab == "sexo":
        return render_sexo(df)
    return html.Div("Seleccione una pestaña")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))  # 8050 es el puerto por defecto si no hay variable PORT
    app.run(host="0.0.0.0", port=port, debug=True)