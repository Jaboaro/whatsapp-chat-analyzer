import re
from typing import Iterable, Tuple, Dict, Any

import pandas as pd


# --------------------------------------------------
# Regex patterns
# --------------------------------------------------

FULL_PATTERN = re.compile(
    r"^[\u200e\u200f\s]*"
    r"\[(\d{1,2}/\d{1,2}/\d{2}),\s"
    r"(\d{1,2}:\d{2}:\d{2})\]\s"
    r"([^:]+):\s(.*)$"
)

SHORT_PATTERN = re.compile(
    r"^[\u200e\u200f\s]*"
    r"\[(\d{1,2}/\d{1,2})\s"
    r"(\d{1,2}:\d{2})\]\s"
    r"([^:]+):\s(.*)$"
)

MESSAGE_START = re.compile(r"^[\u200e\u200f\s]*\[\d{1,2}/\d{1,2}")


# --------------------------------------------------
# Helpers
# --------------------------------------------------


def clean_line(line: str) -> str:
    """
    Remove invisible Unicode characters commonly found
    in WhatsApp exports and normalize line endings.
    """
    return (
        line.replace("\ufeff", "")  # BOM
        .replace("\u200e", "")
        .replace("\u200f", "")
        .rstrip("\n")
    )


# --------------------------------------------------
# Core parsing logic
# --------------------------------------------------


def parse_lines(lines: Iterable[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parse WhatsApp chat lines into a DataFrame.

    Parameters
    ----------
    lines : iterable of str
        Lines from a WhatsApp exported .txt file.

    Returns
    -------
    df : pandas.DataFrame
        Columns:
        - datetime
        - sender
        - message
        - inferred_date (bool)

    stats : dict
        Parsing statistics for data quality inspection.
    """

    data = []
    stats = {
        "total_lines": 0,
        "parsed_messages": 0,
        "multiline_messages": 0,
        "inferred_dates": 0,
        "ignored_lines": 0,
    }

    current_message = None
    last_datetime = None

    for raw_line in lines:
        stats["total_lines"] += 1
        line = clean_line(raw_line)

        # ------------------------------------------
        # 1. New message starts
        # ------------------------------------------
        if MESSAGE_START.match(line):

            if current_message is not None:
                data.append(current_message)
                stats["parsed_messages"] += 1

            m_full = FULL_PATTERN.match(line)
            m_short = SHORT_PATTERN.match(line)

            inferred = False

            if m_full:
                date, hour, sender, message = m_full.groups()
                dt = pd.to_datetime(f"{date} {hour}", format="%d/%m/%y %H:%M:%S")
                last_datetime = dt

            elif m_short and last_datetime is not None:
                day_month, hour, sender, message = m_short.groups()
                year = last_datetime.year
                dt = pd.to_datetime(
                    f"{day_month}/{year} {hour}", format="%d/%m/%Y %H:%M"
                )
                last_datetime = dt
                inferred = True
                stats["inferred_dates"] += 1

            else:
                current_message = None
                stats["ignored_lines"] += 1
                continue

            current_message = {
                "datetime": dt,
                "sender": sender,
                "message": message,
                "inferred_date": inferred,
            }

        # ------------------------------------------
        # 2. Multiline continuation
        # ------------------------------------------
        else:
            if current_message is not None:
                current_message["message"] += "\n" + line
                stats["multiline_messages"] += 1
            else:
                stats["ignored_lines"] += 1

    # ----------------------------------------------
    # Flush last message
    # ----------------------------------------------
    if current_message is not None:
        data.append(current_message)
        stats["parsed_messages"] += 1

    df = pd.DataFrame(data)

    return df, stats


# --------------------------------------------------
# Public API helpers
# --------------------------------------------------


def parse_chat_file(file_obj) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parse a WhatsApp chat from a file-like object
    (e.g. Streamlit UploadedFile).
    """
    lines = file_obj.read().decode("utf-8").splitlines(keepends=True)
    return parse_lines(lines)


def parse_chat_path(path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parse a WhatsApp chat from a filesystem path.
    """
    with open(path, encoding="utf-8") as f:
        return parse_lines(f)
