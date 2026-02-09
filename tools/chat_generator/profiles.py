from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


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
    datetime_format="%m/%d/%y, %H:%M%S",
    line_separator=" - ",
    sender_message_separator=": ",
    media_messages={
        "image": "<Image omitted>",
        "video": "<Video omitted>",
        "audio": "<Audio omitted>",
        "sticker": "<Sticker omitted>",
        "gif": "<GIF omitted>",
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
        "gif": "GIF omitido",
    },
)

if __name__ == "__main__":
    from datetime import datetime

    dt = datetime(2023, 1, 12, 18, 42)
    line = ES_PROFILE.format_line(dt, "Alice", "Hello")
    print(line)
