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
        # Obtener las fechas de inicio y fin
        fecha_inicio = row['fecha_inicio']
        fecha_fin = row['fecha_fin']

        # Imprimir para verificar valores de las fechas
        st.write(f"Proceso: {row['proceso']}, Fecha Inicio: {fecha_inicio}, Fecha Fin: {fecha_fin}")

        # Calcular la duración del proceso
        duracion = (fecha_fin - fecha_inicio).days
        st.write(f"Duración calculada: {duracion} días")

        # Agregar la barra de Gantt para cada proceso
        fig.add_trace(go.Bar(
            x=[fecha_inicio, fecha_fin],  # Fecha de inicio y fin (rango en eje x)
            y=[row['proceso'], row['proceso']],  # Proceso
            orientation='h',  # Horizontal
            text=f"Progreso: {row['progreso']}%",  # Mostrar el progreso en el tooltip
            hoverinfo='text',
            width=0.4,  # Anchura de la barra
            marker=dict(color='skyblue'),
            showlegend=False
        ))

    # Agregar las líneas verticales para F_EMISION, F_ENTREGA y la fecha actual
    fecha_actual = datetime.now().date()
    fechas_importantes = {
        'F_EMISION': pd.to_datetime('2024-07-01').date(),
        'F_ENTREGA': pd.to_datetime('2024-09-15').date(),
        'Hoy': fecha_actual
    }

    for etiqueta, fecha in fechas_importantes.items():
        st.write(f"{etiqueta}: {fecha}")  # Verificar las fechas importantes
        fig.add_shape(
            type="line",
            x0=fecha,
            x1=fecha,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color='red' if etiqueta == 'Hoy' else 'green', width=2),
        )
        fig.add_annotation(
            x=fecha,
            y=1,
            yref="paper",
            text=etiqueta,
            showarrow=False,
            yshift=10
        )

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

# Ejemplo de datos modificados
df = pd.DataFrame({
    'proceso': ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO'],
    'fecha_inicio': ['2024-07-01', '2024-07-10', '2024-07-20', '2024-08-01', '2024-08-15'],
    'fecha_fin': ['2024-07-05', '2024-07-15', '2024-07-25', '2024-08-05', '2024-08-20'],
    'progreso': [100, 80, 60, 90, 75]
})

# Convertir las fechas a datetime en el DataFrame
df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'])
df['fecha_fin'] = pd.to_datetime(df['fecha_fin'])

# Título de la aplicación
st.title("Gráfico de Gantt - Proceso por Pedido")

# Llamar a la función para crear el gráfico
create_gantt(df)
