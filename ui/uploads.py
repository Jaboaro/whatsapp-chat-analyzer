"""
UI helpers for uploading and parsing WhatsApp chat exports.

This module is responsible for:
- Handling file upload via Streamlit
- Parsing the uploaded WhatsApp .txt file
- Managing Streamlit cache lifecycle when files change
- Stopping execution gracefully when no valid data is available
"""

import pandas as pd
import streamlit as st

from parser.io import parse_chat_file as _parse_chat_file


@st.cache_data(show_spinner=False)
def parse_chat_file(uploaded_file):
    """
    Parse a WhatsApp chat export file with Streamlit caching.

    This function is a thin, cache-enabled wrapper around the core
    `parser.whatsapp_parser.parse_chat_file` function.

    Caching is used to avoid re-parsing the same uploaded file across
    Streamlit reruns.

    Parameters
    ----------
    uploaded_file : UploadedFile
        File uploaded via `st.file_uploader`.

    Returns
    -------
    tuple[pd.DataFrame, dict]
        - Parsed messages dataframe
        - Optional metadata extracted during parsing
    """
    return _parse_chat_file(uploaded_file)


def load_chat() -> pd.DataFrame:
    """
    Handle WhatsApp chat upload and parsing lifecycle.

    This function:
    - Prompts the user to upload a `.txt` WhatsApp export
    - Clears cached data when no file is uploaded
    - Parses the file with a user-visible spinner
    - Stops Streamlit execution if parsing fails or yields no messages

    Returns
    -------
    pd.DataFrame
        Parsed chat messages dataframe.

    Streamlit Behavior
    ------------------
    - Calls `st.stop()` if no file is uploaded
    - Calls `st.stop()` if parsing produces an empty dataframe
    """
    uploaded_file = st.file_uploader("Upload a WhatsApp .txt export", type=["txt"])

    if uploaded_file is None:
        st.info("Please upload a WhatsApp chat file to begin.")
        st.cache_data.clear()
        st.stop()

    with st.spinner("Parsing chat..."):
        df, metadata = parse_chat_file(uploaded_file)

    if df.empty:
        st.error("No messages could be parsed from this file.")
        st.stop()

    return df
