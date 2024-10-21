import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

# Función para conectar a la base de datos
def conectar_bd():
    conn = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return conn




# Función para ejecutar la consulta
def ejecutar_consulta(pedido):
    conn = conectar_bd()
    query = """
    SELECT e.CoddocOrdenVenta AS PEDIDO, a.coddocordenproduccion as OP,
           c.nommaecombo as COMBO, d.nommaetalla as TALLA, 
           b.dcantidadrequerido as UNID, b.dcantidadprogramado AS UNID_PROG
    FROM docOrdenProduccion a
    INNER JOIN docOrdenVenta e ON a.IdDocumento_Referencia = e.IdDocumento_OrdenVenta
    INNER JOIN docOrdenProduccionItem b ON b.IdDocumento_OrdenProduccion = a.IdDocumento_OrdenProduccion
    INNER JOIN maecombo c ON b.idmaecombo = c.idmaecombo
    INNER JOIN maetalla d ON d.idmaetalla = b.idmaetalla
    WHERE e.CoddocOrdenVenta = ?
    """
    df = pd.read_sql(query, conn, params=[pedido])
    conn.close()
    return df

# Función para generar el archivo Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# Aplicación Streamlit
st.title('Consulta de Pedidos')

pedido = st.text_input('Ingrese el número de PEDIDO:')

if st.button('Consultar'):
    if pedido:
        df = ejecutar_consulta(pedido)
        if not df.empty:
            st.write(df)
            
            excel_file = to_excel(df)
            st.download_button(
                label="Descargar resultados como Excel",
                data=excel_file,
                file_name=f'resultado_pedido_{pedido}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.write('No se encontraron resultados para este pedido.')
    else:
        st.write('Por favor, ingrese un número de pedido.')
