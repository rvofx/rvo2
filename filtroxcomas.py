import streamlit as st
import pandas as pd

# Crear la tabla de ejemplo
data = {
    'pedido': [1116, 1160, 1161, 1162, 1163, 1164, 1166, 1167, 1169],
    'f_emision': ['30/04/2024', '3/05/2024', '3/05/2024', '6/05/2024', '6/05/2024', '3/05/2024', '6/05/2024', '6/05/2024', '7/05/2024'],
    'f_entrega': ['8/07/2024', '8/07/2024', '8/07/2024', '8/07/2024', '8/07/2024', '8/07/2024', '8/07/2024', '8/07/2024', '15/07/2024'],
    'dias': [69, 66, 66, 63, 63, 66, 63, 63, 69],
    'cliente': ['ragman textilha'] * 9,
    'po': ['224-95', '224-122', '224-123', '224-124', '224-125', '224-126', '224-127', '224-1282', '224-129']
}

df = pd.DataFrame(data)

# Campo de entrada de texto para introducir los valores de los pedidos
pedido_input = st.text_input("Introduzca los valores de los pedidos separados por comas:")

# Parsear los valores ingresados por el usuario
pedidos_seleccionados = [int(p.strip()) for p in pedido_input.split(',') if p.strip()]

# Filtrar el DataFrame por los pedidos seleccionados
if pedidos_seleccionados:
    df_filtrado = df[df['pedido'].isin(pedidos_seleccionados)]
    st.write(df_filtrado)
else:
    st.write(df)
