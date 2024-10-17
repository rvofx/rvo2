import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc
from datetime import datetime

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
        MIN(d.dtFechaEmision) AS FECHA_ENVIO,
        MIN(f.NommaeAnexoProveedor) AS PROVEEDOR,
        SUM(b.dCantidadSal) AS UNIDADES_ENVIADAS
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
    SELECT c.CoddocOrdenProduccion AS OP, MIN(A.dtFechaRegistro) as FECHA_REGRESO,
        MIN(d.NommaeAnexoProveedor) AS PROVEEDOR, SUM(b.dCantidadIng) AS UNIDADES_REGRESADAS
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

    # Asegurar que las fechas sean del tipo correcto
    df_enviadas['FECHA_ENVIO'] = pd.to_datetime(df_enviadas['FECHA_ENVIO'], errors='coerce')
    df_regresadas['FECHA_REGRESO'] = pd.to_datetime(df_regresadas['FECHA_REGRESO'], errors='coerce')

    # Combinar datos detallados
    df_detallado = pd.merge(df_enviadas, df_regresadas, on=['OP', 'PROVEEDOR'], how='outer').fillna(0)
    df_detallado['SALDO'] = df_detallado['UNIDADES_ENVIADAS'] - df_detallado['UNIDADES_REGRESADAS']
    
    # Ordenar por OP
    df_detallado = df_detallado.sort_values('OP')

    # Calcular totales
    total_enviadas = df_detallado['UNIDADES_ENVIADAS'].sum()
    total_regresadas = df_detallado['UNIDADES_REGRESADAS'].sum()
    saldo_total = total_enviadas - total_regresadas

    # Mostrar estadísticas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Unidades Enviadas", f"{total_enviadas:,.0f}")
    col2.metric("Total de Unidades Regresadas", f"{total_regresadas:,.0f}")
    col3.metric("Saldo Total", f"{saldo_total:,.0f}")

    # Tabla de resumen por proveedor
    st.subheader("Resumen por Proveedor")
    df_resumen = df_detallado.groupby('PROVEEDOR').agg({
        'UNIDADES_ENVIADAS': 'sum',
        'UNIDADES_REGRESADAS': 'sum',
        'SALDO': 'sum'
    }).reset_index()
    st.dataframe(df_resumen.style.format({
        'UNIDADES_ENVIADAS': '{:,.0f}',
        'UNIDADES_REGRESADAS': '{:,.0f}',
        'SALDO': '{:,.0f}'
    }))

    # Gráfico de barras apiladas
    st.subheader("Distribución de Unidades por Proveedor")
    fig = px.bar(df_resumen, x='PROVEEDOR', y=['UNIDADES_REGRESADAS', 'SALDO'],
                 title="Unidades Regresadas vs Saldo por Proveedor",
                 labels={'value': 'Unidades', 'variable': 'Tipo'},
                 color_discrete_map={'UNIDADES_REGRESADAS': 'green', 'SALDO': 'blue'})
    st.plotly_chart(fig)

    # Mostrar datos detallados combinados
    st.subheader("Datos Detallados por OP")
    
    # Función para formatear fechas
    def format_date(date):
        return date.strftime('%Y-%m-%d') if pd.notnull(date) else ''

    # Aplicar el formato personalizado
    df_detallado['FECHA_ENVIO_FORMATTED'] = df_detallado['FECHA_ENVIO'].apply(format_date)
    df_detallado['FECHA_REGRESO_FORMATTED'] = df_detallado['FECHA_REGRESO'].apply(format_date)

    st.dataframe(df_detallado.style.format({
        'UNIDADES_ENVIADAS': '{:,.0f}',
        'UNIDADES_REGRESADAS': '{:,.0f}',
        'SALDO': '{:,.0f}',
        'FECHA_ENVIO_FORMATTED': '{}',
        'FECHA_REGRESO_FORMATTED': '{}'
    }).hide_columns(['FECHA_ENVIO', 'FECHA_REGRESO']))

except Exception as e:
    st.error(f"Ocurrió un error al cargar los datos: {str(e)}")
