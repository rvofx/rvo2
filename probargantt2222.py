import plotly.figure_factory as ff
from datetime import datetime
import pandas as pd
import streamlit as st

def create_gantt(df, f_emision, f_entrega):
    # Preparar los datos para el gráfico de Gantt
    gantt_data = []
    for _, row in df.iterrows():
        gantt_data.append(dict(
            Task=row['proceso'],
            Start=row['fecha_inicio'],
            Finish=row['fecha_fin'],
            Description=f"Progreso: {row['progreso']}%"
        ))

    # Crear el gráfico de Gantt
    fig = ff.create_gantt(gantt_data, index_col='Task', show_colorbar=True, group_tasks=True)

    # Ajustar el diseño del gráfico
    fig.update_layout(
        title="Gráfico de Gantt - Procesos de Producción",
        xaxis_title="Fecha",
        yaxis_title="Proceso",
        height=600,
    )

    # Añadir líneas verticales para fechas importantes
    lineas = [
        ("F. Emisión", f_emision, "green"),
        ("F. Entrega", f_entrega, "red"),
        ("Hoy", datetime.today().date(), "blue")
    ]

    for nombre, fecha, color in lineas:
        fig.add_vline(x=fecha, line_dash="dash", line_color=color, annotation_text=nombre, annotation_position="top right")

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    # Imprimir información de los procesos
    for _, row in df.iterrows():
        duracion = (row['fecha_fin'] - row['fecha_inicio']).days
        st.write(f"Proceso: {row['proceso']}, Fecha Inicio: {row['fecha_inicio']}, Fecha Fin: {row['fecha_fin']}, Duración: {duracion} días")

# Datos de prueba
df = pd.DataFrame({
    'proceso': ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO'],
    'fecha_inicio': ['2024-07-01', '2024-07-10', '2024-07-20', '2024-08-01', '2024-08-15'],
    'fecha_fin': ['2024-07-05', '2024-07-15', '2024-07-25', '2024-08-05', '2024-08-20'],
    'progreso': [100, 80, 60, 90, 75]
})

# Convertir las fechas a datetime en el DataFrame
df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'])
df['fecha_fin'] = pd.to_datetime(df['fecha_fin'])

# Definir F_EMISION y F_ENTREGA
f_emision = datetime(2024, 6, 28)
f_entrega = datetime(2024, 8, 25)

# Título de la aplicación
st.title("Gráfico de Gantt - Proceso por Pedido")

# Llamar a la función para crear el gráfico
create_gantt(df, f_emision, f_entrega)
