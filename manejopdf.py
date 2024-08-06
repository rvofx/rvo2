import os
import fitz  # PyMuPDF
import pandas as pd
import streamlit as st
from zipfile import ZipFile
from io import BytesIO

def extract_pdf_info(file):
    try:
        document = fitz.open(stream=file.read(), filetype="pdf")
        num_pages = document.page_count
        text = ""
        
        # Extrae el texto de cada página
        for page_num in range(num_pages):
            page = document.load_page(page_num)
            text += page.get_text()
        
        return text
    except Exception as e:
        st.error(f'Error al procesar el archivo: {e}')
        return None

# Título de la aplicación
st.title("Extracción de información de PDFs")

# Subida de un archivo ZIP con PDFs
uploaded_file = st.file_uploader("Sube un archivo ZIP con PDFs", type="zip")

if uploaded_file is not None:
    with ZipFile(uploaded_file) as z:
        # Lista para almacenar la información de los PDFs
        pdf_info_list = []
        
        for file_name in z.namelist():
            if file_name.endswith('.pdf'):
                with z.open(file_name) as pdf_file:
                    text = extract_pdf_info(pdf_file)
                    if text is not None:
                        pdf_info = {
                            'Nombre': file_name,
                            'Texto': text
                        }
                        pdf_info_list.append(pdf_info)
        
        # Crea un DataFrame de pandas con la información recopilada
        df = pd.DataFrame(pdf_info_list)

        # Mostrar la tabla en la aplicación
        st.write(df)

        # Botón para descargar el archivo CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Descargar CSV", data=csv, file_name='informacion_pdfs.csv', mime='text/csv')
