import streamlit as st
import pandas as pd

# Título de la aplicación con estilo personalizado
st.markdown(
    "<h1 style='color: red; font-family: Tahoma; font-size: 40px;'>Selector de Ciudades por País</h1>", 
    unsafe_allow_html=True
)

# Subir el archivo Excel
file = st.file_uploader("Carga el archivo Excel con los datos de países y ciudades", type=["xlsx"])

if file is not None:
    # Cargar datos desde el archivo Excel
    df = pd.read_excel(file)

    # Crear un diccionario a partir de los datos
    data = df.groupby("País")["Ciudad"].apply(list).to_dict()

    # Selección del país
    pais_seleccionado = st.selectbox("Selecciona un país:", list(data.keys()))

    # Mostrar las ciudades correspondientes
    if pais_seleccionado:
        st.write(f"Ciudades en {pais_seleccionado}:")
        for ciudad in data[pais_seleccionado]:
            st.write(f"- {ciudad}")
else:
    st.write("Por favor, sube un archivo Excel para continuar.")
