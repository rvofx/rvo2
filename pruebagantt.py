# Función para crear el gráfico de Gantt
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import streamlit as st

def create_gantt(df, f_emision, f_entrega):
    # Crear el gráfico de Gantt
    fig = go.Figure()

    # Iterar sobre los procesos y agregar trazas al gráfico
    for i, row in df.iterrows():
        fecha_inicio = row['fecha_inicio']
        fecha_fin = row['fecha_fin']

        if fecha_inicio >= fecha_fin:
            st.write(f"Error: La fecha de inicio ({fecha_inicio}) es mayor o igual a la fecha de fin ({fecha_fin}) para el proceso {row['proceso']}")
            continue

        duracion = (fecha_fin - fecha_inicio).days
        st.write(f"Proceso: {row['proceso']}, Fecha Inicio: {fecha_inicio}, Fecha Fin: {fecha_fin}, Duración: {duracion} días")

        # Agregar la barra de Gantt para cada proceso
        fig.add_trace(go.Bar(
            x=[fecha_inicio, fecha_fin],  # Fecha de inicio y fin
            y=[row['proceso']],  # Proceso
            orientation='h',
            text=f"Progreso: {row['progreso']}%",
            hoverinfo='text',
            width=0.4,
            marker=dict(color='skyblue'),
            showlegend=False
        ))

    # Trazar la fecha de emisión y la fecha de entrega
    fig.add_vline(x=f_emision, line_width=2, line_dash="dash", line_color="green", annotation_text="F. Emisión", annotation_position="top right")
    fig.add_vline(x=f_entrega, line_width=2, line_dash="dash", line_color="red", annotation_text="F. Entrega", annotation_position="top right")

    # Trazar el día actual
    dia_actual = datetime.today().date()
    fig.add_vline(x=dia_actual, line_width=2, line_dash="dash", line_color="blue", annotation_text="Hoy", annotation_position="top left")

    # Configuración del eje X (fechas) y eje Y (procesos)
    fig.update_layout(
        title="Gráfico de Gantt - Procesos de Producción",
        xaxis_title="Fecha",
        yaxis_title="Proceso",
        xaxis=dict(type='date', tickformat='%d-%m-%Y', dtick="D1"),  # Mostrar un tick por día
        yaxis=dict(categoryorder="array", categoryarray=df['proceso']),
        bargap=0.3
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

# Datos de prueba ajustados
df = pd.DataFrame({
    'proceso': ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO'],
    'fecha_inicio': ['2024-07-01', '2024-07-10', '2024-07-20', '2024-08-01', '2024-08-15'],
    'fecha_fin': ['2024-07-05', '2024-07-15', '2024-07-25', '2024-08-05', '2024-08-20'],
    'progreso': [100, 80, 60, 90, 75]
})

# Convertir las fechas a datetime en el DataFrame
df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.date
df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.date

# Definir F_EMISION y F_ENTREGA
f_emision = datetime(2024, 6, 28).date()  # Ejemplo de fecha de emisión
f_entrega = datetime(2024, 8, 25).date()  # Ejemplo de fecha de entrega

# Título de la aplicación
st.title("Gráfico de Gantt - Proceso por Pedido")

# Llamar a la función para crear el gráfico
create_gantt(df, f_emision, f_entrega)
