import streamlit as st
import pdfplumber
from pyzbar.pyzbar import decode
from PIL import Image
from collections import Counter

# Función para leer códigos de barras en una imagen
def extract_barcodes_from_image(image):
    barcodes = decode(image)
    return [barcode.data.decode('utf-8') for barcode in barcodes]

# Función para procesar el PDF
def process_pdf(file):
    with pdfplumber.open(file) as pdf:
        barcodes = []
        for page in pdf.pages:
            # Convertir la página en una imagen para decodificar los códigos de barras
            image = page.to_image(resolution=300)
            pil_image = Image.frombytes('RGB', image.original.size, image.original.tobytes())
            barcodes += extract_barcodes_from_image(pil_image)
        return barcodes

# Aplicación de Streamlit
st.title("Lectura de Códigos de Barras en PDF")

# Subir archivo PDF
uploaded_file = st.file_uploader("Sube un archivo PDF con códigos de barras", type="pdf")

if uploaded_file is not None:
    st.write("Procesando el archivo...")
    
    # Procesar el PDF y extraer códigos de barras
    barcodes = process_pdf(uploaded_file)
    
    # Contar los códigos de barra repetidos
    barcode_counts = Counter(barcodes)
    repeated_barcodes = {barcode: count for barcode, count in barcode_counts.items() if count > 1}
    
    st.write(f"Total de códigos de barra encontrados: {len(barcodes)}")
    
    if repeated_barcodes:
        st.write("Códigos de barra repetidos:")
        for barcode, count in repeated_barcodes.items():
            st.write(f"{barcode}: {count} veces")
    else:
        st.write("No se encontraron códigos de barra repetidos.")

