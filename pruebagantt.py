# Función para crear el gráfico de Gantt
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import streamlit as st

def create_gantt(df):
    # Crear el gráfico de Gantt
    fig = go.Figure()
    
    # Definir los procesos y fechas
    processes = ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO']
    date_min_cols = ['2024-07-10', '2024-07-19', '2024-08-15', '2024-08-20', '2024-09-02']
    date_max_cols = ['2024-07-12', '2024-07-24', '2024-08-21', '2024-08-23', '2024-09-12']
    progress_cols = [116, 116, 101, 105, 103]  # Progresos ficticios para el ejemplo

    # Iterar sobre los procesos y agregar trazas al gráfico
    for i, process in enumerate(processes):
        # Convertir las fechas en objetos datetime
        date_min = pd.to_datetime(date_min_cols[i])
        date_max = pd.to_datetime(date_max_cols[i])
        
        # Calcular la duración del proceso
        duration = (date_max - date_min).days
        
        # Agregar la barra de Gantt para cada proceso
        fig.add_trace(go.Bar(
            x=[duration],  # Duración en días
            y=[process],   # Proceso
            base=[date_min],  # Fecha de inicio
            orientation='h',  # Horizontal
            text=f"Progreso: {progress_cols[i]}%",  # Mostrar el progreso en el tooltip
            hoverinfo='text',
            marker=dict(color='skyblue'),
            showlegend=False
        ))
    
    # Agregar las líneas verticales para F_EMISION, F_ENTREGA y fecha actual
    current_date = datetime.now().date()
    important_dates = {
        'F_EMISION': pd.to_datetime('2024-07-01').date(),
        'F_ENTREGA': pd.to_datetime('2024-09-30').date(),
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
        xaxis=dict(type='date', tickformat='%d-%m-%Y', dtick="D2"),
        yaxis=dict(categoryorder="array", categoryarray=processes),
        bargap=0.3
    )
    
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
