import streamlit as st
import pyodbc
import pandas as pd

# Conexión a la base de datos SQL Server
#connection = pyodbc.connect('DRIVER={SQL Server};SERVER=your_server;DATABASE=your_db;UID=your_user;PWD=your_password')

connection = pyodbc.connect(
        "driver={ODBC Driver 17 for SQL Server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )

# Sidebar para la selección de fechas y área
start_date = st.sidebar.date_input("Fecha de inicio", value=pd.to_datetime('2024-01-01'))
end_date = st.sidebar.date_input("Fecha de fin", value=pd.to_datetime('2024-12-31'))

# Consulta SQL para obtener datos filtrados
query = f"""
SELECT *,
       CONCAT(RIGHT('00' + CAST(dia AS VARCHAR(2)), 2), '-',
              RIGHT('00' + CAST(mes AS VARCHAR(2)), 2), '-',
              año) AS CUMPLEAÑOS
FROM (
    SELECT a.nommaeanexotrabajador AS NOMBRE,
           b.nommaecentrocosto AS AREA,
           c.nommaecargo AS CARGO,
           DAY(a.dtfechanacimiento) AS dia,
           '2024' AS año,
           MONTH(a.dtfechanacimiento) AS mes,
           a.bdesactivado
    FROM maeanexotrabajador a
    INNER JOIN maecentrocosto b ON a.idmaecentrocosto = b.idmaecentrocosto
    INNER JOIN maecargo c ON a.idmaecargo = c.idmaecargo
    WHERE a.bcesado = 0
      AND a.dtfechanacimiento IS NOT NULL
) sc
WHERE sc.bdesactivado = 0
  AND CAST(CONCAT(año, '-', RIGHT('00' + CAST(mes AS VARCHAR(2)), 2), '-', RIGHT('00' + CAST(dia AS VARCHAR(2)), 2)) AS DATE) BETWEEN '{start_date}' AND '{end_date}'
ORDER BY CAST(CONCAT(año, '-', RIGHT('00' + CAST(mes AS VARCHAR(2)), 2), '-', RIGHT('00' + CAST(dia AS VARCHAR(2)), 2)) AS DATE);
"""

# Ejecutar la consulta y obtener los datos
data = pd.read_sql(query, connection)

# Obtener las opciones únicas para el campo 'area'
areas = data['area'].unique()

# Crear un multiselect box para seleccionar el área
selected_area = st.sidebar.multiselect("Seleccionar Área", areas)

# Filtrar los datos por el área seleccionada
filtered_data = data[data['area'].isin(selected_area)]

# Mostrar los datos filtrados
#st.write(filtered_data)

columns_to_show = ['NOMBRE','AREA', 'CARGO','CUMPLEAÑOS']
st.write(f"Registros: {len(filtered_data)}")
st.dataframe(filtered_data[columns_to_show], hide_index=True)
