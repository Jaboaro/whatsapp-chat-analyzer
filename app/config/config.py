import os


def is_cloud() -> bool:
    return os.getenv("STREAMLIT_SHARING_MODE") is not None
