import pandas as pd
import streamlit as st
from datetime import date
from config.constants import DATE_PRESETS, TEXT_FILTER_MODES, TextFilterMode, DatePreset
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class SidebarFilters:
    """
    Container for all sidebar filter values.

    This immutable dataclass groups all user-selected filters
    so they can be passed around the application as a single object.
    """

    users: list[str]
    start_date: date
    end_date: date
    text: str
    mode: TextFilterMode
    window_days: int


def resolve_date_range(
    range_preset: DatePreset, min_date: date, max_date: date
) -> Tuple[date, date]:
    """
    Resolve a date preset into a concrete (start_date, end_date) pair.

    Presets like "Last 7 days" are computed relative to the maximum
    date available in the dataset, not the current system date.

    Parameters
    ----------
    range_preset : DatePreset
        Selected date range preset.
    min_date : datetime.date
        Earliest date available in the dataset.
    max_date : datetime.date
        Latest date available in the dataset.

    Returns
    -------
    tuple[datetime.date, datetime.date]
        Start and end dates (inclusive).
    """
    match range_preset:
        case "All time":
            start_date, end_date = min_date, max_date
        case "Last 7 days":
            end_date = max_date
            start_date = max_date - pd.Timedelta(days=7)
        case "Last 30 days":
            end_date = max_date
            start_date = max_date - pd.Timedelta(days=30)
        case "Last 90 days":
            end_date = max_date
            start_date = max_date - pd.Timedelta(days=90)
        case "Custom":
            date_range = st.sidebar.date_input(
                "Custom date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
            if len(date_range) == 2:
                start_date, end_date = date_range
            elif len(date_range) == 1:
                start_date = end_date = date_range[0]
            else:
                start_date = min_date
                end_date = max_date
        case _:
            # Defensive programming: should never happen if typed correctly
            raise ValueError(f"Unsupported range preset: {range_preset}")

    return start_date, end_date


def render_sidebar(df: pd.DataFrame) -> SidebarFilters:
    """
    Render the sidebar UI and collect all filter values.

    This function is responsible only for user interaction
    and returns a structured object containing the selected filters.
    No data filtering is performed here.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw messages dataframe containing at least 'sender' and 'datetime'.

    Returns
    -------
    SidebarFilters
        Immutable container with all selected filter values.
    """
    st.sidebar.header("🔍 Filters")

    # Date filter
    min_date: date = df["datetime"].min().date()
    max_date: date = df["datetime"].max().date()

    range_preset = st.sidebar.selectbox(
        "Date range",
        DATE_PRESETS,
    )

    start_date, end_date = resolve_date_range(range_preset, min_date, max_date)

    # User filter
    selected_users = st.sidebar.multiselect(
        "Participants",
        options=sorted(df["sender"].unique()),
        default=sorted(df["sender"].unique()),
    )

    # Text filter
    st.sidebar.subheader("Message content")

    text_filter = st.sidebar.text_input("Text")
    filter_mode = st.sidebar.selectbox(
        "Filter mode",
        TEXT_FILTER_MODES,
    )

    window_days = st.sidebar.slider(
        "Rolling average window (days)",
        min_value=3,
        max_value=60,
        value=14,
        step=1,
        key="rolling_window",
    )
    # All sidebar state is returned as a single immutable object
    return SidebarFilters(
        users=selected_users,
        start_date=start_date,
        end_date=end_date,
        text=text_filter,
        mode=filter_mode,
        window_days=window_days,
    )
