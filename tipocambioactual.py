import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from playwright.sync_api import sync_playwright
import time

def scrape_sunat_exchange_rate():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            
            # Navegar a la página
            page.goto("https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias")
            
            # Esperar a que la tabla se cargue
            page.wait_for_selector('.form-table', timeout=15000)
            
            # Dar un pequeño tiempo adicional para asegurar la carga completa
            time.sleep(2)
            
            # Extraer datos de la tabla
            rows = page.query_selector_all('.form-table tr')
            
            data = []
            # Ignorar la primera fila (encabezados)
            for row in rows[1:]:
                cols = row.query_selector_all('td')
                if len(cols) == 3:
                    try:
                        date_str = cols[0].inner_text().strip()
                        buy = float(cols[1].inner_text().strip())
                        sell = float(cols[2].inner_text().strip())
                        date = datetime.strptime(date_str, '%d/%m/%Y').date()
                        data.append({
                            'Fecha': date,
                            'Compra': buy,
                            'Venta': sell
                        })
                    except (ValueError, TypeError):
                        continue
            
            return pd.DataFrame(data)
            
        finally:
            browser.close()

def main():
    st.set_page_config(page_title="Tipo de Cambio SUNAT", layout="wide")
    
    st.title("📊 Consulta de Tipo de Cambio SUNAT")
    
    st.markdown("""
    Esta aplicación muestra el tipo de cambio oficial de SUNAT en tiempo real.
    Los datos son extraídos directamente de la página web de SUNAT.
    """)
    
    # Intentar cargar datos al inicio si no existen
    if 'data' not in st.session_state:
        with st.spinner('Cargando datos iniciales...'):
            try:
                df = scrape_sunat_exchange_rate()
                st.session_state['data'] = df
            except Exception as e:
                st.error(f'Error al cargar datos iniciales: {str(e)}')
    
    if st.button("🔄 Actualizar Datos"):
        with st.spinner('Obteniendo datos de SUNAT...'):
            try:
                df = scrape_sunat_exchange_rate()
                st.session_state['data'] = df
                st.success('¡Datos actualizados exitosamente!')
            except Exception as e:
                st.error(f'Error al obtener los datos: {str(e)}')
                return
    
    if 'data' in st.session_state:
        df = st.session_state['data']
        
        # Mostrar datos más recientes
        st.subheader("💱 Tipo de Cambio Actual")
        latest_data = df.iloc[0]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fecha", latest_data['Fecha'].strftime('%d/%m/%Y'))
        with col2:
            st.metric("Compra", f"S/ {latest_data['Compra']:.3f}")
        with col3:
            st.metric("Venta", f"S/ {latest_data['Venta']:.3f}")
        
        # Gráfico
        st.subheader("📈 Evolución del Tipo de Cambio")
        fig = px.line(df, x='Fecha', y=['Compra', 'Venta'],
                     title='Evolución del Tipo de Cambio SUNAT',
                     labels={'value': 'Tipo de Cambio (S/)', 'variable': 'Tipo'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de datos
        st.subheader("📋 Tabla de Datos")
        st.dataframe(df)
        
        # Botón de descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar datos como CSV",
            data=csv,
            file_name='tipo_cambio_sunat.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()
