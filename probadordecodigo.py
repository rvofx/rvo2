import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime, timedelta

def load_data(file):
    df = pd.read_excel(file)
    st.write("Columnas en el archivo Excel:", df.columns.tolist())
    st.write("Primeras filas del DataFrame:")
    st.write(df.head())
    return df

def create_gantt(df, pedido_column, procesos):
    df_pedido = df[df[pedido_column] == pedido]
    
    gantt_data = []
    
    for proceso in procesos:
        start = df_pedido[f'{proceso} INICIO'].iloc[0]
        finish = df_pedido[f'{proceso} FINAL'].iloc[0]
        
        gantt_data.append(dict(Task=proceso, Start=start, Finish=finish))
    
    fig = ff.create_gantt(gantt_data, index_col='Task', show_colorbar=True, group_tasks=True)
    fig.update_layout(title=f'Diagrama de Gantt para Pedido {pedido}')

    # Obtener el rango de fechas del diagrama
    all_dates = [task['Start'] for task in gantt_data] + [task['Finish'] for task in gantt_data]
    min_date = min(all_dates)
    max_date = max(all_dates)

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
        
        # Permitir al usuario seleccionar la columna de PEDIDO
        pedido_column = st.selectbox('Seleccionar columna de PEDIDO', df.columns.tolist())
        
        if pedido_column:
            pedidos = df[pedido_column].unique()
            selected_pedido = st.selectbox('Seleccionar PEDIDO', pedidos)
            
            # Permitir al usuario seleccionar los procesos
            all_columns = df.columns.tolist()
            process_columns = [col for col in all_columns if 'INICIO' in col or 'FINAL' in col]
            processes = list(set([col.split()[0] for col in process_columns]))
            selected_processes = st.multiselect('Seleccionar procesos', processes, default=processes)
            
            if st.button('Generar Diagrama de Gantt'):
                try:
                    fig = create_gantt(df, pedido_column, selected_processes)
                    st.plotly_chart(fig)
                except Exception as e:
                    st.error(f"Error al generar el diagrama: {str(e)}")
                    st.write("DataFrame para el pedido seleccionado:")
                    st.write(df[df[pedido_column] == selected_pedido])

if __name__ == "__main__":
    main()
