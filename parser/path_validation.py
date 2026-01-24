import re
import os
from pathlib import PurePosixPath, PureWindowsPath
from enum import Enum


class PathStyle(Enum):
    UNIX = "unix"
    WINDOWS = "windows"


# =========================
# === UNIX / POSIX ========
# =========================

SEGMENT_UNIX = r"(?:\.{1,2}|[a-zA-Z0-9._-]+)"

ABSOLUTE_UNIX_REGEX = rf"^/(?:{SEGMENT_UNIX}/)*{SEGMENT_UNIX}?$"
RELATIVE_UNIX_REGEX = rf"^(?:{SEGMENT_UNIX}/)*{SEGMENT_UNIX}$"


def is_valid_absolute_unix_path(path: str) -> bool:
    return bool(re.fullmatch(ABSOLUTE_UNIX_REGEX, path))


def is_valid_relative_unix_path(path: str) -> bool:
    return bool(re.fullmatch(RELATIVE_UNIX_REGEX, path))


# =========================
# ===== WINDOWS ===========
# =========================

SEGMENT_WIN = r"(?:\.{1,2}|[^<>:\"/\\|?*\x00-\x1F]+)"

ABSOLUTE_WINDOWS_REGEX = rf"""
^(
    [a-zA-Z]:\\(?:{SEGMENT_WIN}\\)*{SEGMENT_WIN}? |
    \\\\[^\\\/]+\\[^\\\/]+(?:\\{SEGMENT_WIN})*
)$
"""

RELATIVE_WINDOWS_REGEX = rf"""
^
(?:\.\\|\.\.\\)?(?:{SEGMENT_WIN}\\)*{SEGMENT_WIN}
$
"""


def is_valid_absolute_windows_path(path: str) -> bool:
    return bool(re.fullmatch(ABSOLUTE_WINDOWS_REGEX, path, re.VERBOSE))


def is_valid_relative_windows_path(path: str) -> bool:
    return bool(re.fullmatch(RELATIVE_WINDOWS_REGEX, path, re.VERBOSE))


# =========================
# === API UNIFICADA =======
# =========================


def is_valid_directory_path(
    path: str,
    style: PathStyle | None = None,
) -> bool:
    """
    Valida estructuralmente un path de carpeta.
    No comprueba existencia.
    """

    if style is None:
        style = PathStyle.WINDOWS if os.name == "nt" else PathStyle.UNIX

    if style == PathStyle.UNIX:
        if not (is_valid_absolute_unix_path(path) or is_valid_relative_unix_path(path)):
            return False
        try:
            PurePosixPath(path)
            return True
        except Exception:
            return False

    if style == PathStyle.WINDOWS:
        if not (
            is_valid_absolute_windows_path(path) or is_valid_relative_windows_path(path)
        ):
            return False
        try:
            PureWindowsPath(path)
            return True
        except Exception:
            return False

    return False
