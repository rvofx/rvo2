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

def obtener_tipo_cambio(fecha):
    """
    Obtiene el tipo de cambio de la SBS para una fecha específica
    """
    url = 'https://www.sbs.gob.pe/app/stats/TC-CV-Historico.asp'
    
    # Formatear la fecha correctamente
    fecha_str = fecha.strftime('%d/%m/%Y')
    
    payload = {
        'FECHA_INICIO': fecha_str,
        'FECHA_FIN': fecha_str,
        'MONEDA': '02',  # Dólar de N.A.
        'button1': 'Consultar'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    try:
        # Mostrar los datos que se están enviando para depuración
        st.write("Consultando fecha:", fecha_str)
        
        # Realizar la solicitud POST
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        tabla = soup.find('table', {'id': 'ctl00_cphContent_rgTipoCambio_ctl00'})
        
        if tabla:
            df = pd.read_html(str(tabla))[0]
            # Limpiar y formatear los datos
            df.columns = ['Fecha', 'Compra', 'Venta']
            return df
        else:
            return None
            
    except Exception as e:
        st.error(f'Error en la consulta: {str(e)}')
        return None

# Crear el formulario
st.subheader("Seleccione la fecha a consultar")

# Selector de fecha único
fecha_consulta = st.date_input(
    "Fecha de consulta",
    datetime.now(),
    format="DD/MM/YYYY"
)

# Botón de consulta
if st.button("Consultar", type="primary"):
    with st.spinner('Consultando datos...'):
        df = obtener_tipo_cambio(fecha_consulta)
        
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
            
        else:
            st.warning("""
            No se encontraron datos para la fecha seleccionada. 
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
