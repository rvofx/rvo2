import streamlit as st
import pyodbc
import pandas as pd

# Función para conectar a SQL Server usando las credenciales de secrets
def sql_connection():
    conn = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return conn


# Función para ejecutar la consulta SQL con filtros
def fetch_data(partida, color, cliente, ref):
    conn = sql_connection()
    query = """
        SELECT a.CoddocOrdenProduccion as PARTIDA, 
               F.ntDescripcion AS DESCRIP, 
               F.dCantidadProgramado AS KG_CRUDO, 
               f.dCantidadRequerido AS KG_PRODUC, 
               a.nvDocumentoReferencia as REF,  
               g.NommaeColor AS COLOR,  
               a.bCierreAprobado AS APROB_DESPACH, 
               a.bProduccionAprobado as DESPACHADO, 
               a.bcerrado AS CERRADO, 
               convert(varchar(15), h.NommaeAnexoCliente) AS Cliente
        FROM docOrdenProduccion a WITH (NOLOCK)
        INNER JOIN docOrdenProduccionItem f WITH (NOLOCK)
            ON f.IdDocumento_OrdenProduccion= a.IdDocumento_OrdenProduccion
        INNER JOIN maeColor g WITH (NOLOCK)
            ON g.IdmaeColor= a.IdmaeColor
        INNER JOIN maeAnexoCliente h WITH (NOLOCK)
            ON h.IdmaeAnexo_Cliente= a.IdmaeAnexo_Cliente
        WHERE a.IdtdDocumentoForm = 138
        AND a.CoddocOrdenProduccion LIKE ? 
        AND g.NommaeColor LIKE ?
        AND h.NommaeAnexoCliente LIKE ?
        AND a.nvDocumentoReferencia LIKE ?
    """
    params = (f'%{partida}%', f'%{color}%', f'%{cliente}%', f'%{ref}%')
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Título de la aplicación
st.title("Búsqueda de Ordenes de Producción")

# Campos de búsqueda
partida = st.text_input("PARTIDA:", "")
color = st.text_input("COLOR:", "")
cliente = st.text_input("CLIENTE:", "")
ref = st.text_input("REF:", "")

# Botón para ejecutar la búsqueda
if st.button("Buscar"):
    # Obtener resultados
    resultados = fetch_data(partida, color, cliente, ref)
    
    # Mostrar resultados
    if not resultados.empty:
        st.dataframe(resultados)
    else:
        st.write("No se encontraron resultados.")

