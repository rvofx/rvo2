import streamlit as st
import pandas as pd

# Crear un ejemplo de DataFrame
data = {
    'Nombre': ['Juan', 'María', 'Pedro', 'Ana'],
    'Edad': [25, 30, 35, 40]
}

df = pd.DataFrame(data)

# Widget para introducir el valor de filtrado
filtro_valor = st.number_input('Introduce el valor para filtrar en la columna "Edad":', min_value=0)

# Filtrar la tabla en tiempo real basado en el valor del widget
filtered_df = df[df['Edad'] > filtro_valor]

# Mostrar la tabla original y la tabla filtrada
st.write(df)

st.write("Tabla filtrada:")
st.write(filtered_df)
