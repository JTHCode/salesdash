"""Unit tests for filter control helpers."""
from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.components import filter_controls


def _sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Order Date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-06-15",
                    "2024-12-31",
                ]
            ),
            "Sales": [100, 200, 300],
            "Total Profit/Loss": [40, 80, 120],
        }
    )


def test_default_date_range_spans_one_year() -> None:
    df = _sample_dataframe()
    start, end = filter_controls._default_date_range(df)
    assert end == pd.Timestamp("2024-12-31").normalize()
    assert (end - start).days <= 365


def test_range_for_preset_calculates_window() -> None:
    end = pd.Timestamp("2024-12-31")
    start, computed_end = filter_controls._range_for_preset(end, 30)
    assert computed_end == end
    assert (computed_end - start).days == 29


def test_coerce_date_range_accepts_single_date() -> None:
    selection = [date(2024, 5, 1)]
    start, end = filter_controls._coerce_date_range(selection)
    assert start == end == pd.Timestamp("2024-05-01")


def test_filter_state_metric_column_mapping() -> None:
    state = filter_controls.FilterState(
        start_date=pd.Timestamp("2024-01-01"),
        end_date=pd.Timestamp("2024-01-31"),
        countries=None,
        statuses=None,
        metric_label="Profit",
    )
    assert state.metric_column == "Total Profit/Loss"


def test_ensure_session_defaults_initialises_session_state() -> None:
    st.session_state.clear()
    df = _sample_dataframe()
    filter_controls._ensure_session_defaults(
        df,
        country_options=["United States"],
        status_options=["Completed", "Returned"],
    )
    assert st.session_state["filters_metric"] in filter_controls.METRIC_MAP
    assert st.session_state["filters_preset"] == "Last 365 Days"
    assert len(st.session_state["filters_countries"]) == 1
    assert st.session_state["filters_statuses"] == ["Completed"]
