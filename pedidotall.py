import streamlit as st
import pandas as pd
import pyodbc

# conexión a la base de datos usando credenciales del archivo secrets
def get_connection():
    conn = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return conn

# función para ejecutar la consulta
def load_data(pedido, estilos):
    query = """
    select 
        a.iddocumento_ordenventa,
        b.coddocordenventa as pedido,
        e.nommaeanexocliente as cliente,
        f.nommaeestilo as estilo,
        c.nommaecombo as combo,
        d.nommaetalla as talla,
        a.dcantidad as cant 
    from 
        docordenventaitem a
    inner join 
        docordenventa b on a.iddocumento_ordenventa = b.iddocumento_ordenventa
    inner join 
        maecombo c on a.idmaecombo = c.idmaecombo
    inner join 
        maetalla d on a.idmaetalla = d.idmaetalla
    inner join 
        maeanexocliente e on e.idmaeanexo_cliente = b.idmaeanexo_cliente
    inner join 
        maeestilo f on f.idmaeestilo = a.idmaeestilo
    where 
        b.coddocordenventa = ?
        {}
    """.format("and f.nommaeestilo in ({})".format(', '.join('?' * len(estilos))) if estilos else "")

    params = [pedido] + estilos if estilos else [pedido]

    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df

# sidebar para ingresar el pedido
pedido_input = st.sidebar.text_input("Ingresa el pedido", "")

# inicializa la lista de estilos
estilos_seleccionados = []
estilos = []  # asegúrate de que `estilos` esté inicializada

if pedido_input:
    # obtener estilos disponibles para el pedido
    with get_connection() as conn:
        estilos_query = """
        select distinct f.nommaeestilo 
        from maeestilo f 
        inner join docordenventaitem a on f.idmaeestilo = a.idmaeestilo 
        inner join docordenventa b on a.iddocumento_ordenventa = b.iddocumento_ordenventa 
        where b.coddocordenventa = ?
        """
        estilos = pd.read_sql(estilos_query, conn, params=[pedido_input])['nommaeestilo'].tolist()

    # sidebar para seleccionar estilos solo si hay estilos disponibles
    if estilos:
        estilos_seleccionados = st.sidebar.multiselect("Selecciona estilos", options=estilos)

# cargar los datos
if st.sidebar.button("Consultar"):
    if pedido_input:
        df = load_data(pedido_input, estilos_seleccionados)

        # creación de tabla dinámica
        if not df.empty:
            # Mostrar el cliente
            cliente = df['cliente'].iloc[0]  # Asumiendo que todos los registros son del mismo cliente
            st.write(f"Cliente: {cliente}")

            # Crear la tabla dinámica con totales
            pivot_table = pd.pivot_table(
                df,
            values='cant',
            index=['estilo', 'combo'],      # eje vertical
            columns=['talla'],        # eje horizontal
            fill_value=0,
            margins=True,  # Agrega totales
            margins_name='Total',  # Nombre para la fila/columna de totales
            aggfunc='sum'  # Especificar que queremos sumar
            )
            st.write(pivot_table)
        else:
            st.write("No hay resultados para la consulta.")
    else:
        st.warning("Por favor, ingresa un número de pedido.")
