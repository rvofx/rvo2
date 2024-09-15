import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
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
    
    return pd.DataFrame(procesos), fecha_pedido, fecha_entrega, fecha_actual

# Crear gráfico de Gantt
def crear_gantt(df, fecha_pedido, fecha_entrega, fecha_actual):
    fig = ff.create_gantt(df, x_start="Inicio Programado", x_end="Fin Programado", y="Tarea",
                          title="Gráfico de Gantt del Pedido",
                          showgrid_x=True, showgrid_y=True)

    # Agregar barras de progreso
    for i, row in df.iterrows():
        fig.add_shape(type="rect",
                      x0=row["Inicio Programado"], y0=i-0.2,
                      x1=row["Inicio Programado"] + (row["Fin Programado"] - row["Inicio Programado"]) * row["Avance"] / 100,
                      y1=i+0.2,
                      fillcolor="green", opacity=0.5, line=dict(width=0))

    # Agregar marcadores para fechas reales
    for i, row in df.iterrows():
        if row["Inicio Real"]:
            fig.add_trace(dict(x=[row["Inicio Real"]], y=[row["Tarea"]], mode="markers",
                               marker=dict(symbol="triangle-up", size=10, color="blue"),
                               showlegend=False))
        if row["Fin Real"]:
            fig.add_trace(dict(x=[row["Fin Real"]], y=[row["Tarea"]], mode="markers",
                               marker=dict(symbol="triangle-down", size=10, color="red"),
                               showlegend=False))

    # Agregar líneas verticales para fechas clave
    fig.add_vline(x=fecha_pedido, line_dash="dash", line_color="purple", annotation_text="Fecha de Pedido")
    fig.add_vline(x=fecha_entrega, line_dash="dash", line_color="orange", annotation_text="Fecha de Entrega Programada")
    fig.add_vline(x=fecha_actual, line_dash="solid", line_color="green", annotation_text="Fecha Actual")

    fig.update_layout(height=400, width=800)
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
