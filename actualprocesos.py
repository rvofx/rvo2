import streamlit as st
import pandas as pd
import pyodbc

# Definir usuarios y contraseñas
usuarios = {
    'rvo': '39',
    'usuario2': 'contrasena2'
}

# Conexión a la base de datos SQL Server
conn = None

# Función de conexión a la base de datos
def conectar_bd():
    global conn
    conn = pyodbc.connect(
        "driver={ODBC Driver 17 for SQL Server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )

# Formulario de inicio de sesión
st.title('Inicio de sesión')
username_input = st.text_input('Usuario')
password_input = st.text_input('Contraseña', type='password')

# Verificar credenciales
if st.button('Iniciar sesión'):
    if username_input in usuarios and usuarios[username_input] == password_input:
        st.success('Inicio de sesión exitoso')
        conectar_bd()

        # Solicitar número de partida al usuario
        partida = st.text_input('Ingresa el número de partida:')

        if partida:
            cursor = conn.cursor()

            # Consulta SQL para obtener los datos de la partida
            query = f'''
            SELECT e.coddocordenproduccion AS partida, a.isecuencia AS orden, c.nommaeproceso AS proceso
            FROM docordenproduccionruta AS a
            INNER JOIN maeproceso AS c ON a.idmaeproceso = c.idmaeproceso
            INNER JOIN docordenproduccion AS e ON a.iddocumento_ordenproduccion = e.iddocumento_ordenproduccion
            WHERE e.coddocordenproduccion = '{partida}' AND a.bcerrado = 0 AND e.bcerrado = 0
            '''

            df = pd.read_sql(query, conn)

            selected_row = st.selectbox('Selecciona una línea de la consulta:', df['partida'])

            if st.button('Confirmar selección'):
                st.write(f"Has seleccionado la partida {selected_row}")

                # Actualizaciones SQL
                for index, row in df.iterrows():
                    update_query_1 = f'''
                    UPDATE docordenproduccionruta
                    SET bcerrado = 1, idsistemausuario_cerrado = 'password', fechacerrado = getdate(), 
                    dtfechahorainicio = getdate(), dtfechahorafin = getdate()
                    WHERE iddocumento_ordenproduccion = '{partida}' AND isecuencia = {row['orden']}
                    '''
                    cursor.execute(update_query_1)
                    conn.commit()

                    update_query_2 = f'''
                    UPDATE docordenproduccion
                    SET idmaeproceso = {row['proceso']}, ntestado = sc.ntestado
                    FROM (
                        SELECT nommaeproceso + ' finalizado' AS ntestado
                        FROM maeproceso
                        WHERE idmaeproceso = {row['proceso']}
                    ) AS sc
                    WHERE iddocumento_ordenproduccion = {partida}
                    '''
                    cursor.execute(update_query_2)
                    conn.commit()

                st.success('Actualizaciones realizadas exitosamente')

        conn.close()  # Cerrar la conexión al finalizar
    else:
        st.error('Usuario o contraseña incorrectos')
else:
    st.write('Por favor, introduce tus credenciales y presiona el botón "Iniciar sesión"')
