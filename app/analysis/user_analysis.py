"""
User-based analysis of WhatsApp messages.

Provides functions to:
- Count messages per user
- Analyze daily activity per user
- Compute user participation shares
- Count media-related messages per user
"""

import pandas as pd
from typing import Optional
from collections.abc import Mapping, Sequence


def messages_per_user(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count total number of messages per sender.


    Parameters
    ----------
    df : pandas.DataFrame
    Parsed WhatsApp messages. Must contain a `sender` column.


    Returns
    -------
    pandas.DataFrame
    Index: sender
    Columns:
    - message_count
    """
    if "sender" not in df.columns:
        raise ValueError("DataFrame must contain a 'sender' column")
    per_user = (
        df.groupby("sender")
        .size()
        .rename("message_count")
        .to_frame()
        .sort_values("message_count", ascending=False)
    )
    return per_user


def messages_per_day_by_user(
    df: pd.DataFrame,
    sender: Optional[str] = None,
) -> pd.DataFrame:
    """
    Aggregate number of messages per day, optionally filtered by sender.


    Parameters
    ----------
    df : pandas.DataFrame
    Parsed WhatsApp messages. Must contain `datetime` and `sender` columns.


    sender : str, optional
    If provided, only messages from this sender are included.


    Returns
    -------
    pandas.DataFrame
    Index: date
    Columns:
    - message_count
    """
    required_columns = {"datetime", "sender"}
    if not required_columns.issubset(df.columns):
        raise ValueError("DataFrame must contain 'datetime' and 'sender' columns")

    filtered = df
    if sender is not None:
        filtered = df[df["sender"] == sender]

    daily = (
        filtered.assign(date=filtered["datetime"].dt.date)
        .groupby("date")
        .size()
        .rename("message_count")
        .to_frame()
        .sort_index()
    )

    return daily


def user_share(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the percentage of messages sent by each user.


    Parameters
    ----------
    df : pandas.DataFrame
    Parsed WhatsApp messages.


    Returns
    -------
    pandas.DataFrame
    Index: sender
    Columns:
    - message_count
    - percentage
    """
    counts = messages_per_user(df)
    total = counts["message_count"].sum()

    result = counts.copy()
    result["percentage"] = 100 * result["message_count"] / total

    return result


# --------------------------------------------------
# Media usage by user
# --------------------------------------------------


def media_counts_by_user(
    df: pd.DataFrame,
    media_patterns: Mapping[str, Sequence[str]],
    message_col: str = "message",
    user_col: str = "sender",
) -> pd.DataFrame:
    """
    Count media messages (images, stickers, etc.) per user.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed WhatsApp messages.
    media_patterns : dict
        Dict like { "Images": ["image omitted", ...], ... }
    message_col : str
        Column containing message text.
    user_col : str
        Column containing sender names.

    Returns
    -------
    pd.DataFrame
        Index: sender
        Columns: media types
    """
    messages = df[message_col].str.lower()

    result = pd.DataFrame(index=df[user_col].unique())

    for media_type, patterns in media_patterns.items():
        mask = messages.apply(lambda msg: any(p in msg for p in patterns))
        counts = df[mask].groupby(user_col).size()
        result[media_type] = counts

    return result.fillna(0).astype(int)
