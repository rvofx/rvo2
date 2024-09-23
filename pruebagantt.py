import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# Configurar la conexión a la base de datos utilizando las credenciales almacenadas en secrets
def connect_db():
    connection = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return connection

# Función para ejecutar la consulta SQL
def run_query(pedido):
    conn = connect_db()
    query = """SELECT gg.PEDIDO, --gg.IdDocumento_OrdenVenta, 
    	gg.F_EMISION, gg.F_ENTREGA, gg.DIAS, gg.CLIENTE, gg.PO, gg.KG_REQ, 
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
    WHERE --c.bCerrado = 0  AND
        c.bAnulado = 0
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
    --AND (CASE WHEN ISDATE(a.dtFechaEntrega) = --1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE --NULL END) BETWEEN '2024-08-01' AND --'2024-12-31' 
    ) gg
INNER JOIN 
    (SELECT 
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
    ) ff
ON gg.IdDocumento_OrdenVenta = ff.IdDocumento_OrdenVenta
WHERE gg.PEDIDO = ?"""

    df = pd.read_sql(query, conn, params=(pedido,))
    conn.close()
    return df

# Parámetros constantes
FACTOR = 0.06
DARM = 0.2
DTENID = 0.25
DTELAPROB = 0.27
DCORTADO = 0.25
DCOSIDO = 0.57

# Interfaz de usuario de Streamlit
st.title("Progreso del Pedido")

# Agrupación en columnas para mejor apariencia
col1, col2, col3 = st.columns([2, 1, 1])

# Columna 1: Pedido (resaltado)
with col1:
    pedido = st.text_input("**Ingresa el número de pedido**")

# Columna 2: Fecha de colocación
with col2:
    fecha_colocacion_input = st.date_input("Fecha de Colocación (opcional)", value=None)

# Columna 3: Fecha de entrega
with col3:
    fecha_entrega_input = st.date_input("Fecha de Entrega (opcional)", value=None)

# Agrupación para parámetros adicionales en tres columnas
col4, col5, col6 = st.columns([1, 1, 1])

with col4:
    dtex = st.number_input("Días proceso en tela", min_value=0, value=0)

with col5:
    dpieza = st.number_input("Días proceso en pieza", min_value=0, value=0)
    dpieza_sw = 1 if dpieza > 0 else 0

with col6:
    dprenda = st.number_input("Días proceso en prenda", min_value=0, value=0)
    dprenda_sw = 1 if dprenda > 0 else 0

