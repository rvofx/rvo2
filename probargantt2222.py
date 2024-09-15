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
    
    return df, fecha_pedido.strftime('%Y-%m-%d'), fecha_entrega.strftime('%Y-%m-%d'), fecha_actual.strftime('%Y-%m-%d')

# Crear gráfico de Gantt
def crear_gantt(df, fecha_pedido, fecha_entrega, fecha_actual):
    fig = go.Figure()

    for i, task in df.iterrows():
        # Barra de fecha programada
        fig.add_trace(go.Bar(
            x=[pd.Timestamp(task['Fin Programado']) - pd.Timestamp(task['Inicio Programado'])],
            y=[task['Tarea']],
            orientation='h',
            base=task['Inicio Programado'],
            marker_color='lightblue',
            name=task['Tarea']
        ))

        # Barra de progreso
        if task['Avance'] > 0:
            progress_duration = (pd.Timestamp(task['Fin Programado']) - pd.Timestamp(task['Inicio Programado'])) * task['Avance'] / 100
            fig.add_trace(go.Bar(
                x=[progress_duration],
                y=[task['Tarea']],
                orientation='h',
                base=task['Inicio Programado'],
                marker_color='green',
                opacity=0.5,
                name=f"{task['Tarea']} (Progreso)"
            ))

        # Marcadores para fechas reales
        if task['Inicio Real']:
            fig.add_trace(go.Scatter(
                x=[task['Inicio Real']],
                y=[task['Tarea']],
                mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='blue'),
                name=f"{task['Tarea']} (Inicio Real)"
            ))
        if task['Fin Real']:
            fig.add_trace(go.Scatter(
                x=[task['Fin Real']],
                y=[task['Tarea']],
                mode='markers',
                marker=dict(symbol='triangle-down', size=10, color='red'),
                name=f"{task['Tarea']} (Fin Real)"
            ))

    # Líneas verticales para fechas clave
    fig.add_vline(x=fecha_pedido, line_dash="dash", line_color="purple", annotation_text="Fecha de Pedido")
    fig.add_vline(x=fecha_entrega, line_dash="dash", line_color="orange", annotation_text="Fecha de Entrega Programada")
    fig.add_vline(x=fecha_actual, line_dash="solid", line_color="green", annotation_text="Fecha Actual")

    fig.update_layout(
        title="Gráfico de Gantt del Pedido",
        xaxis_title="Fecha",
        yaxis_title="Tarea",
        height=400,
        width=800,
        showlegend=False
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
