import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import streamlit as st

def create_gantt(df, f_emision, f_entrega):
    # Crear el gráfico de Gantt
    fig = go.Figure()

    # Crear la línea de tiempo para cada proceso
    for i, row in df.iterrows():
        fecha_inicio = row['fecha_inicio']
        fecha_fin = row['fecha_fin']
        if fecha_inicio >= fecha_fin:
            st.write(f"Error: La fecha de inicio ({fecha_inicio}) es mayor o igual a la fecha de fin ({fecha_fin}) para el proceso {row['proceso']}")
            continue
        duracion = (fecha_fin - fecha_inicio).days
        st.write(f"Proceso: {row['proceso']}, Fecha Inicio: {fecha_inicio}, Fecha Fin: {fecha_fin}, Duración: {duracion} días")

        # Usar timeline en lugar de add_trace
        fig.add_trace(go.Timeline(
            x0=fecha_inicio,
            x1=fecha_fin,
            y=row['proceso'],
            text=f"Progreso: {row['progreso']}%",
            hoverinfo='text',
            mode='lines',
            line=dict(color='skyblue', width=20),
            name=row['proceso']
        ))

    # Trazar la fecha de emisión, fecha de entrega y día actual
    lineas = [
        ("F. Emisión", f_emision, "green"),
        ("F. Entrega", f_entrega, "red"),
        ("Hoy", datetime.today().date(), "blue")
    ]

    for nombre, fecha, color in lineas:
        fig.add_shape(
            type="line",
            x0=fecha, x1=fecha,
            y0=-0.5, y1=len(df)-0.5,
            line=dict(color=color, width=2, dash="dash"),
            name=nombre
        )
        fig.add_annotation(
            x=fecha,
            y=len(df),
            text=nombre,
            showarrow=False,
            yshift=10,
            font=dict(color=color)
        )

    # Configuración del diseño
    fig.update_layout(
        title="Gráfico de Gantt - Procesos de Producción",
        xaxis_title="Fecha",
        yaxis_title="Proceso",
        xaxis=dict(type='date', tickformat='%d-%m-%Y', dtick="D1"),
        yaxis=dict(categoryorder="array", categoryarray=df['proceso']),
        height=600,
        showlegend=False
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

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
