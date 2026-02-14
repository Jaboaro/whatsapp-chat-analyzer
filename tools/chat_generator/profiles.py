from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Dict


@dataclass(frozen=True)
class ExportProfile:
    """
    WhatsApp export format profile.

    This class encapsulates all locale-specific formatting rules
    required to generate a valid WhatsApp chat export.

    It deliberately does NOT include any language-specific message
    content, only structural tokens.
    """

    locale: str
    datetime_format: str
    line_separator: str
    sender_message_separator: str
    media_messages: Mapping[str, str]

    def format_datetime(self, dt) -> str:
        """Format a datetime according to the export profile."""
        return dt.strftime(self.datetime_format)

    def format_line(
        self,
        dt,
        sender: str,
        message: str,
    ) -> str:
        """
        Format a single WhatsApp message line.

        Example (EN):
        01/12/23, 18:42 - Alice: Hello!
        """
        return (
            f"{self.format_datetime(dt)}"
            f"{self.line_separator}"
            f"{sender}"
            f"{self.sender_message_separator}"
            f"{message}"
        )


EN_PROFILE = ExportProfile(
    locale="en",
    datetime_format="[%m/%d/%y, %H:%M:%S]",
    line_separator=" ",
    sender_message_separator=": ",
    media_messages={
        "image": "image omitted",
        "video": "video omitted",
        "audio": "audio omitted",
        "sticker": "sticker omitted",
    },
)

ES_PROFILE = ExportProfile(
    locale="es",
    datetime_format="[%d/%m/%y, %H:%M:%S]",
    line_separator=" ",
    sender_message_separator=": ",
    media_messages={
        "image": "imagen omitida",
        "video": "video omitido",
        "audio": "audio omitido",
        "sticker": "sticker omitido",
    },
)


@dataclass(frozen=True)
class UserProfile:
    """
    Synthetic user behavior profile.

    Defines how a user behaves in the generated chat:
    - relative message frequency
    - probability of sending media
    - distribution of media types
    - burstiness multiplier (optional)
    """

    name: str
    message_rate_multiplier: float
    media_probability: float
    media_type_distribution: Dict[str, float]
    burstiness: float = 1.0


TALKER = UserProfile(
    name="talker",
    message_rate_multiplier=1.8,
    media_probability=0.05,
    media_type_distribution={"image": 1.0},
    burstiness=1.2,
)

LURKER = UserProfile(
    name="lurker",
    message_rate_multiplier=0.4,
    media_probability=0.02,
    media_type_distribution={"image": 1.0},
    burstiness=0.8,
)

MEDIA_SENDER = UserProfile(
    name="media_sender",
    message_rate_multiplier=0.8,
    media_probability=0.6,
    media_type_distribution={
        "image": 0.6,
        "video": 0.2,
        "audio": 0.1,
        "sticker": 0.1,
    },
    burstiness=1.1,
)

BALANCED = UserProfile(
    name="balanced",
    message_rate_multiplier=1.0,
    media_probability=0.15,
    media_type_distribution={
        "image": 0.5,
        "video": 0.2,
        "audio": 0.2,
        "sticker": 0.1,
    },
    burstiness=1.0,
)

DEFAULT_PROFILE_MIX = [
    (TALKER, 0.2),
    (MEDIA_SENDER, 0.15),
    (BALANCED, 0.45),
    (LURKER, 0.2),
]

if __name__ == "__main__":
    from datetime import datetime

    dt = datetime(2023, 1, 12, 18, 42)
    line = EN_PROFILE.format_line(dt, "Alice", "Hello")
    print(line)
