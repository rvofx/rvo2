import streamlit as st
import pandas as pd

def load_excel(file):
    return pd.read_excel(file)

def compare_excels(df1, df2):
    # Ordenar las filas para que el orden no importe
    df1_sorted = df1.sort_values(by=df1.columns.tolist()).reset_index(drop=True)
    df2_sorted = df2.sort_values(by=df2.columns.tolist()).reset_index(drop=True)
    
    # Comparar los DataFrames
    if df1_sorted.equals(df2_sorted):
        return "Los archivos son iguales."
    else:
        # Encontrar diferencias
        diff_df1 = df1_sorted[~df1_sorted.isin(df2_sorted).all(axis=1)]
        diff_df2 = df2_sorted[~df2_sorted.isin(df1_sorted).all(axis=1)]
        return diff_df1, diff_df2

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
        diff_df1, diff_df2 = result
        st.error("Los archivos tienen diferencias:")
        st.write("Filas en el primer archivo pero no en el segundo:")
        st.dataframe(diff_df1)
        st.write("Filas en el segundo archivo pero no en el primero:")
        st.dataframe(diff_df2)
