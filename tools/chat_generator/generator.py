from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterable, List

from .profiles import ExportProfile
from .distributions import (
    seed_random,
    messages_per_day,
    random_datetime_on_day,
    response_delay,
    is_conversation_break,
)

TEXT_SNIPPETS = [
    "ok",
    "👍",
    "😂",
    "sounds good",
    "I'll check later",
    "jajaja",
    "perfect",
    "yes",
    "no",
    "maybe",
    "😂😂",
]


def generate_chat(
    users: List[str],
    start_date: datetime,
    days: int,
    avg_messages_per_day: int,
    export_profile: ExportProfile,
    seed: int | None = None,
    active_hours: Iterable[int] | None = range(9, 23),
    media_probability: float = 0.15,
    multiline_probability: float = 0.05,
) -> str:
    """
    Generate a synthetic WhatsApp chat export.

    Parameters
    ----------
    users : list of str
        Chat participants.
    start_date : datetime
        Start date of the chat.
    days : int
        Number of days to generate.
    avg_messages_per_day : int
        Average number of messages per day.
    export_profile : ExportProfile
        WhatsApp export formatting profile.
    seed : int, optional
        Random seed for deterministic generation.
    active_hours : iterable of int, optional
        Preferred activity hours.
    media_probability : float
        Probability that a message is media.
    multiline_probability : float
        Probability that a text message spans multiple lines.

    Returns
    -------
    str
        WhatsApp-formatted chat text.
    """

    seed_random(seed)

    lines: list[str] = []
    current_time: datetime | None = None
    last_sender: str | None = None

    for day_offset in range(days):
        day = start_date + timedelta(days=day_offset)
        num_messages = messages_per_day(avg_messages_per_day, 0.8)

        if num_messages == 0:
            continue

        for _ in range(num_messages):
            # Start a new conversation or day
            if current_time is None or is_conversation_break():
                current_time = random_datetime_on_day(day, active_hours)
                last_sender = None
            else:
                current_time += response_delay()

            # Choose sender (avoid same sender too often)
            if last_sender and random.random() < 0.7:
                sender = random.choice([u for u in users if u != last_sender])
            else:
                sender = random.choice(users)
            last_sender = sender

            # Decide message type
            if random.random() < media_probability:
                media_type = random.choice(list(export_profile.media_messages))
                message = export_profile.media_messages[media_type]
            else:
                message = random.choice(TEXT_SNIPPETS)

                # Multiline message
                if random.random() < multiline_probability:
                    message += "\n" + random.choice(TEXT_SNIPPETS)

            line = export_profile.format_line(
                dt=current_time,
                sender=sender,
                message=message,
            )

            lines.append(line)

    return "\n".join(lines)
