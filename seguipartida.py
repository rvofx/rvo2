import streamlit as st
import pyodbc
import pandas as pd
from datetime import datetime, timedelta

# Función para conectar a SQL Server
def connect_to_db():
    conn = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return conn


# Consulta para obtener PARTIDAS sin F_TENIDO y con más de x días
def get_partidas_sin_tenido(dias):
    conn = connect_to_db()
    query = f"""
        SELECT a.CoddocOrdenProduccion AS PARTIDA, DATEDIFF(DAY, a.dtFechaEmision, GETDATE()) AS DIAS  , LEFT(f.NommaeItemInventario, 35) AS TELA, FORMAT(a.dtFechaEmision, 'dd-MM') AS F_EMISION, 
               --FORMAT(j.dtFechaHoraFin, 'dd-MM') AS F_TENIDO, 
               --FORMAT(a.FechaCierreAprobado, 'dd-MM') AS F_APROB_TELA, 
               a.dCantidad AS KG, 
               a.nvDocumentoReferencia AS REF, g.NommaeColor AS COLOR, --a.bCierreAprobado AS AP_DES, 
               --a.bProduccionAprobado AS DESP, a.bcerrado AS CERR, 
               LEFT(h.NommaeAnexoCliente, 15) AS Cliente 
               --a.ntEstado AS ESTADO, k.NommaeRuta AS RUTA
        FROM docOrdenProduccion a WITH (NOLOCK)
        INNER JOIN maeItemInventario f WITH (NOLOCK) ON f.IdmaeItem_Inventario = a.IdmaeItem
        INNER JOIN maeColor g WITH (NOLOCK) ON g.IdmaeColor = a.IdmaeColor
        INNER JOIN maeAnexoCliente h WITH (NOLOCK) ON h.IdmaeAnexo_Cliente = a.IdmaeAnexo_Cliente
        --INNER JOIN docRecetaOrdenProduccion i ON a.IdDocumento_OrdenProduccion = i.IdDocumento_OrdenProduccion
        --INNER JOIN docReceta j ON i.IdDocumento_Receta = j.IdDocumento_Receta
        LEFT JOIN docRecetaOrdenProduccion i ON a.IdDocumento_OrdenProduccion = i.IdDocumento_OrdenProduccion  -- LEFT JOIN
        LEFT JOIN docReceta j ON i.IdDocumento_Receta = j.IdDocumento_Receta
        INNER JOIN maeruta k ON a.IdmaeRuta = k.IdmaeRuta
        WHERE a.IdtdDocumentoForm = 138
        AND j.dtFechaHoraFin IS NULL
        AND DATEDIFF(DAY, a.dtFechaEmision, GETDATE()) > {dias}
        AND a.dtFechaEmision > '01-07-2024'
        and j.bAnulado =0
        AND a.IdmaeAnexo_Cliente IN (47, 49, 91, 93, 111, 1445, 2533, 2637, 4294, 4323, 4374, 4411, 4413, 4469, 5506, 6577)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Consulta para obtener PARTIDAS con F_TENIDO pero sin F_APROB_TELA y que RUTA no contenga "ESTAMP"
def get_partidas_con_tenido_sin_aprob_tela(dias):
    conn = connect_to_db()
    query = f"""
        SELECT a.CoddocOrdenProduccion AS PARTIDA,DATEDIFF(DAY, a.dtFechaEmision, GETDATE()) AS DIAS    , DATEDIFF(DAY, j.dtFechaHoraFin, GETDATE()) AS DIAS_TEN  , LEFT(f.NommaeItemInventario, 35) AS TELA, FORMAT(a.dtFechaEmision, 'dd-MM') AS F_EMISION,
              FORMAT(j.dtFechaHoraFin, 'dd-MM') AS F_TENIDO, --FORMAT(a.FechaCierreAprobado, 'dd-MM') AS F_APROB_TELA, 
              a.dCantidad AS KG, 
               a.nvDocumentoReferencia AS REF, g.NommaeColor AS COLOR, --a.bCierreAprobado AS AP_DES, 
               --a.bProduccionAprobado AS DESP, --a.bcerrado AS CERR, 
               LEFT(h.NommaeAnexoCliente, 15) AS Cliente,
               a.ntEstado AS ESTADO --, k.NommaeRuta AS RUTA
        FROM docOrdenProduccion a WITH (NOLOCK)
        INNER JOIN maeItemInventario f WITH (NOLOCK) ON f.IdmaeItem_Inventario = a.IdmaeItem
        INNER JOIN maeColor g WITH (NOLOCK) ON g.IdmaeColor = a.IdmaeColor
        INNER JOIN maeAnexoCliente h WITH (NOLOCK) ON h.IdmaeAnexo_Cliente = a.IdmaeAnexo_Cliente
        INNER JOIN docRecetaOrdenProduccion i ON a.IdDocumento_OrdenProduccion = i.IdDocumento_OrdenProduccion
        INNER JOIN docReceta j ON i.IdDocumento_Receta = j.IdDocumento_Receta
        INNER JOIN maeruta k ON a.IdmaeRuta = k.IdmaeRuta
        WHERE a.IdtdDocumentoForm = 138
        AND j.dtFechaHoraFin IS NOT NULL
        and j.bAnulado =0
        AND a.FechaCierreAprobado IS NULL
        AND LOWER(k.NommaeRuta) NOT LIKE '%estamp%'
        AND DATEDIFF(DAY, j.dtFechaHoraFin, GETDATE()) > {dias}
        AND a.dtFechaEmision > '01-07-2024'
        AND a.IdmaeAnexo_Cliente IN (47, 49, 91, 93, 111, 1445, 2533, 2637, 4294, 4323, 4374, 4411, 4413, 4469, 5506, 6577)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Interfaz de Streamlit
st.title("Seguimiento de Partidas")

# Selección de días para la primera consulta
dias_sin_tenido = st.number_input("Días sin TEÑIR (por defecto 8)", min_value=1, value=8)
if st.button("Mostrar partidas no TEÑIDAS"):
    df_sin_tenido = get_partidas_sin_tenido(dias_sin_tenido)
    st.write(df_sin_tenido)

# Selección de días para la segunda consulta
dias_con_tenido = st.number_input("Días entre TEÑIDO y el día actual (por defecto 5)", min_value=1, value=5)
if st.button("Mostrar partidas TEÑIDAS pero no APROBADAS"):
    df_con_tenido = get_partidas_con_tenido_sin_aprob_tela(dias_con_tenido)
    st.write(df_con_tenido)
