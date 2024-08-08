import streamlit as st
import pandas as pd

def transform_table(df):
    # Inicializar una lista para almacenar los datos transformados
    transformed_data = []

    # Obtener las columnas de colores (todas las columnas después de 'QTY' y 'TDX' / 'TMX')
    color_columns = [col for col in df.columns if col not in ['GRAFICO', 'QTY', 'TDX', 'TMX']]

    # Recorrer las filas del DataFrame original
    for _, row in df.iterrows():
        grafico = row['GRAFICO']
        qty = row['QTY']
        
        # Para cada columna de color, dividir las celdas por ' / ' y contar las ocurrencias
        for color_column in color_columns:
            color_values = str(row[color_column]).split(' / ')
            for color in color_values:
                if color:  # Verificar que el valor no esté vacío
                    count = color_values.count(color)
                    
                    # Determinar el valor de TX basado en el valor de X
                    if color_column == 'ROJO':  # Ejemplo de lógica; ajusta según el color real
                        tx_value = row['TDX']
                    else:
                        tx_value = row['TMX']
                    
                    transformed_data.append([grafico, qty, color, tx_value, count, color_column])

    # Crear un DataFrame a partir de la lista de datos transformados
    transformed_df = pd.DataFrame(transformed_data, columns=['GRAFICO', 'QTY', 'X', 'TX', 'Q', 'COLOR'])
    
    # Filtrar el DataFrame para mostrar solo filas donde 'X' sea 'TD' o 'TM' y 'TX' no sea vacío
    filtered_df = transformed_df[
        transformed_df['X'].isin(['TD', 'TM']) & 
        transformed_df['TX'].notna() &
        (transformed_df['TX'] != '')
    ]
    
    # Eliminar filas duplicadas
    unique_df = filtered_df.drop_duplicates()
    
    return unique_df

# Crear la aplicación Streamlit
def main():
    st.title('Transformación de Datos de Excel')

    # Subir archivo Excel
    uploaded_file = st.file_uploader("Elige un archivo Excel", type=["xlsx"])
    
    if uploaded_file:
        try:
            # Leer el archivo Excel
            df = pd.read_excel(uploaded_file)

            # Asegurarse de que la estructura del DataFrame sea la esperada
            required_columns = ['GRAFICO', 'QTY', 'TDX', 'TMX']
            if all(col in df.columns for col in required_columns):
                # Transformar la tabla
                transformed_df = transform_table(df)

                # Mostrar la tabla transformada
                st.write("Tabla transformada:", transformed_df)
            else:
                st.error(f"El archivo debe contener al menos las columnas: {', '.join(required_columns)}")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    main()
