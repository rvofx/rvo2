import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Datos de ejemplo
data = {
    'Proceso': ['Proceso 1', 'Proceso 2', 'Proceso 3', 'Proceso 4'],
    'Fecha Inicio Programada': ['2023-09-01', '2023-09-05', '2023-09-10', '2023-09-15'],
    'Fecha Final Programada': ['2023-09-10', '2023-09-15', '2023-09-20', '2023-09-25'],
    'Fecha Inicio Real': ['2023-09-02', '2023-09-06', '2023-09-11', '2023-09-16'],
    'Fecha Final Real': ['2023-09-11', '2023-09-16', '2023-09-21', '2023-09-26']
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

# Asegurarse de que las fechas estén en el formato adecuado para plotly
fecha_emision_str = fecha_emision.strftime('%Y-%m-%d')
fecha_final_str = fecha_final.strftime('%Y-%m-%d')
fecha_actual_str = fecha_actual.strftime('%Y-%m-%d')

# Añadir las líneas verticales
fig.add_vline(x=fecha_emision_str, line_dash="dash", line_color="blue", annotation_text="Fecha Emisión")
fig.add_vline(x=fecha_final_str, line_dash="dash", line_color="red", annotation_text="Fecha Final")
fig.add_vline(x=fecha_actual_str, line_dash="dash", line_color="green", annotation_text="Fecha Actual")

# Mostrar el gráfico
st.plotly_chart(fig)

