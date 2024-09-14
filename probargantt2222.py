# Función para crear el gráfico de Gantt
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import streamlit as st

def create_gantt():
    # Crear el gráfico de Gantt
    fig = go.Figure(df)
    processes = ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO']
    date_min_cols = ['2024-07-10', '2024-07-19', '2024-08-15', '2024-08-20', '2024-09-02']
    date_max_cols = ['2024-07-12', '2024-07-24', '2024-08-21', '2024-08-23', '2024-09-12']
    progress_cols = ['116', '116', '101', '105', '103']
    
    for i, process in enumerate(processes):
        # Asegúrate de que las fechas sean objetos datetime
        date_min = pd.to_datetime(df[date_min_cols[i]][0])
        date_max = pd.to_datetime(df[date_max_cols[i]][0])

	
        fig.add_trace(go.Bar(
            x=[date_max - date_min],
            y=[process],
            base=[date_min],
            orientation='h',
            text=f"Progreso: {df[progress_cols[i]].iloc[0]}%",
            hoverinfo='text',
            marker=dict(color='skyblue'),
            showlegend=False
        ))
    
    # Agregar las líneas verticales para F_EMISION, F_ENTREGA y fecha actual
    current_date = datetime.now().date()
    important_dates = {
        'F_EMISION': pd.to_datetime(df['2024-07-01'][0]).date(),
        'F_ENTREGA': pd.to_datetime(df['2024-09-15'][0]).date(),
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
    # Configuración del eje X (días) y eje Y (procesos)
    fig.update_layout(
        title="Gráfico de Gantt - Procesos de Producción",
        xaxis_title="Fecha",
        yaxis_title="Proceso",
        xaxis=dict(type='date', tickformat='%d', dtick="D2"),
        yaxis=dict(categoryorder="array", categoryarray=processes),
        bargap=0.3
    )
    
    st.plotly_chart(fig)

st.title("Gráfico de Gantt - Proceso por Pedido")
create_gantt()

