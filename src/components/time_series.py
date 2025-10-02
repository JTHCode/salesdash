"""Time-series visualization component.""" 
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from services.analytics_service import aggregate_time_series
except ImportError:  # pragma: no cover
    from src.services.analytics_service import aggregate_time_series  # type: ignore

Interval = Literal["M", "Q", "Y"]
INTERVAL_LABELS: dict[Interval, str] = {
    "M": "Monthly",
    "Q": "Quarterly",
    "Y": "Yearly",
}


@dataclass(frozen=True)
class TimeSeriesState:
    """Captures time-series configuration from user interactions."""

    interval: Interval
    metric_column: str
    metric_label: str


def _default_interval() -> Interval:
    return "M"


def _resolve_interval() -> Interval:
    if "time_series_interval" not in st.session_state:
        st.session_state["time_series_interval"] = _default_interval()
    return st.session_state["time_series_interval"]


def _render_interval_controls(active_metric: str) -> TimeSeriesState:
    interval = _resolve_interval()
    label_map = {label: key for key, label in INTERVAL_LABELS.items()}
    selection = st.radio(
        "Aggregation Interval",
        options=list(INTERVAL_LABELS.values()),
        index=list(INTERVAL_LABELS.keys()).index(interval),
        horizontal=True,
        key="time_series_interval_label",
    )
    chosen_interval = label_map[selection]
    st.session_state["time_series_interval"] = chosen_interval

    return TimeSeriesState(
        interval=chosen_interval,
        metric_column=active_metric,
        metric_label="Revenue" if active_metric == "Sales" else "Profit",
    )


def _annotate_peaks(points_x: list[pd.Timestamp], points_y: list[float], fig: go.Figure) -> None:
    if not points_x or not points_y:
        return
    series = pd.Series(points_y, index=points_x)
    fig.add_annotation(
        x=series.idxmax(),
        y=series.max(),
        text="Peak",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=series.idxmin(),
        y=series.min(),
        text="Trough",
        showarrow=True,
        arrowhead=1,
    )


def _build_chart(df: pd.DataFrame, state: TimeSeriesState) -> go.Figure:
    fig = px.area(
        df,
        x="Order Date",
        y=state.metric_column,
        title=f"{state.metric_label} Trend ({INTERVAL_LABELS[state.interval]})",
        labels={"Order Date": "Period", state.metric_column: state.metric_label},
    )
    fig = go.Figure(fig)

    x_points = list(pd.to_datetime(df["Order Date"]))
    y_points = list(df[state.metric_column])
    _annotate_peaks(x_points, y_points, fig)

    fig.update_traces(hovertemplate="Period: %{x|%Y-%m} <br>Value: %{y:,.0f}")
    fig.update_layout(height=450)
    return fig


def _append_delta_trace(df: pd.DataFrame, fig: go.Figure) -> None:
    if df.empty or "Delta" not in df.columns:
        return
    fig.add_trace(
        go.Bar(
            x=df["Order Date"],
            y=df["Delta"],
            name="Period Change",
            opacity=0.3,
            marker_color="#EF553B",
            yaxis="y2",
            hovertemplate="Change: %{y:+,.0f}",
        )
    )
    fig.update_layout(
        yaxis2=dict(
            title="Change",
            overlaying="y",
            side="right",
            showgrid=False,
        )
    )


def _prepare_data(df: pd.DataFrame, state: TimeSeriesState) -> pd.DataFrame:
    aggregated = aggregate_time_series(df, period=state.interval)
    if aggregated.empty:
        return aggregated
    metric_series = aggregated[state.metric_column]
    aggregated["Delta"] = metric_series.diff().fillna(0)
    return aggregated


def render(
    filtered_df: pd.DataFrame,
    *,
    metric_column: str,
) -> None:
    """Render the time-series visualization based on current filters."""
    st.subheader("Time-Series Trends")

    config = _render_interval_controls(metric_column)
    prepared = _prepare_data(filtered_df, config)

    if prepared.empty:
        st.warning("No data available for the selected filters.")
        return

    fig = _build_chart(prepared, config)
    _append_delta_trace(prepared, fig)

    st.plotly_chart(fig, use_container_width=True)


__all__ = ["render"]
