import streamlit as st


def is_cloud() -> bool:
    """
    Determine if the app is running in a cloud environment (e.g., Streamlit Cloud).

    This function checks for the presence of a specific secret key that should be
    set in the Streamlit Cloud deployment. If the key is found and truthy, it
    indicates that the app is running in the cloud.

    Returns
    -------
    bool
        True if running in a cloud environment, False otherwise.
    """
    return st.secrets.get("IS_CLOUD", False)
