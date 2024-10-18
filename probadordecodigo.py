import streamlit as st
import pyodbc
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# Función para conectar a SQL Server
def connect_to_db():
    conn = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return conn

# Funciones para obtener datos (sin cambios)
def get_partidas_sin_tenido(dias):
    # ... (código sin cambios)

def get_partidas_con_tenido_sin_aprob_tela(dias):
    # ... (código sin cambios)

def get_partidas_con_tenido_sin_aprob_tela_estamp(dias):
    # ... (código sin cambios)

def highlight_mofijado(row):
    return ['background-color: yellow' if row['FLAG'] == 1 else '' for _ in row]

# Nueva función para filtrar por cliente
def filter_by_client(df, client):
    if client == "Todos":
        return df
    return df[df['Cliente'] == client]

# Interfaz de Streamlit
st.title("Seguimiento de Partidas")

# Estilos personalizados
st.markdown("""
    <style>
    .input-number-box {
        width: 100px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicializar el estado de sesión
if 'df_sin_tenido' not in st.session_state:
    st.session_state.df_sin_tenido = None
if 'df_con_tenido' not in st.session_state:
    st.session_state.df_con_tenido = None
if 'df_con_tenido_estamp' not in st.session_state:
    st.session_state.df_con_tenido_estamp = None

# Sección 1: Partidas no TEÑIDAS
dias_sin_tenido = st.number_input("Días sin TEÑIR (por defecto 8)", min_value=1, value=8)

if st.button("Mostrar partidas no TEÑIDAS") or st.session_state.df_sin_tenido is not None:
    if st.session_state.df_sin_tenido is None:
        st.session_state.df_sin_tenido = get_partidas_sin_tenido(dias_sin_tenido)

    df_sin_tenido = st.session_state.df_sin_tenido
    
    # Selector de cliente
    clientes = ["Todos"] + sorted(df_sin_tenido['Cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("Filtrar por cliente (Partidas no TEÑIDAS):", clientes, key='cliente_sin_tenido')
    
    # Filtrar por cliente
    df_filtrado = filter_by_client(df_sin_tenido, cliente_seleccionado)
    
    # Mostrar estadísticas y tabla filtrada
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['KG'].sum()
    
    st.write(f"TOTAL REGISTROS: {total_registros}")
    st.write(f"TOTAL KG: {total_kg:.0f}")
    
    styled_df = df_filtrado.style.apply(highlight_mofijado, axis=1).format({"KG": "{:.1f}"})
    st.write(styled_df, unsafe_allow_html=True)

# Sección 2: Partidas TEÑIDAS pero no APROBADAS
dias_con_tenido = st.number_input("Días entre TEÑIDO y el día actual (por defecto 5) Partidas que no llevan estampado", min_value=1, value=5)

if st.button("Mostrar partidas TEÑIDAS pero no APROBADAS") or st.session_state.df_con_tenido is not None:
    if st.session_state.df_con_tenido is None:
        st.session_state.df_con_tenido = get_partidas_con_tenido_sin_aprob_tela(dias_con_tenido)

    df_con_tenido = st.session_state.df_con_tenido
    
    # Selector de cliente
    clientes = ["Todos"] + sorted(df_con_tenido['Cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("Filtrar por cliente (Partidas TEÑIDAS pero no APROBADAS):", clientes, key='cliente_con_tenido')
    
    # Filtrar por cliente
    df_filtrado = filter_by_client(df_con_tenido, cliente_seleccionado)
    
    # Mostrar estadísticas y tabla filtrada
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['KG'].sum()
    
    st.write(f"TOTAL REGISTROS: {total_registros}")
    st.write(f"TOTAL KG: {total_kg:.0f}")
    
    st.write(df_filtrado)

# Sección 3: Partidas TEÑIDAS (estamp) pero no APROBADAS
dias_con_tenido_estamp = st.number_input("Días entre TEÑIDO y el día actual (por defecto 5) Partidas que llevan estampado", min_value=1, value=20)

if st.button("Mostrar partidas TEÑIDAS (estamp) pero no APROBADAS") or st.session_state.df_con_tenido_estamp is not None:
    if st.session_state.df_con_tenido_estamp is None:
        st.session_state.df_con_tenido_estamp = get_partidas_con_tenido_sin_aprob_tela_estamp(dias_con_tenido_estamp)

    df_con_tenido_estamp = st.session_state.df_con_tenido_estamp
    
    # Selector de cliente
    clientes = ["Todos"] + sorted(df_con_tenido_estamp['Cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("Filtrar por cliente (Partidas TEÑIDAS (estamp) pero no APROBADAS):", clientes, key='cliente_con_tenido_estamp')
    
    # Filtrar por cliente
    df_filtrado = filter_by_client(df_con_tenido_estamp, cliente_seleccionado)
    
    # Mostrar estadísticas y tabla filtrada
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['KG'].sum()
    
    st.write(f"TOTAL REGISTROS: {total_registros}")
    st.write(f"TOTAL KG: {total_kg:.0f}")
    
    st.write(df_filtrado)
