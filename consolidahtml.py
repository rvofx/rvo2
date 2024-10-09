import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import re

def extract_software_list(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Removemos scripts y estilos
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Obtenemos el texto y lo dividimos en líneas
    text = soup.get_text(separator='\n')
    
    # Limpiamos las líneas y eliminamos líneas vacías
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Eliminamos líneas duplicadas manteniendo el orden
    unique_lines = []
    seen = set()
    for line in lines:
        if line not in seen:
            unique_lines.append(line)
            seen.add(line)
    
    return unique_lines

def main():
    st.title("Procesador de Inventario de Software")
    st.write("Sube los archivos HTML con las listas de software instalado en cada máquina.")

    # Subida de archivos
    uploaded_files = st.file_uploader("Sube tus archivos HTML", 
                                    type=['html', 'htm'],
                                    accept_multiple_files=True)

    if uploaded_files:
        all_data = []
        
        for file in uploaded_files:
            try:
                content = file.read().decode('utf-8')
                software_list = extract_software_list(content)
                
                # Agregamos cada software como una fila separada
                for software in software_list:
                    all_data.append({
                        'Máquina': file.name.replace('.html', '').replace('.htm', ''),
                        'Software Instalado': software
                    })
            except Exception as e:
                st.error(f"Error procesando {file.name}: {str(e)}")

        if all_data:
            # Crear DataFrame
            df = pd.DataFrame(all_data)
            
            # Mostrar datos
            st.subheader("Software por máquina")
            st.dataframe(df)
            
            # Estadísticas básicas
            st.subheader("Estadísticas")
            total_machines = len(df['Máquina'].unique())
            total_software = len(df)
            st.write(f"Total de máquinas procesadas: {total_machines}")
            st.write(f"Total de software encontrado: {total_software}")
            
            # Botones de descarga
            col1, col2 = st.columns(2)
            
            # CSV completo
            csv = df.to_csv(index=False).encode('utf-8')
            col1.download_button(
                label="Descargar CSV completo",
                data=csv,
                file_name="inventario_software_completo.csv",
                mime="text/csv"
            )
            
            # Lista única de software
            unique_software = pd.DataFrame(df['Software Instalado'].unique(), 
                                         columns=['Software'])
            csv_unique = unique_software.to_csv(index=False).encode('utf-8')
            col2.download_button(
                label="Descargar lista única de software",
                data=csv_unique,
                file_name="lista_software_unico.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
