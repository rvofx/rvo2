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
    
    # Primera selección de tallas
    columnas_tallas_grupo1 = st.multiselect("Selecciona el primer grupo de columnas de tallas para calcular repeticiones", columnas)
    
    # Segunda selección de tallas
    columnas_tallas_grupo2 = st.multiselect("Selecciona el segundo grupo de columnas de tallas para calcular repeticiones", columnas)

    # Tercera selección de tallas (opcional)
    columnas_tallas_grupo3 = st.multiselect("Selecciona el tercer grupo de columnas de tallas para calcular repeticiones (opcional)", columnas)

    # Repetir filas en función de las columnas seleccionadas para todos los grupos de tallas
    if columnas_tallas_grupo1 or columnas_tallas_grupo2 or columnas_tallas_grupo3:
        filas_repetidas = []
        for _, row in df.iterrows():
            # Repetir por el primer grupo de tallas
            for talla in columnas_tallas_grupo1:
                nueva_fila = row[columnas_info].copy()
                nueva_fila["Talla"] = talla
                nueva_fila["Cantidad"] = row[talla]  # La cantidad correspondiente a esa talla
                filas_repetidas.append(nueva_fila)
            
            # Repetir por el segundo grupo de tallas
            for talla in columnas_tallas_grupo2:
                nueva_fila = row[columnas_info].copy()
                nueva_fila["Talla"] = talla
                nueva_fila["Cantidad"] = row[talla]  # La cantidad correspondiente a esa talla
                filas_repetidas.append(nueva_fila)

            # Repetir por el tercer grupo de tallas (opcional)
            if columnas_tallas_grupo3:
                for talla in columnas_tallas_grupo3:
                    nueva_fila = row[columnas_info].copy()
                    nueva_fila["Talla"] = talla
                    nueva_fila["Cantidad"] = row[talla]  # La cantidad correspondiente a esa talla
                    filas_repetidas.append(nueva_fila)
        
        # Convertir las filas expandidas en un dataframe
        df_repetido = pd.DataFrame(filas_repetidas)
        
        # Mostrar el dataframe con las filas repetidas
        st.write("Datos repetidos según las tallas seleccionadas:")
        st.dataframe(df_repetido)
        
        # Botón para descargar el archivo filtrado con las repeticiones
        st.download_button(
            label="Descargar Excel con filas repetidas",
            data=descargar_excel(df_repetido),
            file_name="archivo_repetido_por_tallas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
