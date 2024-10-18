import streamlit as st
import pyodbc
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# función para conectar a sql server
def connect_to_db():
    conn = pyodbc.connect(
        "driver={odbc driver 17 for sql server};"
        "server=" + st.secrets["server"] + ";"
        "database=" + st.secrets["database"] + ";"
        "uid=" + st.secrets["username"] + ";"
        "pwd=" + st.secrets["password"] + ";"
    )
    return conn

# consultas (sin cambios, omitidas para brevity)

# nueva función para filtrar por cliente
def filter_by_client(df, client):
    if client == "todos":
        return df
    return df[df['cliente'] == client]

# interfaz de streamlit
st.title("seguimiento de partidas")

# Inicializar session state
if 'dias_sin_tenido' not in st.session_state:
    st.session_state.dias_sin_tenido = 8
if 'dias_con_tenido' not in st.session_state:
    st.session_state.dias_con_tenido = 5
if 'dias_con_tenido_estamp' not in st.session_state:
    st.session_state.dias_con_tenido_estamp = 20

# estilos personalizados
st.markdown("""
    <style>
    .input-number-box {
        width: 100px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# sección 1: partidas no teñidas
st.session_state.dias_sin_tenido = st.number_input("días sin teñir (por defecto 8)", min_value=1, value=st.session_state.dias_sin_tenido)

if st.button("mostrar partidas no teñidas"):
    df_sin_tenido = get_partidas_sin_tenido(st.session_state.dias_sin_tenido)

    # selector de cliente
    clientes = ["todos"] + sorted(df_sin_tenido['cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("filtrar por cliente (partidas no teñidas):", clientes)

    # filtrar por cliente
    df_filtrado = filter_by_client(df_sin_tenido, cliente_seleccionado)

    # mostrar estadísticas y tabla filtrada
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['kg'].sum()

    st.write(f"total registros: {total_registros}")
    st.write(f"total kg: {total_kg:.0f}")

    styled_df = df_filtrado.style.apply(highlight_mofijado, axis=1).format({"kg": "{:.1f}"})
    st.write(styled_df, unsafe_allow_html=True)

# sección 2: partidas teñidas pero no aprobadas
st.session_state.dias_con_tenido = st.number_input("días entre teñido y el día actual (por defecto 5) partidas que no llevan estampado", min_value=1, value=st.session_state.dias_con_tenido)

if st.button("mostrar partidas teñidas pero no aprobadas"):
    df_con_tenido = get_partidas_con_tenido_sin_aprob_tela(st.session_state.dias_con_tenido)

    # selector de cliente
    clientes = ["todos"] + sorted(df_con_tenido['cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("filtrar por cliente (partidas teñidas pero no aprobadas):", clientes)

    # filtrar por cliente
    df_filtrado = filter_by_client(df_con_tenido, cliente_seleccionado)

    # mostrar estadísticas y tabla filtrada
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['kg'].sum()

    st.write(f"total registros: {total_registros}")
    st.write(f"total kg: {total_kg:.0f}")

    st.write(df_filtrado)

# sección 3: partidas teñidas (estamp) pero no aprobadas
st.session_state.dias_con_tenido_estamp = st.number_input("días entre teñido y el día actual (por defecto 20) partidas que llevan estampado", min_value=1, value=st.session_state.dias_con_tenido_estamp)

if st.button("mostrar partidas teñidas (estamp) pero no aprobadas"):
    df_con_tenido_estamp = get_partidas_con_tenido_sin_aprob_tela_estamp(st.session_state.dias_con_tenido_estamp)

    # selector de cliente
    clientes = ["todos"] + sorted(df_con_tenido_estamp['cliente'].unique().tolist())
    cliente_seleccionado = st.selectbox("filtrar por cliente (partidas teñidas (estamp) pero no aprobadas):", clientes)

    # filtrar por cliente
    df_filtrado = filter_by_client(df_con_tenido_estamp, cliente_seleccionado)

    # mostrar estadísticas y tabla filtrada
    total_registros = len(df_filtrado)
    total_kg = df_filtrado['kg'].sum()

    st.write(f"total registros: {total_registros}")
    st.write(f"total kg: {total_kg:.0f}")

    st.write(df_filtrado)
