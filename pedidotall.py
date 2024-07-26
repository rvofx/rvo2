import streamlit as st
import pandas as pd
import pyodbc

# Conexión a la base de datos usando credenciales del archivo secrets



def get_connection():
    conn = pyodbc.connect(
        "driver={ODBC Driver 17 for SQL Server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
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

# Sidebar para ingresar el pedido
pedido_input = st.sidebar.text_input("Ingresa el pedido (ejemplo: 413979)", "")

estilos_seleccionados = []
if pedido_input:
    # Obtener estilos disponibles para el pedido
    with get_connection() as conn:
        estilos_query = """
        SELECT DISTINCT f.nommaeestilo 
        FROM maeestilo f 
        INNER JOIN docordenventaitem a ON f.idmaeestilo = a.idmaeestilo 
        INNER JOIN docordenventa b ON a.iddocumento_ordenventa = b.iddocumento_ordenventa 
        WHERE b.coddocordenventa = ?
        """
        estilos = pd.read_sql(estilos_query, conn, params=[pedido_input])['nommaeestilo'].tolist()

    # Sidebar para seleccionar estilos
    estilos_seleccionados = st.sidebar.multiselect("Selecciona estilos", opciones=estilos)

# Cargar los datos
if st.sidebar.button("Actualizar"):
    if pedido_input:
        df = load_data(pedido_input, estilos_seleccionados)

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
    else:
        st.warning("Por favor, ingresa un número de pedido.")
