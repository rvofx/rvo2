import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import io
from PIL import Image
import fitz  # PyMuPDF

def extract_labels_from_pdf(pdf_file, code):
    """Extract pages containing the specified code from PDF"""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    matching_pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if code in text:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            matching_pages.append(img)
            
    return matching_pages

def create_pdf_with_labels(images):
    """Create a PDF from a list of images"""
    output = io.BytesIO()
    if images:
        first_image = images[0]
        first_image.save(
            output,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=images[1:]
        )
    return output.getvalue()

def main():
    st.title("Extractor de Etiquetas por Código")
    
    # File uploaders
    excel_file = st.file_uploader("Cargar archivo Excel", type=['xlsx', 'xls'])
    pdf_file = st.file_uploader("Cargar archivo PDF con etiquetas", type=['pdf'])
    
    if excel_file and pdf_file:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        if 'Code' not in df.columns:
            st.error("El archivo Excel debe contener una columna llamada 'Code'")
            return
            
        # Process button
        if st.button("Procesar Archivos"):
            output_pdf = PdfWriter()
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process each code
            for index, row in df.iterrows():
                code = row['Code']
                status_text.text(f"Procesando código: {code}")
                
                # Extract labels for current code
                matching_pages = extract_labels_from_pdf(pdf_file, code)
                
                if matching_pages:
                    # Create PDF for current code
                    pdf_bytes = create_pdf_with_labels(matching_pages)
                    
                    # Add pages to final PDF
                    temp_pdf = PdfReader(io.BytesIO(pdf_bytes))
                    for page in temp_pdf.pages:
                        output_pdf.add_page(page)
                
                # Update progress
                progress_bar.progress((index + 1) / len(df))
                pdf_file.seek(0)  # Reset PDF file pointer
            
            # Save final PDF
            final_pdf = io.BytesIO()
            output_pdf.write(final_pdf)
            final_pdf.seek(0)
            
            # Offer download
            st.download_button(
                label="Descargar PDF",
                data=final_pdf,
                file_name="etiquetas_extraidas.pdf",
                mime="application/pdf"
            )
            
            status_text.text("¡Procesamiento completado!")

if __name__ == "__main__":
    main()
