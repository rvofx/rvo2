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

    # Agrupar por gráfico y verificar si todos los colores están en la lista
    graficos_validos = []
    
    for grafico, group in df_graficos.groupby('GRAFICO'):
        colores_cuerpo_validos = group['COLOR_CUERPO'].isin(colores_disponibles).all()
        colores_aplicacion_validos = group['COLOR_APLICACION'].isin(colores_disponibles).all()
        
        if colores_cuerpo_validos and colores_aplicacion_validos:
            graficos_validos.append(grafico)

    # Mostrar los resultados
    num_graficos_validos = len(graficos_validos)
    if num_graficos_validos > 0:
        st.success(f"Se encontraron {num_graficos_validos} gráficos con colores completos:")
        st.write(graficos_validos)
    else:
        st.warning("No se encontraron gráficos con colores completos.")
