import streamlit as st
import pandas as pd

# Título de la aplicación
st.title('Validación de Gráficos por Colores')

# Cargar los archivos Excel
uploaded_file_graficos = st.file_uploader("Sube el archivo de gráficos (GRAFICO, COLOR_CUERPO, COLOR_APLICACION)", type=["xlsx", "xls"])
uploaded_file_colores = st.file_uploader("Sube el archivo de colores (COLOR)", type=["xlsx", "xls"])

if uploaded_file_graficos is not None and uploaded_file_colores is not None:
    # Leer los archivos Excel
    df_graficos = pd.read_excel(uploaded_file_graficos)
    df_colores = pd.read_excel(uploaded_file_colores)

    # Obtener lista de colores disponibles
    colores_disponibles = df_colores['COLOR'].tolist()

    # Filtrar gráficos con colores completos
    graficos_validos = df_graficos[
        (df_graficos['COLOR_CUERPO'].isin(colores_disponibles)) & 
        (df_graficos['COLOR_APLICACION'].isin(colores_disponibles))
    ]['GRAFICO'].unique()

    # Mostrar los resultados
    if len(graficos_validos) > 0:
        st.success("Gráficos con colores completos:")
        st.write(graficos_validos)
    else:
        st.warning("No se encontraron gráficos con colores completos.")
