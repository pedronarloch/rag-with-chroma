import streamlit as st

ticker = st.text_input("Ticker", placeholder="e.g. BBAS3")
list_of_files = st.file_uploader("Upload the document", type="pdf")

if st.button("Upload Documents"):
    st.write("Hit the API!")
