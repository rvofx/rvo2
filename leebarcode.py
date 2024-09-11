import streamlit as st
from PyPDF2 import PdfReader
import pytesseract
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

# Función para leer códigos de barra usando Tesseract OCR
def read_barcodes(images):
    barcodes = []
    for image in images:
        text = pytesseract.image_to_string(image)
        if text:
            barcodes.append(text.strip())
    return barcodes

# Aplicación en Streamlit
st.title("Lector de Códigos de Barras en PDF con Tesseract OCR")

# Subir el archivo PDF
uploaded_file = st.file

