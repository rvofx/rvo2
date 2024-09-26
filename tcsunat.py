import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_exchange_rates():
    url = "https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar la tabla específica por su ID
        table = soup.find('table', {'id': 'ctl00_cphContent_rgTipoCambio_ctl00'})
        
        if table is None:
            st.error("No se pudo encontrar la tabla específica.")
            return None
        
        data = []
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Saltar la fila del encabezado
            cols = row.find_all('td')
            if len(cols) == 3:
                currency = cols[0].text.strip()
                buy = cols[1].text.strip()
                sell = cols[2].text.strip()
                data.append([currency, buy, sell])
        
        if not data:
            st.error("No se pudieron extraer datos de la tabla.")
            return None
        
        return pd.DataFrame(data, columns=['Moneda', 'Compra (S/)', 'Venta (S/)'])
    
    except requests.RequestException as e:
        st.error(f"Error al conectar con la página web: {e}")
    except Exception as e:
        st.error(f"Error inesperado: {e}")
    
    return None

st.title('Tipo de Cambio SBS')

if st.button('Obtener Tipo de Cambio'):
    with st.spinner('Cargando datos...'):
        df = get_exchange_rates()
    
    if df is not None and not df.empty:
        st.success('Datos obtenidos con éxito!')
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar datos como CSV",
            data=csv,
            file_name="tipo_cambio_sbs.csv",
            mime="text/csv",
        )
    else:
        st.error('No se pudieron obtener los datos. Por favor, intenta de nuevo más tarde.')

st.info('Si continúas experimentando problemas, verifica tu conexión a internet o contacta al administrador del sistema.')
