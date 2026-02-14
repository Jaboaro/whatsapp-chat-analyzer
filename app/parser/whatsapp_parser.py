"""
WhatsApp chat parser.

This module parses raw WhatsApp .txt exports into structured messages,
handling common inconsistencies such as:
- Multiline messages
- Missing years in timestamps
- Quoted replies
- Invisible Unicode characters
- Platform-dependent export formats

Parsing is performed in two phases:
1. Message segmentation
2. Message block parsing

Note:
- File/path handling is moved to parser.io
"""

import re
from typing import Iterable, List, Optional, Tuple, Dict, TypedDict
from datetime import datetime
import pandas as pd

from .import_config import ChatImportConfig

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
# TypedDicts
# --------------------------------------------------


class ParsedMessage(TypedDict):
    datetime: datetime
    sender: str
    message: str
    quoted_message: bool


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


def infer_date_format(blocks: List[str], sample_size: int = 50) -> str:
    """
    Infer whether dates are in DD/MM/YY or MM/DD/YY format.

    Strategy:
    - Extract first N FULL_PATTERN date strings
    - Attempt parsing with both formats
    - Choose format with more valid parses
    """

    candidates: List[str] = []

    for block in blocks[:sample_size]:
        m = FULL_PATTERN.match(block)
        if m:
            date_str = m.group(1)
            candidates.append(date_str)

    if not candidates:
        return "%d/%m/%y"  # Safe default

    def score(fmt: str) -> int:
        valid = 0
        for d in candidates:
            try:
                datetime.strptime(d, fmt)
                valid += 1
            except ValueError:
                pass
        return valid

    ddmm_score = score("%d/%m/%y")
    mmdd_score = score("%m/%d/%y")

    return "%d/%m/%y" if ddmm_score >= mmdd_score else "%m/%d/%y"


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
    Tuple[List[str], Dict[str,int]]
        - List of full message blocks (including multi-line messages).
        - Stats dictionary with keys: total_lines, parsed_messages, multiline_messages.
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
    date_format: str,
    detect_quoted: bool = True,
) -> Tuple[Optional[ParsedMessage], Optional[datetime], Tuple[int, int], bool]:
    """
    Parse a full WhatsApp message block into structured data.

    Parameters
    ----------
    block : str
        Full message block (possibly multi-line).
    last_datetime : Optional[datetime]
        Datetime of the previous successfully parsed message.
    detect_quoted : bool
        If True, messages with timestamps earlier than previous
        message are considered quoted replies.

    Returns
    -------
    Tuple[
        Optional[ParsedMessage],
        Optional[datetime],
        Tuple[int, int],
        bool
    ]
        - parsed_message_dict or None
        - updated last_datetime
        - tuple (inferred_dates, ignored_lines)
        - is_quote flag
    """
    m_full = FULL_PATTERN.match(block)
    inferred_dates = 0
    ignored_messages = 0
    inferred = False

    if m_full:
        date, hour, sender, message = m_full.groups()
        dt = datetime.strptime(f"{date} {hour}", f"{date_format} %H:%M:%S")

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
        short_format = date_format.replace("%y", "%Y")
        dt = datetime.strptime(
            f"{day.zfill(2)}/{month.zfill(2)}/{year} {hour}:00",
            f"{short_format} %H:%M:%S",
        )

        # Quoted message heuristic: timestamp goes backward
        if detect_quoted and dt < last_datetime:
            return (
                {
                    "datetime": last_datetime,
                    "sender": sender,
                    "message": message,
                    "quoted_message": True,
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
    lines: Iterable[str],
    detect_quoted: bool = True,
    import_config: Optional[ChatImportConfig] = None,
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Parse a WhatsApp chat from an iterable of strings (chat.txt format).

    Parameters
    ----------
    lines : Iterable[str]
        Each line from a WhatsApp export file.
    detect_quoted : bool
        Enable heuristic detection of quoted messages.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str,int]]
        - DataFrame with columns: datetime, sender, message, quoted_message
        - Stats dictionary with keys:
          total_lines, parsed_messages, multiline_messages,
          inferred_dates, ignored_lines, quoted_messages
    """

    blocks, segment_stats = segment_messages(lines)

    if import_config and import_config.date_format:
        date_format = import_config.date_format
    else:
        date_format = infer_date_format(blocks)

    data: List[ParsedMessage] = []
    last_datetime: Optional[datetime] = None

    stats: Dict[str, int] = {
        "total_lines": segment_stats["total_lines"],
        "parsed_messages": segment_stats["parsed_messages"],
        "multiline_messages": segment_stats["multiline_messages"],
        "inferred_dates": 0,
        "ignored_lines": 0,
        "quoted_messages": 0,
    }

    first_quote = True
    for block in blocks:

        parsed, last_datetime, block_stats, is_quote = parse_message_block(
            block,
            last_datetime,
            date_format=date_format,
            detect_quoted=detect_quoted,
        )

        if parsed is not None:
            if is_quote:
                data[-1]["message"] += (
                    f"\n[{parsed['datetime'].strftime('%d/%m %H:%M')}] "
                    f"{parsed['sender']}: {parsed['message']}"
                )

                if first_quote:
                    first_quote = False
                    stats["multiline_messages"] += 1
                    stats["quoted_messages"] += 1
                    data[-1]["quoted_message"] = True
            else:
                data.append(parsed)

        stats["inferred_dates"] += block_stats[0]
        stats["ignored_lines"] += block_stats[1]
    return pd.DataFrame(data), stats
