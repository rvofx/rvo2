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
st.title("Aplicación para selección de columnas")

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
    columnas_tallas_grupo1 = st.multiselect("Selecciona el primer grupo de columnas de tallas para calcular repeticiones", columnas)
    
    # Segunda selección de tallas (generará nuevas columnas Talla2 y Cantidad2)
    #columnas_tallas_grupo2 = st.multiselect("Selecciona el segundo grupo de columnas de tallas para generar nuevas columnas Talla2 y Cantidad2", columnas)
    columnas_tallas_grupo2 = st.multiselect("Selecciona el segundo grupo de columnas de tallas para generar nuevas columnas Talla2 y Data2", columnas)

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
        
        # Si se selecciona un segundo grupo de tallas, añadir nuevas columnas Talla2 y Cantidad2
        if columnas_tallas_grupo2:
            # Crear listas para almacenar los valores de Talla2 y Cantidad2 para cada fila
            tallas2 = []
            #cantidades2 = []
            datas2 = []
            
            for _, row in df.iterrows():
                for talla2 in columnas_tallas_grupo2:
                    # Añadir las tallas y cantidades correspondientes del segundo grupo
                    tallas2.append(talla2)
                    #cantidades2.append(row[talla2])
                    datas2.append(row[talla2])
            
            # Crear nuevas columnas en el dataframe original
            df_repetido["Talla2"] = tallas2
            #df_repetido["Cantidad2"] = cantidades2
            df_repetido["data2"] = datas2

        # Mostrar el dataframe con las filas repetidas y las nuevas columnas
        st.write("Datos repetidos con nuevas columnas Talla2 y data2:")
        st.dataframe(df_repetido)
        
        # Botón para descargar el archivo filtrado con las repeticiones y nuevas columnas
        st.download_button(
            label="Descargar Excel con filas repetidas y nuevas columnas",
            data=descargar_excel(df_repetido),
            file_name="archivo_repetido_y_nuevas_columnas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
