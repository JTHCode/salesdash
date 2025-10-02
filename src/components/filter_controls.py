"""Sidebar filter controls for the analytics dashboard."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Sequence

import pandas as pd
import streamlit as st

METRIC_MAP: dict[str, str] = {
    "Revenue": "Sales",
    "Profit": "Total Profit/Loss",
}

PRESET_WINDOWS: dict[str, int | None] = {
    "Last 30 Days": 30,
    "Last 90 Days": 90,
    "Last 180 Days": 180,
    "Last 365 Days": 365,
    "Custom Range": None,
}


@dataclass(frozen=True)
class FilterState:
    """Represents the sidebar filter selections."""

    start_date: pd.Timestamp
    end_date: pd.Timestamp
    countries: tuple[str, ...] | None
    statuses: tuple[str, ...] | None
    metric_label: str

    @property
    def metric_column(self) -> str:
        return METRIC_MAP[self.metric_label]


def _normalize_timestamp(value: date | pd.Timestamp) -> pd.Timestamp:
    stamp = pd.Timestamp(value)
    return stamp.normalize()


def _default_date_range(df: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    min_date = pd.to_datetime(df["Order Date"].min(), errors="coerce")
    max_date = pd.to_datetime(df["Order Date"].max(), errors="coerce")

    if pd.isna(min_date) or pd.isna(max_date):
        today = pd.Timestamp.utcnow().normalize()
        return today - timedelta(days=365), today

    start = max(min_date, max_date - timedelta(days=365))
    return start.normalize(), max_date.normalize()


def _coerce_date_range(selection: Iterable[date]) -> tuple[pd.Timestamp, pd.Timestamp]:
    values = list(selection)
    if not values:
        today = pd.Timestamp.utcnow().normalize()
        return today, today
    if len(values) == 1:
        stamp = _normalize_timestamp(values[0])
        return stamp, stamp
    start = _normalize_timestamp(values[0])
    end = _normalize_timestamp(values[-1])
    return (start if start <= end else end, end if end >= start else start)


def _range_for_preset(latest: pd.Timestamp, days: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    end = latest
    start = (latest - timedelta(days=days - 1)).normalize()
    return start, end


def _ensure_session_defaults(
    df: pd.DataFrame,
    country_options: Sequence[str],
    status_options: Sequence[str],
) -> None:
    default_start, default_end = _default_date_range(df)
    if "filters_date_range" not in st.session_state:
        st.session_state["filters_date_range"] = (
            default_start.date(),
            default_end.date(),
        )
    if "filters_preset" not in st.session_state:
        st.session_state["filters_preset"] = "Last 365 Days"
    if "filters_metric" not in st.session_state:
        st.session_state["filters_metric"] = next(iter(METRIC_MAP))
    if "filters_countries" not in st.session_state:
        st.session_state["filters_countries"] = list(country_options)
    if "filters_statuses" not in st.session_state:
        default_statuses = [
            status for status in status_options if status.lower() == "completed"
        ] or list(status_options)
        st.session_state["filters_statuses"] = default_statuses


def render(
    df: pd.DataFrame,
    *,
    country_options: Sequence[str],
    status_options: Sequence[str],
) -> FilterState:
    """Render sidebar controls and return the resulting filter state."""
    st.sidebar.header("Filters")
    _ensure_session_defaults(df, country_options, status_options)

    min_stamp = pd.to_datetime(df["Order Date"].min(), errors="coerce")
    max_stamp = pd.to_datetime(df["Order Date"].max(), errors="coerce")
    if pd.isna(min_stamp) or pd.isna(max_stamp):
        default_start, default_end = _default_date_range(df)
        min_date = default_start.date()
        max_date = default_end.date()
        latest_stamp = default_end
    else:
        min_date = min_stamp.date()
        max_date = max_stamp.date()
        latest_stamp = max_stamp

    preset_label = st.sidebar.selectbox(
        "Quick Date Range",
        options=list(PRESET_WINDOWS.keys()),
        index=list(PRESET_WINDOWS.keys()).index(st.session_state["filters_preset"]),
        key="filters_preset",
    )

    if preset_label != "Custom Range":
        days = PRESET_WINDOWS[preset_label]
        if days is not None:
            start, end = _range_for_preset(latest_stamp.normalize(), days)
            st.session_state["filters_date_range"] = (
                start.date(),
                end.date(),
            )

    date_selection = st.sidebar.date_input(
        "Date Range",
        value=st.session_state["filters_date_range"],
        min_value=min_date,
        max_value=max_date,
        key="filters_date_input",
    )

    if isinstance(date_selection, date):
        date_tuple = (date_selection, date_selection)
    else:
        date_tuple = tuple(date_selection)
    st.session_state["filters_date_range"] = date_tuple

    start_date, end_date = _coerce_date_range(date_tuple)

    metric_label = st.sidebar.radio(
        "Primary Metric",
        options=list(METRIC_MAP.keys()),
        index=list(METRIC_MAP.keys()).index(st.session_state["filters_metric"]),
        key="filters_metric",
        horizontal=True,
    )

    selected_countries = st.sidebar.multiselect(
        "Countries",
        options=list(country_options),
        default=st.session_state["filters_countries"],
        key="filters_countries",
    ) or list(country_options)

    selected_statuses = st.sidebar.multiselect(
        "Order Status",
        options=list(status_options),
        default=st.session_state["filters_statuses"],
        key="filters_statuses",
    ) or list(status_options)

    filter_state = FilterState(
        start_date=start_date,
        end_date=end_date,
        countries=tuple(selected_countries),
        statuses=tuple(selected_statuses),
        metric_label=metric_label,
    )

    st.session_state["filters"] = filter_state
    return filter_state


__all__ = ["FilterState", "METRIC_MAP", "PRESET_WINDOWS", "render"]
