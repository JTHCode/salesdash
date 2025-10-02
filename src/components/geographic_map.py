"""Geographic performance visualization."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from services.analytics_service import get_geographic_data
except ImportError:  # pragma: no cover - support `streamlit run src/app.py`
    from src.services.analytics_service import get_geographic_data  # type: ignore

RankingMode = Literal["top", "bottom"]


@dataclass(frozen=True)
class GeographicState:
    """Shared state for geographic component interactions."""

    metric_column: str
    metric_label: str


def _fetch_geo_frame(df: pd.DataFrame) -> pd.DataFrame:
    records = get_geographic_data(df)
    return pd.DataFrame(records)


def _format_hover(row: pd.Series) -> str:
    return (
        f"{row['Country']}<br>Sales: ${row['Sales']:,.0f}<br>"
        f"Profit: ${row['Total Profit/Loss']:,.0f}<br>"
        f"Margin: {row['Profit Margin']:.1f}%"
    )


def _build_map(df: pd.DataFrame, state: GeographicState) -> go.Figure:
    hover_text = df.apply(_format_hover, axis=1)

    fig = go.Figure(
        go.Choropleth(
            locations=df["Country"],
            locationmode="country names",
            z=df[state.metric_column],
            colorscale="Blues",
            colorbar_title=state.metric_label,
            text=hover_text,
            hoverinfo="text",
        )
    )
    fig.update_layout(
        title=f"{state.metric_label} by Country",
        geo=dict(showframe=False, showcoastlines=True, projection_type="equirectangular"),
        height=500,
    )
    return fig


def _render_ranking_table(df: pd.DataFrame, state: GeographicState) -> None:
    ranking_col = state.metric_column
    top = df.nlargest(5, ranking_col)
    bottom = df.nsmallest(5, ranking_col)

    st.subheader("Regional Rankings")
    col1, col2 = st.columns(2)

    def _render_table(target_df: pd.DataFrame, label: str, container) -> None:
        if target_df.empty:
            container.info("No data available")
            return
        pretty = target_df[[
            "Country",
            "Sales",
            "Total Profit/Loss",
            "Profit Margin",
        ]].copy()
        pretty.columns = [
            "Country",
            "Sales",
            "Profit",
            "Margin %",
        ]
        container.caption(label)
        container.dataframe(
            pretty.style.format({
                "Sales": "${:,.0f}",
                "Profit": "${:,.0f}",
                "Margin %": "{:.1f}%",
            }),
            use_container_width=True,
        )

    _render_table(top, f"Top 5 {state.metric_label} Regions", col1)
    _render_table(bottom, f"Bottom 5 {state.metric_label} Regions", col2)


def render(
    filtered_df: pd.DataFrame,
    *,
    metric_column: str,
    metric_label: str,
) -> None:
    """Render geographic choropleth and rankings based on filter state."""
    st.subheader("Geographic Performance")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return

    state = GeographicState(metric_column=metric_column, metric_label=metric_label)
    geo_frame = _fetch_geo_frame(filtered_df)

    if geo_frame.empty:
        st.warning("No geographic data available for the selected filters.")
        return

    fig = _build_map(geo_frame, state)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Regional Rankings", expanded=True):
        _render_ranking_table(geo_frame, state)


__all__ = ["render"]
