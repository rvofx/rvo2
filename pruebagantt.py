import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Subida del archivo Excel
uploaded_file = st.file_uploader("Carga el archivo Excel del pedido", type="xlsx")

if uploaded_file:
    # Lectura del Excel
    df = pd.read_excel(uploaded_file)

    # Extracción de columnas importantes
    f_emision = pd.to_datetime(df['F_EMISION'][0])
    f_entrega = pd.to_datetime(df['F_ENTREGA'][0])
    fecha_actual = datetime.now()

    # Procesos y sus fechas mínimas y máximas
    procesos = ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO']
    fechas_min = [df['FMINARM'][0], df['FMINTENID'][0], df['FMINTELAPROB'][0], df['FMINCORTE'][0], df['FMINCOSIDO'][0]]
    fechas_max = [df['FMAXARM'][0], df['FMAXTENID'][0], df['FMAXTELAPROB'][0], df['FMAXCORTE'][0], df['FMAXCOSIDO'][0]]
    
    # Porcentajes de avance
    porcentajes = [df['KG_ARMP'][0], df['KG_TENIDP'][0], df['KG_TELAPROBP'][0], df['CORTADOP'][0], df['COSIDOP'][0]]

    # Crear figura de Gantt
    fig = go.Figure()

    for i, proceso in enumerate(procesos):
        fig.add_trace(go.Bar(
            x=[(pd.to_datetime(fechas_max[i]) - pd.to_datetime(fechas_min[i])).days],
            y=[proceso],
            base=pd.to_datetime(fechas_min[i]),
            orientation='h',
            text=f"{porcentajes[i]} de avance",
            marker=dict(color='skyblue')
        ))

    # Añadir líneas verticales para F_EMISION, F_ENTREGA, y fecha actual
    for date, label in zip([f_emision, f_entrega, fecha_actual], ['F. Emisión', 'F. Entrega', 'Fecha Actual']):
        --fig.add_vline(x=date, line=dict(color="red"), annotation_text=label, annotation_position="top")
        fig.add_vline(x=date.strftime('%Y-%m-%d'), line_color="red", annotation_text=label, annotation_position="top")


    # Líneas verticales cada dos días
    days_range = pd.date_range(f_emision, f_entrega, freq='2D')
    for day in days_range:
        fig.add_vline(x=day, line=dict(color="gray", dash='dash'))

    # Configurar eje X para mostrar los días
    fig.update_layout(
        title="Diagrama de Gantt de Procesos",
        xaxis_title="Fecha",
        yaxis_title="Proceso",
        xaxis=dict(type='date')
    )

    st.plotly_chart(fig)
