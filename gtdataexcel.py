import streamlit as st
import pandas as pd
import pyodbc


# Función para conectar a la base de datos
def connect_to_database():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=" + st.secrets["server"] + ";"
            "DATABASE=" + st.secrets["database"] + ";"
            "UID=" + st.secrets["username"] + ";"
            "PWD=" + st.secrets["password"] + ";"
        )
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

# Función para ejecutar la consulta SQL y obtener resultados
def get_sql_data(conn, po):
    query = f"SELECT coddocordenproduccion, dcantidadprogramado FROM docordenproduccion WHERE coddocordenproduccion = '{po}'"
    df = pd.read_sql(query, conn)
    return df

# Aplicación Streamlit
def main():
    st.title("Aplicación para consulta SQL y actualización de Excel")

    uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx"])

    if uploaded_file is not None:
        excel_data = pd.read_excel(uploaded_file)
        conn = connect_to_database()

        new_data = excel_data.copy()
       
        
        for index, row in new_data.iterrows():
            po = row['po']
            sql_data = get_sql_data(conn, po)
            if not sql_data.empty:
                new_data.at[index, 'dcantidadprogramado'] = sql_data['dcantidadprogramado'].values[0]

        st.write(new_data)

        st.write("Descarga el archivo Excel actualizado:")
        st.dataframe(new_data)

        # Convertir el DataFrame a formato CSV en memoria (como una cadena de texto)
        csv = new_data.to_csv(index=False)

        # Generar el enlace de descarga del archivo CSV utilizando st.markdown
        b64 = base64.b64encode(csv.encode()).decode()  # Codifica el CSV en base64
        href = f'<a href="data:file/csv;base64,{b64}" download="excel_actualizado.csv">Descargar archivo CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
       

if __name__ == '__main__':
    main()
