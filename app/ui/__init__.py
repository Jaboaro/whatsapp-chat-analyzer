"""
UI public API.

This package contains all Streamlit rendering logic for the application.
All functions exposed here assume that input data has already been parsed
and filtered at the application level.
"""

from ui.sidebar import render_sidebar, SidebarFilters
from ui.uploads import load_chat
from ui.content import TITLE_CAPTION, EXPORTATION_STEPS, ABOUT_THIS_PROJECT
from ui.renders import (
    render_messages_by_sender,
    render_media_by_sender,
    render_weekday_charts,
    render_hour_chart,
    render_temporal_activity,
    render_activity_heatmap,
)

__all__ = [
    # Upload / input
    "load_chat",
    # Sidebar
    "render_sidebar",
    "SidebarFilters",
    # Static content
    "TITLE_CAPTION",
    "EXPORTATION_STEPS",
    "ABOUT_THIS_PROJECT",
    # Renders
    "render_messages_by_sender",
    "render_media_by_sender",
    "render_weekday_charts",
    "render_hour_chart",
    "render_temporal_activity",
    "render_activity_heatmap",
]
