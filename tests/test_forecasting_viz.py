"""Tests for the forecast visualization helpers."""
from __future__ import annotations

import pandas as pd

from src.components.filter_controls import FilterState
from src.components.forecasting_viz import (
    ForecastSegments,
    prepare_forecast_segments,
    summarize_forecast_insights,
)


def _build_sample_frame() -> pd.DataFrame:
    periods = pd.date_range("2024-01-01", periods=6, freq="MS")
    data = pd.DataFrame(
        {
            "period_start": list(periods[:3]) + list(periods[3:]),
            "metric": ["Sales"] * 6,
            "value": [120_000, 125_000, 130_000, 132_000, 135_000, 138_000],
            "lower_bound": [115_000, 120_000, 126_000, 128_000, 129_000, 132_000],
            "upper_bound": [125_000, 130_000, 134_000, 136_000, 141_000, 145_000],
            "type": ["actual", "actual", "actual", "forecast", "forecast", "forecast"],
            "horizon": [0, 0, 0, 1, 2, 3],
            "method": ["moving_average"] * 6,
        }
    )
    return data


def _build_filter_state() -> FilterState:
    return FilterState(
        start_date=pd.Timestamp("2024-01-01"),
        end_date=pd.Timestamp("2024-03-31"),
        countries=None,
        statuses=None,
        metric_label="Revenue",
    )


def test_prepare_forecast_segments_filters_by_metric_and_horizon() -> None:
    forecast_frame = _build_sample_frame()
    filter_state = _build_filter_state()

    segments = prepare_forecast_segments(forecast_frame, filter_state, horizon=2)

    assert len(segments.actual) == 3
    assert len(segments.forecast) == 2
    assert segments.forecast["horizon"].max() == 2
    assert segments.actual["period_start"].min() >= filter_state.start_date
    assert segments.actual["period_start"].max() <= filter_state.end_date


def test_summarize_forecast_insights_handles_positive_trend() -> None:
    forecast_frame = _build_sample_frame()
    filter_state = _build_filter_state()
    segments = prepare_forecast_segments(forecast_frame, filter_state, horizon=2)

    summary = summarize_forecast_insights(
        segments=segments,
        metric_label=filter_state.metric_label,
        horizon=2,
        method="moving_average",
    )

    assert "Method: moving_average" in summary
    assert "Revenue is projected" in summary
    assert "%" in summary  # includes percent change wording


def test_summarize_forecast_insights_fallback_when_forecast_missing() -> None:
    empty_segments = ForecastSegments(actual=pd.DataFrame(), forecast=pd.DataFrame())

    summary = summarize_forecast_insights(
        segments=empty_segments,
        metric_label="Revenue",
        horizon=6,
        method="moving_average",
    )

    assert "Forecast data is unavailable" in summary