# Si el botón se presiona y hay un número de pedido ingresado, se ejecuta la consulta
if st.button("Ejecutar Consulta"):
    if pedido:
        try:
            # Ejecutar la consulta y obtener los resultados
            df = run_query(pedido)
            if df.empty:
                st.warning("No se encontraron datos para este pedido.")
            else:
                # Mostrar los datos en una tabla
                st.dataframe(df)

                # Procesar los datos para el gráfico de Gantt
                f_emision = pd.to_datetime(df['F_EMISION'].iloc[0])
                dias = df['DIAS'].iloc[0]

                # Recalcular DIAS si alguna de las fechas de colocación o entrega ha sido ingresada
                if fecha_colocacion_input is not None or fecha_entrega_input is not None:
                    if fecha_colocacion_input is not None and fecha_entrega_input is not None:
                        # Si ambas fechas fueron ingresadas, recalcular DIAS
                        dias = (pd.to_datetime(fecha_entrega_input) - pd.to_datetime(fecha_colocacion_input)).days
                    elif fecha_colocacion_input is not None:
                        # Si solo la fecha de colocación fue ingresada
                        fecha_entrega_original = pd.to_datetime(df['F_ENTREGA'].iloc[0])
                        dias = (fecha_entrega_original - pd.to_datetime(fecha_colocacion_input)).days
                    elif fecha_entrega_input is not None:
                        # Si solo la fecha de entrega fue ingresada
                        fecha_colocacion_original = pd.to_datetime(df['F_EMISION'].iloc[0])
                        dias = (pd.to_datetime(fecha_entrega_input) - fecha_colocacion_original).days

                # Cálculo de las fechas de inicio y fin
                start_armado = f_emision + timedelta(days=FACTOR * (dias-dtex-dpieza-dprenda))
                start_tenido = f_emision + timedelta(days=2 * FACTOR * (dias-dtex-dpieza-dprenda))
                start_telaprob = f_emision + timedelta(days=3 * FACTOR * (dias-dtex-dpieza-dprenda)+dtex+dpieza+dprenda-(dpieza*dpieza_sw)-(dprenda*dprenda_sw))
                start_corte = f_emision + timedelta(days=4 * FACTOR * (dias-dtex-dpieza-dprenda)+dtex+dpieza+dprenda-(dprenda*dprenda_sw))
                start_costura = f_emision + timedelta(days=6 * FACTOR * (dias-dtex-dpieza-dprenda)+dtex+dpieza+dprenda)

                finish_armado = f_emision + timedelta(days=(FACTOR + DARM) * (dias-dtex-dpieza-dprenda))
                finish_tenido = f_emision + timedelta(days=(2 * FACTOR + DTENID) * (dias-dtex-dpieza-dprenda))
                finish_telaprob = f_emision + timedelta(days=(3 * FACTOR + DTELAPROB) * (dias-dtex-dpieza-dprenda)+dtex+dpieza+dprenda-(dpieza*dpieza_sw)-(dprenda*dprenda_sw))
                finish_corte = f_emision + timedelta(days=(4 * FACTOR + DCORTADO) * (dias-dtex-dpieza-dprenda)+dtex+dpieza+dprenda-(dprenda*dprenda_sw))
                finish_costura = f_emision + timedelta(days=(6 * FACTOR + DCOSIDO) * (dias-dtex-dpieza-dprenda)+dtex+dpieza+dprenda)

                # Crear DataFrame para el gráfico de Gantt
                df_gantt = pd.DataFrame({
                    'Proceso': ['ARMADO', 'TEÑIDO', 'TELA_APROB', 'CORTE', 'COSTURA'],
                    'Start': [start_armado, start_tenido, start_telaprob, start_corte, start_costura],
                    'Finish': [finish_armado, finish_tenido, finish_telaprob, finish_corte, finish_costura],
                    'Start Real': [pd.to_datetime(df['FMINARM'].iloc[0]), pd.to_datetime(df['FMINTENID'].iloc[0]), 
                                   pd.to_datetime(df['FMINTELAPROB'].iloc[0]), pd.to_datetime(df['FMINCORTE'].iloc[0]), 
                                   pd.to_datetime(df['FMINCOSIDO'].iloc[0])],
                    'Finish Real': [pd.to_datetime(df['FMAXARM'].iloc[0]), pd.to_datetime(df['FMAXTENID'].iloc[0]), 
                                    pd.to_datetime(df['FMAXTELAPROB'].iloc[0]), pd.to_datetime(df['FMAXCORTE'].iloc[0]), 
                                    pd.to_datetime(df['FMAXCOSIDO'].iloc[0])],
                    'Avance': [df['KG_ARMP'].iloc[0], df['KG_TENIDP'].iloc[0], df['KG_TELAPROBP'].iloc[0], 
                               df['CORTADOP'].iloc[0], df['COSIDOP'].iloc[0]]
                })

                # Crear el gráfico de Gantt
                fig = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Proceso", text="Avance")

                # Cambiar el color de las barras
                for trace in fig.data:
                    trace.marker.color = 'lightsteelblue'  # Puedes cambiar a cualquier color válido

                # Mostrar las etiquetas del eje X cada 7 días
                tick0_date = f_emision.strftime('%Y-%m-%d')
                fig.update_xaxes(tickmode='linear', tick0=tick0_date, dtick=7 * 24 * 60 * 60 * 1000)

                # Ajustar el diseño del gráfico
                fig.update_yaxes(autorange="reversed")

                # Agregar las barras de las fechas reales
                fig.add_trace(go.Scatter(
                    x=df_gantt['Start Real'],
                    y=df_gantt['Proceso'],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color='black'),    
                    name='Start Real'
                ))
                fig.add_trace(go.Scatter(
                    x=df_gantt['Finish Real'],
                    y=df_gantt['Proceso'],
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=10, color='red'),
                    name='Finish Real'
                ))

                # Determinar fechas de colocación y entrega basadas en la entrada del usuario
                fecha_colocacion = pd.to_datetime(df['F_EMISION'].iloc[0]) if fecha_colocacion_input is None else fecha_colocacion_input
                fecha_entrega = pd.to_datetime(df['F_ENTREGA'].iloc[0]) if fecha_entrega_input is None else fecha_entrega_input

                # Agregar líneas verticales para las fechas de colocación y entrega
                fig.add_shape(
                    type="line",
                    x0=fecha_colocacion,
                    y0=0,
                    x1=fecha_colocacion,
                    y1=len(df_gantt),
                    line=dict(color="green", width=2, dash="dash"),
                    name="Fecha Colocación"
                )
                fig.add_shape(
                    type="line",
                    x0=fecha_entrega,
                    y0=0,
                    x1=fecha_entrega,
                    y1=len(df_gantt),
                    line=dict(color="red", width=2, dash="dash"),
                    name="Fecha Entrega"
                )

                # Agregar una línea vertical para la fecha actual
                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                fig.add_shape(
                    type="line",
                    x0=fecha_actual,
                    y0=0,
                    x1=fecha_actual,
                    y1=len(df_gantt),
                    line=dict(color="blue", width=2, dash="dash"),
                    name="Fecha Actual"
                )
		# Mostrar el gráfico
                st.title(f"Pedido: {df['PEDIDO'].iloc[0]}")
                st.write(f"Cliente: {df['CLIENTE'].iloc[0]}")
                st.plotly_chart(fig)
                

        except Exception as e:
            st.error(f"Error al ejecutar la consulta: {str(e)}")
    else:
        st.warning("Por favor ingresa un número de pedido.")
