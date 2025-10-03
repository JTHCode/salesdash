"""Offline forecasting pipeline and loader utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

try:
    import streamlit as st
except ImportError:  # pragma: no cover - streamlit is optional during tests
    st = None  # type: ignore

from ..data_loader import load_data


@dataclass(frozen=True)
class ForecastConfig:
    """Configuration options for the forecast pipeline."""

    metric: str = "Sales"
    horizon: int = 12
    confidence_level: float = 0.95
    window: int = 3


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_ARTIFACT_PATH = ROOT_DIR / "data" / "processed" / "forecast_sales.csv"
_EXPECTED_COLUMNS = {
    "period_start",
    "metric",
    "value",
    "type",
    "lower_bound",
    "upper_bound",
    "method",
    "horizon",
    "generated_at",
    "confidence_level",
    "evaluation_metric",
    "evaluation_value",
    "training_start",
    "training_end",
}
_METHOD_IDENTIFIER = "moving_average"


def _cache_decorator():
    """Return the Streamlit cache decorator when available."""

    if st is None or not hasattr(st, "cache_data"):
        def _identity(func):
            return func

        return _identity
    return st.cache_data(show_spinner=False)


def _resolve_artifact_path(path: Optional[Path]) -> Path:
    """Return the concrete artifact path for the pipeline."""

    if path is not None:
        return path
    return DEFAULT_ARTIFACT_PATH


def _prepare_training_frame(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Aggregate the canonical dataset into a monthly training series."""

    if df is None or df.empty:
        raise ValueError("Sales dataset is empty; cannot build forecast model.")
    if "Order Date" not in df.columns:
        raise KeyError("Dataset missing 'Order Date' column required for forecasting.")
    if metric not in df.columns:
        raise KeyError(f"Dataset missing metric column '{metric}'.")

    frame = df[["Order Date", metric]].copy()
    frame["Order Date"] = pd.to_datetime(frame["Order Date"], errors="coerce")
    frame = frame.dropna(subset=["Order Date", metric])

    aggregated = (
        frame.set_index("Order Date")[metric]
        .resample("MS")
        .sum()
        .to_frame(name="value")
        .reset_index()
        .rename(columns={"Order Date": "period_start"})
    )

    aggregated = aggregated.sort_values("period_start").reset_index(drop=True)
    if aggregated.empty:
        raise ValueError("Monthly aggregation produced no rows; check data integrity.")
    return aggregated


def _in_sample_moving_average(values: pd.Series, window: int) -> pd.Series:
    """Return rolling moving-average estimates for the historical series."""

    window = max(1, window)
    moving_avg = values.rolling(window=window, min_periods=1).mean()
    return moving_avg


def _forecast_moving_average(values: pd.Series, window: int, horizon: int) -> np.ndarray:
    """Forecast using a simple moving average extended iteratively."""

    window = max(1, window)
    history = values.tolist()
    recent: list[float] = history[-window:] if history else []

    if not recent and history:
        recent = history

    forecasts: list[float] = []
    for _ in range(horizon):
        if not recent:
            avg = 0.0
        else:
            avg = float(sum(recent) / len(recent))
        forecasts.append(avg)
        recent.append(avg)
        if len(recent) > window:
            recent = recent[-window:]
    return np.array(forecasts, dtype=float)


