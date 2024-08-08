import streamlit as st
import pandas as pd

def transform_table(df):
    # Inicializar una lista para almacenar los datos transformados
    transformed_data = []

    # Recorrer las filas del DataFrame original
    for _, row in df.iterrows():
        grafico = row['GRAFICO']
        qty = row['QTY']
        qty_x = row['QTY']  # Suponiendo que QTY es equivalente a TX en la Tabla 2
        
        # Para cada columna de color, dividir las celdas por ' / ' y contar las ocurrencias
        for color_column in ['ROJO', 'VERDE', 'AZUL']:
            color_values = str(row[color_column]).split(' / ')
            for color in color_values:
                if color:  # Verificar que el valor no esté vacío
                    count = color_values.count(color)
                    transformed_data.append([grafico, qty, color, row['TDX'] if color in row['ROJO'] else row['TMX'], count, color_column])

    # Crear un DataFrame a partir de la lista de datos transformados
    transformed_df = pd.DataFrame(transformed_data, columns=['GRAFICO', 'QTY', 'X', 'TX', 'Q', 'COLOR'])
    return transformed_df

# Crear la aplicación Streamlit
def main():
    st.title('Transformación de Datos de Excel')

    # Subir archivo Excel
    uploaded_file = st.file_uploader("Elige un archivo Excel", type=["xlsx"])
    
    if uploaded_file:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file)

        # Asegurarse de que la estructura del DataFrame sea la esperada
        required_columns = ['GRAFICO', 'QTY', 'TDX', 'TMX', 'ROJO', 'VERDE', 'AZUL']
        if all(col in df.columns for col in required_columns):
            # Transformar la tabla
            transformed_df = transform_table(df)

            # Mostrar la tabla transformada
            st.write("Tabla transformada:", transformed_df)
        else:
            st.error(f"El archivo debe contener las columnas: {', '.join(required_columns)}")

if __name__ == "__main__":
    main()
