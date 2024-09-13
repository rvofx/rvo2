import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Datos de ejemplo
data = {
    'Proceso': ['Proceso 1', 'Proceso 2', 'Proceso 3', 'Proceso 4'],
    'Fecha Inicio Programada': ['2023-09-01', '2023-09-05', '2023-09-10', '2023-09-15'],
    'Fecha Final Programada': ['2023-09-10', '2023-09-15', '2023-09-20', '2023-09-25'],
    'Fecha Inicio Real': ['2023-09-02', '2023-09-06', '2023-09-11', '2023-09-16'],
    'Fecha Final Real': ['2023-09-11', '2023-09-16', '2023-09-21', '2023-09-26'],
    'Fecha Emisión': ['2023-08-30', '2023-08-30', '2023-08-30', '2023-08-30'],  # Fecha de emisión independiente
    'Fecha Final': ['2023-09-27', '2023-09-27', '2023-09-27', '2023-09-27']     # Fecha final independiente
}

# Convertir datos a DataFrame
df = pd.DataFrame(data)

# Convertir las fechas a formato datetime
df['Fecha Inicio Programada'] = pd.to_datetime(df['Fecha Inicio Programada'])
df['Fecha Final Programada'] = pd.to_datetime(df['Fecha Final Programada'])
df['Fecha Inicio Real'] = pd.to_datetime(df['Fecha Inicio Real'])
df['Fecha Final Real'] = pd.to_datetime(df['Fecha Final Real'])
df['Fecha Emisión'] = pd.to_datetime(df['Fecha Emisión'])
df['Fecha Final'] = pd.to_datetime(df['Fecha Final'])

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

# Mostrar el gráfico
st.plotly_chart(fig)

