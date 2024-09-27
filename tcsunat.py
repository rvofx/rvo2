import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd

def get_table_data(url):
    try:
        scraper = cloudscraper.create_scraper(browser='chrome')
        response = scraper.get(url)
        st.write(f"Estado de la respuesta: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
        
        # Buscar elementos específicos que deberían estar en la página
        specific_element = soup.find('span', id='ctl00_cphContent_lblFecha')
        if specific_element:
            st.write(f"Fecha encontrada: {specific_element.text}")
        else:
            st.warning("No se encontró la fecha en la página.")
        
        return []
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
    return []

def main():
    st.title("Extractor de Datos de Tipo de Cambio SBS")
    
    url = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"
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
        scraper = cloudscraper.create_scraper(browser='chrome')
        response = scraper.get(url)
        st.code(response.text[:1000], language='html')  # Mostrar los primeros 1000 caracteres

if __name__ == "__main__":
    main()
