# Función para crear el gráfico de Gantt
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import streamlit as st

def create_gantt(df):
    # Crear el gráfico de Gantt
    fig = go.Figure()

    # Iterar sobre los procesos y agregar trazas al gráfico
    for i, row in df.iterrows():
        # Obtener las fechas de inicio y fin, asegurando que solo se considere la fecha (sin tiempo)
        fecha_inicio = row['fecha_inicio'].date()  # Convertir a solo fecha
        fecha_fin = row['fecha_fin'].date()  # Convertir a solo fecha

        # Asegurarnos de que la fecha de inicio sea menor a la de fin
        if fecha_inicio >= fecha_fin:
            st.write(f"Error: La fecha de inicio ({fecha_inicio}) es mayor o igual a la fecha de fin ({fecha_fin}) para el proceso {row['proceso']}")
            continue

        # Imprimir para verificar valores de las fechas
        st.write(f"Proceso: {row['proceso']}, Fecha Inicio: {fecha_inicio}, Fecha Fin: {fecha_fin}")

        # Calcular la duración del proceso
        duracion = (fecha_fin - fecha_inicio).days
        st.write(f"Duración calculada: {duracion} días")

        # Agregar la barra de Gantt para cada proceso
        fig.add_trace(go.Bar(
            x=[duracion],  # Usar la duración como la longitud de la barra en el eje X
            y=[row['proceso']],  # Proceso
            base=[fecha_inicio],  # La barra empieza en la fecha de inicio
            orientation='h',  # Horizontal
            text=f"Progreso: {row['progreso']}%",  # Mostrar el progreso en el tooltip
            hoverinfo='text',
            width=0.4,  # Anchura de la barra
            marker=dict(color='skyblue'),
            showlegend=False
        ))

    # Configuración del eje X (fechas) y eje Y (procesos)
    fig.update_layout(
        title="Gráfico de Gantt - Procesos de Producción",
        xaxis_title="Fecha",
        yaxis_title="Proceso",
        xaxis=dict(type='date', tickformat='%d-%m-%Y', dtick="D2"),  # Ajuste para que muestre un tick cada dos días
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
#df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.date
#df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.date

# Título de la aplicación
st.title("Gráfico de Gantt - Proceso por Pedido")

# Llamar a la función para crear el gráfico
create_gantt(df)

