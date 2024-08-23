import streamlit as st
import pandas as pd

def transformar_excel(df):
    # Filtramos las columnas relevantes para el procesamiento
    columnas_relevantes = df.columns[:5]
    tallas = df.columns[5:]
    
    # Creamos una lista para almacenar las filas transpuestas
    data = []
    
    # Recorremos cada fila del dataframe original
    for i, row in df.iterrows():
        for talla in tallas:
            # Agregamos una nueva fila para cada talla
            data.append([row[col] for col in columnas_relevantes] + [talla, row[talla]])
    
    # Convertimos la lista en un DataFrame
    df_transformado = pd.DataFrame(data, columns=list(columnas_relevantes) + ['Talla', 'Cantidad'])
    
    return df_transformado

st.title("Transponer Tallas y Cantidades")

# Cargar el archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel", type="xlsx")

if uploaded_file:
    # Leer el archivo Excel
    df = pd.read_excel(uploaded_file)
    
    # Transformar el Excel
    df_transformado = transformar_excel(df)
    
    # Mostrar el DataFrame transpuesto
    st.write("Archivo transformado:")
    st.dataframe(df_transformado)
    
    # Descargar el nuevo archivo Excel
    output_file = "transformado.xlsx"
    df_transformado.to_excel(output_file, index=False)
    
    with open(output_file, "rb") as file:
        st.download_button(
            label="Descargar archivo transformado",
            data=file,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
