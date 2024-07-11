import streamlit as st
import pandas as pd
import pyodbc
import os

# obtener las credenciales de la base de datos desde las variables de entorno
#server = os.getenv('db_server')
#database = os.getenv('db_database')
#username = os.getenv('db_username')
#password = os.getenv('db_password')

# conexión a la base de datos sql server
conn = None

# función de conexión a la base de datos
def conectar_bd():
    global conn
    #conn_str = f'driver=ODBC Driver 17 for SQL Server;server={server};database={database};uid={username};pwd={password}'
    #conn = pyodbc.connect(conn_str)
    conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=" + st.secrets["server"] + ";"
    "DATABASE=" + st.secrets["database"] + ";"
    "UID=" + st.secrets["username"] + ";"
    "PWD=" + st.secrets["password"] + ";"
    )


# formulario de inicio de sesión
st.title('Inicio de sesión')
username_input = st.text_input('Usuario')
password_input = st.text_input('Contraseña', type='password')

# lista de usuarios y contraseñas
usuarios = {
    'rvo': '39',
    'usuario2': 'contrasena2'
}

# verificar credenciales
if st.button('Iniciar sesión'):
    if username_input in usuarios and usuarios[username_input] == password_input:
        st.success('Inicio de sesión exitoso')
        conectar_bd()

        # resto de tu código...

    else:
        st.error('Usuario o contraseña incorrectos')

        # Solicitar número de partida al usuario
        partida = st.text_input('Ingresa el número de partida:')

        if partida:
            cursor = conn.cursor()

            # Consulta SQL para obtener los datos de partida
            query = f'''
            SELECT e.coddocordenproduccion AS partida, a.isecuencia AS orden, c.nommaeproceso AS proceso
            FROM docordenproduccionruta a
            INNER JOIN maeproceso c ON a.idmaeproceso = c.idmaeproceso
            INNER JOIN docordenproduccion e ON a.iddocumento_ordenproduccion = e.iddocumento_ordenproduccion
            WHERE e.coddocordenproduccion = '{partida}' AND a.bcerrado = 0 AND e.bcerrado = 0
            '''

            df = pd.read_sql(query, conn)

            selected_row = st.selectbox('Selecciona una línea de la consulta:', df['partida'])

            if st.button('Confirmar selección'):
                st.write(f"Has seleccionado la partida {selected_row}")

                # Actualizaciones SQL
                update_query_1 = f'''
                UPDATE docordenproduccionruta
                SET bcerrado = 1, idsistemausuario_cerrado = 'password', fechacerrado = GETDATE(), 
                dtfechahorainicio = GETDATE(), dtfechahorafin = GETDATE()
                WHERE iddocumento_ordenproduccion = '{partida}' AND isecuencia = '{orden}'
                '''
                cursor.execute(update_query_1)
                conn.commit()

                update_query_2 = f'''
                UPDATE docordenproduccion
                SET idmaeproceso = {proceso}, ntestado = sc.ntestado
                FROM (
                    SELECT nommaeproceso + ' ' + 'finalizado' AS ntestado
                    FROM maeproceso
                    WHERE idmaeproceso = {proceso}
                ) sc
                WHERE iddocumento_ordenproduccion = {partida}
                '''
                cursor.execute(update_query_2)
                conn.commit()

                st.success('Actualizaciones realizadas exitosamente')

else:
    st.write('Por favor, introduce tus credenciales y presiona el botón "Iniciar sesión"')
