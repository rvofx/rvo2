import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def obtener_tipo_cambio(fecha):
    url = "https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx"
    
    try:
        # Obtener el contenido de la página
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP erróneos
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
                        return compra, venta, None
            
            return None, None, "No se encontró el tipo de cambio para la fecha especificada en la tabla"
        else:
            return None, None, "No se pudo encontrar la tabla de tipos de cambio en la página"
    
    except requests.RequestException as e:
        return None, None, f"Error al hacer la solicitud HTTP: {str(e)}"
    except Exception as e:
        return None, None, f"Error inesperado: {str(e)}"

st.title('Tipo de Cambio USD/PEN')

# Obtener la fecha actual
fecha_actual = datetime.now()

# Calcular la fecha del día anterior
fecha_ayer = fecha_actual - timedelta(days=1)

# Si la fecha de ayer es sábado o domingo, retroceder hasta el viernes
while fecha_ayer.weekday() > 4:  # 5 = Sábado, 6 = Domingo
    fecha_ayer -= timedelta(days=1)

fecha_str = fecha_ayer.strftime('%d/%m/%Y')

st.write(f"Obteniendo tipo de cambio para la fecha: {fecha_str}")

compra, venta, error = obtener_tipo_cambio(fecha_ayer)

if compra and venta:
    st.success(f"Tipo de cambio del {fecha_str}:")
    st.write(f"Compra: S/ {compra}")
    st.write(f"Venta: S/ {venta}")
else:
    st.error(f"No se pudo obtener el tipo de cambio para la fecha {fecha_str}")
    if error:
        st.write(f"Detalles del error: {error}")

st.write("Nota: Los tipos de cambio generalmente no se publican en fines de semana o feriados.")
