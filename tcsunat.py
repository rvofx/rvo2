import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

@st.cache_resource
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def get_table_data(url):
    driver = get_driver()
    try:
        driver.get(url)
        st.write("Página cargada. Esperando contenido...")
        
        # Esperar a que aparezca la tabla
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_cphContent_rdGridTC"))
        )
        
        # Dar un poco más de tiempo para que se cargue completamente
        time.sleep(2)
        
        # Obtener el contenido de la página
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
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
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
    finally:
        driver.quit()
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

if __name__ == "__main__":
    main()
