import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from parser.whatsapp_parser import parse_chat_file
from analysis.time_analysis import daily_activity_with_trend
from analysis.user_analysis import messages_per_user, messages_per_day_by_user
from analysis.weekly_analysis import (
    messages_by_weekday,
    messages_by_hour,
    weekday_hour_matrix,
)

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
    This app allows you to explore **temporal patterns** in your WhatsApp chats.


    **Your data is never stored**: all processing happens locally in your browser session.


    ### What can you do with this app?
    - Upload a WhatsApp exported `.txt` chat
    - See how message activity evolves over time
    - Apply smoothing to reveal long-term trends
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

if uploaded_file is None:
    st.info("Please upload a WhatsApp chat file to begin.")
    st.stop()

# --------------------------------------------------
# Parsing
# --------------------------------------------------

with st.spinner("Parsing chat..."):
    df, stats = parse_chat_file(uploaded_file)

if df.empty:
    st.error("No messages could be parsed from this file.")
    st.stop()

# --------------------------------------------------
# Data overview
# --------------------------------------------------
st.subheader("Parsing summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Parsed mesagges", stats["parsed_messages"])
col2.metric("Multiline continuations", stats["multiline_messages"])
col3.metric("Inferred dates", stats["inferred_dates"])
col4.metric("Ignored lines", stats["ignored_lines"])

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
# User-level analysis
# --------------------------------------------------


st.subheader("👥 Participants overview")


per_user_df = messages_per_user(df)
st.bar_chart(per_user_df["message_count"])


users = per_user_df.index.tolist()


selected_user = st.selectbox(
    "Select a participant for temporal analysis",
    options=["All"] + users,
)


# --------------------------------------------------
# Temporal analysis controls
# --------------------------------------------------


st.subheader("📈 Message activity over time")


window_days = st.slider(
    "Rolling average window (days)",
    min_value=3,
    max_value=60,
    value=14,
    step=1,
)


# --------------------------------------------------
# Temporal analysis
# --------------------------------------------------


with st.spinner("Computing temporal analysis..."):
    if selected_user == "All":
        daily_df = daily_activity_with_trend(df, window_days=window_days)
    else:
        user_daily = messages_per_day_by_user(df, sender=selected_user)
        daily_df = daily_activity_with_trend(
            user_daily.reset_index().rename(columns={"date": "datetime"}),
            window_days=window_days,
        )


# --------------------------------------------------
# Visualization
# --------------------------------------------------


st.bar_chart(
    daily_df["message_count"],
    height=300,
)


st.line_chart(
    daily_df["rolling_mean"],
    height=300,
)

# --------------------------------------------------
# Weekly & hourly patterns
# --------------------------------------------------

st.subheader("🗓️ Weekly and hourly patterns")

weekly_df = messages_by_weekday(df)
hourly_df = messages_by_hour(df)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Messages by weekday**")
    st.bar_chart(weekly_df["message_count"])

with col2:
    st.markdown("**Messages by hour of day**")
    st.bar_chart(hourly_df["message_count"])

# --------------------------------------------------
# Weekday x hour heatmap (data view)
# --------------------------------------------------

# --------------------------------------------------
# Weekday x hour heatmap
# --------------------------------------------------

st.subheader("🔥 Activity heatmap (weekday × hour)")

heatmap_df = weekday_hour_matrix(df)

fig, ax = plt.subplots(figsize=(14, 4))

im = ax.imshow(
    heatmap_df.values,
    aspect="auto",
    interpolation="nearest",
)

# Axis labels
ax.set_xlabel("Hour of day")
ax.set_ylabel("Day of week")

# Ticks
ax.set_xticks(np.arange(len(heatmap_df.columns)))
ax.set_xticklabels(heatmap_df.columns)

ax.set_yticks(np.arange(len(heatmap_df.index)))
ax.set_yticklabels(heatmap_df.index)

# Colorbar
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Number of messages")

plt.tight_layout()
st.pyplot(fig)
# --------------------------------------------------
# Raw data (optional)
# --------------------------------------------------


with st.expander("Show aggregated data"):
    st.dataframe(daily_df)
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
