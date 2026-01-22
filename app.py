import streamlit as st
import pandas as pd

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

st.title("WhatsApp Chat Analyzer")

st.markdown(
    """
    This App analyze your WhatsApp chat locally.
    **Your data are not saved nor sended to any server**
    """
)
uploaded_file = st.file_uploader("Upload your .txt file from WhatsApp")

if uploaded_file is not None:
    st.success("File successfully loaded")

    # Placeholder para parsing
    st.info("Parseando chat...")
    # df = parse_chat(uploaded_file)

    # Placeholder para resultados
    st.info("Mostrando análisis (MVP)")
