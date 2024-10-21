import streamlit as st
import pandas as pd

# Función para descargar el dataframe filtrado como archivo Excel
def descargar_excel(df):
    return df.to_excel("resultado_filtrado.xlsx", index=False)

# Título de la aplicación
st.title("Selección de columnas en Excel")

# Subir el archivo Excel
archivo_excel = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

# Si el archivo ha sido subido
if archivo_excel:
    # Leer el archivo Excel
    df = pd.read_excel(archivo_excel)
    
    # Mostrar las primeras filas del archivo
    st.write("Vista previa de los datos:")
    st.dataframe(df.head())
    
    # Lista de columnas disponibles
    columnas = df.columns.tolist()
    
    # Permitir que el usuario seleccione las columnas que quiere
    columnas_seleccionadas = st.multiselect("Selecciona las columnas que deseas", columnas)
    
    # Filtrar el dataframe basado en las columnas seleccionadas
    if columnas_seleccionadas:
        df_filtrado = df[columnas_seleccionadas]
        st.write("Datos filtrados:")
        st.dataframe(df_filtrado)
        
        # Botón para descargar el archivo filtrado
        st.download_button(
            label="Descargar Excel filtrado",
            data=df_filtrado.to_excel(index=False, engine='openpyxl'),
            file_name="archivo_filtrado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
