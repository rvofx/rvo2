import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Datos de ejemplo
data = {
    'Proceso': ['Proceso 1', 'Proceso 2', 'Proceso 3', 'Proceso 4'],
    'Fecha Inicio Programada': ['2023-09-01', '2023-09-05', '2023-09-10', '2023-09-15'],
    'Fecha Final Programada': ['2023-10-10', '2023-10-15', '2023-10-20', '2023-10-25'],
    'Fecha Inicio Real': ['2023-09-02', '2023-09-06', '2023-09-11', '2023-09-16'],
    'Fecha Final Real': ['2023-10-11', '2023-10-16', '2023-10-21', '2023-10-26']
}

# Convertir datos a DataFrame
df = pd.DataFrame(data)

# Convertir las fechas a formato datetime
df['Fecha Inicio Programada'] = pd.to_datetime(df['Fecha Inicio Programada'])
df['Fecha Final Programada'] = pd.to_datetime(df['Fecha Final Programada'])
df['Fecha Inicio Real'] = pd.to_datetime(df['Fecha Inicio Real'])
df['Fecha Final Real'] = pd.to_datetime(df['Fecha Final Real'])

# Calcular fechas clave
fecha_emision = df['Fecha Inicio Programada'].min()  # Fecha de emisión
fecha_final = df['Fecha Final Real'].max()  # Fecha final del proceso
fecha_actual = datetime.now()

# Crear el gráfico Gantt
fig = px.timeline(df, x_start="Fecha Inicio Programada", x_end="Fecha Final Real", y="Proceso",
                  color="Proceso", title="Gráfico Gantt con Fechas Programadas y Reales")

# Añadir las líneas verticales utilizando add_shape para mayor flexibilidad
fig.add_shape(
    type="line",
    x0=fecha_emision, y0=0, x1=fecha_emision, y1=1,
    line=dict(color="blue", width=2, dash="dash"),
    xref='x', yref='paper',  # 'paper' hace referencia al área del gráfico, no a los datos
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
