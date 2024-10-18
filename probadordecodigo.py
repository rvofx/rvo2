import streamlit as st
import pyodbc
import pandas as pd

st.set_page_config(layout="wide")

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

# Consultas para obtener datos
def get_partidas_sin_tenido(dias):
    conn = connect_to_db()
    query = f"""
        SELECT a.coddocordenproduccion AS partida, 
               DATEDIFF(day, a.dtfechaemision, GETDATE()) AS dias, 
               LEFT(f.nommaeiteminventario, 35) AS tela, 
               FORMAT(a.dtfechaemision, 'dd-mm') AS f_emision, 
               a.dcantidad AS kg, 
               a.nvdocumentoreferencia AS ref, 
               g.nommaecolor AS color,
               LEFT(h.nommaeanexocliente, 15) AS cliente, 
               CASE WHEN LOWER(k.nommaeruta) LIKE '%mofijado%' THEN 1 ELSE 0 END AS flag
        FROM docordenproduccion a WITH (NOLOCK)
        INNER JOIN maeiteminventario f WITH (NOLOCK) ON f.idmaeitem_inventario = a.idmaeitem
        INNER JOIN maecolor g WITH (NOLOCK) ON g.idmaecolor = a.idmaecolor
        INNER JOIN maeanexocliente h WITH (NOLOCK) ON h.idmaeanexo_cliente = a.idmaeanexo_cliente
        INNER JOIN maeruta k ON a.idmaeruta = k.idmaeruta
        WHERE a.idtddocumentoform = 138
        AND DATEDIFF(day, a.dtfechaemision, GETDATE()) > {dias}
        AND a.dtfechaemision > '01-07-2024'
        AND a.idmaeanexo_cliente IN (47, 49, 91, 93, 111, 1445, 2533, 2637, 4294, 4323, 4374, 4411, 4413, 4469, 5506, 6577)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Filtrar por cliente
def filter_by_client(df, client):
    if client == "todos":
        return df
    return df[df['cliente'] == client]

# Interfaz de Streamlit
st.title("Seguimiento de Partidas")

# Inicializar session state
if 'dias_sin_tenido' not in st.session_state:
    st.session_state.dias_sin_tenido = 8
if 'dias_con_tenido' not in st.session_state:
    st.session_state.dias_con_tenido = 5
if 'dias_con_tenido_estamp' not in st.session_state:
    st.session_state.dias_con_tenido_estamp = 20

# Estilos personalizados
st.markdown("""
    <style>
    .input-number-box {
        width: 100px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sección 1: Partidas no teñidas
st.session_state.dias_sin_tenido = st.number_input("Días sin teñir (por defecto 8)", min_value=1, value=st.session_state.dias_sin_tenido)

if st.button("Mostrar partidas no teñidas"):
    df_sin_tenido = get_partidas_sin_tenido(st.session_state.dias_sin_tenido)

    # Selector de cliente
    clientes = ["todos"] + sorted(df_sin_tenido['cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("Filtrar por cliente (partidas no teñidas):", clientes)

    # Filtrar por cliente
    df_filtrado = filter_by_client(df_sin_tenido, cliente_seleccionado)

    # Mostrar estadísticas y tabla filtrada
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['kg'].sum()

    st.write(f"Total registros: {total_registros}")
    st.write(f"Total kg: {total_kg:.0f}")

    styled_df = df_filtrado.style.apply(lambda row: ['background-color: yellow' if row['flag'] == 1 else '' for _ in row], axis=1).format({"kg": "{:.1f}"})
    st.write(styled_df, unsafe_allow_html=True)

# Sección 2: Partidas teñidas pero no aprobadas
st.session_state.dias_con_tenido = st.number_input("Días entre teñido y el día actual (por defecto 5)", min_value=1, value=st.session_state.dias_con_tenido)

if st.button("Mostrar partidas teñidas pero no aprobadas"):
    df_con_tenido = get_partidas_con_tenido_sin_aprob_tela(st.session_state.dias_con_tenido)

    # Selector de cliente
    clientes = ["todos"] + sorted(df_con_tenido['cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("Filtrar por cliente (partidas teñidas pero no aprobadas):", clientes)

    # Filtrar por cliente
    df_filtrado = filter_by_client(df_con_tenido, cliente_seleccionado)

    # Mostrar estadísticas y tabla filtrada
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['kg'].sum()

    st.write(f"Total registros: {total_registros}")
    st.write(f"Total kg: {total_kg:.0f}")

    st.write(df_filtrado)

# Sección 3: Partidas teñidas (estamp) pero no aprobadas
st.session_state.dias_con_tenido_estamp = st.number_input("Días entre teñido y el día actual (por defecto 20) partidas que llevan estampado", min_value=1, value=st.session_state.dias_con_tenido_estamp)

if st.button("Mostrar partidas teñidas (estamp) pero no aprobadas"):
    df_con_tenido_estamp = get_partidas_con_tenido_sin_aprob_tela_estamp(st.session_state.dias_con_tenido_estamp)

    # Selector de cliente
    clientes = ["todos"] + sorted(df_con_tenido_estamp['cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("Filtrar por cliente (partidas teñidas (estamp) pero no aprobadas):", clientes)

    # Filtrar por cliente
    df_filtrado = filter_by_client(df_con_tenido_estamp, cliente_seleccionado)

    # Mostrar estadísticas y tabla filtrada
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['kg'].sum()

    st.write(f"Total registros: {total_registros}")
    st.write(f"Total kg: {total_kg:.0f}")

    st.write(df_filtrado)
