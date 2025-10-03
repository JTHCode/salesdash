"""Unit tests for the offline forecasting pipeline."""
from __future__ import annotations

import pandas as pd

from src.services import (
    ForecastConfig,
    generate_forecast_artifact,
    load_forecast_results,
)

EXPECTED_COLUMNS = {
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


def test_generate_forecast_artifact_creates_expected_schema(tmp_path) -> None:
    """The offline generator should emit a CSV with all required columns."""

    output_path = tmp_path / "forecast.csv"
    config = ForecastConfig(horizon=6, window=3)

    artifact_path = generate_forecast_artifact(output_path=output_path, config=config)

    assert artifact_path == output_path
    assert artifact_path.exists(), "Expected forecast artifact to be written to disk."

    frame = pd.read_csv(artifact_path)
    missing = EXPECTED_COLUMNS.difference(frame.columns)
    assert not missing, f"Missing forecast columns: {sorted(missing)}"

    assert {"actual", "forecast"}.issubset(set(frame["type"].unique()))
    assert frame["horizon"].max() == config.horizon
    assert set(frame["method"].unique()) == {"moving_average"}


def test_load_forecast_results_generates_when_missing(tmp_path) -> None:
    """Loader should create the artifact automatically when absent."""

    output_path = tmp_path / "fresh_forecast.csv"
    assert not output_path.exists()

    frame = load_forecast_results(artifact_path=output_path)

    assert output_path.exists(), "Loader should generate missing artifacts."
    assert not frame.empty
    assert EXPECTED_COLUMNS.issubset(frame.columns)

    typed = set(frame["type"].unique())
    assert {"actual", "forecast"}.issubset(typed)
    assert (frame.loc[frame["type"] == "actual", "horizon"] == 0).all()
    assert (frame.loc[frame["type"] == "forecast", "horizon"] > 0).all()
    assert set(frame["method"].unique()) == {"moving_average"}
    assert (frame.loc[frame["type"] == "forecast", "evaluation_metric"] == "MAE").all()


__all__ = [
    "EXPECTED_COLUMNS",
    "test_generate_forecast_artifact_creates_expected_schema",
    "test_load_forecast_results_generates_when_missing",
]
