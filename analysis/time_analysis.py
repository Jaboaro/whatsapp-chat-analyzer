import pandas as pd
from typing import Optional

# --------------------------------------------------
# Temporal aggregations
# --------------------------------------------------


def messages_per_day(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate number of messages per calendar day.


    Parameters
    ----------
    df : pandas.DataFrame
    Parsed WhatsApp messages. Must contain a `datetime` column.


    Returns
    -------
    pandas.DataFrame
    Index: date
    Columns:
    - message_count
    """
    if "datetime" not in df.columns:
        raise ValueError("DataFrame must contain a 'datetime' column")

    daily = (
        df.assign(date=df["datetime"].dt.date)
        .groupby("date")
        .size()
        .rename("message_count")
        .to_frame()
        .sort_index()
    )

    return daily


# --------------------------------------------------
# Smoothing / rolling metrics
# --------------------------------------------------
def rolling_mean(
    daily_df: pd.DataFrame,
    window_days: int = 14,
    min_periods: Optional[int] = None,
) -> pd.DataFrame:
    """
    Compute a rolling mean over daily message counts.


    Parameters
    ----------
    daily_df : pandas.DataFrame
    Output of `messages_per_day`, indexed by date and
    containing a `message_count` column.


    window_days : int, default 14
    Size of the rolling window in days.


    min_periods : int, optional
    Minimum number of observations required to compute a value.
    Defaults to `window_days`.


    Returns
    -------
    pandas.DataFrame
    Same index as input with an additional column:
    - rolling_mean
    """
    if "message_count" not in daily_df.columns:
        raise ValueError("DataFrame must contain a 'message_count' column")

    if min_periods is None:
        min_periods = window_days

    result = daily_df.copy()
    result["rolling_mean"] = (
        result["message_count"]
        .rolling(window=window_days, min_periods=min_periods)
        .mean()
    )

    return result


# --------------------------------------------------
# Convenience pipeline
# --------------------------------------------------


def daily_activity_with_trend(
    df: pd.DataFrame,
    window_days: int = 14,
) -> pd.DataFrame:
    """
    Full pipeline to compute daily activity and its rolling trend.


    Parameters
    ----------
    df : pandas.DataFrame
    Parsed WhatsApp messages.


    window_days : int, default 14
    Rolling window size for smoothing.


    Returns
    -------
    pandas.DataFrame
    Columns:
    - message_count
    - rolling_mean
    """
    daily = messages_per_day(df)
    daily = rolling_mean(daily, window_days=window_days)
    return daily
