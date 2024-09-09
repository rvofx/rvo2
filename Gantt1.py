import streamlit as st
import pyodbc
import pandas as pd

# Configurar la conexión a la base de datos utilizando las credenciales almacenadas en secrets
def connect_db():
    try:
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=" + st.secrets["server"] + ";"
            "DATABASE=" + st.secrets["database"] + ";"
            "UID=" + st.secrets["username"] + ";"
            "PWD=" + st.secrets["password"] + ";"
        )
        st.success("Conexión a la base de datos exitosa")
        return connection
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

# Función para ejecutar la consulta SQL
def run_query():
    conn = connect_db()
    query = """
    SELECT gg.*, ff.IdDocumento_OrdenVenta AS IdDocumento_OrdenVenta_FF -- Alias para evitar duplicidad
    FROM (
        SELECT *
        FROM (
            SELECT
                a.CoddocOrdenVenta AS PEDIDO, 
                a.IdDocumento_OrdenVenta,
                CASE WHEN ISDATE(a.dtFechaEmision) = 1 THEN CONVERT(DATE, a.dtFechaEmision) ELSE NULL END AS F_EMISION,
                CASE WHEN ISDATE(a.dtFechaEntrega) = 1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE NULL END AS F_ENTREGA,
                CONVERT(INT, a.dtFechaEntrega - a.dtFechaEmision) AS DIAS,
                SUBSTRING(b.NommaeAnexoCliente, 1, 15) AS CLIENTE,
                a.nvDocumentoReferencia AS PO,
                CONVERT(INT, COALESCE(d.KG, 0)) AS KG_REQ,
                FORMAT(CASE WHEN d.KG = 0 THEN 0 ELSE (COALESCE(t.KG_ARM, 0) / d.KG) END, '0%') AS KG_ARMP,
                FORMAT(CASE WHEN d.KG = 0 THEN 0 ELSE (COALESCE(t.KG_TEÑIDOS, 0) / d.KG) END, '0%') AS KG_TENIDP,
                FORMAT(CASE WHEN d.KG = 0 THEN 0 ELSE (COALESCE(t.KG_PRODUC, 0) / d.KG) END, '0%') AS KG_TELAPROBP,
                CONVERT(INT, a.dCantidad) AS UNID,
                FORMAT(CASE WHEN a.dCantidad = 0 THEN 0 ELSE (COALESCE(programado.PROG, 0) / a.dCantidad) END, '0%') AS PROGP,
                FORMAT(CASE WHEN a.dCantidad = 0 THEN 0 ELSE (COALESCE(cortado.CORTADO, 0) / a.dCantidad) END, '0%') AS CORTADOP,
                FORMAT(CASE WHEN a.dCantidad = 0 THEN 0 ELSE (COALESCE(cosido.COSIDO, 0) / a.dCantidad) END, '0%') AS COSIDOP
            FROM docOrdenVenta a
            INNER JOIN maeAnexoCliente b ON a.IdmaeAnexo_Cliente = b.IdmaeAnexo_Cliente
            LEFT JOIN (
                SELECT
                    c.IdDocumento_Referencia AS PEDIDO,
                    SUM(c.dCantidad) AS KG
                FROM docOrdenVentaItem c
                WHERE c.IdDocumento_Referencia > 0
                GROUP BY c.IdDocumento_Referencia
            ) d ON a.IdDocumento_OrdenVenta = d.PEDIDO
            LEFT JOIN (
                SELECT
                    x.IdDocumento_Referencia AS PEDIDO,
                    SUM(y.dCantidadProgramado) AS KG_ARM,
                    SUM(z.bcerrado * y.dCantidadRequerido) AS KG_PRODUC,
                    SUM(s.bcerrado * y.dCantidadProgramado) AS KG_TEÑIDOS
                FROM docOrdenProduccionItem y
                INNER JOIN docOrdenProduccion z ON y.IdDocumento_OrdenProduccion = z.IdDocumento_OrdenProduccion
                INNER JOIN docOrdenVentaItem x ON (z.IdDocumento_Referencia = x.IdDocumento_OrdenVenta AND y.idmaeItem = x.IdmaeItem)
                INNER JOIN docOrdenProduccionRuta s ON y.IdDocumento_OrdenProduccion = s.IdDocumento_OrdenProduccion
                WHERE s.IdmaeReceta > 0
                GROUP BY x.IdDocumento_Referencia
            ) t ON a.IdDocumento_OrdenVenta = t.PEDIDO
            LEFT JOIN (
                SELECT 
                    g.IdDocumento_OrdenVenta,
                    SUM(a.dCantidadProgramado) AS PROG
                FROM dbo.docOrdenProduccion c WITH (NOLOCK)
                INNER JOIN dbo.docOrdenProduccionItem a WITH (NOLOCK)
                    ON c.IdDocumento_OrdenProduccion = a.IdDocumento_OrdenProduccion
                INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK)
                    ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
                INNER JOIN dbo.docOrdenProduccionRuta b WITH (NOLOCK)
                    ON c.IdDocumento_OrdenProduccion = b.IdDocumento_OrdenProduccion
                WHERE c.bCerrado = 0
                    AND c.bAnulado = 0
                    AND c.IdtdDocumentoForm = 127
                    AND b.IdmaeCentroCosto = 29
                GROUP BY g.IdDocumento_OrdenVenta
            ) AS programado
            ON a.IdDocumento_OrdenVenta = programado.IdDocumento_OrdenVenta
            LEFT JOIN (
                SELECT 
                    g.IdDocumento_OrdenVenta,
                    SUM(b.dCantidadIng) AS CORTADO
                FROM dbo.docNotaInventario a WITH (NOLOCK)
                INNER JOIN dbo.maeCentroCosto a1 WITH (NOLOCK)
                    ON a.IdmaeCentroCosto = a1.IdmaeCentroCosto
                    AND a1.bConOrdenProduccion = 1
                INNER JOIN dbo.docNotaInventarioItem b WITH (NOLOCK)
                    ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario
                INNER JOIN dbo.docOrdenProduccion c WITH (NOLOCK)
                    ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
                INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK)
                    ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
                WHERE a.IdtdDocumentoForm = 131
                    AND a.bDevolucion = 0
                    AND a.bDesactivado = 0
                    AND a.bAnulado = 0
                    AND a.IdmaeCentroCosto = 29
                GROUP BY g.IdDocumento_OrdenVenta
            ) AS cortado
            ON a.IdDocumento_OrdenVenta = cortado.IdDocumento_OrdenVenta
            LEFT JOIN (
                SELECT 
                    g.IdDocumento_OrdenVenta,
                    SUM(b.dCantidadIng) AS COSIDO
                FROM dbo.docNotaInventario a WITH (NOLOCK)
                INNER JOIN dbo.maeCentroCosto a1 WITH (NOLOCK)
                    ON a.IdmaeCentroCosto = a1.IdmaeCentroCosto
                    AND a1.bConOrdenProduccion = 1
                INNER JOIN dbo.docNotaInventarioItem b WITH (NOLOCK)
                    ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario
                INNER JOIN dbo.docOrdenProduccion c WITH (NOLOCK)
                    ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
                INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK)
                    ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
                WHERE a.IdtdDocumentoForm = 131
                    AND a.bDevolucion = 0
                    AND a.bDesactivado = 0
                    AND a.bAnulado = 0
                    AND a.IdmaeCentroCosto = 47
                GROUP BY g.IdDocumento_OrdenVenta
            ) AS cosido
            ON a.IdDocumento_OrdenVenta = cosido.IdDocumento_OrdenVenta
            WHERE
                a.IdtdDocumentoForm = 10
                AND a.IdtdTipoVenta = 4
                AND a.bAnulado = 0
                AND (CASE WHEN ISDATE(a.dtFechaEntrega) = 1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE NULL END) BETWEEN '2024-08-01' AND '2024-12-31'
        ) gg
    ) gg
    INNER JOIN (
        SELECT 
            x.IdDocumento_OrdenVenta,
            q0.FMINARM,
            q0.FMAXARM,
            q1.FMINTENID,
            q1.FMAXTENID,
            q2.FMINTELAPROB,
            q2.FMAXTELAPROB,
            q3.FMINCORTE,
            q3.FMAXCORTE,
            q4.FMINCOSIDO,
            q4.FMAXCOSIDO
        FROM docOrdenVenta x
        LEFT JOIN (
            SELECT 
                x.IdDocumento_OrdenVenta, 
                MIN(b.dtFechaEmision) AS FMINARM,
                MAX(b.dtFechaEmision) AS FMAXARM
            FROM docOrdenVentaItem a
            INNER JOIN docOrdenProduccion b ON b.IdDocumento_Referencia = a.IdDocumento_OrdenVenta
            WHERE b.IdtdDocumentoForm = 138 
              AND b.IdtdDocumentoForm_Referencia = 152 
              AND x.CoddocOrdenVenta IS NOT NULL
              AND a.IdDocumento_OrdenVenta > 0
            GROUP BY x.IdDocumento_OrdenVenta
        ) q0 ON x.IdDocumento_OrdenVenta = q0.IdDocumento_OrdenVenta
        -- Agregar las demás subconsultas similares a q0 para las fechas de teñido, tela aprobada, corte y cosido
    ) ff
    ON gg.IdDocumento_OrdenVenta = ff.IdDocumento_OrdenVenta
    """


    st.write(query)  # Imprime la consulta para depuración
    
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error al ejecutar la consulta SQL: {e}")
        return None


    df = pd.read_sql(query, conn)
    return df

# Interfaz de usuario de Streamlit
def main():
    st.title("Consulta de Producción")
    st.write("Esta aplicación muestra el progreso de producción.")
    
    # Ejecutar la consulta SQL
    df = run_query()
    
    # Mostrar los resultados
    if df is not None:
        st.dataframe(df)

if __name__ == "__main__":
    main()


