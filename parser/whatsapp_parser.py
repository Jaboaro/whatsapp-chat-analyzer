import re
import os
import platform
from typing import Iterable, List, Optional, Tuple, Dict
from datetime import datetime
import pandas as pd
from parser.path_validation import is_valid_directory_path, PathStyle
import time

# --------------------------------------------------
# Regex patterns
# --------------------------------------------------

FULL_PATTERN = re.compile(
    r"^[\u200e\u200f\s]*"
    r"\[(\d{1,2}/\d{1,2}/\d{2}),\s"
    r"(\d{1,2}:\d{2}:\d{2})\]\s"
    r"([^:]+):\s(.*)$",
    re.DOTALL,
)


SHORT_PATTERN = re.compile(
    r"^[\u200e\u200f\s]*"
    r"\[(\d{1,2}/\d{1,2})\s"
    r"(\d{1,2}:\d{2})\]\s"
    r"([^:]+):\s(.*)$",
    re.DOTALL,
)

MESSAGE_START = re.compile(r"^[\u200e\u200f\s]*\[")


# --------------------------------------------------
# Utilities
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
# Phase 1 - Message segmentation
# --------------------------------------------------


def segment_messages(lines: Iterable[str]) -> Tuple[List[str], Dict[str, int]]:
    """
    Group raw lines into full WhatsApp message blocks.

    Parameters
    ----------
    lines : iterable of str
        Raw lines from a WhatsApp exported chat file.

    Returns
    -------
    list of str
        Each element is a full message block (including multi-line messages).
    """
    messages: List[str] = []
    current: List[str] = []
    stats = {"total_lines": 0, "parsed_messages": 0, "multiline_messages": 0}
    previous_line_message_start = False
    for raw_line in lines:
        stats["total_lines"] += 1
        line = clean_line(raw_line)

        if MESSAGE_START.match(line):
            stats["parsed_messages"] += 1
            if current:
                messages.append("\n".join(current))
            current = [line]
            previous_line_message_start = True
        else:
            if current:
                current.append(line)
            if previous_line_message_start:
                stats["multiline_messages"] += 1
                previous_line_message_start = False

    if current:
        messages.append("\n".join(current))
    return messages, stats


# --------------------------------------------------
# Phase 2 — Message parsing
# --------------------------------------------------


def parse_message_block(
    block: str,
    last_datetime: Optional[datetime],
    detect_quoted: bool = True,
) -> Tuple[Optional[dict], Optional[datetime], Tuple[int, int], bool]:
    """
    Parse a full WhatsApp message block into structured data.

    Parameters
    ----------
    block : str
        Full message block (possibly multi-line).
    last_datetime : pandas.Timestamp or None
        Datetime of the previous successfully parsed message.

    Returns
    -------
    tuple
        (parsed_message_dict or None, updated_last_datetime)
    """
    m_full = FULL_PATTERN.match(block)
    inferred_dates: int = 0
    ignored_messages: int = 0
    inferred: bool = False

    if m_full:
        date, hour, sender, message = m_full.groups()
        dt = datetime.strptime(f"{date} {hour}", "%d/%m/%y %H:%M:%S")

        return (
            {
                "datetime": dt,
                "sender": sender,
                "message": message,
                "quoted_message": False,
            },
            dt,
            (inferred_dates, ignored_messages),
            False,
        )
    m_short = SHORT_PATTERN.match(block)
    if m_short and last_datetime is not None:
        day_month, hour, sender, message = m_short.groups()
        day, month = day_month.split("/")
        year = last_datetime.year
        dt = datetime.strptime(
            f"{day.zfill(2)}/{month.zfill(2)}/{year} {hour}:00", "%d/%m/%Y %H:%M:%S"
        )

        # quoted heuristic
        if detect_quoted and dt < last_datetime:
            return (
                {
                    "datetime": last_datetime,
                    "sender": sender,
                    "message": message,
                },
                last_datetime,
                (0, 0),
                True,
            )

        inferred_dates += 1
        inferred = True
        return (
            {
                "datetime": dt,
                "sender": sender,
                "message": message,
                "quoted_message": False,
            },
            dt,
            (inferred_dates, ignored_messages),
            False,
        )
    ignored_messages += 1
    return None, last_datetime, (inferred_dates, ignored_messages), False


# --------------------------------------------------
# Public API helpers
# --------------------------------------------------
def parse_chat(
    lines: Iterable[str], detect_quoted: bool = True
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Parse a WhatsApp chat from an interable string, each element a line in format chat.txt

    Parameters
    ----------
    lines : a string iterable

    Returns
    -------
    pandas.DataFrame
        Columns: datetime, sender, message
    Dict[str,int]
        Dictionary with statistics about parsing
        Keys: "total_lines", "parsed_messages", "multiline_messages", "inferred_dates", "ignored_messages":
    """

    t0 = time.perf_counter()
    blocks, stats_segmets = segment_messages(lines)
    t1 = time.perf_counter()

    print(f"Segmentation: {t1 - t0:.2f}s")
    data = []
    last_datetime: Optional[datetime] = None

    stats: Dict[str, int] = {
        "total_lines": stats_segmets["total_lines"],
        "parsed_messages": stats_segmets["parsed_messages"],
        "multiline_messages": stats_segmets["multiline_messages"],
        "inferred_dates": 0,
        "ignored_lines": 0,
        "quoted_messages": 0,
    }

    first_quote = True
    for block in blocks:
        parsed, last_datetime, stats_blocks, is_quote = parse_message_block(
            block, last_datetime, detect_quoted=detect_quoted
        )
        if parsed is not None:
            if is_quote:
                data[-1][
                    "message"
                ] += f"\n[{parsed["datetime"].strftime("%d/%m %H:%M")}] {parsed["sender"]}: {parsed["message"]}"
                if first_quote:
                    first_quote = False
                    stats["multiline_messages"] += 1
                    stats["quoted_messages"] += 1
                    data[-1]["quoted_message"] = True
            else:
                data.append(parsed)

        stats["inferred_dates"] += stats_blocks[0]
        stats["ignored_lines"] += stats_blocks[1]
    t2 = time.perf_counter()
    print(f"Parsing: {t2 - t1:.2f}s")
    return pd.DataFrame(data), stats


def parse_chat_file(file_obj) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Parse a WhatsApp chat from a file-like object into a DataFrame
    (e.g. Streamlit UploadedFile).

    Parameters
    ----------
    file_obj : a file-like object (e.g. Streamlit UploadedFile)

    Returns
    -------
    pandas.DataFrame
        Columns: datetime, sender, message, inferred_date
    """
    lines = file_obj.read().decode("utf-8").splitlines(keepends=True)
    return parse_chat(lines)


def parse_chat_path(path: str) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Load and parse a WhatsApp exported chat file into a DataFrame.

    Parameters
    ----------
    path : str
        Path to the exported WhatsApp .txt file.

    Returns
    -------
    pandas.DataFrame
        Columns: datetime, sender, message
    """
    path_style = PathStyle.WINDOWS if platform.system() == "Windows" else PathStyle.UNIX

    if not is_valid_directory_path(path, path_style):
        raise ValueError(f"{path} is not a valid {path_style} path")

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(path, encoding="utf-8") as lines:
        data, stats = parse_chat(lines)
    return data, stats
