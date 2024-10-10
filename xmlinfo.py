import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

# Función para extraer información relevante del XML
def extract_xml_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Diccionario para almacenar la información relevante
    data = {}
    
    # Extraer información de Sistema Operativo, CPU, RAM y Almacenamiento
    os_info = root.find(".//section[@title='Operating System']/entry[@title='Model']")
    cpu_info = root.find(".//section[@title='CPU']/entry[@title='Intel Processor @ 2.40GHz']")
    ram_info = root.find(".//section[@title='RAM']/entry[@title='8.00GB']")
    storage_info = root.find(".//section[@title='Storage']/entry[@title='238GB NVMe']")
    
    if os_info is not None:
        data['Operating System'] = os_info.get('value')
    if cpu_info is not None:
        data['CPU'] = cpu_info.get('value')
    if ram_info is not None:
        data['RAM'] = ram_info.get('value')
    if storage_info is not None:
        data['Storage'] = storage_info.get('value')

    return data

# Streamlit app
st.title("XML Uploader and Data Extractor")

uploaded_files = st.file_uploader("Sube los archivos XML", type="xml", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    
    for file in uploaded_files:
        data = extract_xml_data(file)
        all_data.append(data)

    # Convertir en DataFrame
    df = pd.DataFrame(all_data)
    st.write("Tabla consolidada de todos los archivos XML subidos:")
    st.dataframe(df)
