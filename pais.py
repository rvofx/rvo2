import streamlit as st
import pandas as pd

# Cargar datos desde el archivo Excel
df = pd.read_excel("paises_ciudades.xlsx")

# Crear un diccionario a partir de los datos
data = df.groupby("País")["Ciudad"].apply(list).to_dict()

# Título de la aplicación
st.title("Selector de Ciudades por País")

# Selección del país
pais_seleccionado = st.selectbox("Selecciona un país:", list(data.keys()))

# Mostrar las ciudades correspondientes
if pais_seleccionado:
    st.write(f"Ciudades en {pais_seleccionado}:")
    for ciudad in data[pais_seleccionado]:
        st.write(f"- {ciudad}")
