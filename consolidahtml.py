import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import io

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Removemos scripts y estilos
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=' ').strip()

def main():
    st.title("Consolidador de Archivos HTML")
    st.write("Esta aplicación te permite subir múltiples archivos HTML y consolidar su contenido en una lista.")

    # Subida de archivos
    uploaded_files = st.file_uploader("Sube tus archivos HTML", 
                                    type=['html', 'htm'],
                                    accept_multiple_files=True)

    if uploaded_files:
        consolidated_data = []
        
        for file in uploaded_files:
            content = file.read().decode('utf-8')
            extracted_text = extract_text_from_html(content)
            consolidated_data.append({
                'Nombre del archivo': file.name,
                'Contenido': extracted_text
            })

        if consolidated_data:
            # Crear DataFrame
            df = pd.DataFrame(consolidated_data)
            
            # Mostrar datos
            st.subheader("Contenido consolidado")
            st.dataframe(df)
            
            # Botón para descargar
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar como CSV",
                data=csv,
                file_name="contenido_consolidado.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
