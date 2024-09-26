import streamlit as st
import requests
import pandas as pd

def get_table_from_url(url):
    # Obtener el contenido HTML de la página
    response = requests.get(url)
    
    # Extraer todas las tablas de la página
    tables = pd.read_html(response.text)
    
    # Devolver la primera tabla encontrada
    # Puedes modificar esto si necesitas una tabla específica
    return tables[0] if tables else None

# Interfaz de usuario de Streamlit
st.title("Extractor de Tablas Web")

# Campo de entrada para la URL
url = st.text_input("Ingresa la URL de la página web:")

if url:
    if st.button("Extraer Tabla"):
        try:
            table = get_table_from_url(url)
            if table is not None:
                st.success("¡Tabla extraída con éxito!")
                st.dataframe(table)
            else:
                st.warning("No se encontraron tablas en la página.")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
