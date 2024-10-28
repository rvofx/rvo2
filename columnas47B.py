import streamlit as st
import pandas as pd
import io
import numpy as np

st.set_page_config(layout="wide")

# Función para descargar el dataframe filtrado como archivo Excel
def descargar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Título de la aplicación
st.title("Aplicación para selección de columnas, Cuadro 47B")
# Slider para el porcentaje de programación
porcentaje_prog = st.slider("Porcentaje de programación", min_value=0.0, max_value=50.0, value=3.0, step=0.1)

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
     # Excluir las columnas ya seleccionadas en el primer grupo
    #columnas_disponibles_grupo2 = [col for col in columnas if col not in columnas_tallas_grupo1]
    #columnas_tallas_grupo2 = st.multiselect("Selecciona el segundo grupo de columnas de tallas para generar nuevas columnas Talla2 y Data2", columnas_disponibles_grupo2)
    
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

        # Calcular la cantidad programada con el porcentaje adicional
        df_repetido['cant_prog'] = df_repetido['Cantidad'].apply(lambda x: int(np.ceil(x * (1 + porcentaje_prog/100))))
         
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
                    #datas2.append(row[talla2])
                    #datas2.append(str(row[talla2]))
                    datas2.append(str(int(row[talla2])) if pd.notna(row[talla2]) else '')
            
            # Crear nuevas columnas en el dataframe original
            df_repetido["Talla2"] = tallas2
            #df_repetido["Cantidad2"] = cantidades2
            df_repetido["data2"] = datas2

        # Mostrar el dataframe con las filas repetidas y las nuevas columnas
        st.write("Tabla final:")
        st.dataframe(df_repetido)
        
        # Botón para descargar el archivo filtrado con las repeticiones y nuevas columnas
        st.download_button(
            label="Descargar Excel",
            data=descargar_excel(df_repetido),
            file_name="archivo_repetido_y_nuevas_columnas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
