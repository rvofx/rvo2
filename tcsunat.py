import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_table_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        st.write(f"Estado de la respuesta: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar la tabla específica por su ID
        table = soup.find('table', id='ctl00_cphContent_rgTipoCambio_ctl00')
        
        if table:
            st.write("Tabla encontrada.")
            df = pd.read_html(str(table))[0]
            return [("Tipo de Cambio", df)]
        else:
            st.warning("No se encontró la tabla específica.")
            
        # Mostrar todas las tablas encontradas para depuración
        all_tables = soup.find_all('table')
        st.write(f"Número total de tablas encontradas: {len(all_tables)}")
        
        return []
    except requests.RequestException as e:
        st.error(f"Error al obtener la página: {str(e)}")
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
    return []

def main():
    st.title("Extractor de Datos de Tipo de Cambio SBS")
    
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
        response = requests.get(url, headers=headers)
        st.code(response.text[:1000], language='html')  # Mostrar los primeros 1000 caracteres

if __name__ == "__main__":
    main()
