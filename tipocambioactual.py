from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Configura el navegador sin cabeza
chrome_options = Options()
chrome_options.add_argument("--headless")  # Sin interfaz gráfica
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Inicializa el navegador con opciones
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Abre la página web
url = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"
driver.get(url)

# Espera 10 segundos para que cargue el contenido
time.sleep(10)

# Extrae el contenido de la página
html_content = driver.page_source

# Procesa la información según sea necesario
print(html_content)

# Cierra el navegador
driver.quit()
