import streamlit as st
import pandas as pd
import io

# Función para descargar el dataframe filtrado como archivo Excel
def descargar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Título de la aplicación
st.title("Aplicación para selección de columnas y cálculo de tallas")

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
    
    # Primera selección: Columnas de información
    columnas_info = st.multiselect("Selecciona las columnas de información que deseas", columnas)
    
    # Filtrar el dataframe basado en las columnas seleccionadas para información
    if columnas_info:
        df_filtrado_info = df[columnas_info]
        
        # Mostrar el dataframe filtrado
        st.write("Datos filtrados (información):")
        st.dataframe(df_filtrado_info)
    
    # Segunda selección: Columnas de tallas
    columnas_tallas = st.multiselect("Selecciona las columnas de tallas para calcular el total", columnas)
    
    # Calcular el total de tallas si se seleccionan columnas
    if columnas_tallas:
        df['Total Tallas'] = df[columnas_tallas].sum(axis=1)
        
        # Mostrar el dataframe con la columna de total de tallas
        st.write("Datos con el total de tallas calculado:")
        st.dataframe(df[['Total Tallas'] + columnas_info])  # Mostrar la columna de total con las columnas de información seleccionadas
        
        # Botón para descargar el archivo filtrado con el total de tallas
        st.download_button(
            label="Descargar Excel con total de tallas",
            data=descargar_excel(df[['Total Tallas'] + columnas_info]),
            file_name="archivo_con_total_tallas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
