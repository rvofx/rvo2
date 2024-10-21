import streamlit as st
import pandas as pd
import io

# Función para descargar el dataframe filtrado como archivo Excel
def descargar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Título de la aplicación
st.title("Selección de columnas en Excel")

# Subir el archivo Excel
archivo_excel = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

# Si el archivo ha sido subido
if archivo_excel:
    # Leer el archivo Excel
    df = pd.read_excel(archivo_excel)
    
    # Mostrar las primeras filas del archivo
    st.write("Vista previa de los datos:")
    st.dataframe(df.head())
    
    # Lista de columnas disponibles
    columnas = df.columns.tolist()
    
    # Permitir que el usuario seleccione las columnas que quiere
    columnas_seleccionadas = st.multiselect("Selecciona las columnas que deseas", columnas)
    
    # Filtrar el dataframe basado en las columnas seleccionadas
    if columnas_seleccionadas:
        df_filtrado = df[columnas_seleccionadas]

        # Si hay una columna de tallas (por ejemplo, las columnas XS, S, M, etc.)
        # debemos expandir las filas para cada talla.
        columnas_tallas = [col for col in df.columns if col in ["XS", "S", "M", "L", "XL", "2X", "3X", "4XL"]]
        
        if columnas_tallas:
            filas_expandida = []
            for _, row in df_filtrado.iterrows():
                for talla in columnas_tallas:
                    # Si el valor de la talla no es NaN o vacío, crea una nueva fila
                    if not pd.isna(row[talla]):
                        nueva_fila = row.copy()
                        nueva_fila["Talla"] = talla
                        nueva_fila["Cantidad"] = row[talla]
                        filas_expandida.append(nueva_fila)
            
            # Convertir las filas expandidas a un dataframe
            df_filtrado = pd.DataFrame(filas_expandida)

        st.write("Datos filtrados:")
        st.dataframe(df_filtrado)
        
        # Botón para descargar el archivo filtrado
        st.download_button(
            label="Descargar Excel filtrado",
            data=descargar_excel(df_filtrado),
            file_name="archivo_filtrado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
