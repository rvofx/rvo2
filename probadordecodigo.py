import streamlit as st
import pyodbc
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# Database connection function

def connect_to_db():
    conn = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return conn

# Function to get partidas sin tenido
def get_partidas_sin_tenido(dias):
    conn = connect_to_db()
    query = f"""
    SELECT * FROM YourTable
    WHERE FechaTenido IS NULL
    AND DATEDIFF(day, FechaCreacion, GETDATE()) > {dias}
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Function to get partidas con tenido sin aprobacion de tela
def get_partidas_con_tenido_sin_aprob_tela(dias):
    conn = connect_to_db()
    query = f"""
    SELECT * FROM YourTable
    WHERE FechaTenido IS NOT NULL
    AND FechaAprobacionTela IS NULL
    AND DATEDIFF(day, FechaTenido, GETDATE()) > {dias}
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Function to get partidas con tenido sin aprobacion de tela estampado
def get_partidas_con_tenido_sin_aprob_tela_estamp(dias):
    conn = connect_to_db()
    query = f"""
    SELECT * FROM YourTable
    WHERE FechaTenido IS NOT NULL
    AND FechaAprobacionTelaEstampado IS NULL
    AND DATEDIFF(day, FechaTenido, GETDATE()) > {dias}
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Function to highlight mofijado
def highlight_mofijado(row):
    return ['background-color: yellow' if row['Mofijado'] else '' for _ in row]

# Function to filter by client
def filter_by_client(df, client):
    if client == "Todos":
        return df
    return df[df['Cliente'] == client]

# Initialize session state
if 'df_sin_tenido' not in st.session_state:
    st.session_state.df_sin_tenido = None
if 'df_con_tenido' not in st.session_state:
    st.session_state.df_con_tenido = None
if 'df_con_tenido_estamp' not in st.session_state:
    st.session_state.df_con_tenido_estamp = None

# Streamlit interface
st.title("Seguimiento de Partidas")

# Custom styles
st.markdown("""
    <style>
    .input-number-box {
        width: 100px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Section 1: Partidas no TEÑIDAS
dias_sin_tenido = st.number_input("Días sin TEÑIR (por defecto 8)", min_value=1, value=8, key="dias_sin_tenido")

if st.button("Mostrar partidas no TEÑIDAS") or st.session_state.df_sin_tenido is not None:
    if st.session_state.df_sin_tenido is None:
        st.session_state.df_sin_tenido = get_partidas_sin_tenido(dias_sin_tenido)
    
    clientes = ["Todos"] + sorted(st.session_state.df_sin_tenido['Cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("Filtrar por cliente (Partidas no TEÑIDAS):", clientes, key="cliente_sin_tenido")
    
    df_filtrado = filter_by_client(st.session_state.df_sin_tenido, cliente_seleccionado)
    
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['KG'].sum()
    
    st.write(f"TOTAL REGISTROS: {total_registros}")
    st.write(f"TOTAL KG: {total_kg:.0f}")
    
    styled_df = df_filtrado.style.apply(highlight_mofijado, axis=1).format({"KG": "{:.1f}"})
    st.write(styled_df, unsafe_allow_html=True)

# Section 2: Partidas TEÑIDAS pero no APROBADAS
dias_con_tenido = st.number_input("Días entre TEÑIDO y el día actual (por defecto 5) Partidas que no llevan estampado", min_value=1, value=5, key="dias_con_tenido")

if st.button("Mostrar partidas TEÑIDAS pero no APROBADAS") or st.session_state.df_con_tenido is not None:
    if st.session_state.df_con_tenido is None:
        st.session_state.df_con_tenido = get_partidas_con_tenido_sin_aprob_tela(dias_con_tenido)
    
    clientes = ["Todos"] + sorted(st.session_state.df_con_tenido['Cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("Filtrar por cliente (Partidas TEÑIDAS pero no APROBADAS):", clientes, key="cliente_con_tenido")
    
    df_filtrado = filter_by_client(st.session_state.df_con_tenido, cliente_seleccionado)
    
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['KG'].sum()
    
    st.write(f"TOTAL REGISTROS: {total_registros}")
    st.write(f"TOTAL KG: {total_kg:.0f}")
    
    st.write(df_filtrado)

# Section 3: Partidas TEÑIDAS (estamp) pero no APROBADAS
dias_con_tenido_estamp = st.number_input("Días entre TEÑIDO y el día actual (por defecto 5) Partidas que llevan estampado", min_value=1, value=20, key="dias_con_tenido_estamp")

if st.button("Mostrar partidas TEÑIDAS (estamp) pero no APROBADAS") or st.session_state.df_con_tenido_estamp is not None:
    if st.session_state.df_con_tenido_estamp is None:
        st.session_state.df_con_tenido_estamp = get_partidas_con_tenido_sin_aprob_tela_estamp(dias_con_tenido_estamp)
    
    clientes = ["Todos"] + sorted(st.session_state.df_con_tenido_estamp['Cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("Filtrar por cliente (Partidas TEÑIDAS (estamp) pero no APROBADAS):", clientes, key="cliente_con_tenido_estamp")
    
    df_filtrado = filter_by_client(st.session_state.df_con_tenido_estamp, cliente_seleccionado)
    
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['KG'].sum()
    
    st.write(f"TOTAL REGISTROS: {total_registros}")
    st.write(f"TOTAL KG: {total_kg:.0f}")
    
    st.write(df_filtrado)

# Button to clear all data and reset the application
if st.button("Limpiar todos los datos"):
    for key in ['df_sin_tenido', 'df_con_tenido', 'df_con_tenido_estamp']:
        if key in st.session_state:
            del st.session_state[key]
    st.experimental_rerun()
