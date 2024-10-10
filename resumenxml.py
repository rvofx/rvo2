import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

# Función para procesar cada archivo XML y extraer la información de "Summary"
def procesar_xml(xml_file, file_name):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Diccionario para almacenar la información básica de la sección "Summary"
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

    # Buscar la sección "Summary" o "Resumen"
    for main_section in root.findall("mainsection"):
        if main_section.attrib.get('title') in ['Summary', 'Resumen']:
            for section in main_section.findall("section"):
                section_title = section.attrib.get('title')

                # Filtrar y extraer las entradas de interés
                if section_title in ["Operating System", "Sistema Operativo"]:
                    for entry in section.findall('entry'):
                        if entry.attrib.get('title'):
                            info["Operating System"] = entry.attrib.get('title')
                elif section_title in ["CPU", "Procesador"]:
                    for entry in section.findall('entry'):
                        if entry.attrib.get('title'):
                            info["CPU"] = entry.attrib.get('title')
                elif section_title in ["RAM", "Memoria RAM"]:
                    for entry in section.findall('entry'):
                        if entry.attrib.get('title'):
                            info["RAM"] = entry.attrib.get('title')
                elif section_title in ["Motherboard", "Placa Madre"]:
                    for entry in section.findall('entry'):
                        if entry.attrib.get('title'):
                            info["Motherboard"] = entry.attrib.get('title')
                elif section_title in ["Graphics", "Gráficos"]:
                    graphics_info = []
                    for entry in section.findall('entry'):
                        if entry.attrib.get('title'):
                            graphics_info.append(entry.attrib.get('title'))
                    info["Graphics"] = ', '.join(graphics_info)
                elif section_title in ["Storage", "Almacenamiento"]:
                    storage_info = []
                    for entry in section.findall('entry'):
                        if entry.attrib.get('title'):
                            storage_info.append(entry.attrib.get('title'))
                    info["Storage"] = ', '.join(storage_info)
                elif section_title in ["Audio", "Sonido"]:
                    for entry in section.findall('entry'):
                        if entry.attrib.get('title'):
                            info["Audio"] = entry.attrib.get('title')

    return info

# Configuración de la aplicación Streamlit
st.title("Visor de Información de Archivos XML")
st.write("Sube tus archivos XML para extraer la información de la sección 'Summary'.")

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
    st.write("### Tabla Consolidada de Información Básica de 'Summary'")
    st.dataframe(df)

else:
    st.write("No se han subido archivos todavía.")
