import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import plotly.express as px
from datetime import datetime

def configure_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return chrome_options

def scrape_sunat_exchange_rate():
    chrome_options = configure_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Cargar la página
        url = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"
        driver.get(url)
        
        # Esperar que la tabla esté presente
        wait = WebDriverWait(driver, 15)
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-table")))
        
        # Extraer datos
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []
        
        for row in rows[1:]:  # Ignorar encabezados
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) == 3:
                date_str = cols[0].text.strip()
                buy = float(cols[1].text.strip())
                sell = float(cols[2].text.strip())
                try:
                    date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    data.append({
                        'Fecha': date,
                        'Compra': buy,
                        'Venta': sell
                    })
                except ValueError:
                    continue
                
        return pd.DataFrame(data)
        
    finally:
        driver.quit()

def main():
    st.set_page_config(page_title="Tipo de Cambio SUNAT", layout="wide")
    
    st.title("📊 Consulta de Tipo de Cambio SUNAT")
    
    st.markdown("""
    Esta aplicación muestra el tipo de cambio oficial de SUNAT en tiempo real.
    Los datos son extraídos directamente de la página web de SUNAT.
    """)
    
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
