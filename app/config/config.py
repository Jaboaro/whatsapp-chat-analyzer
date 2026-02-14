import streamlit as st


def is_cloud() -> bool:
    return st.secrets.get("IS_CLOUD", False)
