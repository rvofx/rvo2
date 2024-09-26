import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_exchange_rates():
    url = "https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table', {'id': 'ctl00_cphContent_rgTipoCambio_ctl00'})
    
    data = []
    for row in table.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        if len(cols) == 3:
            currency = cols[0].text.strip()
            buy = cols[1].text.strip()
            sell = cols[2].text.strip()
            data.append([currency, buy, sell])
    
    return pd.DataFrame(data, columns=['Moneda', 'Compra (S/)', 'Venta (S/)'])

st.title('Tipo de Cambio SBS')

if st.button('Obtener Tipo de Cambio'):
    df = get_exchange_rates()
    st.dataframe(df)
    
    # Opción para descargar como CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar datos como CSV",
        data=csv,
        file_name="tipo_cambio_sbs.csv",
        mime="text/csv",
    )
