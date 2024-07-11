import streamlit as st
import pandas as pd
import pyodbc
import os

# Formulario de inicio de sesión
st.title('Inicio de Sesión')
username = st.text_input('Usuario')
password = st.text_input('Contraseña', type='password')

# Lista de usuarios y contraseñas
usuarios = {
    'rvo': '39',
    'usuario2': 'contrasena2'
}

# Obtener las credenciales de la base de datos desde las variables de entorno
server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

# Conexión a la base de datos SQL Server
conn = None

# Función de conexión a la base de datos
def conectar_bd():
    global conn
    conn_str = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)

# Resto del código sigue igual

# Resto del código sigue igual


# Verificar credenciales
if st.button('Iniciar Sesión'):
    if username in usuarios and usuarios[username] == password:
        st.success('Inicio de sesión exitoso')
        conectar_bd()

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
        st.error('Usuario o contraseña incorrectos')
