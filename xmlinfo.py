import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

# Función para extraer toda la información de la primera sección del XML
def extract_first_section_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Diccionario para almacenar la información
    data = {}

    # Extraer el primer 'mainsection'
    first_section = root.find('mainsection')
    if first_section is not None:
        # Recorrer cada subsección dentro del primer 'mainsection'
        for section in first_section.findall('section'):
            section_title = section.attrib.get('title', 'Unknown Section')
            entries = section.findall('entry')

            # Recorrer cada entrada dentro de la subsección
            for entry in entries:
                entry_title = entry.attrib.get('title', 'Unknown Entry')
                entry_value = entry.attrib.get('value', 'No data')

                # Guardar el título de la entrada y su valor
                data[f"{section_title} - {entry_title}"] = entry_value

    return data

# Streamlit app
st.title("XML Uploader and First Section Extractor")

uploaded_files = st.file_uploader("Sube los archivos XML", type="xml", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    
    for file in uploaded_files:
        data = extract_first_section_data(file)
        all_data.append(data)

    # Convertir en DataFrame
    if all_data:
        df = pd.DataFrame(all_data)
        st.write("Tabla con la información de la primera página de cada archivo XML:")
        st.dataframe(df)
    else:
        st.write("No se encontró información relevante en los archivos XML.")
