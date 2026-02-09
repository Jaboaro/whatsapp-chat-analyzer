import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from parser.whatsapp_parser import parse_chat_file
from parser.v2 import parse_chat_file as parse_chat_file_old
import time

# --------------------------------------------------
# File uploader
# --------------------------------------------------
st.subheader("Upload your chat")

uploaded_file = st.file_uploader("Upload a WhatsApp .txt export", type=["txt"], key=1)
uploaded_file2 = st.file_uploader("Upload a WhatsApp .txt export", type=["txt"], key=2)
if uploaded_file is None or uploaded_file2 is None:
    st.info("Please upload a WhatsApp chat file to begin.")
    st.stop()

# --------------------------------------------------
# Parsing
# --------------------------------------------------

with st.spinner("Parsing chat..."):
    init1 = time.time()
    df, stats = parse_chat_file(uploaded_file)
    print(df.head())
    end1 = time.time()
    print(f"New: {end1-init1}")

with st.spinner("Parsing chat2..."):
    init2 = time.time()
    df2, stats2 = parse_chat_file_old(uploaded_file2)
    end2 = time.time()

    print(f"Old: {end2-init2}")


# --------------------------------------------------
# Data overview
# --------------------------------------------------
st.subheader("Parsing summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Parsed mesagges", stats["parsed_messages"])
col2.metric("Multiline continuations", stats["multiline_messages"])
col3.metric("Inferred dates", stats["inferred_dates"])
col4.metric("Ignored lines", stats["ignored_lines"])
col1, col2, col3, col4 = st.columns(4)

st.dataframe(df)

col1.metric("Parsed mesagges", stats2["parsed_messages"])
col2.metric("Multiline continuations", stats2["multiline_messages"])
col3.metric("Inferred dates", stats2["inferred_dates"])
col4.metric("Ignored lines", stats2["ignored_lines"])


st.dataframe(df2)
print(df.dtypes)
