import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc
from sqlalchemy import create_engine

# Configuración de la página
st.set_page_config(page_title="Dashboard de Unidades por Proveedor", layout="wide")

# Función para conectar a la base de datos
def connect_to_db():
    connection = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return connection

# Función para ejecutar la consulta de unidades enviadas
def run_query_enviadas():
    conn = connect_to_db()
    query = """
    SELECT 
        e.CoddocOrdenProduccion AS OP,
        MIN(d.dtFechaEmision) AS FECHA,
        MIN(f.NommaeAnexoProveedor) AS PROVEEDOR,
        SUM(b.dCantidadSal) AS TOTAL_UNIDADES
    FROM docNotaInventarioItem b
    INNER JOIN docGuiaRemisionDetalle c ON b.IdDocumento_NotaInventario = c.IdDocumento_NotaInventario
    INNER JOIN docGuiaRemision d ON c.IdDocumento_GuiaRemision = d.IdDocumento_GuiaRemision
    INNER JOIN docNotaInventario a ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario
    INNER JOIN docOrdenProduccion e ON a.IdDocumento_OrdenProduccion = e.IdDocumento_OrdenProduccion
    INNER JOIN maeAnexoProveedor f ON f.IdmaeAnexo_Proveedor = d.IdmaeAnexo_Destino
    WHERE d.IdmaeAnexo_Destino IN (6536, 4251, 6546)
        AND b.dCantidadSal > 0
        AND c.IdtdDocumentoForm_NotaInventario = 130
        AND d.dtFechaEmision > '01-09-2024'
        AND a.bAnulado = 0
        AND d.bAnulado = 0
    GROUP BY e.CoddocOrdenProduccion
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Función para ejecutar la consulta de unidades regresadas
def run_query_regresadas():
    conn = connect_to_db()
    query = """
    SELECT c.CoddocOrdenProduccion AS OP, MIN(A.dtFechaRegistro) as FECHA,
        MIN(d.NommaeAnexoProveedor) AS PROVEEDOR, SUM(b.dCantidadIng) AS TOTAL_UNIDADES
    FROM docNotaInventario a 
    INNER JOIN docNotaInventarioItem b ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario
    INNER JOIN docOrdenProduccion c ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
    INNER JOIN maeAnexoProveedor d ON a.IdmaeAnexo = d.IdmaeAnexo_Proveedor
    WHERE a.IdmaeAnexo IN (6536,4251, 6546)
        AND a.dtFechaRegistro > '01-09-2024'
        AND a.IdtdDocumentoForm = 131
        AND a.bAnulado = 0
        AND a.IdmaeSunatCTipoComprobantePago = 10
    GROUP BY c.CoddocOrdenProduccion
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Título de la aplicación
st.title("Dashboard de Unidades por Proveedor")

# Cargar datos
try:
    df_enviadas = run_query_enviadas()
    df_regresadas = run_query_regresadas()

    # Procesar datos
    total_enviadas = df_enviadas.groupby('PROVEEDOR')['TOTAL_UNIDADES'].sum().reset_index()
    total_enviadas = total_enviadas.rename(columns={'TOTAL_UNIDADES': 'UNIDADES_ENVIADAS'})

    total_regresadas = df_regresadas.groupby('PROVEEDOR')['TOTAL_UNIDADES'].sum().reset_index()
    total_regresadas = total_regresadas.rename(columns={'TOTAL_UNIDADES': 'UNIDADES_REGRESADAS'})

    # Combinar datos
    df_final = pd.merge(total_enviadas, total_regresadas, on='PROVEEDOR', how='outer').fillna(0)
    df_final['SALDO'] = df_final['UNIDADES_ENVIADAS'] - df_final['UNIDADES_REGRESADAS']
    df_final = df_final.sort_values('SALDO', ascending=False)

    # Mostrar estadísticas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Unidades Enviadas", f"{df_final['UNIDADES_ENVIADAS'].sum():,.0f}")
    col2.metric("Total de Unidades Regresadas", f"{df_final['UNIDADES_REGRESADAS'].sum():,.0f}")
    col3.metric("Saldo Total", f"{df_final['SALDO'].sum():,.0f}")

    # Tabla de resumen por proveedor
    st.subheader("Resumen por Proveedor")
    st.dataframe(df_final.style.format({
        'UNIDADES_ENVIADAS': '{:,.0f}',
        'UNIDADES_REGRESADAS': '{:,.0f}',
        'SALDO': '{:,.0f}'
    }))

    # Gráfico de barras apiladas
    st.subheader("Distribución de Unidades por Proveedor")
    fig = px.bar(df_final, x='PROVEEDOR', y=['UNIDADES_REGRESADAS', 'SALDO'],
                 title="Unidades Regresadas vs Saldo por Proveedor",
                 labels={'value': 'Unidades', 'variable': 'Tipo'},
                 color_discrete_map={'UNIDADES_REGRESADAS': 'green', 'SALDO': 'blue'})
    st.plotly_chart(fig)

    # Mostrar datos detallados
    st.subheader("Datos Detallados de Unidades Enviadas")
    st.dataframe(df_enviadas)

    st.subheader("Datos Detallados de Unidades Regresadas")
    st.dataframe(df_regresadas)

except Exception as e:
    st.error(f"Ocurrió un error al cargar los datos: {str(e)}")
