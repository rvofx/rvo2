import streamlit as st
import pandas as pd

# Crear un ejemplo de DataFrame
data = {
    'Nombre': ['Juan', 'María', 'Pedro', 'Ana'],
    'Edad': [25, 30, 35, 40]
}

df = pd.DataFrame(data)

# Widget para introducir el valor de filtrado
filtro_valor = st.number_input('Introduce el valor para filtrar:', min_value=0)

# Aplicar el filtro interactivo y mostrar la tabla resultante
filtered_df = df[df['Edad'] > filtro_valor]
st.write(filtered_df)
