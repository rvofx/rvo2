import streamlit as st
import pandas as pd
import pyodbc

# Conexión a la base de datos usando credenciales del archivo secrets
def get_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={st.secrets["db"]["server"]};'
        f'DATABASE={st.secrets["db"]["database"]};'
        f'UID={st.secrets["db"]["user"]};'
        f'PWD={st.secrets["db"]["password"]}'
    )
    return conn

# Función para ejecutar la consulta
def load_data(pedido, estilos):
    query = """
    SELECT 
        a.iddocumento_ordenventa,
        b.coddocordenventa AS pedido,
        e.nommaeanexocliente AS cliente,
        f.nommaeestilo AS estilo,
        c.nommaecombo AS combo,
        d.nommaetalla AS talla,
        a.dcantidad AS cant 
    FROM 
        docordenventaitem a
    INNER JOIN 
        docordenventa b ON a.iddocumento_ordenventa = b.iddocumento_ordenventa
    INNER JOIN 
        maecombo c ON a.idmaecombo = c.idmaecombo
    INNER JOIN 
        maetalla d ON a.idmaetalla = d.idmaetalla
    INNER JOIN 
        maeanexocliente e ON e.idmaeanexo_cliente = b.idmaeanexo_cliente
    INNER JOIN 
        maeestilo f ON f.idmaeestilo = a.idmaeestilo
    WHERE 
        b.coddocordenventa = ?
        {}

    """.format("AND f.nommaeestilo IN ({})".format(', '.join('?' * len(estilos))) if estilos else "")

    params = [pedido] + estilos if estilos else [pedido]

    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df

# Sidebar para seleccionar el pedido
pedido = st.sidebar.selectbox("Selecciona el pedido", options=[413979, 413980, 413981]) # debés cambiar estos valores por tus pedidos reales

# Sidebar para seleccionar estilos
if pedido:
    with get_connection() as conn:
        estilos_query = "SELECT DISTINCT nommaeestilo FROM maeestilo f INNER JOIN docordenventaitem a ON f.idmaeestilo = a.idmaeestilo WHERE a.iddocumento_ordenventa = ?"
        estilos = pd.read_sql(estilos_query, conn, params=[pedido])['nommaeestilo'].tolist()

    estilos_seleccionados = st.sidebar.multiselect("Selecciona estilos", opciones=estilos)

# Cargar los datos
if st.sidebar.button("Actualizar"):
    df = load_data(pedido, estilos_seleccionados)

    # Creación de tabla dinámica
    if not df.empty:
        pivot_table = pd.pivot_table(
            df,
            values='cant',
            index=['estilo', 'cliente'],      # Eje vertical
            columns=['combo', 'talla'],        # Eje horizontal
            fill_value=0
        )
        st.write(pivot_table)
    else:
        st.write("No hay resultados para la consulta.")
