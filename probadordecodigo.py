import streamlit as st
import pandas as pd
import numpy as np
import io

def process_excel(df, pattern_columns, repeat_columns, transpose_columns):
    # Determine pattern length
    pattern_length = len(pattern_columns)
    
    # Create a new DataFrame to store the processed data
    new_df = pd.DataFrame()
    
    # Process each group of rows based on the pattern length
    for i in range(0, len(df), pattern_length):
        group = df.iloc[i:i+pattern_length]
        
        # Add repeated columns
        for col in repeat_columns:
            if col in group.columns:
                new_df[col] = group[col].iloc[0]
            else:
                st.error(f"Column '{col}' not found in the input data.")
                return None
        
        # Add transposed columns
        for k, col in enumerate(transpose_columns):
            if col in group.columns:
                transposed = group[col].tolist()
                new_df = pd.concat([new_df, pd.DataFrame({f"{col}_{i+1}": [value] for i, value in enumerate(transposed)})], axis=1)
            else:
                st.error(f"Column '{col}' not found in the input data.")
                return None
    
    return new_df

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
        if pattern_columns and repeat_columns and transpose_columns:
            result_df = process_excel(df, pattern_columns, repeat_columns, transpose_columns)
            if result_df is not None:
                st.write("Processed Data:")
                st.dataframe(result_df)

                # Create a download button for the processed Excel
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
            st.error("Please select at least one pattern column, one repeat column, and one column to transpose.")
