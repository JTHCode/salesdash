"""Placeholder geographic map component for Story 1.1."""
from __future__ import annotations

import streamlit as st

PLACEHOLDER_MESSAGE = "Story 1.2/1.3 will render a geographic heatmap with Plotly."


def render(current_df) -> None:
    """Render placeholder geographic section."""
    st.subheader("Geographic Performance")
    st.info(PLACEHOLDER_MESSAGE)
    st.caption(
        "Dataset currently filtered to {rows:,} rows across {countries} countries.".format(
            rows=len(current_df),
            countries=current_df["Country"].nunique() if "Country" in current_df else 0,
        )
    )


__all__ = ["render"]
