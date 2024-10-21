import streamlit as st
import pandas as pd
import numpy as np
import io

def process_excel(df, pattern_columns, repeat_columns, transpose_columns):
    # [El código de la función process_excel permanece igual]
    # ...

st.title("Excel Processor")

uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("Original Data:")
    st.dataframe(df)

    columns = df.columns.tolist()

    pattern_columns = st.multiselect(
        "Select columns that form the repeating pattern:",
        columns
    )

    repeat_columns = st.multiselect(
        "Select columns to repeat in all lines:",
        columns
    )

    transpose_columns = st.multiselect(
        "Select columns to transpose:",
        columns
    )

    if st.button("Process Excel"):
        if pattern_columns and repeat_columns:
            result_df = process_excel(df, pattern_columns, repeat_columns, transpose_columns)
            st.write("Processed Data:")
            st.dataframe(result_df)

            # Crear un botón de descarga para el Excel procesado
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                result_df.to_excel(writer, index=False, sheet_name='Processed Data')
            output.seek(0)
            
            st.download_button(
                label="Download processed Excel file",
                data=output,
                file_name="processed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Please select at least one pattern column and one repeat column.")
