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
st.title("Aplicación para selección de columnas y repetición por tallas")

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
    columnas_tallas = st.multiselect("Selecciona las columnas de tallas para calcular repeticiones", columnas)
    
    # Repetir filas en función de las columnas seleccionadas para tallas
    if columnas_tallas:
        filas_repetidas = []
        for _, row in df.iterrows():
            for talla in columnas_tallas:
                nueva_fila = row[columnas_info].copy()
                nueva_fila["Talla"] = talla
                nueva_fila["Cantidad"] = row[talla]  # La cantidad correspondiente a esa talla
                filas_repetidas.append(nueva_fila)
        
        # Convertir las filas expandidas en un dataframe
        df_repetido = pd.DataFrame(filas_repetidas)
        
        # Mostrar el dataframe con las filas repetidas
        st.write("Datos repetidos según las tallas seleccionadas:")
        st.dataframe(df_repetido)
        
        # Botón para descargar el archivo filtrado con las repeticiones
        st.download_button(
            label="Descargar Excel con filas repetidas",
            data=descargar_excel(df_repetido),
            file_name="archivo_repetido_por_tallas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
