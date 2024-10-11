import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Consulta Tipo de Cambio SBS",
    page_icon="💱",
    layout="wide"
)

# Título y descripción
st.title("📊 Consulta de Tipo de Cambio SBS")
st.markdown("Consulta el tipo de cambio histórico de diferentes monedas según la SBS")

# Diccionario de monedas disponibles
MONEDAS = {
    "Dólar de N. A.": "02",
    "Euro": "03",
    "Yen Japonés": "04",
    "Libra Esterlina": "05"
}

def obtener_tipo_cambio(fecha, moneda):
    """
    Obtiene el tipo de cambio de la SBS para una fecha y moneda específica
    """
    url = 'https://www.sbs.gob.pe/app/stats/TC-CV-Historico.asp'
    
    # Formatear la fecha correctamente
    fecha_str = fecha.strftime('%d/%m/%Y')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }
    
    # Parámetros del formulario
    payload = {
        'FECHA_INICIO': fecha_str,
        'FECHA_FIN': fecha_str,
        'MONEDA': moneda,
        'button1': 'Consultar'
    }
    
    try:
        # Realizar la solicitud POST
        session = requests.Session()
        response = session.post(url, data=payload, headers=headers)
        
        if response.status_code != 200:
            st.error(f"Error en la solicitud: {response.status_code}")
            return None
            
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar la tabla específica que contiene los tipos de cambio
        tabla = soup.find('table', {'id': 'ctl00_cphContent_rgTipoCambio_ctl00'})
        
        if tabla:
            # Encontrar todas las filas de datos
            filas = tabla.find_all('tr')[1:]  # Ignorar la fila de encabezado
            
            if filas:
                # Extraer los datos de la primera fila (la más reciente)
                fila = filas[0]
                celdas = fila.find_all('td')
                
                if len(celdas) >= 3:
                    fecha = celdas[0].text.strip()
                    compra = float(celdas[1].text.strip())
                    venta = float(celdas[2].text.strip())
                    
                    # Crear DataFrame
                    df = pd.DataFrame({
                        'Fecha': [fecha],
                        'Compra': [compra],
                        'Venta': [venta]
                    })
                    return df
        
        st.warning("No se encontraron datos para la fecha seleccionada")
        return None
            
    except Exception as e:
        st.error(f'Error en la consulta: {str(e)}')
        return None

# Crear el formulario
st.subheader("Parámetros de consulta")

col1, col2 = st.columns(2)

with col1:
    # Selector de moneda
    moneda_seleccionada = st.selectbox(
        "Seleccione la moneda:",
        options=list(MONEDAS.keys()),
        index=0
    )

with col2:
    # Selector de fecha
    fecha_consulta = st.date_input(
        "Fecha de consulta",
        datetime.now(),
        format="DD/MM/YYYY"
    )

# Botón de consulta
if st.button("Consultar", type="primary"):
    with st.spinner('Consultando datos...'):
        codigo_moneda = MONEDAS[moneda_seleccionada]
        df = obtener_tipo_cambio(fecha_consulta, codigo_moneda)
        
        if df is not None and not df.empty:
            # Mostrar los datos en una tabla
            st.subheader("Resultado de la consulta")
            st.dataframe(df, use_container_width=True)
            
            # Mostrar los valores específicos
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tipo de Cambio Compra", f"S/ {df['Compra'].iloc[0]:.3f}")
            with col2:
                st.metric("Tipo de Cambio Venta", f"S/ {df['Venta'].iloc[0]:.3f}")
            
            # Opción para descargar los datos
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Descargar datos en CSV",
                csv,
                "tipo_cambio.csv",
                "text/csv",
                key='download-csv'
            )

# Información adicional
with st.expander("ℹ️ Información importante"):
    st.markdown("""
    - Los tipos de cambio son publicados solo en días hábiles
    - Los datos del día actual pueden no estar disponibles hasta cierta hora
    - Para obtener el tipo de cambio del día, consultar después de las 5:00 PM
    - Se recomienda consultar días anteriores para obtener datos históricos
    - Fuente: Superintendencia de Banca, Seguros y AFP (SBS)
    """)
