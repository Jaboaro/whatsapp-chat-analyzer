from typing import Literal, Tuple, Dict, List

# ------------------
# Filter modes
# ------------------

TextFilterMode = Literal[
    "Contains",
    "Starts with",
    "Exact match",
    "Regex",
]


TEXT_FILTER_MODES: Tuple[TextFilterMode, ...] = (
    "Contains",
    "Starts with",
    "Exact match",
    "Regex",
)

# ------------------
# Date presets
# ------------------
DatePreset = Literal[
    "All time",
    "Last 7 days",
    "Last 30 days",
    "Last 90 days",
    "Custom",
]


DATE_PRESETS: Tuple[DatePreset, ...] = (
    "All time",
    "Last 7 days",
    "Last 30 days",
    "Last 90 days",
    "Custom",
)

# ------------------
# Media patterns
# ------------------

MEDIA_PATTERNS: Dict[str, List[str]] = {
    "Images": ["image omitted", "imagen omitida"],
    "Stickers": ["sticker omitted", "sticker omitido"],
    "Audios": ["audio omitted", "audio omitido"],
    "Videos": ["video omitted", "video omitido"],
}
