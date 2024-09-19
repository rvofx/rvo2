import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Crear el DataFrame original (Ejemplo de un solo pedido)
data = {
    'PEDIDO': [1198],
    'IdDocumento': [441563],
    'F_EMISION': ['2024-06-20'],
    'F_ENTREGA': ['2024-09-06'],
    'DIAS': [78],
    'CLIENTE': ['THE BEAUFORT BO'],
    'KG_ARMP': ['114%'],
    'KG_TENIDP': ['114%'],
    'KG_TELAPROBP': ['102%'],
    'CORTADOP': ['113%'],
    'COSIDOP': ['19%'],
    'FMINARM': ['2024-06-25'],
    'FMAXARM': ['2024-07-05'],
    'FMINTENID': ['2024-06-28'],
    'FMAXTENID': ['2024-07-20'],
    'FMINTELAPROB': ['2024-07-12'],
    'FMAXTELAPROB': ['2024-09-06'],
    'FMINCORTE': ['2024-07-17'],
    'FMAXCORTE': ['2024-09-09'],
    'FMINCOSIDO': ['2024-08-08'],
    'FMAXCOSIDO': ['2024-09-12']
}

df = pd.DataFrame(data)

# Crear un nuevo DataFrame con los procesos y sus fechas correspondientes
df_gantt = pd.DataFrame({
    'Task': ['ARM', 'TENID', 'TELAPROB', 'CORTE', 'COSIDO'],
    'Start': [df['FMINARM'][0], df['FMINTENID'][0], df['FMINTELAPROB'][0], df['FMINCORTE'][0], df['FMINCOSIDO'][0]],
    'Finish': [df['FMAXARM'][0], df['FMAXTENID'][0], df['FMAXTELAPROB'][0], df['FMAXCORTE'][0], df['FMAXCOSIDO'][0]],
    'Start Real': [df['FMINARM'][0], df['FMINTENID'][0], df['FMINTELAPROB'][0], df['FMINCORTE'][0], df['FMINCOSIDO'][0]],
    'Finish Real': [df['FMAXARM'][0], df['FMAXTENID'][0], df['FMAXTELAPROB'][0], df['FMAXCORTE'][0], df['FMAXCOSIDO'][0]],
    'Resource': [df['KG_ARMP'][0], df['KG_TENIDP'][0], df['KG_TELAPROBP'][0], df['CORTADOP'][0], df['COSIDOP'][0]]
})


st.dataframe(df_gantt)

# Crear el gráfico de Gantt
fig = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Task", text="Resource")

# Ajustar el diseño del gráfico
fig.update_yaxes(autorange="reversed")  # Esto invierte el eje Y para que los pedidos estén en orden

# Agregar las barras de las fechas reales
fig.add_trace(go.Scatter(
    x=df_gantt['Start Real'],
    y=df_gantt['Task'],
    mode='markers',
    marker=dict(color='black', size=10),
    name='Start Real'
))

fig.add_trace(go.Scatter(
    x=df_gantt['Finish Real'],
    y=df_gantt['Task'],
    mode='markers',
    marker=dict(color='red', size=10),
    name='Finish Real'
))

# Fechas de colocación y entrega
fecha_colocacion = df['F_EMISION'][0]
fecha_entrega = df['F_ENTREGA'][0]

# Agregar líneas verticales para las fechas de colocación y entrega
fig.add_shape(
    type="line",
    x0=fecha_colocacion, y0=0, x1=fecha_colocacion, y1=len(df_gantt),
    line=dict(color="green", width=2, dash="dash"),
    name="Fecha Colocación"
)

fig.add_shape(
    type="line",
    x0=fecha_entrega, y0=0, x1=fecha_entrega, y1=len(df_gantt),
    line=dict(color="red", width=2, dash="dash"),
    name="Fecha Entrega"
)

# Obtener la fecha actual
fecha_actual = datetime.now().strftime('%Y-%m-%d')

# Agregar una línea vertical para la fecha actual
fig.add_shape(
    type="line",
    x0=fecha_actual, y0=0, x1=fecha_actual, y1=len(df_gantt),
    line=dict(color="black", width=2, dash="dash"),
    name="Fecha Actual"
)



# Mostrar la aplicación Streamlit
st.title("Pedido",df['PEDIDO'][0])
st.write("Este es un gráfico de Gantt que muestra el avance de los procesos de los pedidos.")
st.plotly_chart(fig)
