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

def create_page_with_labels(images, code):
    """Create a single page containing all labels for a code arranged in a grid"""
    # Define page size (A4)
    page_width = 2480  # A4 at 300 DPI
    page_height = 3508
    
    # Calculate image size and grid layout
    max_images_per_row = 2
    image_width = page_width // max_images_per_row - 100  # Leave some margin
    
    # Create new white page
    page = Image.new('RGB', (page_width, page_height), 'white')
    
    # Add title with code
    title_font_size = 50
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(page)
    try:
        font = ImageFont.truetype("arial.ttf", title_font_size)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), f"Código: {code}", font=font, fill='black')
    
    # Calculate positions for images
    start_y = 150  # Leave space for title
    current_x = 50
    current_y = start_y
    
    for idx, img in enumerate(images):
        # Resize image maintaining aspect ratio
        aspect_ratio = img.width / img.height
        new_height = int(image_width / aspect_ratio)
        resized_img = img.resize((image_width, new_height), Image.Resampling.LANCZOS)
        
        # If we're starting a new row
        if idx % max_images_per_row == 0 and idx != 0:
            current_x = 50
            current_y += new_height + 50
        
        # Paste image
        page.paste(resized_img, (current_x, current_y))
        current_x += image_width + 50
    
    return page

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
            # Create output PDF
            output = io.BytesIO()
            first_page = True
            
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
                    # Create page with all labels for this code
                    page = create_page_with_labels(matching_pages, code)
                    
                    # Save to PDF
                    if first_page:
                        page.save(output, "PDF", resolution=300.0)
                        first_page = False
                    else:
                        page.save(output, "PDF", resolution=300.0, append=True)
                
                # Update progress
                progress_bar.progress((index + 1) / len(df))
                pdf_file.seek(0)  # Reset PDF file pointer
            
            # Offer download
            output.seek(0)
            st.download_button(
                label="Descargar PDF",
                data=output,
                file_name="etiquetas_por_codigo.pdf",
                mime="application/pdf"
            )
            
            status_text.text("¡Procesamiento completado!")

if __name__ == "__main__":
    main()
