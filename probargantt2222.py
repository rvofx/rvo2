# Función para crear el gráfico de Gantt
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import streamlit as st

def create_gantt(df, f_emision, f_entrega):
    # Crear el gráfico de Gantt
    fig = go.Figure()

    # Iterar sobre los procesos y agregar trazas al gráfico
    for i, row in df.iterrows():
        fecha_inicio = row['fecha_inicio']
        fecha_fin = row['fecha_fin']

        # Asegurarnos de que la fecha de inicio sea menor a la de fin
        if fecha_inicio >= fecha_fin:
            st.write(f"Error: La fecha de inicio ({fecha_inicio}) es mayor o igual a la fecha de fin ({fecha_fin}) para el proceso {row['proceso']}")
            continue

        # Calcular la duración del proceso en días
        duracion = (fecha_fin - fecha_inicio).days

        # Impresiones intermedias para verificar los valores
        st.write(f"Proceso: {row['proceso']}")
        st.write(f"Fecha Inicio: {fecha_inicio}")
        st.write(f"Fecha Fin: {fecha_fin}")
        st.write(f"Duración calculada: {duracion} días")

        # Usar add_shape para agregar las barras manualmente entre las fechas de inicio y fin
        fig.add_shape(
            type="rect",  # Crear una barra rectangular
            x0=fecha_inicio, x1=fecha_fin,  # Usar la fecha de inicio y fin como límites de la barra
            y0=i-0.4, y1=i+0.4,  # Controlar la altura de la barra en el eje Y
            line=dict(color='skyblue'),  # Color de la barra
            fillcolor='skyblue',
        )

    # Trazar la fecha de emisión y la fecha de entrega usando add_shape()
    fig.add_shape(
        type="line",
        x0=f_emision, x1=f_emision,  # Usar la fecha de emisión para las posiciones x0 y x1
        y0=-0.5, y1=len(df)-0.5,  # Ajustar el rango vertical de la línea
        line=dict(color="green", width=2, dash="dash"),
        name="F. Emisión"
    )
    fig.add_shape(
        type="line",
        x0=f_entrega, x1=f_entrega,  # Usar la fecha de entrega para las posiciones x0 y x1
        y0=-0.5, y1=len(df)-0.5,  # Ajustar el rango vertical de la línea
        line=dict(color="red", width=2, dash="dash"),
        name="F. Entrega"
    )

    # Trazar el día actual
    dia_actual = datetime.today().date()
    fig.add_shape(
        type="line",
        x0=dia_actual, x1=dia_actual,  # Usar el día actual
        y0=-0.5, y1=len(df)-0.5,
        line=dict(color="blue", width=2, dash="dash"),
        name="Hoy"
    )

    # Configuración del eje X (fechas) y eje Y (procesos)
    fig.update_layout(
        title="Gráfico de Gantt - Procesos de Producción",
        xaxis_title="Fecha",
        yaxis_title="Proceso",
        xaxis=dict(type='date', tickformat='%d-%m-%Y', dtick="D1"),  # Mostrar un tick por día
        yaxis=dict(
            tickvals=list(range(len(df))),  # Alinear cada proceso con su índice
            ticktext=df['proceso'],  # Mostrar nombres de los procesos
        ),
        bargap=0.3,
        height=400 + 100 * len(df)  # Ajustar el tamaño en función de la cantidad de procesos
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
df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'])
df['fecha_fin'] = pd.to_datetime(df['fecha_fin'])

# Definir F_EMISION y F_ENTREGA
f_emision = datetime(2024, 6, 28)  # Ejemplo de fecha de emisión
f_entrega = datetime(2024, 8, 25)  # Ejemplo de fecha de entrega

# Título de la aplicación
st.title("Gráfico de Gantt - Proceso por Pedido")

# Llamar a la función para crear el gráfico
create_gantt(df, f_emision, f_entrega)
