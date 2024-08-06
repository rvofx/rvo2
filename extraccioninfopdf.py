import os
import pdfplumber
import pandas as pd
import streamlit as st
from zipfile import ZipFile
from io import BytesIO

def extract_pdf_info(file, num_columns=3):
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_width = page.width
                page_height = page.height
                column_width = page_width / num_columns
                columns_text = []

                for col in range(num_columns):
                    left = col * column_width
                    right = (col + 1) * column_width

                    # Asegurar que las bounding boxes están dentro de los límites de la página
                    crop_box = (max(left, 0), 0, min(right, page_width), page_height)
                    column_text = page.within_bbox(crop_box).extract_text()
                    if column_text:
                        columns_text.append(column_text.strip())

                # Concatenar el texto de las columnas en orden vertical
                text += "\n".join(columns_text) + "\n"
        
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
