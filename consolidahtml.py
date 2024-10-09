import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import io

def extract_software_table(html_content, machine_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Encontrar todas las tablas
    tables = soup.find_all('table')
    
    data = []
    for table in tables:
        # Encontrar todas las filas
        rows = table.find_all('tr')
        
        # Verificar si es la tabla correcta buscando los encabezados
        headers = [th.text.strip() for th in rows[0].find_all(['th', 'td'])]
        if 'Program Name' in headers and 'Size' in headers and 'Installed On' in headers:
            # Procesar cada fila de la tabla
            for row in rows[1:]:  # Saltamos la fila de encabezados
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 3:
                    program_name = cols[0].text.strip()
                    size = cols[1].text.strip()
                    installed_on = cols[2].text.strip()
                    
                    data.append({
                        'Machine Name': machine_name,
                        'Program Name': program_name,
                        'Size': size,
                        'Installed On': installed_on
                    })
    
    return data

def main():
    st.title("Consolidador de Inventario de Software")
    st.write("Sube los archivos HTML que contienen las tablas de software instalado.")

    # Subida de archivos
    uploaded_files = st.file_uploader(
        "Sube tus archivos HTML", 
        type=['html', 'htm'],
        accept_multiple_files=True
    )

    if uploaded_files:
        all_data = []
        
        with st.spinner('Procesando archivos...'):
            for file in uploaded_files:
                try:
                    # Obtener el nombre de la máquina del nombre del archivo
                    machine_name = file.name.replace('.html', '').replace('.htm', '')
                    
                    # Leer y procesar el contenido
                    content = file.read().decode('utf-8')
                    table_data = extract_software_table(content, machine_name)
                    all_data.extend(table_data)
                except Exception as e:
                    st.error(f"Error procesando {file.name}: {str(e)}")

        if all_data:
            # Crear DataFrame
            df = pd.DataFrame(all_data)
            
            # Mostrar estadísticas
            st.subheader("Estadísticas del procesamiento")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de máquinas", len(df['Machine Name'].unique()))
            col2.metric("Total de programas", len(df))
            col3.metric("Archivos procesados", len(uploaded_files))
            
            # Mostrar tabla consolidada
            st.subheader("Tabla Consolidada de Software")
            st.dataframe(
                df,
                column_config={
                    "Machine Name": "Nombre de Máquina",
                    "Program Name": "Nombre del Programa",
                    "Size": "Tamaño",
                    "Installed On": "Fecha de Instalación"
                },
                hide_index=True
            )
            
            # Opciones de descarga
            col1, col2 = st.columns(2)
            
            # CSV completo
            csv = df.to_csv(index=False).encode('utf-8')
            col1.download_button(
                label="Descargar CSV completo",
                data=csv,
                file_name="inventario_software_completo.csv",
                mime="text/csv"
            )
            
            # Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Inventario', index=False)
            excel_data = excel_buffer.getvalue()
            
            col2.download_button(
                label="Descargar Excel",
                data=excel_data,
                file_name="inventario_software_completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
