import streamlit as st
from PyPDF2 import PdfReader
from pyzbar.pyzbar import decode
from PIL import Image
import io

# Función para extraer imágenes del PDF
def extract_images_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    images = []
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        if '/XObject' in page['/Resources']:
            xobject = page['/Resources']['/XObject'].get_object()
            for obj in xobject:
                if xobject[obj]['/Subtype'] == '/Image':
                    data = xobject[obj]._data
                    image = Image.open(io.BytesIO(data))
                    images.append(image)
    return images

# Función para leer códigos de barra
def read_barcodes(images):
    barcodes = []
    for image in images:
        decoded = decode(image)
        for barcode in decoded:
            barcodes.append(barcode.data.decode('utf-8'))
    return barcodes

st.title("Lector de Códigos de Barras en PDF")

# Subir el archivo PDF
uploaded_file = st.file_uploader("Sube un archivo PDF", type="pdf")

if uploaded_file is not None:
    st.write("Procesando el archivo...")

    # Extraer las imágenes del PDF
    images = extract_images_from_pdf(uploaded_file)

    if images:
        # Leer los códigos de barras
        barcodes = read_barcodes(images)

        if barcodes:
            # Buscar códigos de barra repetidos
            unique_barcodes = set(barcodes)
            repeated_barcodes = [code for code in unique_barcodes if barcodes.count(code) > 1]

            st.write(f"Se encontraron {len(barcodes)} códigos de barras.")

            if repeated_barcodes:
                st.write("Códigos de barras repetidos:")
                for code in repeated_barcodes:
                    st.write(code)
            else:
                st.write("No hay códigos de barras repetidos.")
        else:
            st.write("No se encontraron códigos de barras en el PDF.")
    else:
        st.write("No se encontraron imágenes en el PDF.")
