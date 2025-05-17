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

# --- Instancia Flask y Dash ---
flask_app = Flask(__name__)
app = Dash(__name__, server=flask_app, url_base_pathname='/')
app.title = "Análisis de Mortalidad 2019 🇨🇴"
server = app.server

# --- Layout simple para verificar despliegue exitoso ---
app.layout = html.Div([
    html.H1("Aplicación de Mortalidad 2019 en Colombia"),
    html.H3("¡La app está desplegada exitosamente en Render! 🎉"),
    html.P("Registros cargados: {:,}".format(kpis['total_registros'])),
    html.P("Sexo con más muertes: {}".format(kpis['sexo_max'])),
    html.P("Departamento con más muertes: {}".format(kpis['dpto_max']))
])

# --- Ejecutar ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)


