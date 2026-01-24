import pandas as pd

import pandas as pd


# --------------------------------------------------
# Weekly and hourly activity patterns
# --------------------------------------------------


def messages_by_weekday(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate number of messages by day of the week.

    Parameters
    ----------
    df : pandas.DataFrame
        Parsed WhatsApp messages. Must contain a `datetime` column.

    Returns
    -------
    pandas.DataFrame
        Index: weekday (Monday -> Sunday)
        Columns:
        - message_count
    """
    if "datetime" not in df.columns:
        raise ValueError("DataFrame must contain a 'datetime' column")

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    result = (
        df.assign(weekday=df["datetime"].dt.day_name())
        .groupby("weekday")
        .size()
        .reindex(weekday_order)
        .rename("message_count")
        .to_frame()
    )

    return result


# --------------------------------------------------
# Hourly activity
# --------------------------------------------------


def messages_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate number of messages by hour of the day.

    Parameters
    ----------
    df : pandas.DataFrame
        Parsed WhatsApp messages. Must contain a `datetime` column.

    Returns
    -------
    pandas.DataFrame
        Index: hour (0-23)
        Columns:
        - message_count
    """
    if "datetime" not in df.columns:
        raise ValueError("DataFrame must contain a 'datetime' column")

    result = (
        df.assign(hour=df["datetime"].dt.hour)
        .groupby("hour")
        .size()
        .rename("message_count")
        .to_frame()
        .sort_index()
    )

    return result


# --------------------------------------------------
# Weekday x hour heatmap matrix
# --------------------------------------------------


def weekday_hour_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a weekday x hour matrix of message counts.

    Parameters
    ----------
    df : pandas.DataFrame
        Parsed WhatsApp messages.

    Returns
    -------
    pandas.DataFrame
        Index: weekday (Monday -> Sunday)
        Columns: hour (0-23)
        Values: message counts
    """
    if "datetime" not in df.columns:
        raise ValueError("DataFrame must contain a 'datetime' column")

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    matrix = (
        df.assign(
            weekday=df["datetime"].dt.day_name(),
            hour=df["datetime"].dt.hour,
        )
        .groupby(["weekday", "hour"])
        .size()
        .unstack(fill_value=0)
        .reindex(weekday_order)
    )

    return matrix
