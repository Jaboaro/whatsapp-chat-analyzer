import pandas as pd
from typing import Optional


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
