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
st.title("Aplicación para selección de columnas y repetición por tallas")

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
    
    # Primera selección: Columnas de información
    columnas_info = st.multiselect("Selecciona las columnas de información que deseas", columnas)
    
    # Filtrar el dataframe basado en las columnas seleccionadas para información
    if columnas_info:
        df_filtrado_info = df[columnas_info]
        
        # Mostrar el dataframe filtrado
        st.write("Datos filtrados (información):")
        st.dataframe(df_filtrado_info)
    
    # Primera selección de tallas (para repetir filas)
    columnas_tallas_grupo1 = st.multiselect("Selecciona el primer grupo de columnas de tallas para calcular repeticiones", [col for col in columnas if col not in columnas_info])
    
    # Segunda selección de tallas (generará nuevas columnas Talla2 y Cantidad2)
    if columnas_tallas_grupo1:
        columnas_disponibles_grupo2 = [col for col in columnas if col not in columnas_info and col not in columnas_tallas_grupo1]
        columnas_tallas_grupo2 = st.multiselect("Selecciona el segundo grupo de columnas de tallas para generar nuevas columnas Talla2 y Cantidad2", columnas_disponibles_grupo2)
    
    # Repetir filas en función del primer grupo de tallas
    if columnas_tallas_grupo1:
        filas_repetidas = []
        for _, row in df.iterrows():
            # Repetir por el primer grupo de tallas
            for talla in columnas_tallas_grupo1:
                nueva_fila = row[columnas_info].copy()
                nueva_fila["Talla"] = talla
                nueva_fila["Cantidad"] = row[talla]  # La cantidad correspondiente a esa talla
                filas_repetidas.append(nueva_fila)
        
        # Convertir las filas expandidas en un dataframe
        df_repetido = pd.DataFrame(filas_repetidas)
        
        # Si se selecciona un segundo grupo de tallas, generar nuevas columnas
        if columnas_tallas_grupo2:
            # Crear nuevas columnas Talla2 y Cantidad2 sin modificar las filas existentes
            df_repetido["Talla2"] = None  # Nueva columna Talla2
            df_repetido["Cantidad2"] = None  # Nueva columna Cantidad2
            
            # Asignar valores a las nuevas columnas (independiente del primer grupo)
            for idx, row in df.iterrows():
                for talla in columnas_tallas_grupo2:
                    df_repetido.at[idx, "Talla2"] = talla
                    df_repetido.at[idx, "Cantidad2"] = row[talla]

        # Mostrar el dataframe con las filas repetidas y nuevas columnas
        st.write("Datos repetidos y nuevas columnas según las tallas seleccionadas:")
        st.dataframe(df_repetido)
        
        # Botón para descargar el archivo filtrado con las repeticiones y nuevas columnas
        st.download_button(
            label="Descargar Excel con filas repetidas y nuevas columnas",
            data=descargar_excel(df_repetido),
            file_name="archivo_repetido_y_nuevas_columnas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
