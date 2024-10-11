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

# Diccionario de monedas disponibles (actualizado con los nombres exactos)
MONEDAS = {
    "Dólar de N. A.": "02",
    "Euro": "03",
    "Yen Japonés": "04",
    "Libra Esterlina": "05"
}

def obtener_tipo_cambio(fecha_inicio, fecha_fin, moneda='02'):
    """
    Obtiene el tipo de cambio de la SBS para un rango de fechas y moneda específica
    """
    url = 'https://www.sbs.gob.pe/app/stats/TC-CV-Historico.asp'
    
    # Asegurarnos de que las fechas estén en el formato correcto
    fecha_inicio_str = fecha_inicio.strftime('%d/%m/%Y')
    fecha_fin_str = fecha_fin.strftime('%d/%m/%Y')
    
    payload = {
        'FECHA_INICIO': fecha_inicio_str,
        'FECHA_FIN': fecha_fin_str,
        'MONEDA': moneda,
        'button1': 'Consultar'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Realizar la solicitud POST con headers
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tabla = soup.find('table', {'id': 'ctl00_cphContent_rgTipoCambio_ctl00'})
        
        if tabla:
            df = pd.read_html(str(tabla))[0]
            df.columns = ['Fecha', 'Compra', 'Venta']
            return df
        else:
            st.error(f"No se encontraron datos para el período {fecha_inicio_str} - {fecha_fin_str}")
            return None
            
    except Exception as e:
        st.error(f'Error al consultar el tipo de cambio: {str(e)}')
        return None

# Crear el formulario en la barra lateral
with st.sidebar:
    st.header("Parámetros de consulta")
    
    # Selector de moneda
    moneda_seleccionada = st.selectbox(
        "Seleccione la moneda:",
        options=list(MONEDAS.keys()),
        index=0  # Seleccionar Dólar por defecto
    )
    
    # Selector de fechas
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input(
            "Fecha inicio",
            datetime.now()
        )
    with col2:
        fecha_fin = st.date_input(
            "Fecha fin",
            datetime.now()
        )
    
    # Botón de consulta
    consultar = st.button("Consultar", type="primary")

# Realizar la consulta cuando se presione el botón
if consultar:
    with st.spinner('Consultando datos...'):
        # Obtener el código de la moneda seleccionada
        codigo_moneda = MONEDAS[moneda_seleccionada]
        
        # Realizar la consulta
        df = obtener_tipo_cambio(fecha_inicio, fecha_fin, codigo_moneda)
        
        if df is not None and not df.empty:
            # Mostrar los datos en una tabla
            st.subheader("Datos del tipo de cambio")
            st.dataframe(df, use_container_width=True)
            
            # Crear gráfico
            st.subheader("Gráfico histórico")
            fig = px.line(df, x='Fecha', y=['Compra', 'Venta'],
                         title=f'Tipo de Cambio - {moneda_seleccionada}',
                         labels={'value': 'Tipo de cambio', 'variable': 'Tipo'},
                         template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas básicas
            st.subheader("Estadísticas")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Promedio Compra", f"S/ {df['Compra'].mean():.3f}")
            with col2:
                st.metric("Promedio Venta", f"S/ {df['Venta'].mean():.3f}")
            with col3:
                st.metric("Diferencial promedio", 
                         f"S/ {(df['Venta'] - df['Compra']).mean():.3f}")
            
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
with st.expander("ℹ️ Información"):
    st.markdown("""
    - Los datos son obtenidos directamente de la SBS (Superintendencia de Banca, Seguros y AFP)
    - Las consultas están limitadas a un período máximo de 90 días
    - Los tipos de cambio mostrados son los oficiales publicados por la SBS
    - La información se actualiza diariamente en días hábiles
    """)
