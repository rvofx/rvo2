import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Datos de ejemplo con fechas entre agosto 2024 y noviembre 2024
data = {
    'Proceso': ['Proceso 1', 'Proceso 2', 'Proceso 3', 'Proceso 4'],
    'Fecha Inicio Programada': ['2024-08-10', '2024-08-20', '2024-09-01', '2024-09-15'],
    'Fecha Final Programada': ['2024-08-20', '2024-09-05', '2024-09-20', '2024-10-05'],
    'Fecha Inicio Real': ['2024-08-12', '2024-08-22', '2024-09-02', '2024-09-16'],
    'Fecha Final Real': ['2024-08-21', '2024-09-06', '2024-09-21', '2024-10-06'],
    'Fecha Emisión': ['2024-08-05', '2024-08-05', '2024-08-05', '2024-08-05'],  # Fecha de emisión independiente
    'Fecha Final': ['2024-10-10', '2024-10-10', '2024-10-10', '2024-10-10']     # Fecha final independiente
}

# Convertir datos a DataFrame
df = pd.DataFrame(data)
"""
# Convertir las fechas a formato datetime
df['Fecha Inicio Programada'] = pd.to_datetime(df['Fecha Inicio Programada'])
df['Fecha Final Programada'] = pd.to_datetime(df['Fecha Final Programada'])
df['Fecha Inicio Real'] = pd.to_datetime(df['Fecha Inicio Real'])
df['Fecha Final Real'] = pd.to_datetime(df['Fecha Final Real'])
df['Fecha Emisión'] = pd.to_datetime(df['Fecha Emisión'])
df['Fecha Final'] = pd.to_datetime(df['Fecha Final'])
"""
# Extraer una fecha de emisión y una fecha final independientes del set de datos
fecha_emision = df['Fecha Emisión'].iloc[0]  # Independiente pero dentro del set
fecha_final = df['Fecha Final'].iloc[0]  # Independiente pero dentro del set
fecha_actual = datetime.now()

# Crear el gráfico Gantt basado en las fechas programadas
fig = px.timeline(df, x_start="Fecha Inicio Programada", x_end="Fecha Final Programada", y="Proceso",
                  color="Proceso", title="Gráfico Gantt con Fechas Programadas")

# Añadir las fechas reales de inicio y fin como marcas
fig.add_trace(go.Scatter(
    x=df['Fecha Inicio Real'], y=df['Proceso'], mode='markers',
    marker=dict(color='blue', size=10),
    name="Fecha Inicio Real"
))

fig.add_trace(go.Scatter(
    x=df['Fecha Final Real'], y=df['Proceso'], mode='markers',
    marker=dict(color='red', size=10),
    name="Fecha Final Real"
))

# Añadir las líneas verticales para las fechas de emisión, final y actual
fig.add_shape(
    type="line",
    x0=fecha_emision, y0=0, x1=fecha_emision, y1=1,
    line=dict(color="blue", width=2, dash="dash"),
    xref='x', yref='paper',
    name="Fecha Emisión"
)

fig.add_shape(
    type="line",
    x0=fecha_final, y0=0, x1=fecha_final, y1=1,
    line=dict(color="red", width=2, dash="dash"),
    xref='x', yref='paper',
    name="Fecha Final"
)

fig.add_shape(
    type="line",
    x0=fecha_actual, y0=0, x1=fecha_actual, y1=1,
    line=dict(color="green", width=2, dash="dash"),
    xref='x', yref='paper',
    name="Fecha Actual"
)

# Añadir marcas verticales cada dos días
fecha_min = df['Fecha Inicio Programada'].min()
fecha_max = df['Fecha Final Programada'].max()

for dia in pd.date_range(start=fecha_min, end=fecha_max, freq='2D'):
    fig.add_vline(x=dia, line_dash="dot", line_color="lightgray", opacity=0.5)

# Ajustar el gráfico para que ocupe todo el ancho de la página
fig.update_layout(width=1500, height=600)

# Mostrar el gráfico
st.plotly_chart(fig, use_container_width=True)
