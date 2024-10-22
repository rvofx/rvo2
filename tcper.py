import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from datetime import datetime
import time
import plotly.graph_objects as go

# Título y descripción
st.title(" Tipo de Cambio")
st.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def configurar_driver():
    """Configura y retorna un driver de Chrome en modo headless"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def obtener_tipo_cambio():
    """Obtiene el tipo de cambio actual"""
    driver = None
    try:
        with st.spinner('Obteniendo tipo de cambio...'):
            driver = configurar_driver()
            driver.get("https://elperuano.pe/")

            time.sleep(5)

            wait = WebDriverWait(driver, 20)

            try:
                lista_dolar = wait.until(
                    EC.presence_of_element_located((By.ID, "uldolar"))
                )
            except:
                lista_dolar = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "fz08"))
                )

            compra_xpath = "//li[contains(text(), 'Compra')]"
            venta_xpath = "//li[contains(text(), 'Venta')]"

            compra_element = driver.find_element(By.XPATH, compra_xpath)
            venta_element = driver.find_element(By.XPATH, venta_xpath)

            compra_texto = compra_element.text
            venta_texto = venta_element.text

            import re
            compra = float(re.findall(r'\d+\.\d+', compra_texto)[0])
            venta = float(re.findall(r'\d+\.\d+', venta_texto)[0])

            st.write("Compra: ",compra)
            st.write("Venta : ",venta)

            return compra, venta

    except Exception as e:
        st.error(f"Error al obtener el tipo de cambio: {str(e)}")
        return None, None

    finally:
        if driver:
            driver.quit()

#
compra, venta = obtener_tipo_cambio()
