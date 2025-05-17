import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from flask import Flask

# --- Configuración de rutas y carga de datos ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "src", "Base_Unificada_Limpia_Completa.csv")

def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    return pd.read_csv(path, encoding='latin-1', sep=';', engine='python')

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

DEPT_COORDS = { "AMAZONAS": (-1.4419, -70.1449), "ANTIOQUIA": (6.2518, -75.5636), "ARAUCA": (7.0856, -70.7591),
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

dpto_options = [{"label": d, "value": d} for d in sorted(df_raw["DEPARTAMENTO"].dropna().unique())]
causa_options = [{"label": c, "value": c} for c in sorted(df_raw["Nombre_capitulo"].dropna().unique())]

flask_app = Flask(__name__)
app = Dash(__name__, server=flask_app, url_base_pathname='/')
server = app.server
app.title = "Análisis de Mortalidad 2019 🇰🇪"

app.layout = html.Div([
    html.H1("Dashboard de Mortalidad Colombia 2019"),
    dcc.Dropdown(id="filter-depto", options=dpto_options, placeholder="Selecciona Departamento"),
    dcc.Dropdown(id="filter-causa", options=causa_options, placeholder="Selecciona Causa"),
    dcc.Tabs(id="tabs", value="mapa", children=[
        dcc.Tab(label="Mapa", value="mapa"),
        dcc.Tab(label="Muertes por Mes", value="mes"),
        dcc.Tab(label="Municipios Violentos", value="violentas"),
        dcc.Tab(label="Menor Mortalidad", value="menor"),
        dcc.Tab(label="Causas", value="causas"),
        dcc.Tab(label="Edad", value="edad"),
        dcc.Tab(label="Sexo", value="sexo")
    ]),
    html.Div(id="contenido")
])

def filter_df(depto, causa):
    df = df_raw.copy()
    if depto:
        df = df[df["DEPARTAMENTO"] == depto]
    if causa:
        df = df[df["Nombre_capitulo"] == causa]
    return df

def render_map(df):
    data = df.groupby("DEPARTAMENTO").size().reset_index(name="Total Muertes")
    data["LAT"] = data["DEPARTAMENTO"].map(lambda x: DEPT_COORDS.get(x, (None, None))[0])
    data["LON"] = data["DEPARTAMENTO"].map(lambda x: DEPT_COORDS.get(x, (None, None))[1])
    data = data.dropna()
    fig = px.scatter_mapbox(data, lat="LAT", lon="LON", size="Total Muertes",
                            hover_name="DEPARTAMENTO", zoom=4, size_max=40,
                            mapbox_style="open-street-map")
    return dcc.Graph(figure=fig)

def render_mes(df):
    df["FECHA"] = pd.to_datetime(dict(year=df["AÑO"], month=df["MES"], day=1))
    df_mes = df.groupby("FECHA").size().reset_index(name="Total Muertes")
    fig = px.line(df_mes, x="FECHA", y="Total Muertes", markers=True)
    return dcc.Graph(figure=fig)

def render_violentas(df):
    df_h = df[df["MANERA_MUERTE"] == "Homicidio"]
    df_h = df_h[df_h["MUNICIPIO"].notna()]
    if df_h.empty:
        return html.Div("Sin datos de homicidios")
    data = df_h["MUNICIPIO"].value_counts().nlargest(10).reset_index()
    data.columns = ["Municipio", "Muertes"]
    fig = px.bar(data, x="Municipio", y="Muertes")
    return dcc.Graph(figure=fig)

def render_menor(df):
    df_filtered = df[df["MUNICIPIO"].notna()]
    conteo = df_filtered["MUNICIPIO"].value_counts().reset_index().sort_values("count", ascending=True).head(10)
    conteo.columns = ["Municipio", "Muertes"]
    fig = px.pie(conteo, names="Municipio", values="Muertes", hole=0.4)
    return dcc.Graph(figure=fig)

def render_causas(df):
    data = df["Nombre_capitulo"].value_counts().reset_index()
    data.columns = ["Causa", "Cantidad"]
    return html.Table([
        html.Thead(html.Tr([html.Th("Causa"), html.Th("Cantidad")])),
        html.Tbody([html.Tr([html.Td(row["Causa"]), html.Td(row["Cantidad"])]) for _, row in data.iterrows()])
    ])

def render_edad(df):
    fig = px.histogram(df, x="GRUPO_EDAD1", nbins=20)
    return dcc.Graph(figure=fig)

def render_sexo(df):
    df["SEXO"] = df["SEXO"].replace({1: "Hombre", 2: "Mujer", 3: "Sin identificar"})
    data = df.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="Cantidad")
    fig = px.bar(data, y="DEPARTAMENTO", x="Cantidad", color="SEXO", orientation="h")
    return dcc.Graph(figure=fig)

@app.callback(
    Output("contenido", "children"),
    Input("tabs", "value"),
    Input("filter-depto", "value"),
    Input("filter-causa", "value"),
)
def update_content(tab, depto, causa):
    df = filter_df(depto, causa)
    if tab == "mapa": return render_map(df)
    elif tab == "mes": return render_mes(df)
    elif tab == "violentas": return render_violentas(df)
    elif tab == "menor": return render_menor(df)
    elif tab == "causas": return render_causas(df)
    elif tab == "edad": return render_edad(df)
    elif tab == "sexo": return render_sexo(df)
    return html.Div("Seleccione una pestaña")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)