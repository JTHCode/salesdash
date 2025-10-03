"""Forecast visualization component for forecast vs actual insights."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from components.filter_controls import FilterState
except ImportError:  # pragma: no cover - package relative fallback
    from .filter_controls import FilterState  # type: ignore

try:
    from services import load_forecast_results
except ImportError:  # pragma: no cover - package relative fallback
    from ..services import load_forecast_results  # type: ignore

DEFAULT_HORIZON_OPTIONS: tuple[int, ...] = (6, 12)
DEFAULT_COLOR_ACTUAL = "#1f77b4"
DEFAULT_COLOR_FORECAST = "#ff7f0e"
CONFIDENCE_FILL = "rgba(255, 127, 14, 0.18)"


@dataclass(frozen=True)
class ForecastSegments:
    """Container for actual and forecast slices ready for rendering."""

    actual: pd.DataFrame
    forecast: pd.DataFrame


def _ensure_horizon_session(default: int = DEFAULT_HORIZON_OPTIONS[-1]) -> None:
    if "forecast_horizon" not in st.session_state:
        st.session_state["forecast_horizon"] = default


def _select_horizon(options: Iterable[int]) -> int:
    _ensure_horizon_session()
    option_list = list(options)
    default_value = st.session_state["forecast_horizon"]
    if default_value not in option_list:
        default_value = option_list[-1]
    default_index = option_list.index(default_value)

    selection = st.radio(
        "Forecast Horizon (months)",
        options=option_list,
        index=default_index,
        horizontal=True,
        key="forecast_horizon_choice",
    )
    st.session_state["forecast_horizon"] = selection
    return selection


def _normalize_periods(frame: pd.DataFrame) -> pd.DataFrame:
    converted = frame.copy()
    periods = pd.to_datetime(converted["period_start"], errors="coerce")
    tzinfo = getattr(periods.dt, "tz", None)
    if tzinfo is not None:
        periods = periods.dt.tz_convert(None)
    converted["period_start"] = periods
    return converted.sort_values("period_start")


def prepare_forecast_segments(
    forecast_frame: pd.DataFrame,
    filter_state: FilterState,
    horizon: int,
) -> ForecastSegments:
    """Return actual/forecast slices constrained by filters and horizon."""
    if forecast_frame.empty:
        return ForecastSegments(pd.DataFrame(), pd.DataFrame())

    normalized = _normalize_periods(forecast_frame)
    metric_subset = normalized.loc[
        normalized["metric"] == filter_state.metric_column
    ].copy()

    if metric_subset.empty:
        return ForecastSegments(pd.DataFrame(), pd.DataFrame())

    metric_subset["horizon"] = metric_subset["horizon"].astype(int)
    actual = metric_subset.loc[metric_subset["type"] == "actual"].copy()
    forecast = metric_subset.loc[
        (metric_subset["type"] == "forecast")
        & (metric_subset["horizon"] <= horizon)
    ].copy()

    start = pd.to_datetime(filter_state.start_date).normalize()
    end = pd.to_datetime(filter_state.end_date).normalize()
    if not actual.empty:
        actual = actual.loc[
            (actual["period_start"] >= start)
            & (actual["period_start"] <= end)
        ].copy()

    return ForecastSegments(
        actual=actual.reset_index(drop=True),
        forecast=forecast.reset_index(drop=True),
    )


def _format_metric_value(value: float, metric_label: str) -> str:
    if any(keyword in metric_label.lower() for keyword in ("revenue", "sales", "profit")):
        return f"${value:,.0f}"
    return f"{value:,.0f}"


def summarize_forecast_insights(
    *,
    segments: ForecastSegments,
    metric_label: str,
    horizon: int,
    method: str | None,
) -> str:
    """Generate a narrative summary for the current forecast view."""
    lines: list[str] = []
    method_display = method or "precomputed forecast"

    if segments.forecast.empty:
        return (
            "Forecast data is unavailable for the selected filters. "
            "Verify the offline artifact and try a different metric."
        )

    forecast_tail = segments.forecast.sort_values("period_start")
    forecast_end = forecast_tail.iloc[-1]
    horizon_label = f"{horizon}-month" if horizon else "forecast"
    projected_value = _format_metric_value(float(forecast_end["value"]), metric_label)
    forecast_period = forecast_end["period_start"].strftime("%B %Y")

    if not segments.actual.empty:
        actual_tail = segments.actual.sort_values("period_start")
        last_actual = actual_tail.iloc[-1]
        last_value = float(last_actual["value"])
        delta = float(forecast_end["value"]) - last_value
        pct_change = (delta / last_value * 100) if last_value else None
        change_phrase = (
            f"{pct_change:+.1f}%" if pct_change is not None else "steady"
        )
        lines.append(
            f"{metric_label} is projected to reach {projected_value} by {forecast_period}, "
            f"a {change_phrase} shift versus the latest actuals."
        )
    else:
        lines.append(
            f"The {horizon_label} projection estimates {metric_label} at {projected_value} by {forecast_period}."
        )

    band_width = float(
        forecast_tail["upper_bound"].sub(forecast_tail["lower_bound"]).mean()
    )
    lines.append(
        "Confidence band width averages "
        f"{_format_metric_value(band_width / 2, metric_label)} around the forecast "
        "centre, signaling expected variability."
    )

    trend_delta = float(forecast_tail.iloc[-1]["value"] - forecast_tail.iloc[0]["value"])
    if trend_delta > 0:
        lines.append(
            "Focus on capacity planning and capturing the forecasted uplift, "
            "as values trend upwards across the horizon."
        )
    elif trend_delta < 0:
        lines.append(
            "Prepare mitigation or retention strategies-the forecast shows a downward trend over the horizon."
        )
    else:
        lines.append(
            "Momentum remains flat; maintain efficiency and monitor for new signals before adjusting strategy."
        )

    lines.append(f"Method: {method_display} using cached artifact (no runtime training).")
    return "\n".join(lines)


def _build_figure(segments: ForecastSegments, metric_label: str) -> go.Figure:
    fig = go.Figure()
    if not segments.actual.empty:
        fig.add_trace(
            go.Scatter(
                x=segments.actual["period_start"],
                y=segments.actual["value"],
                mode="lines",
                name=f"Actual {metric_label}",
                line=dict(color=DEFAULT_COLOR_ACTUAL, width=3),
                hovertemplate="Period: %{x|%b %Y}<br>Value: %{y:,.0f}",
            )
        )

    if not segments.forecast.empty:
        fig.add_trace(
            go.Scatter(
                x=segments.forecast["period_start"],
                y=segments.forecast["upper_bound"],
                mode="lines",
                line=dict(width=0),
                name="Upper Confidence",
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=segments.forecast["period_start"],
                y=segments.forecast["lower_bound"],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor=CONFIDENCE_FILL,
                name="Confidence Interval",
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=segments.forecast["period_start"],
                y=segments.forecast["value"],
                mode="lines",
                name=f"Forecast {metric_label}",
                line=dict(color=DEFAULT_COLOR_FORECAST, width=3, dash="dash"),
                hovertemplate="Period: %{x|%b %Y}<br>Forecast: %{y:,.0f}",
            )
        )

    fig.update_layout(
        height=480,
        margin=dict(t=60, r=30, b=30, l=60),
        yaxis_title=metric_label,
        xaxis_title="Period",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def render(
    current_df: pd.DataFrame,
    *,
    filter_state: FilterState,
) -> None:
    """Render forecasts with interactive controls and narrative."""
    st.subheader("Forecast Outlook")

    horizon = _select_horizon(DEFAULT_HORIZON_OPTIONS)

    try:
        forecast_frame = load_forecast_results()
    except Exception as exc:  # pragma: no cover - surfaced in UI
        st.error(
            "Unable to load forecast artifact. "
            "Run `python -m src.services.forecasting_service` and retry."
        )
        st.caption(str(exc))
        return

    segments = prepare_forecast_segments(
        forecast_frame,
        filter_state=filter_state,
        horizon=horizon,
    )

    if segments.actual.empty and segments.forecast.empty:
        st.warning(
            "No forecast data is available for the selected filters and metric."
        )
        return

    fig = _build_figure(segments, metric_label=filter_state.metric_label)
    st.plotly_chart(fig, use_container_width=True)

    method = (
        segments.forecast["method"].iloc[0]
        if not segments.forecast.empty and "method" in segments.forecast
        else None
    )
    summary = summarize_forecast_insights(
        segments=segments,
        metric_label=filter_state.metric_label,
        horizon=horizon,
        method=method,
    )

    st.markdown("### Forecast Narrative")
    st.info(summary)

    st.caption(
        "Forecast data sourced from the offline artifact (`data/processed/forecast_sales.csv`)."
    )


__all__ = [
    "render",
    "prepare_forecast_segments",
    "summarize_forecast_insights",
]



