import streamlit as st
import pyodbc
import pandas as pd

# Conexión a la base de datos usando secrets
def get_db_connection():
    connection = pyodbc.connect(
        f"DRIVER={st.secrets['database']['driver']};"
        f"SERVER={st.secrets['database']['server']};"
        f"DATABASE={st.secrets['database']['database']};"
        f"UID={st.secrets['database']['username']};"
        f"PWD={st.secrets['database']['password']}"
    )
    return connection

# Función para ejecutar la consulta y obtener los resultados
def load_data():
    query = """
    SELECT [IdthTipoCambio] AS ID,
           [IdmaeAño] AS AÑO,
           [IdmaePeriodoContable] as P_CON,
           [IdmaeMoneda] AS MON,
           [dtFecha],
           [dCompra],
           [dVenta],
           [IdSistemaUsuarioCreacion] AS USU,
           [FechaCreacion],
           [IdSistemaUsuarioModificacion] AS U_MO,
           [FechaUltimaModificacion] AS F_MOD
    FROM [GarmentData].[dbo].[thTipoCambio]
    WHERE FechaCreacion > '2024-10-01'
    """
    
    conn = get_db_connection()
    data = pd.read_sql(query, conn)
    conn.close()
    
    return data

# Interfaz de la aplicación
st.title('Consulta de Tipos de Cambio')

# Botón para cargar datos
if st.button('Cargar datos'):
    df = load_data()
    
    # Mostrar los resultados en una tabla
    st.write('Resultados de la consulta:')
    st.dataframe(df)
