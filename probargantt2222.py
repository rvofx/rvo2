import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Generar datos de prueba
def generar_datos_prueba():
    fecha_actual = datetime.now().date()
    fecha_pedido = fecha_actual - timedelta(days=30)
    fecha_entrega = fecha_actual + timedelta(days=60)

    procesos = [
        {
            "Tarea": "Diseño",
            "Inicio Programado": fecha_pedido + timedelta(days=5),
            "Fin Programado": fecha_pedido + timedelta(days=15),
            "Inicio Real": fecha_pedido + timedelta(days=7),
            "Fin Real": fecha_pedido + timedelta(days=18),
            "Avance": 100
        },
        {
            "Tarea": "Fabricación",
            "Inicio Programado": fecha_pedido + timedelta(days=16),
            "Fin Programado": fecha_pedido + timedelta(days=45),
            "Inicio Real": fecha_pedido + timedelta(days=19),
            "Fin Real": fecha_actual + timedelta(days=5),
            "Avance": 80
        },
        {
            "Tarea": "Control de Calidad",
            "Inicio Programado": fecha_pedido + timedelta(days=46),
            "Fin Programado": fecha_pedido + timedelta(days=55),
            "Inicio Real": fecha_actual + timedelta(days=6),
            "Fin Real": fecha_actual + timedelta(days=6),
            "Avance": 0
        },
        {
            "Tarea": "Empaque y Envío",
            "Inicio Programado": fecha_pedido + timedelta(days=56),
            "Fin Programado": fecha_entrega,
            "Inicio Real": None,
            "Fin Real": None,
            "Avance": 0
        }
    ]
    
    df = pd.DataFrame(procesos)
    
    # Convertir fechas a cadenas para evitar problemas con Plotly
    date_columns = ['Inicio Programado', 'Fin Programado', 'Inicio Real', 'Fin Real']
    for col in date_columns:
        df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)
    
    return df, fecha_pedido, fecha_entrega, fecha_actual
# Crear gráfico de Gantt (con cambios)
def crear_gantt(df, fecha_pedido, fecha_entrega, fecha_actual):
    fig = go.Figure()

    # Convertir fechas a objetos datetime si son strings
    fecha_pedido = pd.to_datetime(fecha_pedido)
    fecha_entrega = pd.to_datetime(fecha_entrega)
    fecha_actual = pd.to_datetime(fecha_actual)

    for i, task in df.iterrows():
        # Barra de fecha programada
        inicio = pd.to_datetime(task['Inicio Programado'])
        fin = pd.to_datetime(task['Fin Programado'])
        fig.add_trace(go.Bar(
            x=[fin - inicio],
            y=[task['Tarea']],
            orientation='h',
            base=inicio,
            marker_color='lightblue',
            name=task['Tarea']
        ))

        # Barra de progreso
        if task['Avance'] > 0:
            progress_duration = (fin - inicio) * task['Avance'] / 100
            fig.add_trace(go.Bar(
                x=[progress_duration],
                y=[task['Tarea']],
                orientation='h',
                base=inicio,
                marker_color='green',
                opacity=0.5,
                name=f"{task['Tarea']} (Progreso)"
            ))

        # Marcadores para fechas reales
        if pd.notnull(task['Inicio Real']):
            fig.add_trace(go.Scatter(
                x=[pd.to_datetime(task['Inicio Real'])],
                y=[task['Tarea']],
                mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='blue'),
                name=f"{task['Tarea']} (Inicio Real)"
            ))
        if pd.notnull(task['Fin Real']):
            fig.add_trace(go.Scatter(
                x=[pd.to_datetime(task['Fin Real'])],
                y=[task['Tarea']],
                mode='markers',
                marker=dict(symbol='triangle-down', size=10, color='red'),
                name=f"{task['Tarea']} (Fin Real)"
            ))

    # Líneas verticales para fechas clave usando add_shape
    shapes = [
        dict(type="line", x0=fecha_pedido, x1=fecha_pedido, y0=0, y1=1, yref="paper",
             line=dict(color="purple", width=2, dash="dash")),
        dict(type="line", x0=fecha_entrega, x1=fecha_entrega, y0=0, y1=1, yref="paper",
             line=dict(color="orange", width=2, dash="dash")),
        dict(type="line", x0=fecha_actual, x1=fecha_actual, y0=0, y1=1, yref="paper",
             line=dict(color="green", width=2))
    ]

    annotations = [
        dict(x=fecha_pedido, y=1.05, yref="paper", text="Fecha de Pedido", showarrow=False),
        dict(x=fecha_entrega, y=1.05, yref="paper", text="Fecha de Entrega Programada", showarrow=False),
        dict(x=fecha_actual, y=1.05, yref="paper", text="Fecha Actual", showarrow=False)
    ]

    fig.update_layout(
        title="Gráfico de Gantt del Pedido",
        xaxis_title="Fecha",
        yaxis_title="Tarea",
        height=400,
        width=800,
        showlegend=False,
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(
            type='date',
            range=[fecha_pedido, fecha_entrega],
            tickformat='%Y-%m-%d',
            dtick='D7',  # Mostrar etiquetas cada 7 días
        )
    )

    return fig

# Aplicación Streamlit
def main():
    st.title("Seguimiento de Pedido - Gráfico de Gantt")

    df, fecha_pedido, fecha_entrega, fecha_actual = generar_datos_prueba()

    st.write("Datos del Pedido:")
    st.dataframe(df)

    fig = crear_gantt(df, fecha_pedido, fecha_entrega, fecha_actual)
    st.plotly_chart(fig)

    st.write(f"Fecha de Pedido: {fecha_pedido}")
    st.write(f"Fecha de Entrega Programada: {fecha_entrega}")
    st.write(f"Fecha Actual: {fecha_actual}")

if __name__ == "__main__":
    main()
