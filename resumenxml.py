import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

# Función para procesar cada archivo XML
def procesar_xml(xml_file, file_name):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Diccionario para almacenar la información básica
    info = {
        "File Name": file_name,
        "Operating System": None,
        "CPU": None,
        "RAM": None,
        "Motherboard": None,
        "Graphics": None,
        "Storage": None,
        "Audio": None
    }

    # Buscar la sección 'Summary' y extraer la información básica
    for main_section in root.findall("mainsection"):
        if main_section.attrib.get('title') == 'Summary':
            for section in main_section.findall("section"):
                section_title = section.attrib.get('title')
                for entry in section.findall('entry'):
                    title = entry.attrib.get('title')
                    if section_title == "Operating System" and title == "Windows 11 Home 64-bit":
                        info["Operating System"] = "Windows 11 Home 64-bit"
                    elif section_title == "CPU":
                        info["CPU"] = entry.attrib.get('title')
                    elif section_title == "RAM":
                        info["RAM"] = entry.attrib.get('title')
                    elif section_title == "Motherboard":
                        info["Motherboard"] = entry.attrib.get('title')
                    elif section_title == "Graphics":
                        info["Graphics"] = entry.attrib.get('title')
                    elif section_title == "Storage":
                        info["Storage"] = entry.attrib.get('title')
                    elif section_title == "Audio":
                        info["Audio"] = entry.attrib.get('title')

    return info

# Configuración de la aplicación Streamlit
st.title("Visor de Información de Archivos XML")
st.write("Sube tus archivos XML para extraer y visualizar la información en una tabla.")

# Subir múltiples archivos XML
uploaded_files = st.file_uploader("Sube los archivos XML", type="xml", accept_multiple_files=True)

# Lista donde se almacenará la información procesada de todos los archivos
datos = []

if uploaded_files:
    for file in uploaded_files:
        # Procesar cada archivo XML y agregar la información a la lista (incluyendo el nombre del archivo)
        file_name = file.name
        datos.append(procesar_xml(file, file_name))

    # Convertir la lista en un DataFrame de pandas para visualizarla como tabla
    df = pd.DataFrame(datos)

    # Mostrar la tabla consolidada
    st.write("### Tabla Consolidada de Información Básica")
    st.dataframe(df)

else:
    st.write("No se han subido archivos todavía.")

