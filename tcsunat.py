import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time

# Configura el navegador en modo headless (sin ventana gráfica)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecución en modo sin ventana
chrome_options.add_argument("--window-size=1920x1080")  # Tamaño de la ventana

# Inicializa el navegador
st.write("Iniciando navegador...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL a consultar
url = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"

# Abre la página
driver.get(url)

# Espera unos segundos para que la página se cargue completamente
time.sleep(5)

# Guarda una captura de pantalla
screenshot_path = "screenshot.png"
driver.save_screenshot(screenshot_path)

# Muestra la imagen en Streamlit
st.image(screenshot_path)

# Cierra el navegador
driver.quit()
