from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ChatImportConfig:
    date_format: Optional[str] = None
    media_placeholder: Optional[str] = None
