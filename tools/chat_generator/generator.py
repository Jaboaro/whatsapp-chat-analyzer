from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterable, List, Dict

from .profiles import ExportProfile, UserProfile, DEFAULT_PROFILE_MIX
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


def _assign_profiles(users: List[str]) -> Dict[str, UserProfile]:
    profiles, weights = zip(*DEFAULT_PROFILE_MIX)

    assigned = random.choices(
        population=profiles,
        weights=weights,
        k=len(users),
    )

    return dict(zip(users, assigned))


def _weighted_choice(distribution: Dict[str, float]) -> str:
    """
    Sample from a weighted distribution dictionary.
    """
    items = list(distribution.keys())
    weights = list(distribution.values())
    return random.choices(items, weights=weights, k=1)[0]


def generate_chat(
    users: List[str],
    start_date: datetime,
    days: int,
    avg_messages_per_day: int,
    export_profile: ExportProfile,
    seed: int | None = None,
    active_hours: Iterable[int] | None = range(9, 23),
    multiline_probability: float = 0.05,
    user_profiles: Dict[str, UserProfile] | None = None,
) -> str:
    """
    Generate a synthetic WhatsApp chat export with heterogeneous user behavior.

    Parameters
    ----------
    users : list of str
        Chat participants.
    start_date : datetime
        Start date of the chat.
    days : int
        Number of days to generate.
    avg_messages_per_day : int
        Baseline average messages per day.
    export_profile : ExportProfile
        WhatsApp export formatting profile.
    seed : int, optional
        Random seed for deterministic generation.
    active_hours : iterable of int, optional
        Preferred activity hours.
    multiline_probability : float
        Probability that a text message spans multiple lines.
    user_profiles : dict[str, UserProfile], optional
        Explicit user behavior profiles. If None, profiles are auto-assigned.

    Returns
    -------
    str
        WhatsApp-formatted chat text.
    """

    seed_random(seed)

    if user_profiles is None:
        user_profiles = _assign_profiles(users)

    lines: list[str] = []
    current_time: datetime | None = None
    last_sender: str | None = None

    for day_offset in range(days):
        day = start_date + timedelta(days=day_offset)
        num_messages = messages_per_day(avg_messages_per_day, 0.8)

        if num_messages == 0:
            continue

        for _ in range(num_messages):

            # Conversation break
            if current_time is None or is_conversation_break():
                current_time = random_datetime_on_day(day, active_hours)
                last_sender = None
            else:
                current_time += response_delay()

            # Choose sender weighted by message_rate_multiplier
            senders = list(user_profiles.keys())
            weights = [user_profiles[u].message_rate_multiplier for u in senders]
            sender = random.choices(senders, weights=weights, k=1)[0]
            last_sender = sender

            profile = user_profiles[sender]

            # Decide media vs text
            if random.random() < profile.media_probability:
                media_type = _weighted_choice(profile.media_type_distribution)
                message = export_profile.media_messages.get(
                    media_type,
                    export_profile.media_messages["image"],
                )
            else:
                message = random.choice(TEXT_SNIPPETS)

                if random.random() < multiline_probability:
                    message += "\n" + random.choice(TEXT_SNIPPETS)

            line = export_profile.format_line(
                dt=current_time,
                sender=sender,
                message=message,
            )

            lines.append(line)

    return "\n".join(lines)
