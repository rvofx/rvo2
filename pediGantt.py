import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configurar la conexión a la base de datos utilizando las credenciales almacenadas en secrets
def connect_db():
    connection = pyodbc.connect(
        "driver={ODBC Driver 17 for SQL Server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return connection

# Función para ejecutar la consulta SQL
def run_query(pedido):
    conn = connect_db()
    query = """SELECT gg.PEDIDO, gg.IdDocumento_OrdenVenta, gg.F_EMISION, gg.F_ENTREGA, gg.DIAS, gg.CLIENTE, gg.PO, gg.KG_REQ, 
       gg.KG_ARMP, gg.KG_TENIDP, gg.KG_TELAPROBP, gg.UNID, gg.PROGP, gg.CORTADOP, gg.COSIDOP, 
       ff.FMINARM, ff.FMAXARM, ff.FMINTENID, ff.FMAXTENID, ff.FMINTELAPROB, ff.FMAXTELAPROB, ff.FMINCORTE, ff.FMAXCORTE, ff.FMINCOSIDO, ff.FMAXCOSIDO
FROM 
    (SELECT
    a.CoddocOrdenVenta AS PEDIDO, 
    a.IdDocumento_OrdenVenta,
    CASE WHEN ISDATE(a.dtFechaEmision) = 1 THEN CONVERT(DATE, a.dtFechaEmision) ELSE NULL END AS F_EMISION,
    CASE WHEN ISDATE(a.dtFechaEntrega) = 1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE NULL END AS F_ENTREGA,
    CONVERT(INT, a.dtFechaEntrega - a.dtFechaEmision) AS DIAS,
    SUBSTRING(b.NommaeAnexoCliente, 1, 15) AS CLIENTE,
    a.nvDocumentoReferencia AS PO,
    CONVERT(INT, COALESCE(d.KG, 0)) AS KG_REQ,
    --CONVERT(INT, COALESCE(t.KG_ARM, 0)) AS KG_ARM,
    FORMAT(CASE WHEN d.KG = 0 THEN 0 ELSE (COALESCE(t.KG_ARM, 0) / d.KG) END, '0%') AS KG_ARMP,
    --CONVERT(INT, COALESCE(t.KG_TEÑIDOS, 0)) AS KG_TEÑIDOS,
    FORMAT(CASE WHEN d.KG = 0 THEN 0 ELSE (COALESCE(t.KG_TEÑIDOS, 0) / d.KG) END, '0%') AS KG_TENIDP,
    --CONVERT(INT, COALESCE(t.KG_PRODUC, 0)) AS KG_DESPACH,
    FORMAT(CASE WHEN d.KG = 0 THEN 0 ELSE (COALESCE(t.KG_PRODUC, 0) / d.KG) END, '0%') AS KG_TELAPROBP,
    CONVERT(INT, a.dCantidad) AS UNID,
    --CONVERT(INT, COALESCE(programado.PROG, 0)) AS PROG,
    FORMAT(CASE WHEN a.dCantidad = 0 THEN 0 ELSE (COALESCE(programado.PROG, 0) / a.dCantidad) END, '0%') AS PROGP,
    --CONVERT(INT, COALESCE(cortado.CORTADO, 0)) AS CORTADO,
    FORMAT(CASE WHEN a.dCantidad = 0 THEN 0 ELSE (COALESCE(cortado.CORTADO, 0) / a.dCantidad) END, '0%') AS CORTADOP,
    --CONVERT(INT, COALESCE(cosido.COSIDO, 0)) AS COSIDO,
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
INNER JOIN 
    (SELECT 
    x.IdDocumento_OrdenVenta,
    --x.CoddocOrdenVenta,
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
    INNER JOIN docOrdenVenta x ON a.IdDocumento_Referencia = x.IdDocumento_OrdenVenta
   
    WHERE b.IdtdDocumentoForm = 138 
      AND b.IdtdDocumentoForm_Referencia = 152 
      AND x.CoddocOrdenVenta IS NOT NULL
      AND a.IdDocumento_Referencia > 0
    GROUP BY x.IdDocumento_OrdenVenta
) q0 ON x.IdDocumento_OrdenVenta = q0.IdDocumento_OrdenVenta

LEFT JOIN (
    SELECT 
        x.IdDocumento_OrdenVenta, 
        MIN(e.dtFechaHoraFin) AS FMINTENID,
        MAX(e.dtFechaHoraFin) AS FMAXTENID
    FROM docOrdenVentaItem a
    INNER JOIN docOrdenProduccion b ON b.IdDocumento_Referencia = a.IdDocumento_OrdenVenta
    INNER JOIN docOrdenVenta x ON a.IdDocumento_Referencia = x.IdDocumento_OrdenVenta
    INNER JOIN docRecetaOrdenProduccion d ON b.IdDocumento_OrdenProduccion = d.IdDocumento_OrdenProduccion
    INNER JOIN docReceta e ON d.IdDocumento_Receta = e.IdDocumento_Receta
    WHERE b.IdtdDocumentoForm = 138 
      AND b.IdtdDocumentoForm_Referencia = 152 
      AND x.CoddocOrdenVenta IS NOT NULL
      AND a.IdDocumento_Referencia > 0
    GROUP BY x.IdDocumento_OrdenVenta
) q1 ON x.IdDocumento_OrdenVenta = q1.IdDocumento_OrdenVenta
LEFT JOIN (
    SELECT 
        x.IdDocumento_OrdenVenta,  
        MIN(b.FechaCierreAprobado) AS FMINTELAPROB,
        MAX(b.FechaCierreAprobado) AS FMAXTELAPROB
    FROM docOrdenVentaItem a
    INNER JOIN docOrdenProduccion b ON b.IdDocumento_Referencia = a.IdDocumento_OrdenVenta
    INNER JOIN docOrdenVenta x ON a.IdDocumento_Referencia = x.IdDocumento_OrdenVenta
    INNER JOIN docOrdenProduccionRuta d ON b.IdDocumento_OrdenProduccion = d.IdDocumento_OrdenProduccion
    WHERE b.IdtdDocumentoForm = 138 
      AND b.IdtdDocumentoForm_Referencia = 152 
      AND x.CoddocOrdenVenta IS NOT NULL
      AND a.IdDocumento_Referencia > 0
    GROUP BY x.IdDocumento_OrdenVenta
) q2 ON x.IdDocumento_OrdenVenta = q2.IdDocumento_OrdenVenta
LEFT JOIN (
    SELECT 
        g.IdDocumento_OrdenVenta,  
        MIN(a.dtFechaRegistro) AS FMINCORTE,
        MAX(a.dtFechaRegistro) AS FMAXCORTE
    FROM dbo.docNotaInventario a WITH (NOLOCK)
    INNER JOIN dbo.maeCentroCosto a1 WITH (NOLOCK) ON a.IdmaeCentroCosto = a1.IdmaeCentroCosto AND a1.bConOrdenProduccion = 1
    INNER JOIN dbo.docNotaInventarioItem b WITH (NOLOCK) ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
    INNER JOIN dbo.docOrdenProduccion c WITH (NOLOCK) ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
	--AND c.bCerrado = 0 
	AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
    INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK) ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
    INNER JOIN dbo.docOrdenProduccionRuta d WITH (NOLOCK) ON a.IddocOrdenProduccionRuta = d.IddocOrdenProduccionRuta
    INNER JOIN dbo.docOrdenProduccionItem e WITH (NOLOCK) ON c.IdDocumento_OrdenProduccion = e.IdDocumento_OrdenProduccion AND b.IdmaeItem_Inventario = e.IdmaeItem
    INNER JOIN dbo.maeItemInventario f WITH (NOLOCK) ON b.IdmaeItem_Inventario = f.IdmaeItem_Inventario AND f.IdtdItemForm = 10
    WHERE a.IdtdDocumentoForm = 131
        AND a.bDevolucion = 0
        AND a.bDesactivado = 0
        AND a.bAnulado = 0
        AND a.IdDocumento_OrdenProduccion <> 0
        AND a.IdmaeCentroCosto = 29
    GROUP BY g.IdDocumento_OrdenVenta
) q3 ON x.IdDocumento_OrdenVenta = q3.IdDocumento_OrdenVenta
LEFT JOIN (
    SELECT 
        g.IdDocumento_OrdenVenta,  
        MIN(a.dtFechaRegistro) AS FMINCOSIDO,
        MAX(a.dtFechaRegistro) AS FMAXCOSIDO
    FROM dbo.docNotaInventario a WITH (NOLOCK)
    INNER JOIN dbo.maeCentroCosto a1 WITH (NOLOCK) ON a.IdmaeCentroCosto = a1.IdmaeCentroCosto AND a1.bConOrdenProduccion = 1
    INNER JOIN dbo.docNotaInventarioItem b WITH (NOLOCK) ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
    INNER JOIN dbo.docOrdenProduccion c WITH (NOLOCK) ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
	--AND c.bCerrado = 0 
	AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
    INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK) ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
    INNER JOIN dbo.docOrdenProduccionRuta d WITH (NOLOCK) ON a.IddocOrdenProduccionRuta = d.IddocOrdenProduccionRuta
    INNER JOIN dbo.docOrdenProduccionItem e WITH (NOLOCK) ON c.IdDocumento_OrdenProduccion = e.IdDocumento_OrdenProduccion AND b.IdmaeItem_Inventario = e.IdmaeItem
    INNER JOIN dbo.maeItemInventario f WITH (NOLOCK) ON b.IdmaeItem_Inventario = f.IdmaeItem_Inventario AND f.IdtdItemForm = 10
    WHERE a.IdtdDocumentoForm = 131
        AND a.bDevolucion = 0
        AND a.bDesactivado = 0
        AND a.bAnulado = 0
        AND a.IdDocumento_OrdenProduccion <> 0
        AND a.IdmaeCentroCosto = 47
    GROUP BY g.IdDocumento_OrdenVenta
) q4 ON x.IdDocumento_OrdenVenta = q4.IdDocumento_OrdenVenta
WHERE x.CoddocOrdenVenta IS NOT NULL
		and x.IdtdDocumentoForm=10 
		and x.IdtdTipoVenta=4
		and x.bAnulado=0
		--and c.IdDocumento_OrdenVenta=441563
--ORDER BY x.IdDocumento_OrdenVenta;
    ) ff
ON gg.IdDocumento_OrdenVenta = ff.IdDocumento_OrdenVenta
WHERE gg.PEDIDO = ? """
    
    df = pd.read_sql(query, conn, params=(pedido,))
    conn.close()
    
    # Convertir columnas de fechas a un único formato
    date_columns = ['F_EMISION', 'F_ENTREGA', 'FMINARM', 'FMAXARM', 'FMINTENID', 'FMAXTENID', 
                    'FMINTELAPROB', 'FMAXTELAPROB', 'FMINCORTE', 'FMAXCORTE', 'FMINCOSIDO', 'FMAXCOSIDO']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col]).dt.date

    return df

