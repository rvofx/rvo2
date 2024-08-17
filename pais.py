import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Selector de Ciudades por País")

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
