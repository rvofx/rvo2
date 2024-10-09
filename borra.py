import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd

def extract_software_table(html_content, machine_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extraer la fecha de generación (después del último <br>)
    generation_info = ''
    br_tags = soup.find_all('br')
    if br_tags:
        last_br = br_tags[-1]
        if last_br.next_sibling:
            generation_info = last_br.next_sibling.strip()
    
    # Encontrar todas las tablas
    tables = soup.find_all('table')
    
    data = []
    for table in tables:
        # Encontrar todas las filas
        rows = table.find_all('tr')
        
        # Verificar si es la tabla correcta buscando los encabezados
        headers = [th.text.strip() for th in rows[0].find_all(['th', 'td'])]
        
        # Mapeo de nombres de columnas español-inglés
        header_mapping = {
            'Nombre del programa': 'Program Name',
            'Tamaño': 'Size',
            'Instalado en': 'Installed On',
            'Program Name': 'Program Name',
            'Size': 'Size',
            'Installed On': 'Installed On'
        }
        
        # Convertir los encabezados encontrados a sus equivalentes en inglés
        mapped_headers = [header_mapping.get(h, h) for h in headers]
        
        # Verificar si es la tabla correcta con cualquiera de los conjuntos de encabezados
        if 'Program Name' in mapped_headers and 'Size' in mapped_headers and 'Installed On' in mapped_headers:
            # Encontrar los índices de las columnas
            program_name_idx = mapped_headers.index('Program Name')
            size_idx = mapped_headers.index('Size')
            installed_on_idx = mapped_headers.index('Installed On')
            
            # Procesar cada fila de la tabla
            for row in rows[1:]:  # Saltamos la fila de encabezados
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 3:
                    program_name = cols[program_name_idx].text.strip()
                    size = cols[size_idx].text.strip()
                    installed_on = cols[installed_on_idx].text.strip()
                    
                    data.append({
                        'Machine Name': machine_name,
                        'Generation Info': generation_info,
                        'Program Name': program_name,
                        'Size': size,
                        'Installed On': installed_on
                    })
    
    return data

def main():
    st.title("Software Inventory Consolidator")
    st.write("Upload HTML files containing installed software tables.")

    # Subida de archivos
    uploaded_files = st.file_uploader(
        "Upload your HTML files", 
        type=['html', 'htm'],
        accept_multiple_files=True
    )

    if uploaded_files:
        all_data = []
        
        with st.spinner('Processing files...'):
            for file in uploaded_files:
                try:
                    # Obtener el nombre de la máquina del nombre del archivo
                    machine_name = file.name.replace('.html', '').replace('.htm', '')
                    
                    # Leer y procesar el contenido
                    content = file.read().decode('utf-8')
                    table_data = extract_software_table(content, machine_name)
                    all_data.extend(table_data)
                except Exception as e:
                    st.error(f"Error processing {file.name}: {str(e)}")

        if all_data:
            # Crear DataFrame
            df = pd.DataFrame(all_data)
            
            # Mostrar estadísticas
            st.subheader("Processing Statistics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Machines", len(df['Machine Name'].unique()))
            col2.metric("Total Programs", len(df))
            col3.metric("Files Processed", len(uploaded_files))
            
            # Mostrar tabla consolidada
            st.subheader("Consolidated Software Table")
            st.dataframe(
                df,
                hide_index=True
            )
            
            # CSV completo
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Complete CSV",
                data=csv,
                file_name="complete_software_inventory.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
