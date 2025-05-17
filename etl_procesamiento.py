import pandas as pd

# === Lectura completa del archivo Anexo1 ===
anexo1 = pd.read_excel("Anexo1.NoFetal2019_CE_15-03-23.xlsx", usecols=[
    "COD_DANE", "AÑO", "MES", "HORA", "MINUTOS", "SEXO", "ESTADO_CIVIL",
    "GRUPO_EDAD1", "NIVEL_EDUCATIVO", "MANERA_MUERTE", "COD_MUERTE"
], engine="openpyxl")

# === Lectura completa de Anexo2 y Anexo3 ===
anexo2 = pd.read_excel("Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx", engine="openpyxl")
anexo3 = pd.read_excel("Anexo3.Divipola_CE_15-03-23.xlsx", engine="openpyxl")

# === Limpieza de nombres de columnas ===
anexo1.columns = anexo1.columns.str.strip()
anexo2.columns = anexo2.columns.str.strip()
anexo3.columns = anexo3.columns.str.strip()

# === Merge 1: Anexo1 + Anexo3 por COD_DANE ===
df13 = anexo1.merge(
    anexo3[["COD_DANE", "DEPARTAMENTO", "MUNICIPIO", "FECHA1erFIS"]],
    how="left",
    on="COD_DANE"
)

# === Merge 2: df13 + Anexo2 por COD_MUERTE y CodigoCIE4 ===
df_final = df13.merge(
    anexo2[["CodigoCIE4", "Nombre_capitulo", "Descripcion_mortalidad", "Detalle"]],
    how="left",
    left_on="COD_MUERTE",
    right_on="CodigoCIE4"
)

# === Selección de columnas finales ===
columnas_deseadas = [
    "COD_DANE", "AÑO", "MES", "HORA", "MINUTOS", "SEXO", "ESTADO_CIVIL", "GRUPO_EDAD1",
    "NIVEL_EDUCATIVO", "MANERA_MUERTE", "Nombre_capitulo", "Descripcion_mortalidad",
    "Detalle", "DEPARTAMENTO", "MUNICIPIO", "FECHA1erFIS"
]

# === Filtrar columnas presentes y exportar ===
df_exportar = df_final[[col for col in columnas_deseadas if col in df_final.columns]]
df_exportar.to_excel("Base_Unificada_Limpia_Completa.xlsx", index=False)

print("✅ Archivo guardado como Base_Unificada_Limpia_Completa.xlsx")