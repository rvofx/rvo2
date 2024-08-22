import streamlit as st
import pandas as pd

def load_excel(file):
    return pd.read_excel(file)

def compare_excels(df1, df2):
    if df1.equals(df2):
        return "Los archivos son iguales."
    else:
        diff = df1.compare(df2)
        return diff

st.title("Comparador de Archivos Excel")

# Carga de los archivos
uploaded_file1 = st.file_uploader("Cargar primer archivo Excel", type=["xlsx"])
uploaded_file2 = st.file_uploader("Cargar segundo archivo Excel", type=["xlsx"])

if uploaded_file1 and uploaded_file2:
    df1 = load_excel(uploaded_file1)
    df2 = load_excel(uploaded_file2)

    result = compare_excels(df1, df2)

    if isinstance(result, str):
        st.success(result)
    else:
        st.error("Los archivos tienen diferencias:")
        st.dataframe(result)
