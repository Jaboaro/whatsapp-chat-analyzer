import pandas as pd
from datetime import date
from typing import Collection

from config.constants import TextFilterMode


def apply_base_filters(
    df: pd.DataFrame,
    users: Collection[str],
    start_date: pd.Timestamp | date,
    end_date: pd.Timestamp | date,
) -> pd.DataFrame:
    """
    Filter messages by participants and date range (inclusive).

    - `start_date` and `end_date` are interpreted as whole days
    - Time information in `datetime` is preserved
    """

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1)

    mask = df["sender"].isin(users) & df["datetime"].between(
        start_ts, end_ts, inclusive="left"
    )

    return df.loc[mask]


def apply_text_filter(
    df: pd.DataFrame,
    text: str | None,
    mode: TextFilterMode,
) -> pd.DataFrame:
    """
    Filter messages by text content.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing a 'message' column.
    text : str | None
        Text to filter by. If empty or None, no filtering is applied.
    mode : TextFilterMode
        Matching strategy.

    Returns
    -------
    pd.DataFrame
        Filtered dataframe.
    """
    required_columns = {"sender", "datetime"}
    missing = required_columns - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    if not text:
        return df

    messages = df["message"].astype(str)

    match mode:
        case "Contains":
            mask = messages.str.contains(text, case=False, na=False)
        case "Starts with":
            mask = messages.str.startswith(text, na=False)
        case "Exact match":
            mask = messages == text
        case "Regex":
            mask = messages.str.contains(text, regex=True, na=False)
        case _:
            # Defensive programming: should never happen if typed correctly
            raise ValueError(f"Unsupported text filter mode: {mode}")
    return df.loc[mask]
