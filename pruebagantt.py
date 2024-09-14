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
        date_min = row['Fecha inicio']
        date_max = row['Fecha fin']

        # Agregar la barra de Gantt para cada proceso (definir fecha inicio y fin)
        fig.add_trace(go.Bar(
            x=[date_min, date_max],  # Rango de fechas de inicio a fin
            y=[row['Proceso'], row['Proceso']],  # El mismo proceso en ambas posiciones
            orientation='h',  # Horizontal
            text=f"Progreso: {row['Progreso']}%",  # Mostrar el progreso en el tooltip
            hoverinfo='text',
            marker=dict(color='skyblue'),
            showlegend=False
        ))

    # Agregar las líneas verticales para F_EMISION, F_ENTREGA y la fecha actual
    current_date = datetime.now().date()
    important_dates = {
        'F_EMISION': pd.to_datetime('2024-07-01').date(),
        'F_ENTREGA': pd.to_datetime('2024-09-15').date(),
        'Hoy': current_date
    }

    for label, date in important_dates.items():
        fig.add_shape(
            type="line",
            x0=date,
            x1=date,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color='red' if label == 'Hoy' else 'green', width=2),
        )
        fig.add_annotation(
            x=date,
            y=1,
            yref="paper",
            text=label,
            showarrow=False,
            yshift=10
        )

    # Configuración del eje X (fechas) y eje Y (procesos)
    fig.update_layout(
        title="Gráfico de Gantt - Procesos de Producción",
        xaxis_title="Fecha",
        yaxis_title="Proceso",
        xaxis=dict(type='date', tickformat='%d-%m-%Y', dtick="D1"),
        yaxis=dict(categoryorder="array", categoryarray=df['Proceso']),
        bargap=0.3
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

# Ejemplo de datos ficticios
df = pd.DataFrame({
    'Proceso': ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO'],
    'Fecha inicio': ['2024-07-10', '2024-07-19', '2024-08-15', '2024-08-20', '2024-09-02'],
    'Fecha fin': ['2024-07-12', '2024-07-24', '2024-08-21', '2024-08-23', '2024-09-12'],
    'Progreso': [116, 116, 101, 105, 103]
})

# Convertir las fechas a datetime en el DataFrame
df['Fecha inicio'] = pd.to_datetime(df['Fecha inicio'])
df['Fecha fin'] = pd.to_datetime(df['Fecha fin'])

# Título de la aplicación
st.title("Gráfico de Gantt - Proceso por Pedido")

# Llamar a la función para crear el gráfico
create_gantt(df)

