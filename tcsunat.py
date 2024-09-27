import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_table_data(url):
    try:
        # Obtener el contenido de la página
        response = requests.get(url)
        response.raise_for_status()  # Esto levantará una excepción para códigos de estado HTTP no exitosos
        st.write(f"Estado de la respuesta: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar todas las tablas en la página
        tables = soup.find_all('table')
        st.write(f"Número de tablas encontradas: {len(tables)}")
        
        # Extraer datos de cada tabla
        all_data = []
        for i, table in enumerate(tables):
            try:
                df = pd.read_html(str(table))[0]
                all_data.append((f"Tabla {i+1}", df))
            except Exception as e:
                st.error(f"Error al procesar la tabla {i+1}: {str(e)}")
        
        return all_data
    except requests.RequestException as e:
        st.error(f"Error al obtener la página: {str(e)}")
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
    return []

def main():
    st.title("Extractor de Datos de Tablas Web")
    
    url = "https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx"
    st.write(f"Extrayendo datos de: {url}")
    
    if st.button("Extraer Datos"):
        with st.spinner('Extrayendo datos...'):
            data = get_table_data(url)
        
        if data:
            for table_name, df in data:
                st.subheader(table_name)
                st.dataframe(df)
        else:
            st.warning("No se pudieron extraer datos. Por favor, revisa los mensajes de error arriba.")

        # Mostrar el HTML de la página para depuración
        st.subheader("Contenido HTML de la página")
        response = requests.get(url)
        st.code(response.text, language='html')

if __name__ == "__main__":
    main()
