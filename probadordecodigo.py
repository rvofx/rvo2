import streamlit as st
import pandas as pd

def main():
    st.title("Excel Data Extractor")

    # File upload
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # Read the uploaded file
        df = pd.read_excel(uploaded_file)

        # Column selection
        columns_to_select = st.multiselect("Select the columns you want to extract", df.columns)

        if st.button("Extract Data"):
            # Filter the DataFrame based on the selected columns
            extracted_data = df[columns_to_select]

            # Download the extracted data as an Excel file
            st.download_button(
                label="Download Excel file",
                data=extracted_data.to_excel(index=False),
                file_name="extracted_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            st.success("Data extracted and downloaded successfully!")

if __name__ == "__main__":
    main()
