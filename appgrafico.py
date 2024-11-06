import streamlit as st
import pandas as pd
import re

# Function to extract the graphic code
def extract_graphic_code(observation):
    match = re.search(r'GRAPHIC:\s*(\d{6})', str(observation))
    return match.group(1) if match else None

# Streamlit app
st.title("Extracción de Código Gráfico")

# File upload
uploaded_file = st.file_uploader("Sube tu archivo Excel", type="xlsx")
if uploaded_file:
    # Read the uploaded Excel file
    df = pd.read_excel(uploaded_file)
    
    # Check for the required column
    if 'nt Observacion' in df.columns:
        # Extract the graphic code
        df['Graphic Code'] = df['nt Observacion'].apply(extract_graphic_code)
        
        # Show the updated DataFrame
        st.write("Datos con la columna 'Graphic Code' añadida:")
        st.write(df)
        
        # Provide download option
        output_file = 'Updated_GRAF.xlsx'
        df.to_excel(output_file, index=False)
        
        # Download link
        with open(output_file, "rb") as file:
            btn = st.download_button(
                label="Descargar archivo con código gráfico",
                data=file,
                file_name="Updated_GRAF.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error("El archivo no tiene una columna llamada 'nt Observacion'.")
