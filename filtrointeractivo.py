import streamlit as st
import pandas as pd

# Crear un ejemplo de DataFrame
data = {
    'Nombre': ['Juan', 'María', 'Pedro', 'Ana'],
    'Edad': [25, 30, 35, 40]
}

df = pd.DataFrame(data)

# Mostrar la tabla original al inicio
st.write("Tabla original:")
st.write(df)

# Widget para introducir el valor de filtrado
filtro_valor = st.number_input('Introduce el valor para filtrar en la columna "Edad":', min_value=0)

# Botón para aplicar el filtro
if st.button("Aplicar Filtro"):
    # Filtrar la tabla en tiempo real basado en el valor del widget
    filtered_df = df[df['Edad'] > filtro_valor]

    # Mostrar la tabla filtrada después de aplicar el filtro
    st.write("Tabla filtrada:")
    st.write(filtered_df)
