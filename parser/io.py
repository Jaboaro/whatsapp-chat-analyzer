import os
import platform
from typing import Tuple, Dict
import pandas as pd

from parser.path_validation import is_valid_directory_path, PathStyle
from parser.whatsapp_parser import parse_chat


def parse_chat_file(file_obj) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Parse a WhatsApp chat from a file-like object into a DataFrame.

    Parameters
    ----------
    file_obj : file-like object
        e.g. Streamlit UploadedFile

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str,int]]
        DataFrame with columns: datetime, sender, message, quoted_message
    """
    lines = file_obj.read().decode("utf-8").splitlines(keepends=True)
    return parse_chat(lines)


def parse_chat_path(path: str) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Load and parse a WhatsApp exported chat file from disk.

    Parameters
    ----------
    path : str
        Path to the exported WhatsApp .txt file.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str,int]]
        DataFrame with columns: datetime, sender, message, quoted_message
    """
    path_style = PathStyle.WINDOWS if platform.system() == "Windows" else PathStyle.UNIX

    if not is_valid_directory_path(path, path_style):
        raise ValueError(f"{path} is not a valid {path_style} path")

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(path, encoding="utf-8") as lines:
        data, stats = parse_chat(lines)
    return data, stats
