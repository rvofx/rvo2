import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
from datetime import datetime

# Conexión a la base de datos SQL Server
def get_data(pedido):
    conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=' + st.secrets["server"] + ';'
    'DATABASE=' + st.secrets["database"] + ';'
    'UID=' + st.secrets["username"] + ';'
    'PWD=' + st.secrets["password"]
)

    query = f"""
        select * from (
            -- Aquí va la consulta SQL proporcionada por ti
            ) WHERE PEDIDO = '{pedido}'
        """
    data = pd.read_sql(query, conn)
    conn.close()
    return data

# Función para generar el gráfico de Gantt
def create_gantt(df):
    fig = px.timeline(df, x_start='start_date', x_end='end_date', y='process',
                      color='process', hover_data=['percentage'])
    
    # Añadir las líneas verticales
    emision = df['F_EMISION'].iloc[0]
    entrega = df['F_ENTREGA'].iloc[0]
    today = datetime.now().date()
    
    fig.add_vline(x=emision, line_width=2, line_dash="dash", line_color="green", annotation_text="F. Emisión")
    fig.add_vline(x=entrega, line_width=2, line_dash="dash", line_color="red", annotation_text="F. Entrega")
    fig.add_vline(x=today, line_width=2, line_dash="dash", line_color="blue", annotation_text="Hoy")
    
    fig.update_layout(title="Diagrama de Gantt - Avance de Procesos", xaxis_title="Días", yaxis_title="Procesos")
    return fig

# Streamlit App
st.title("Diagrama de Gantt de Avance de Procesos")
pedido = st.text_input("Ingrese el número de pedido:")

if pedido:
    data = get_data(pedido)
    
    if not data.empty:
        # Procesar los datos para el gráfico de Gantt
        gantt_data = pd.DataFrame({
            'process': ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO'],
            'start_date': [data['FMINARM'].iloc[0], data['FMINTENID'].iloc[0], data['FMINTELAPROB'].iloc[0], data['FMINCORTE'].iloc[0], data['FMINCOSIDO'].iloc[0]],
            'end_date': [data['FMAXARM'].iloc[0], data['FMAXTENID'].iloc[0], data['FMAXTELAPROB'].iloc[0], data['FMAXCORTE'].iloc[0], data['FMAXCOSIDO'].iloc[0]],
            'percentage': [data['KG_ARMP'].iloc[0], data['KG_TENIDP'].iloc[0], data['KG_TELAPROBP'].iloc[0], data['CORTADOP'].iloc[0], data['COSIDOP'].iloc[0]]
        })

        fig = create_gantt(gantt_data)
        st.plotly_chart(fig)
    else:
        st.error("No se encontraron datos para el pedido ingresado.")


