import sys
from pathlib import Path

# -------------------------
# Ensure project root is in sys.path
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# -------------------------
# Standard imports
# -------------------------

import streamlit as st

from config.constants import MEDIA_PATTERNS
from filters.data_filters import apply_base_filters, apply_text_filter
from parser.io import parse_chat_file as _parse_chat_file

from ui.content import TITLE_CAPTION, EXPORTATION_STEPS, ABOUT_THIS_PROJECT
from ui.renders import (
    render_messages_by_sender,
    render_media_by_sender,
    render_weekday_charts,
    render_hour_chart,
    render_temporal_activity,
    render_activity_heatmap,
)
from ui.sidebar import render_sidebar
from ui.uploads import load_chat


# ---------------------------------------------------
# Cache
# ---------------------------------------------------
@st.cache_data(show_spinner=False)
def parse_chat_file(uploaded_file):
    return _parse_chat_file(uploaded_file)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# --------------------------------------------------
# Main Page
# --------------------------------------------------
st.title("📊 WhatsApp Chat Analyzer")
st.caption(TITLE_CAPTION)

with st.expander("How to export your WhatsApp chats"):
    st.markdown(EXPORTATION_STEPS)

st.subheader("Upload your chat")
raw_df = load_chat()

filters = render_sidebar(raw_df)

base_df = apply_base_filters(
    raw_df, filters.users, filters.start_date, filters.end_date
)

if base_df.empty:
    st.warning(
        f"""
        No messages found for:\n
        • Dates: {filters.start_date} → {filters.end_date}\n
        • Users: {", ".join(filters.users) if filters.users else "None"}
        """
    )
    st.stop()


content_df = apply_text_filter(base_df, filters.text, filters.mode)

st.subheader("Data overview")

col1, col2 = st.columns(2)

col1.metric("Total messages", len(raw_df))
col2.metric("Unique senders", raw_df["sender"].nunique())

# --------------------------------------------------
# User-level analysis
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_messages_by_sender(content_df)
with col2:
    render_media_by_sender(base_df, MEDIA_PATTERNS)
with col3:
    render_weekday_charts(content_df)
with col4:
    render_hour_chart(content_df)

with st.expander("Activity heatmap (weekday × hour)"):
    render_activity_heatmap(content_df)

render_temporal_activity(content_df, filters.window_days)

st.markdown("---")
st.markdown(ABOUT_THIS_PROJECT)