def _build_forecast_rows(
    history: pd.DataFrame,
    config: ForecastConfig,
    *,
    artifact_timestamp: pd.Timestamp,
) -> pd.DataFrame:
    """Return combined actual and forecast rows with metadata columns."""

    window = max(1, config.window)
    in_sample = _in_sample_moving_average(history["value"], window)
    residuals = history["value"] - in_sample
    residuals = residuals.dropna()

    mae_value = float(mean_absolute_error(history["value"], in_sample))
    std_error = float(residuals.std(ddof=1)) if len(residuals) > 1 else 0.0
    z_value = 1.96 if abs(config.confidence_level - 0.95) < 1e-3 else 1.0

    last_period = history["period_start"].max()
    future_periods = pd.date_range(
        last_period + pd.offsets.MonthBegin(1),
        periods=config.horizon,
        freq="MS",
    )

    forecast_values = _forecast_moving_average(history["value"], window, config.horizon)
    ci_delta = z_value * std_error if std_error else 0.0

    forecast_frame = pd.DataFrame(
        {
            "period_start": future_periods,
            "metric": config.metric,
            "value": forecast_values,
            "type": "forecast",
            "lower_bound": np.maximum(forecast_values - ci_delta, 0.0),
            "upper_bound": forecast_values + ci_delta,
            "method": _METHOD_IDENTIFIER,
            "horizon": np.arange(1, config.horizon + 1, dtype=int),
            "generated_at": artifact_timestamp,
            "confidence_level": config.confidence_level,
            "evaluation_metric": "MAE",
            "evaluation_value": mae_value,
            "training_start": history["period_start"].min(),
            "training_end": history["period_start"].max(),
        }
    )

    actual_frame = history.assign(
        metric=config.metric,
        type="actual",
        lower_bound=history["value"],
        upper_bound=history["value"],
        method=_METHOD_IDENTIFIER,
        horizon=0,
        generated_at=artifact_timestamp,
        confidence_level=config.confidence_level,
        evaluation_metric="MAE",
        evaluation_value=mae_value,
        training_start=history["period_start"].min(),
        training_end=history["period_start"].max(),
    )

    combined = pd.concat([actual_frame, forecast_frame], ignore_index=True)
    combined["period_start"] = pd.to_datetime(combined["period_start"], errors="coerce")
    combined["generated_at"] = pd.to_datetime(combined["generated_at"], errors="coerce")
    combined["training_start"] = pd.to_datetime(combined["training_start"], errors="coerce")
    combined["training_end"] = pd.to_datetime(combined["training_end"], errors="coerce")
    combined["metric"] = combined["metric"].astype(str)
    return combined


def generate_forecast_artifact(
    *,
    output_path: Optional[Path] = None,
    config: Optional[ForecastConfig] = None,
) -> Path:
    """Run the offline forecasting pipeline and persist the artifact."""

    resolved_path = _resolve_artifact_path(output_path)
    resolved_config = config or ForecastConfig()

    data = load_data()
    history = _prepare_training_frame(data, resolved_config.metric)
    artifact_timestamp = pd.Timestamp.utcnow()
    combined = _build_forecast_rows(
        history,
        resolved_config,
        artifact_timestamp=artifact_timestamp,
    )

    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(resolved_path, index=False)
    return resolved_path


@_cache_decorator()
def load_forecast_results(
    *,
    artifact_path: Optional[Path] = None,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Load the offline forecast artifact as a DataFrame.

    Args:
        artifact_path: Optional custom location of the forecast artifact.
        force_refresh: When True, regenerate the artifact before loading.

    Returns:
        DataFrame containing actuals and forecast rows with metadata columns.

    Raises:
        ValueError: If the loaded artifact is missing expected columns.
    """

    resolved_path = _resolve_artifact_path(artifact_path)
    if force_refresh or not resolved_path.exists():
        generate_forecast_artifact(output_path=resolved_path)

    frame = pd.read_csv(
        resolved_path,
        parse_dates=["period_start", "generated_at", "training_start", "training_end"],
    )
    missing_columns = _EXPECTED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise ValueError(
            "Forecast artifact missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    return frame


def _format_cli_message(path: Path) -> str:
    """Return a human-friendly CLI summary string."""

    size_bytes = path.stat().st_size if path.exists() else 0
    return f"Forecast artifact generated at {path} ({size_bytes} bytes)."


def main() -> None:  # pragma: no cover - CLI helper
    """Execute the offline forecast pipeline when run as a script."""

    path = generate_forecast_artifact()
    print(_format_cli_message(path))


if __name__ == "__main__":  # pragma: no cover - module execution entry point
    main()
