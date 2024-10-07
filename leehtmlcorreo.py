import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd

# Función para leer el archivo HTML y extraer las tablas
def extract_tables_from_html(file):
    # Leer el archivo HTML
    html_content = file.read()
    
    # Usar BeautifulSoup para procesar el HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Buscar todas las tablas en el HTML
    tables = soup.find_all('table')
    
    # Lista para guardar cada tabla como un DataFrame
    dfs = []
    
    for table in tables:
        # Leer la tabla como un DataFrame
        df = pd.read_html(str(table))[0]
        dfs.append(df)
    
    # Concatenar todas las tablas en una sola si hay más de una
    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
    else:
        final_df = pd.DataFrame()  # Por si no hay tablas
    
    return final_df

# Interfaz de Streamlit
st.title('Extracción de Tablas desde Archivos HTML')

# Cargar el archivo HTML
uploaded_file = st.file_uploader("Sube tu archivo HTML", type=["html"])

if uploaded_file is not None:
    # Extraer las tablas del archivo HTML
    result_df = extract_tables_from_html(uploaded_file)
    
    if not result_df.empty:
        st.write("Tabla Consolidada:")
        st.dataframe(result_df)
        
        # Opción para descargar la tabla consolidada en formato Excel
        st.download_button(
            label="Descargar tabla en Excel",
            data=result_df.to_csv(index=False),
            file_name="tabla_consolidada.csv",
            mime="text/csv"
        )
    else:
        st.warning("No se encontraron tablas en el archivo HTML.")
