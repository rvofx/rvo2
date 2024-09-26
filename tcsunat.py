import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def obtener_tipo_cambio_sunat():
    url = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"
    
    # Realizar la solicitud HTTP
    response = requests.get(url)
    response.raise_for_status()  # Verificar que la solicitud fue exitosa
    
    # Parsear el contenido HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscar la tabla que contiene el tipo de cambio
    table = soup.find("table", {"class": "class=\"form-table\""})
    
    # Extraer los datos de la tabla (compra y venta)
    if table:
        rows = table.find_all("tr")
        
        # Asumiendo que la tabla tiene las columnas Compra y Venta
        compra = rows[1].find_all("td")[1].text.strip()
        venta = rows[1].find_all("td")[2].text.strip()
        
        return compra, venta
    else:
        return None, None

# Título de la aplicación
st.title("Tipo de Cambio Dólar - SUNAT")

# Mostrar la fecha y hora actual
st.write(f"Consulta realizada el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Botón para obtener el tipo de cambio
if st.button("Obtener tipo de cambio"):
    compra, venta = obtener_tipo_cambio_sunat()
    
    if compra and venta:
        st.success(f"Compra: {compra} | Venta: {venta}")
    else:
        st.error("No se pudo obtener el tipo de cambio. Intenta nuevamente.")

# Instrucciones sobre cómo ejecutar la aplicación
st.write("Esta aplicación muestra el tipo de cambio de compra y venta del dólar en soles de la SUNAT en tiempo real.")