# Función para crear el gráfico de Gantt
#import plotly.graph_objs as go
#from datetime import datetime
#import pandas as pd
#import streamlit as st

def create_gantt(df):
    # Crear el gráfico de Gantt
    fig = go.Figure()
    processes = ['ARM', 'TENID', 'TELAPROB', 'CORTADO', 'COSIDO']
    date_min_cols = ['FMINARM', 'FMINTENID', 'FMINTELAPROB', 'FMINCORTE', 'FMINCOSIDO']
    date_max_cols = ['FMAXARM', 'FMAXTENID', 'FMAXTELAPROB', 'FMAXCORTE', 'FMAXCOSIDO']
    progress_cols = ['KG_ARMP', 'KG_TENIDP', 'KG_TELAPROBP', 'CORTADOP', 'COSIDOP']

	st.write("Processes:", processes)
	st.write("Date Min Columns:", date_min_cols)
	st.write("Date Max Columns:", date_max_cols)
	st.write("Progress Columns:", progress_cols)
	
    
    for i, process in enumerate(processes):
        # Asegúrate de que las fechas sean objetos datetime
        #date_min = pd.to_datetime(df[date_min_cols[i]][0])
        #date_max = pd.to_datetime(df[date_max_cols[i]][0])
		date_min = [date_min_cols[i]][0]
        date_max = [date_max_cols[i]][0]

	
        fig.add_trace(go.Bar(
            x=[date_max - date_min],
            y=[process],
            base=[date_min],
            orientation='h',
            text=f"Progreso: {df[progress_cols[i]].iloc[0]}%",
            hoverinfo='text',
            marker=dict(color='skyblue'),
            showlegend=False
        ))
    
    # Agregar las líneas verticales para F_EMISION, F_ENTREGA y fecha actual
    current_date = datetime.now().date()
    important_dates = {
        'F_EMISION': pd.to_datetime(df['F_EMISION'][0]).date(),
        'F_ENTREGA': pd.to_datetime(df['F_ENTREGA'][0]).date(),
        'Hoy': current_date
    }
    
    for label, date in important_dates.items():
	    fig.add_shape(
	        type="line",
	        x0=date,
	        x1=date,
	        y0=0,
	        y1=1,
	        yref="paper",
	        line=dict(color='red' if label == 'Hoy' else 'green', width=2),
	    )
	    fig.add_annotation(
	        x=date,
	        y=1,
	        yref="paper",
	        text=label,
	        showarrow=False,
	        yshift=10
	    )
    # Configuración del eje X (días) y eje Y (procesos)
    fig.update_layout(
        title="Gráfico de Gantt - Procesos de Producción",
        xaxis_title="Fecha",
        yaxis_title="Proceso",
        xaxis=dict(type='date', tickformat='%d', dtick="D2"),
        yaxis=dict(categoryorder="array", categoryarray=processes),
        bargap=0.3
    )
    
    st.plotly_chart(fig)



# Interfaz de Streamlit
st.title("Gráfico de Gantt - Proceso por Pedido")

pedido = st.text_input("Ingrese el número de pedido:")

if pedido:
    df = run_query(pedido)
    if not df.empty:
        st.dataframe(df)  # Mostrar los datos obtenidos
        create_gantt(df)  # Crear el gráfico de Gantt
    else:
        st.warning("No se encontraron datos para el pedido ingresado.")

