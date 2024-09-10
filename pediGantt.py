import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configurar la conexión a la base de datos utilizando las credenciales almacenadas en secrets
def connect_db():
    connection = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return connection

# Función para ejecutar la consulta SQL
def run_query(pedido):
    conn = connect_db()
    query = """..."""  # El código SQL que ya tienes va aquí
    df = pd.read_sql(query, conn, params=(pedido,))
    conn.close()
    return df

# Función para generar el gráfico de Gantt
def create_gantt_chart(df):
    # Definir los procesos y las fechas asociadas
    procesos = ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO']
    fmin = ['FMINARM', 'FMINTENID', 'FMINTELAPROB', 'FMINCORTE', 'FMINCOSIDO']
    fmax = ['FMAXARM', 'FMAXTENID', 'FMAXTELAPROB', 'FMAXCORTE', 'FMAXCOSIDO']
    porcentaje = ['KG_ARMP', 'KG_TENIDP', 'KG_TELAPROBP', 'CORTADOP', 'COSIDOP']

    # Crear el dataframe para el gráfico de Gantt
    gantt_data = []
    for i in range(len(procesos)):
        gantt_data.append({
            'Proceso': procesos[i],
            'Fecha Inicio': df[fmin[i]].values[0],
            'Fecha Fin': df[fmax[i]].values[0],
            'Porcentaje': df[porcentaje[i]].values[0]
        })

    gantt_df = pd.DataFrame(gantt_data)

    # Crear el gráfico de Gantt con Plotly Express
    fig = px.timeline(
        gantt_df,
        x_start='Fecha Inicio',
        x_end='Fecha Fin',
        y='Proceso',
        color='Porcentaje',
        hover_name='Proceso',
        title='Diagrama de Gantt del Pedido'
    )

    # Añadir las líneas verticales para F_EMISION, F_ENTREGA y la fecha actual
    f_emision = df['F_EMISION'].values[0]
    f_entrega = df['F_ENTREGA'].values[0]
    fecha_actual = datetime.today()

    fig.add_vline(x=f_emision, line_width=2, line_dash="dash", line_color="blue", annotation_text="F_EMISION", annotation_position="top")
    fig.add_vline(x=f_entrega, line_width=2, line_dash="dash", line_color="green", annotation_text="F_ENTREGA", annotation_position="top")
    fig.add_vline(x=fecha_actual, line_width=2, line_dash="dash", line_color="red", annotation_text="Hoy", annotation_position="top")

    # Añadir líneas verticales tenues cada dos días
    fig.update_xaxes(
        tickformat="%d-%m-%Y",
        dtick="2D",
        ticklabelmode="period"
    )

    fig.update_layout(xaxis_title="Fecha", yaxis_title="Procesos")
    return fig

# Interfaz de usuario de Streamlit
st.title("Data Pedido")

# Campo de entrada para ingresar el número de pedido
pedido = st.text_input("Ingresa el número de pedido")

# Si el botón se presiona y hay un número de pedido ingresado, se ejecuta la consulta
if st.button("Ejecutar Consulta"):
    if pedido:
        try:
            # Ejecutar la consulta y mostrar el resultado filtrado por pedido
            result = run_query(pedido)
            st.dataframe(result)  # Mostrar los resultados en una tabla

            # Crear y mostrar el gráfico de Gantt
            fig = create_gantt_chart(result)
            st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Error al ejecutar la consulta: {e}")
    else:
        st.warning("Por favor ingresa un número de pedido.")
