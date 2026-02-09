import streamlit as st
import plotly.express as px
from pandas import DataFrame
from collections.abc import Mapping, Sequence

from analysis.user_analysis import messages_per_user, media_counts_by_user
from analysis.time_analysis import daily_activity_with_trend
from analysis.weekly_analysis import (
    messages_by_weekday,
    messages_by_hour,
    weekday_hour_matrix,
)


def _clean_axes(fig):
    fig.update_xaxes(showgrid=False, showline=False, ticks="", title=None)
    fig.update_yaxes(showgrid=False, showline=False, ticks="", title=None)
    return fig


def render_messages_by_sender(df: DataFrame) -> None:
    """
    Render a pie chart showing the distribution of messages by sender.

    This visualization reflects the relative participation of each user
    in the conversation, based on the number of messages sent.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing at least a 'sender' column.
        Typically filtered by date, users and optionally message content.
    """
    if df.empty:
        st.info("No messages match the selected filters.")
        return
    per_user_df = messages_per_user(df).reset_index()
    per_user_df = per_user_df.sort_values("sender")
    fig = px.pie(
        per_user_df,
        title="Messages by sender",
        values="message_count",
        names="sender",
        category_orders={"sender": sorted(per_user_df["sender"])},
        height=300,
    )
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=0))
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>")
    st.plotly_chart(fig, width="stretch")


def render_media_by_sender(
    df: DataFrame, media_patterns: Mapping[str, Sequence[str]]
) -> None:
    """
    Render a grouped bar chart showing media messages by sender.

    Media types (images, videos, audios, stickers, etc.) are detected
    by matching message content against language-dependent patterns.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame filtered by base filters (date range and users).
        Message content filtering is intentionally not applied here.
    media_patterns : dict[str, list[str]]
        Mapping of media category names to lists of string patterns
        used to identify each media type.
    """
    if df.empty:
        st.info("No media messages in the selected filters.")
        return
    media_counts = media_counts_by_user(df, media_patterns)
    media_counts = media_counts.sort_index(axis=0)
    media_counts = media_counts[sorted(media_counts.columns)]
    fig = px.bar(media_counts.T, height=320, title="Media by sender")
    fig.update_layout(
        barmode="group",
        bargap=0.15,
        margin=dict(l=20, r=20, t=30, b=0),
        legend_title_text=None,
    )
    fig = _clean_axes(fig)
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>User: %{fullData.name}<br>Count: %{y}<extra></extra>"
    )
    st.plotly_chart(fig, width="stretch")


def render_weekday_charts(df: DataFrame) -> None:
    """
    Render a bar chart showing message activity by weekday.

    The chart aggregates messages across all weeks, providing insight
    into which days of the week are more active overall.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing a 'datetime' column.
        Usually filtered by users, date range and optionally text.
    """
    if df.empty:
        st.info("No messages in the selected filters.")
        return

    weekly_df = messages_by_weekday(df)

    fig = px.bar(weekly_df["message_count"], height=350, title="Messages by weekday")
    fig.update_layout(
        barmode="group",
        bargap=0.15,
        margin=dict(l=20, r=20, t=30, b=0),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, showline=False, ticks="", title=None)
    fig.update_yaxes(showgrid=False, showline=False, ticks="", title=None)
    fig.update_traces(hovertemplate="Count: %{y}<extra></extra>")
    st.plotly_chart(fig, width="stretch")


def render_hour_chart(df: DataFrame) -> None:
    """
    Render a bar chart showing message activity by hour of day.

    Useful for identifying daily activity patterns, such as
    peak chatting hours.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing a 'datetime' column.
        Usually filtered by users, date range and optionally text.
    """
    if df.empty:
        st.info("No messages in the selected filters.")
        return
    hourly_df = messages_by_hour(df)
    fig = px.bar(
        hourly_df["message_count"], height=320, title="Messages by hour of day"
    )
    fig.update_layout(
        barmode="group",
        bargap=0.15,
        margin=dict(l=20, r=20, t=30, b=0),
        showlegend=False,
    )
    fig = _clean_axes(fig)
    fig.update_traces(hovertemplate="Count: %{y}<extra></extra>")
    st.plotly_chart(fig, width="stretch")


def render_temporal_activity(
    df: DataFrame,
    window_days: int,
    min_num_coincidences=100,
) -> None:
    """
    Render message activity over time as a bar chart with optional trend line.

    Daily message counts are displayed as bars. A rolling average trend line
    is overlaid only if the number of data points is sufficiently large,
    to avoid misleading smoothing on sparse data.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing a 'datetime' column.
        Typically filtered by users, date range and message content.
    window_days : int
        Window size (in days) used to compute the rolling average.
    min_num_coincidences : int, default=100
        Minimum number of daily observations required to display
        the rolling mean line.
    """
    if df.empty:
        st.info("No messages to display for the selected range.")
        return

    daily_df = daily_activity_with_trend(df, window_days=window_days)

    fig = px.bar(daily_df["message_count"], opacity=0.4)
    if len(daily_df) >= min_num_coincidences:
        line_fig = px.line(daily_df["rolling_mean"])
        line_fig.update_traces(line_color="red")

        for trace in line_fig.data:
            fig.add_traces(trace)

    fig.update_layout(
        title="Message activity over time",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        hovermode="x unified",
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, showline=False, ticks="", title=None)
    fig.update_yaxes(showgrid=False, title=None)
    fig.update_traces(hovertemplate="%{y}<extra></extra>")
    st.plotly_chart(fig, width="stretch")


def render_activity_heatmap(df: DataFrame) -> None:
    """
    Render a heatmap of message activity by weekday and hour of day.

    This visualization highlights temporal patterns combining both
    day of the week and hour of the day, making it easy to spot
    recurring activity hotspots.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing a 'datetime' column.
        Usually filtered by users, date range and optionally text.
    """
    if df.empty:
        st.info("No messages in the selected filters.")
        return
    heatmap_df = weekday_hour_matrix(df)
    fig = px.imshow(
        heatmap_df,
        labels=dict(x="Hour of day", y="Day of week", color="Number of messages"),
        x=heatmap_df.columns,
        y=heatmap_df.index,
        color_continuous_scale="blues",
    )
    fig.update_layout(
        title="Activity heatmap (weekday × hour)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, width="stretch")
