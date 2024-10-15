import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime, timedelta

def load_data(file):
    return pd.read_excel(file)

def create_gantt(df, pedido):
    df_pedido = df[df['PEDIDO'] == pedido]
    
    procesos = ['TELA', 'LAVADO', 'CORTE', 'COSTURA', 'ACABADO', 'AUD']
    gantt_data = []
    
    for proceso in procesos:
        start = df_pedido[f'{proceso} INICIO'].iloc[0]
        finish = df_pedido[f'{proceso} FINAL'].iloc[0]
        
        gantt_data.append(dict(Task=proceso, Start=start, Finish=finish))
    
    fig = ff.create_gantt(gantt_data, index_col='Task', show_colorbar=True, group_tasks=True)
    fig.update_layout(title=f'Diagrama de Gantt para Pedido {pedido}')
    
    # Calcular las fechas mínima y máxima
    min_date = min(task['Start'] for task in gantt_data)
    max_date = max(task['Finish'] for task in gantt_data)
    
    # Agregar líneas verticales tenues cada 2 días
    current_date = min_date
    while current_date <= max_date:
        fig.add_vline(x=current_date, line_width=1, line_dash="dash", line_color="lightgray")
        current_date += timedelta(days=2)
    
    # Agregar línea roja en el día actual
    today = datetime.now().date()
    fig.add_vline(x=today, line_width=2, line_color="red")
    
    return fig

def main():
    st.title('Generador de Diagrama de Gantt')
    
    uploaded_file = st.file_uploader("Cargar archivo Excel", type=['xlsx'])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        pedidos = df['PEDIDO'].unique()
        selected_pedido = st.selectbox('Seleccionar PEDIDO', pedidos)
        
        if st.button('Generar Diagrama de Gantt'):
            fig = create_gantt(df, selected_pedido)
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
