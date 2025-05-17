# 🧠 Análisis de Mortalidad en Colombia - Aplicación Web Interactiva 🇨🇴

**👩‍💻 Estudiantes:** Diana Carolina González Díaz y Ana María García Arias 
**📘 Asignatura:** Aplicaciones I  
**📊 Actividad 4:** Visualización Interactiva de Datos de Mortalidad (Año 2019)

---

## 📌 Descripción del Proyecto

Este proyecto consiste en una aplicación web interactiva desarrollada con **Dash**, una biblioteca de Python para construir interfaces analíticas.  
La app permite explorar datos de mortalidad en Colombia correspondientes al año 2019, con el fin de identificar patrones **geográficos**, **demográficos** y **temporales** de manera clara y visual.

---

## 🎯 Objetivos

- Visualizar datos reales de mortalidad en Colombia a través de gráficos interactivos.
- Explorar variables clave como causa de muerte, edad, género, municipio y mes.
- Permitir filtrado y análisis dinámico desde una interfaz intuitiva.
- Usar herramientas modernas de ciencia de datos y visualización.

---

## 🧱 Estructura de la Aplicación

La aplicación está compuesta por las siguientes secciones:

- 🗺️ **Mapa de burbujas por departamento**  
  Visualiza la cantidad de muertes por región geográfica.

- 📆 **Distribución mensual de muertes**  
  Gráfico temporal que muestra la evolución de casos por mes.

- 🔫 **Ciudades con mayor número de muertes violentas**  
  Identifica los municipios más afectados por homicidios y suicidios.

- 🥧 **Municipios con menor mortalidad**  
  Gráfico de torta con los 10 municipios con menor número de casos.

- 📋 **Top 10 causas de muerte**  
  Visualización de las causas más comunes.

- 📊 **Histograma de muertes por edad (quinquenal)**  
  Agrupa los casos por rangos de edad de 5 años.

- 🚻 **Distribución por sexo y departamento**  
  Compara el número de muertes entre hombres y mujeres por región.


---


📁 Estructura del Repositorio

📦 APP_MUERTESCOL/
├── 📂 env/ # Entorno virtual (no se sube al repositorio)
├── 📂 src/ # Código fuente de la aplicación
│ ├── 📄 app.py # Aplicación principal construida con Dash
│ ├── 📄 etl_procesamiento.py # Script para limpieza y transformación de datos
│ ├── 📊 Base_Unificada_...xlsx # Base de datos principal con registros de mortalidad
│ ├── 📄 Anexo1.NoFetal2019_... # Datos no fetales
│ ├── 📄 Anexo2.CodigosDeMuerte # Códigos y clasificaciones de causas de muerte
│ └── 📄 Anexo3.Divipola_... # Información geográfica DIVIPOLA
│
├── 📄 requirements.txt # Lista de dependencias necesarias para ejecutar el proyecto
├── 📄 README.md # Documentación general del proyecto

⚙️ Cómo Ejecutar la Aplicación
1. Clonar el repositorio
bash
Copiar
Editar
git clone https://github.com/Diana1295Dev/App_muertesCOL.git
cd App_muertesCOL
2. Crear un entorno virtual (opcional pero recomendado)
bash
Copiar
Editar
python -m venv env
source env/bin/activate  # En Linux o Mac
env\Scripts\activate     # En Windows
3. Instalar las dependencias
bash
Copiar
Editar
pip install -r requirements.txt
4. Ejecutar la aplicación
bash
Copiar
Editar
python app.py
Una vez ejecutado, abre tu navegador y visita:

cpp
Copiar
Editar
http://127.0.0.1:8050/


## 🖼️ Capturas de Pantalla

> *(Puedes agregar imágenes aquí usando Markdown)*

```markdown
![](imagenes/mapa_burbujas.png)
![](imagenes/muertes_mes.png)
![](imagenes/violencia_municipios.png)
![](imagenes/menor_mortalidad.png)