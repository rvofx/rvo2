import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_exchange_rates():
    url = "https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Imprimir el contenido de la respuesta para diagnóstico
        st.text("Contenido de la respuesta:")
        st.text(response.text[:500] + "...")  # Mostrar los primeros 500 caracteres
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar todas las tablas en la página
        all_tables = soup.find_all('table')
        st.text(f"Número de tablas encontradas: {len(all_tables)}")
        
        # Intentar encontrar la tabla específica
        table = soup.find('table', {'id': 'ctl00_cphContent_rgTipoCambio_ctl00'})
        
        if table is None:
            st.error("No se pudo encontrar la tabla específica. Buscando alternativas...")
            
            # Buscar una tabla que contenga datos de tipo de cambio
            for t in all_tables:
                headers = t.find_all('th')
                if headers and any("Moneda" in th.text for th in headers):
                    table = t
                    st.success("Se encontró una tabla alternativa con datos de tipo de cambio.")
                    break
            
            if table is None:
                st.error("No se pudo encontrar ninguna tabla con datos de tipo de cambio.")
                return None
        
        data = []
        rows = table.find_all('tr')
        
        st.text(f"Número de filas en la tabla: {len(rows)}")
        
        for row in rows[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 3:
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
        st.text(f"Detalles del error: {str(e)}")
    
    return None

st.title('Tipo de Cambio SBS (Versión de Diagnóstico)')

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
        st.error('No se pudieron obtener los datos. Revisa los mensajes de diagnóstico arriba.')

st.info('Esta es una versión de diagnóstico. Si ves errores, por favor comparte los mensajes de diagnóstico para ayudar a resolver el problema.')
