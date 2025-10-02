"""Unit tests for time-series visualization helpers."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go

from src.components import time_series


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Order Date": pd.to_datetime(
                [
                    "2024-01-31",
                    "2024-02-29",
                    "2024-03-31",
                    "2024-04-30",
                ]
            ),
            "Sales": [100, 150, 90, 120],
            "Total Profit/Loss": [40, 60, 30, 50],
            "Quantity Ordered": [10, 15, 8, 12],
        }
    )


def test_prepare_data_diff_column_added() -> None:
    df = _sample_frame()
    state = time_series.TimeSeriesState(interval="M", metric_column="Sales", metric_label="Revenue")
    prepared = time_series._prepare_data(df, state)
    assert "Delta" in prepared.columns
    assert prepared["Delta"].iloc[0] == 0
    assert prepared["Delta"].iloc[1] == 50


def test_build_chart_handles_annotations() -> None:
    df = _sample_frame()
    df["Delta"] = [0, 50, -60, 30]
    state = time_series.TimeSeriesState(interval="M", metric_column="Sales", metric_label="Revenue")
    fig = time_series._build_chart(df, state)
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text.startswith("Revenue Trend")
    assert any(annotation.text == "Peak" for annotation in fig.layout.annotations)


def test_append_delta_trace_adds_secondary_axis() -> None:
    df = _sample_frame()
    df["Delta"] = [0, 50, -60, 30]
    fig = go.Figure()
    time_series._append_delta_trace(df, fig)
    assert len(fig.data) == 1
    assert fig.data[0].name == "Period Change"
    assert fig.layout.yaxis2.title.text == "Change"
