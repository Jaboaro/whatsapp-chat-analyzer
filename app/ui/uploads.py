"""
UI helpers for uploading and parsing WhatsApp chat exports.

This module is responsible for:
- Handling file upload via Streamlit
- Parsing the uploaded WhatsApp .txt file
- Managing Streamlit cache lifecycle when files change
- Stopping execution gracefully when no valid data is available
"""

from pathlib import Path
import pandas as pd
import streamlit as st
from io import BytesIO
import random

from parser.io import parse_chat_file as _parse_chat_file
from config.config import is_cloud
from ui.content import CLOUD_DISABLED_WARNING
from tools.chat_generator.profiles import ES_PROFILE

# Optional: import generator only if available
try:
    from tools.chat_generator.generator import generate_chat
except ImportError:
    generate_chat = None

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_CHAT_PATH = BASE_DIR / Path("data/sample_chats/sample_chat_es.txt")


DEMO_MODE = True


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


def _generate_sample_chat_bytes() -> BytesIO:
    """
    Generate a synthetic chat in memory and return it as BytesIO.
    """

    if generate_chat is None:
        # Fallback to static sample if generator missing
        return BytesIO(SAMPLE_CHAT_PATH.read_bytes())
    num_users = random.randint(2, 6)
    users = random.sample(
        ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"], num_users
    )
    chat_text = generate_chat(
        users=users,
        start_date=pd.Timestamp("2024-01-01"),
        days=random.randint(30, 365),
        avg_messages_per_day=random.randint(100, 300),
        export_profile=ES_PROFILE,
    )

    return BytesIO(chat_text.encode("utf-8"))


def load_chat() -> pd.DataFrame:
    """
    Handle WhatsApp chat upload and parsing lifecycle.
    Load a WhatsApp chat either from user upload or from a bundled sample.

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
    if "chat_source" not in st.session_state:
        st.session_state["chat_source"] = None

    if DEMO_MODE:
        st.warning(CLOUD_DISABLED_WARNING)

    uploaded_file = st.file_uploader(
        "Upload a WhatsApp .txt export",
        type=["txt"],
        disabled=DEMO_MODE,
        help="Disabled in demo mode (Streamlit Cloud deployment).",
    )
    if DEMO_MODE:
        # Defensive: if we're in demo mode, ignore any uploaded file and force sample chat
        uploaded_file = None

    col1, col2 = st.columns([1, 7])

    with col1:
        if st.button("Try default sample chat"):
            st.session_state["chat_source"] = "sample"

    with col2:
        if st.button("Generate new sample chat"):
            st.session_state["chat_source"] = "demo_generated"
            st.session_state["demo_chat_bytes"] = _generate_sample_chat_bytes()

    # Uploaded file takes precedence
    if uploaded_file is not None:
        st.session_state["chat_source"] = "upload"

    elif st.session_state["chat_source"] == "upload":
        # File was removed → reset
        st.session_state["chat_source"] = None

    chat_source = st.session_state.get("chat_source")

    if chat_source is None:
        st.info("Please upload a WhatsApp chat file to begin.")
        st.cache_data.clear()
        st.stop()

    match chat_source:
        case "sample":
            file_obj = SAMPLE_CHAT_PATH.open("rb")
            st.info("Loaded a synthetic sample chat (no real data).")

        case "upload":
            file_obj = uploaded_file

        case "demo_generated":
            file_obj = st.session_state.get("demo_chat_bytes")
            st.info("Generated synthetic sample chat (dynamic demo).")

        case _:
            st.stop()  # defensive, should never happen

    with st.spinner("Parsing chat..."):
        df, metadata = parse_chat_file(file_obj)

    if df.empty:
        st.error("No messages could be parsed from this file.")
        st.stop()

    return df
