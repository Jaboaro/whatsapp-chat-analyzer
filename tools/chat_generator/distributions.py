from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterable, Sequence


# --------------------------------------------------
# Seeding
# --------------------------------------------------


def seed_random(seed: int | None) -> None:
    """
    seed the random number generator.

    Parameters
    ----------
    seed : int or None
        If provided, ensures deterministic outputs
    """

    if seed is not None:
        random.seed(seed)


# --------------------------------------------------
# Seeding
# --------------------------------------------------


def messages_per_day(avg_messages: int, variability: float = 0.3) -> int:
    """
    Sample the number of messages for a given day.

    Parameters
    ----------
    avg_messages : int
        Average messages per day.
    variability : float
        Relative variability (0 = constant, 1 = very noisy).

    Returns
    -------
    int
        Number of messages for the day.
    """

    if avg_messages <= 0:
        return 0

    std = avg_messages * variability
    value = random.gauss(avg_messages, std)

    return max(0, int(round(value)))


# --------------------------------------------------
# Time of day sampling
# --------------------------------------------------


def sample_hour(active_hours: Sequence[int] | None = None) -> int:
    """
    Sample an hour of the day.

    Parameters
    ----------
    active_hours : sequence of int, optional
        Preferred active hours (e.g. range(9, 23)).
        If None, any hour is equally likely.

    Returns
    -------
    int
        Hour of day (0-23).
    """
    if active_hours:
        return random.choice(list(active_hours))

    return random.randint(0, 23)


def sample_minute() -> int:
    """Sample a minute (0-59)."""
    return random.randint(0, 59)


# --------------------------------------------------
# Response delays
# --------------------------------------------------


def response_delay(min_seconds: int = 5, max_seconds: int = 4 * 60 * 60) -> timedelta:
    """
    Sample a response delay between messages.

    Uses a log-normal–like heuristic to favor short replies
    while allowing long pauses.

    Parameters
    ----------
    min_seconds : int
        Minimum delay.
    max_seconds : int
        Maximum delay.

    Returns
    -------
    timedelta
    """
    # log-uniform approximation
    delay = random.expovariate(1 / 300)

    seconds = int(min_seconds + delay)
    seconds = min(seconds, max_seconds)

    return timedelta(seconds=seconds)


# --------------------------------------------------
# Conversation gaps
# --------------------------------------------------


def is_conversation_break(
    probability: float = 0.15,
) -> bool:
    """
    Randomly decide whether a new conversation starts.

    Parameters
    ----------
    probability : float
        Probability of starting a new conversation.

    Returns
    -------
    bool
    """
    return random.random() < probability


# --------------------------------------------------
# Timestamp helpers
# --------------------------------------------------


def random_datetime_on_day(
    day: datetime,
    active_hours: Iterable[int] | None = None,
) -> datetime:
    """
    Generate a random datetime within a given day.

    Parameters
    ----------
    day : datetime
        Date (time component is ignored).
    active_hours : iterable of int, optional
        Restrict activity to certain hours.

    Returns
    -------
    datetime
    """
    hour = sample_hour(list(active_hours) if active_hours else None)
    minute = sample_minute()
    second = random.randint(0, 59)

    return day.replace(
        hour=hour,
        minute=minute,
        second=second,
        microsecond=0,
    )
