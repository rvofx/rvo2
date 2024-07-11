import streamlit as st
import pandas as pd
import pyodbc

# Definir usuarios y contraseñas
usuarios = {
    'rvo': '39',
    'usuario2': 'contrasena2'
}

# conexión a la base de datos sql server
conn = None

# función de conexión a la base de datos
def conectar_bd():
    conn = pyodbc.connect(
        driver=st.secrets["db_driver"],
        server=st.secrets["db_server"],
        database=st.secrets["db_database"],
        uid=st.secrets["db_username"],
        pwd=st.secrets["db_password"]
    )
    return conn

# formulario de inicio de sesión
st.title('inicio de sesión')
username_input = st.text_input('usuario')
password_input = st.text_input('contraseña', type='password')

# verificar credenciales
if st.button('iniciar sesión'):
    if username_input in usuarios and usuarios[username_input] == password_input:
        st.success('inicio de sesión exitoso')
        conectar_bd()

        # solicitar número de partida al usuario
        partida = st.text_input('ingresa el número de partida:')

        if partida:
            cursor = conn.cursor()

            # consulta sql para obtener los datos de partida
            query = f'''
            select e.coddocordenproduccion as partida, a.isecuencia as orden, c.nommaeproceso as proceso
            from docordenproduccionruta a
            inner join maeproceso c on a.idmaeproceso = c.idmaeproceso
            inner join docordenproduccion e on a.iddocumento_ordenproduccion = e.iddocumento_ordenproduccion
            where e.coddocordenproduccion = '{partida}' and a.bcerrado = 0 and e.bcerrado = 0
            '''

            df = pd.read_sql(query, conn)

            selected_row = st.selectbox('selecciona una línea de la consulta:', df['partida'])

            if st.button('confirmar selección'):
                st.write(f"has seleccionado la partida {selected_row}")

                # actualizaciones sql
                update_query_1 = f'''
                update docordenproduccionruta
                set bcerrado = 1, idsistemausuario_cerrado = 'password', fechacerrado = getdate(), 
                dtfechahorainicio = getdate(), dtfechahorafin = getdate()
                where iddocumento_ordenproduccion = '{partida}' and isecuencia = '{orden}'
                '''
                cursor.execute(update_query_1)
                conn.commit()

                update_query_2 = f'''
                update docordenproduccion
                set idmaeproceso = {proceso}, ntestado = sc.ntestado
                from (
                    select nommaeproceso + ' ' + 'finalizado' as ntestado
                    from maeproceso
                    where idmaeproceso = {proceso}
                ) sc
                where iddocumento_ordenproduccion = {partida}
                '''
                cursor.execute(update_query_2)
                conn.commit()

                st.success('actualizaciones realizadas exitosamente')

    else:
        st.error('usuario o contraseña incorrectos')

else:
    st.write('Por favor, introduce tus credenciales y presiona el botón "iniciar sesión"')
