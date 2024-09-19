import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Crear el DataFrame original (Ejemplo de un solo pedido)
data = {
    'PEDIDO': [1198],
    'IdDocumento': [441563],
    'F_EMISION': ['6/20/2024'],
    'F_ENTREGA': ['9/6/2024'],
    'DIAS': [78],
    'CLIENTE': ['THE BEAUFORT BO'],
    'KG_ARMP': ['114%'],
    'KG_TENIDP': ['114%'],
    'KG_TELAPROBP': ['102%'],
    'CORTADOP': ['113%'],
    'COSIDOP': ['19%'],
    'FMINARM': ['6/25/2024'],
    'FMAXARM': ['7/5/2024'],
    'FMINTENID': ['6/28/2024'],
    'FMAXTENID': ['7/20/2024'],
    'FMINTELAPROB': ['7/12/2024'],
    'FMAXTELAPROB': ['9/6/2024'],
    'FMINCORTE': ['7/17/2024'],
    'FMAXCORTE': ['9/9/2024'],
    'FMINCOSIDO': ['8/8/2024'],
    'FMAXCOSIDO': ['9/12/2024']
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
    x=df_gant['Finish Real'],
    y=df-gantt['Task'],
    mode='markers',
    marker=dict(color='red', size=10),
    name='Finish Real'
))

# Fechas de colocación y entrega
fecha_colocacion = '2024-08-15'
fecha_entrega = '2024-10-31'

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

# Agregar anotaciones para las fechas de colocación, entrega y actual
fig.add_annotation(
    x=fecha_colocacion, y=len(df) + 0.5,
    text="Emisión: ", #+ fecha_colocacion,
    showarrow=False,
    xshift=10,
    font=dict(color="green", size=12)
)

fig.add_annotation(
    x=fecha_entrega, y=len(df) + 0.5,
    text="Entrega: ", #+ fecha_entrega,
    showarrow=False,
    xshift=10,
    font=dict(color="red", size=12)
)

#fig.add_annotation(
    #x=fecha_actual, y=len(df) + 0.5,
    #text="Fecha Actual: " + fecha_actual,
    #showarrow=False,
    #xshift=10,
    #font=dict(color="black", size=12)
#)

# Mostrar la aplicación Streamlit
st.title("Avance de Procesos de Pedido")
st.write("Este es un gráfico de Gantt que muestra el avance de los procesos de los pedidos.")
st.plotly_chart(fig)
