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
    url = 'https://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx'
    
    # Formatear la fecha correctamente
    fecha_str = fecha.strftime('%d/%m/%Y')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Origin': 'https://www.sbs.gob.pe',
        'Referer': 'https://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx'
    }
    
    # Parámetros del formulario
    payload = {
        'ctl00$cphContent$ctl00$rgTipoCambio$ctl00$ctl02$ctl00$txtFecha': fecha_str,
        'ctl00$cphContent$ctl00$rgTipoCambio$ctl00$ctl02$ctl00$ddlMoneda': moneda
    }
    
    try:
        # Mostrar información de depuración
        st.write("Consultando con los siguientes parámetros:")
        st.write(f"- Fecha: {fecha_str}")
        st.write(f"- Código de moneda: {moneda}")
        
        # Realizar la solicitud GET inicial para obtener tokens
        session = requests.Session()
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Obtener tokens del formulario
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']
        
        # Añadir tokens al payload
        payload.update({
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            '__ASYNCPOST': 'true',
            'ctl00$cphContent$ctl00$btnConsultar': 'Consultar'
        })
        
        # Realizar la consulta POST
        response = session.post(url, data=payload, headers=headers)
        response.raise_for_status()
        
        # Parsear respuesta
        soup = BeautifulSoup(response.text, 'html.parser')
        tabla = soup.find('table', {'class': 'APLI_grid'})
        
        if tabla:
            df = pd.read_html(str(tabla))[0]
            return df
        else:
            st.error("No se encontró la tabla de tipos de cambio en la respuesta")
            return None
            
    except Exception as e:
        st.error(f'Error en la consulta: {str(e)}')
        if 'response' in locals():
            st.write("Código de respuesta:", response.status_code)
            st.write("Contenido de respuesta:", response.text[:500])
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
            if 'Compra' in df.columns and 'Venta' in df.columns:
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
        else:
            st.warning("""
            No se encontraron datos para la fecha y moneda seleccionadas. 
            Esto puede deberse a:
            - La fecha seleccionada es un fin de semana o feriado
            - La fecha es muy reciente y los datos aún no han sido publicados
            - La fecha es muy antigua
            
            Por favor, intente con otra fecha.
            """)

# Información adicional
with st.expander("ℹ️ Información importante"):
    st.markdown("""
    - Los tipos de cambio son publicados solo en días hábiles
    - Los datos del día actual pueden no estar disponibles hasta cierta hora
    - Se recomienda consultar días anteriores para obtener datos históricos
    - Fuente: Superintendencia de Banca, Seguros y AFP (SBS)
    """)
