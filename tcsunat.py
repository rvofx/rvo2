import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def obtener_tipo_cambio(fecha):
    url = "https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx"
    
    # Obtener el contenido de la página
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Buscar la tabla con los datos
    tabla = soup.find('table', {'id': 'ctl00_cphContent_rgTipoCambio_ctl00'})
    
    if tabla:
        filas = tabla.find_all('tr')
        for fila in filas:
            celdas = fila.find_all('td')
            if len(celdas) >= 4:
                fecha_str = celdas[0].text.strip()
                if fecha_str == fecha.strftime('%d/%m/%Y'):
                    compra = celdas[1].text.strip()
                    venta = celdas[2].text.strip()
                    return compra, venta
    
    return None, None

st.title('Tipo de Cambio USD/PEN')

fecha_ayer = datetime.now() - timedelta(days=1)
fecha_str = fecha_ayer.strftime('%d/%m/%Y')

st.write(f"Obteniendo tipo de cambio para la fecha: {fecha_str}")

compra, venta = obtener_tipo_cambio(fecha_ayer)

if compra and venta:
    st.success(f"Tipo de cambio del {fecha_str}:")
    st.write(f"Compra: S/ {compra}")
    st.write(f"Venta: S/ {venta}")
else:
    st.error(f"No se pudo obtener el tipo de cambio para la fecha {fecha_str}")
