"""Placeholder forecasting component for Story 1.1."""
from __future__ import annotations

import streamlit as st

PLACEHOLDER_MESSAGE = "Story 1.3 will integrate forecasting services and visualisations."


def render(current_df) -> None:
    """Render placeholder forecasting container."""
    st.subheader("Forecast Preview")
    st.warning(PLACEHOLDER_MESSAGE)
    st.caption(
        "Selection ready for forecasting pipeline with {rows:,} records.".format(
            rows=len(current_df)
        )
    )


__all__ = ["render"]
