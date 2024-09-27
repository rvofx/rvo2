import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_table_data(url):
    # Obtener el contenido de la página
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar todas las tablas en la página
    tables = soup.find_all('table')
    
    # Extraer datos de cada tabla
    all_data = []
    for i, table in enumerate(tables):
        df = pd.read_html(str(table))[0]
        all_data.append((f"Tabla {i+1}", df))
    
    return all_data

def main():
    st.title("Extractor de Datos de Tablas Web")
    
    url = "https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx"
    st.write(f"Extrayendo datos de: {url}")
    
    if st.button("Extraer Datos"):
        data = get_table_data(url)
        
        for table_name, df in data:
            st.subheader(table_name)
            st.dataframe(df)

if __name__ == "__main__":
    main()
