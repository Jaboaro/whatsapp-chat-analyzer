"""
Path validation utilities for parser.io.

Provides structural validation for UNIX and Windows paths without checking existence.
"""

import os
from pathlib import PurePosixPath, PureWindowsPath
from enum import Enum
import re


class PathStyle(Enum):
    UNIX = "unix"
    WINDOWS = "windows"


# =========================
# === Regex helpers =======
# =========================

# Allow more realistic folder/file names (UTF-8, spaces)
SEGMENT_UNIX = r"(?:\.{1,2}|[^/]+)"
SEGMENT_WIN = r"(?:\.{1,2}|[^<>:\"/\\|?*\x00-\x1F]+)"


# -------------------------
# UNIX / POSIX
# -------------------------

ABSOLUTE_UNIX_REGEX = rf"^/(?:{SEGMENT_UNIX}/)*{SEGMENT_UNIX}?$"
RELATIVE_UNIX_REGEX = rf"^(?:{SEGMENT_UNIX}/)*{SEGMENT_UNIX}$"


def _is_valid_absolute_unix_path(path: str) -> bool:
    return bool(re.fullmatch(ABSOLUTE_UNIX_REGEX, path))


def _is_valid_relative_unix_path(path: str) -> bool:
    return bool(re.fullmatch(RELATIVE_UNIX_REGEX, path))


# -------------------------
# WINDOWS
# -------------------------

ABSOLUTE_WINDOWS_REGEX = rf"""
^(
    [a-zA-Z]:\\(?:{SEGMENT_WIN}\\)*{SEGMENT_WIN}? |   # Drive letter
    \\\\[^\\\/]+\\[^\\\/]+(?:\\{SEGMENT_WIN})*       # UNC path
)$
"""
RELATIVE_WINDOWS_REGEX = rf"^(?:\.\\|\.\.\\)?(?:{SEGMENT_WIN}\\)*{SEGMENT_WIN}$"


def _is_valid_absolute_windows_path(path: str) -> bool:
    return bool(re.fullmatch(ABSOLUTE_WINDOWS_REGEX, path, re.VERBOSE))


def _is_valid_relative_windows_path(path: str) -> bool:
    return bool(re.fullmatch(RELATIVE_WINDOWS_REGEX, path, re.VERBOSE))


# =========================
# === Public API =========
# =========================


def is_valid_directory_path(path: str, style: PathStyle | None = None) -> bool:
    """
    Check if a path is structurally valid for the given OS style.

    Parameters
    ----------
    path : str
        Path string to validate.
    style : PathStyle | None
        OS style. Defaults to current OS.

    Returns
    -------
    bool
        True if structurally valid (absolute or relative), False otherwise.
    """
    if style is None:
        style = PathStyle.WINDOWS if os.name == "nt" else PathStyle.UNIX

    try:
        if style == PathStyle.UNIX:
            if not (
                _is_valid_absolute_unix_path(path) or _is_valid_relative_unix_path(path)
            ):
                return False
            PurePosixPath(path)  # Structural validation
            return True

        if style == PathStyle.WINDOWS:
            if not (
                _is_valid_absolute_windows_path(path)
                or _is_valid_relative_windows_path(path)
            ):
                return False
            PureWindowsPath(path)  # Structural validation
            return True

        return False
    except Exception:
        return False
