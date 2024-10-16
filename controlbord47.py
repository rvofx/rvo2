import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc
from sqlalchemy import create_engine

# Configuración de la página
st.set_page_config(page_title="Dashboard de Unidades por Proveedor", layout="wide")

# Función para conectar a la base de datos
#def connect_to_db():
    #server = st.secrets["server"]
    #database = st.secrets["database"]
    #username = st.secrets["username"]
    #password = st.secrets["password"]
    #driver = st.secrets["driver"]
    
    #connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    #return pyodbc.connect(connection_string)
    
def connect_to_db():
    connection = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return connection

# Función para ejecutar la consulta
def run_query():
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

# Título de la aplicación
st.title("Dashboard de Unidades por Proveedor")

# Cargar datos
try:
    df = run_query()

     # Agregar esta nueva sección justo después de cargar los datos
    # Tabla de total de unidades por proveedor
    st.subheader("Total de Unidades por Proveedor")
    total_por_proveedor = df.groupby('PROVEEDOR')['TOTAL_UNIDADES'].sum().reset_index()
    total_por_proveedor = total_por_proveedor.sort_values('TOTAL_UNIDADES', ascending=False)
    st.table(total_por_proveedor)
    
    # Mostrar datos en una tabla
    
    st.subheader("Datos de Unidades por Proveedor")
    st.dataframe(df)
    
    # Crear gráfico de barras

    #st.subheader("Gráfico de Unidades por Proveedor")
    #fig = px.bar(total_por_proveedor, x='PROVEEDOR', y='TOTAL_UNIDADES', title='Total de Unidades por Proveedor')
    #st.plotly_chart(fig, use_container_width=True)

    
    #st.subheader("Gráfico de Unidades por Proveedor")
    #fig = px.bar(df, x='PROVEEDOR', y='TOTAL_UNIDADES', title='Total de Unidades por Proveedor')
    #st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar estadísticas
    st.subheader("Estadísticas")
    total_unidades = df['TOTAL_UNIDADES'].sum()
    #promedio_unidades = df['TOTAL_UNIDADES'].mean()
    
    col1, col2 = st.columns(2)
    col1.metric("Total de Unidades", f"{total_unidades:,.0f}")
    col2.metric("Promedio de Unidades por Proveedor", f"{promedio_unidades:,.2f}")

except Exception as e:
    st.error(f"Ocurrió un error al cargar los datos: {str(e)}")
