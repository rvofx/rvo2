import streamlit as st
import pandas as pd

# Create the Streamlit app
st.title("Order Data Explorer")

# Request the user to provide the Excel file
st.write("Please upload the order data Excel file:")
uploaded_file = st.file_uploader("", type=['xlsx', 'xls'], accept_multiple_files=False)

if uploaded_file is not None:
    # Load the data from the uploaded file
    df = pd.read_excel(uploaded_file)

    # Allow the user to select the order
    order_num = st.selectbox("Select Order", df['ORDEN'].unique())

    # Filter the data for the selected order
    order_data = df[df['ORDEN'] == order_num]

    # Display the order details
    st.subheader(f"Order {order_num}")
    st.write(order_data)

    # Allow the user to download the data
    if st.button("Download Data"):
        st.download_button(
            label="Download data as CSV",
            data=order_data.to_csv(index=False),
            file_name='order_data.csv',
            mime='text/csv',
        )
else:
    st.write("Please upload the Excel file to continue.")
