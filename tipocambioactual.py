from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Inicializa el navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Abre la página web
url = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"
driver.get(url)

# Espera 10 segundos (puedes ajustar esto según lo que tarde en cargar la página)
time.sleep(10)

# Extrae el contenido de la página
html_content = driver.page_source

# También puedes encontrar elementos específicos si conoces el HTML
# Por ejemplo, para extraer una tabla:
try:
    table = driver.find_element(By.TAG_NAME, "table")
    print(table.text)
except Exception as e:
    print("No se encontró la tabla:", e)

# Cierra el navegador
driver.quit()

# Aquí puedes trabajar con html_content o la tabla
