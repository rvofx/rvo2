import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

# Función para extraer información relevante del XML
def extract_xml_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Diccionario para almacenar la información relevante
    data = {}
    
    # Buscar la sección "Summary" donde están las principales categorías
    summary_section = root.find(".//mainsection[@title='Summary']")
    
    if summary_section is not None:
        # Extraer información de cada subsección relevante
        for section in summary_section.findall('section'):
            section_title = section.attrib.get('title', 'Unknown')
            entry = section.find('entry')
            if entry is not None:
                # Capturar el valor del atributo 'title' y el atributo 'value'
                data[section_title] = entry.attrib.get('value', 'No data')
    
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
    if all_data:
        df = pd.DataFrame(all_data)
        st.write("Tabla consolidada de todos los archivos XML subidos:")
        st.dataframe(df)
    else:
        st.write("No se encontró información relevante en los archivos XML.")
