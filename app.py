import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("📊 WhatsApp Chat Analyzer")

st.markdown(
    """
    Analyze your WhatsApp conversations with **robust parsing** and
    **clear temporal insights**, even when the exported data is messy.
    """
)

# --------------------------------------------------
# What does this app do?
# --------------------------------------------------
st.subheader("What does this app do?")

st.markdown(
    """
    This app allows you to:
    - Upload a WhatsApp chat export (`.txt`)
    - Automatically clean and parse your data
    - Visualize message activity over time and by user

    The focus of this project is not only analysis, but also **data quality
    and robustness**.
    """
)

# --------------------------------------------------
# Privacy notice
# --------------------------------------------------
st.info(
    """
    🔒 **Privacy notice**

    Your data is processed **locally in memory**.
    No chats are stored, logged, or sent to any external server.
    """
)

# --------------------------------------------------
# How to export WhatsApp chats
# --------------------------------------------------
with st.expander("How to export your WhatsApp chats"):
    st.markdown(
        """
        **On Android**
        1. Open the chat you want to export
        2. Tap the three dots (⋮) → *More* → *Export chat*
        3. Choose **Without media**
        4. Save or share the `.txt` file

        **On iOS**
        1. Open the chat
        2. Tap the contact or group name
        3. Tap *Export Chat*
        4. Choose **Without media**

        ⚠️ This app currently supports **text-only** exports.
        """
    )

# --------------------------------------------------
# File uploader
# --------------------------------------------------
st.subheader("Upload your chat")

uploaded_file = st.file_uploader("Upload a WhatsApp .txt export", type=["txt"])

# --------------------------------------------------
# Main logic placeholder
# --------------------------------------------------
if uploaded_file is not None:
    st.success("File uploaded successfully")

    with st.spinner("Parsing chat..."):
        # Placeholder for parser logic
        # df = parse_chat(uploaded_file)

        # Temporary mock DataFrame for layout/testing
        df = pd.DataFrame(
            {
                "datetime": pd.date_range("2025-01-01", periods=30, freq="D"),
                "sender": ["User A", "User B"] * 15,
                "message": ["Example message"] * 30,
            }
        )

    # --------------------------------------------------
    # Data overview
    # --------------------------------------------------
    st.subheader("Data overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total messages", len(df))
    col2.metric("Unique senders", df["sender"].nunique())
    col3.metric(
        "Date range", f"{df['datetime'].min().date()} → {df['datetime'].max().date()}"
    )

    # --------------------------------------------------
    # Filters
    # --------------------------------------------------
    st.subheader("Filters")

    min_date = df["datetime"].min().date()
    max_date = df["datetime"].max().date()

    date_range = st.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    selected_users = st.multiselect(
        "Select users",
        options=sorted(df["sender"].unique()),
        default=sorted(df["sender"].unique()),
    )

    # Apply filters (placeholder logic)
    filtered_df = df[
        (df["sender"].isin(selected_users))
        & (df["datetime"].dt.date >= date_range[0])
        & (df["datetime"].dt.date <= date_range[1])
    ]

    # --------------------------------------------------
    # Analysis section (placeholders)
    # --------------------------------------------------
    st.subheader("Analysis")

    st.markdown(
        """
        The following visualizations will be available in the MVP:
        - Messages per day
        - 14-day rolling average
        - Messages per user
        - Activity by hour of day
        """
    )

    st.warning(
        "Analysis visualizations are not implemented yet. "
        "This section is a placeholder for the MVP."
    )

else:
    st.warning("Please upload a WhatsApp `.txt` file to start the analysis.")

# --------------------------------------------------
# Footer / About
# --------------------------------------------------
st.markdown("---")
st.markdown(
    """
    **About this project**

    This is a portfolio project focused on:
    - Parsing messy real-world data
    - Temporal analysis of conversations
    - Building small, usable data applications

    Source code and documentation will be available on GitHub.
    """
)
