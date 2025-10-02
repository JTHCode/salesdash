"""Smoke tests for analytics infrastructure."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

from src import data_loader
from src.services.analytics_service import (
    aggregate_time_series,
    build_comparison_window,
    calculate_kpis,
)


def _sample_dataframe(values: list[dict[str, object]]) -> pd.DataFrame:
    frame = pd.DataFrame(values)
    frame["Order Date"] = pd.to_datetime(frame["Order Date"], utc=False)
    return frame


def test_load_data_returns_dataframe() -> None:
    frame = data_loader.load_data(force_refresh=True)
    assert isinstance(frame, pd.DataFrame)
    assert not frame.empty
    for column in [
        "Customer ID",
        "Customer Name",
        "Quantity Ordered",
        "Order Date",
        "Sales",
        "Country",
    ]:
        assert column in frame.columns

    assert data_loader.CANONICAL_CSV_PATH.exists()
    assert data_loader.PROCESSED_DATA_PATH.exists()


def test_get_filtered_data_respects_date_range() -> None:
    frame = data_loader.load_data()
    start = frame["Order Date"].min()
    end = frame["Order Date"].min()
    filtered = data_loader.get_filtered_data(frame, start, end)
    assert not filtered.empty
    assert filtered["Order Date"].min() >= start
    assert filtered["Order Date"].max() <= end


def test_available_filters_return_sorted_sequences() -> None:
    frame = data_loader.load_data()
    countries = data_loader.available_countries(frame)
    statuses = data_loader.available_statuses(frame)
    assert list(countries) == sorted(countries)
    assert list(statuses) == sorted(statuses)
    assert countries
    assert statuses


def test_build_comparison_window_returns_prior_period() -> None:
    full = _sample_dataframe(
        [
            {
                "Order Date": datetime(2023, 1, 31),
                "Sales": 150.0,
                "Total Profit/Loss": 15.0,
                "Quantity Ordered": 2,
            },
            {
                "Order Date": datetime(2023, 2, 1),
                "Sales": 200.0,
                "Total Profit/Loss": 20.0,
                "Quantity Ordered": 3,
            },
        ]
    )
    current = full.iloc[[1]].copy()

    comparison = build_comparison_window(current, full)
    assert not comparison.empty
    assert comparison["Order Date"].iloc[0] == datetime(2023, 1, 31)


def test_build_comparison_window_handles_missing_history() -> None:
    full = _sample_dataframe(
        [
            {
                "Order Date": datetime(2023, 3, 1),
                "Sales": 100.0,
                "Total Profit/Loss": 10.0,
                "Quantity Ordered": 1,
            }
        ]
    )
    current = full.copy()

    comparison = build_comparison_window(current, full)
    assert comparison.empty


def test_aggregate_time_series_monthly() -> None:
    frame = _sample_dataframe(
        [
            {
                "Order Date": datetime(2023, 1, 1),
                "Sales": 100.0,
                "Total Profit/Loss": 30.0,
                "Quantity Ordered": 2,
            },
            {
                "Order Date": datetime(2023, 1, 15),
                "Sales": 50.0,
                "Total Profit/Loss": 10.0,
                "Quantity Ordered": 1,
            },
            {
                "Order Date": datetime(2023, 2, 1),
                "Sales": 200.0,
                "Total Profit/Loss": 60.0,
                "Quantity Ordered": 3,
            },
        ]
    )

    aggregated = aggregate_time_series(frame)
    assert list(aggregated.columns) == [
        "Order Date",
        "Sales",
        "Total Profit/Loss",
        "Quantity Ordered",
        "Profit Margin",
    ]
    assert len(aggregated) == 2
    january = aggregated.iloc[0]
    assert january["Sales"] == pytest.approx(150.0)
    assert january["Quantity Ordered"] == 3
    assert january["Profit Margin"] == pytest.approx((40.0 / 150.0) * 100)


def test_calculate_kpis_basic_metrics() -> None:
    current = _sample_dataframe(
        [
            {
                "Order Date": datetime(2023, 1, 1),
                "Sales": 1000.0,
                "Total Profit/Loss": 250.0,
                "Quantity Ordered": 10,
            },
            {
                "Order Date": datetime(2023, 1, 2),
                "Sales": 500.0,
                "Total Profit/Loss": 125.0,
                "Quantity Ordered": 5,
            },
        ]
    )

    result = calculate_kpis(current)

    assert result["total_revenue"] == pytest.approx(1500.0)
    assert result["total_profit"] == pytest.approx(375.0)
    assert result["profit_margin"] == pytest.approx((375.0 / 1500.0) * 100)
    assert result["total_orders"] == 2
    assert result["avg_order_value"] == pytest.approx(750.0)
    assert result["revenue_change"] is None
    assert result["profit_change"] is None


def test_calculate_kpis_percentage_change() -> None:
    current = _sample_dataframe(
        [
            {
                "Order Date": datetime(2023, 2, 1),
                "Sales": 200.0,
                "Total Profit/Loss": 40.0,
                "Quantity Ordered": 2,
            }
        ]
    )
    comparison = _sample_dataframe(
        [
            {
                "Order Date": datetime(2023, 1, 1),
                "Sales": 100.0,
                "Total Profit/Loss": 20.0,
                "Quantity Ordered": 1,
            }
        ]
    )

    result = calculate_kpis(current, comparison)

    assert result["revenue_change"] == pytest.approx(100.0)
    assert result["profit_change"] == pytest.approx(100.0)


def test_calculate_kpis_handles_zero_baseline() -> None:
    current = _sample_dataframe(
        [
            {
                "Order Date": datetime(2023, 3, 1),
                "Sales": 50.0,
                "Total Profit/Loss": 5.0,
                "Quantity Ordered": 1,
            }
        ]
    )
    comparison = _sample_dataframe(
        [
            {
                "Order Date": datetime(2023, 2, 1),
                "Sales": 0.0,
                "Total Profit/Loss": 0.0,
                "Quantity Ordered": 0,
            }
        ]
    )

    result = calculate_kpis(current, comparison)

    assert result["revenue_change"] is None
    assert result["profit_change"] is None


def test_calculate_kpis_empty_input_returns_zeroes() -> None:
    empty = pd.DataFrame(columns=["Order Date", "Sales", "Total Profit/Loss"])
    result = calculate_kpis(empty)

    assert result["total_revenue"] == 0.0
    assert result["total_profit"] == 0.0
    assert result["profit_margin"] == 0.0
    assert result["total_orders"] == 0
    assert result["avg_order_value"] == 0.0
    assert result["revenue_change"] is None
    assert result["profit_change"] is None


def test_calculate_kpis_is_deterministic_across_calls() -> None:
    current = _sample_dataframe(
        [
            {
                "Order Date": datetime(2023, 4, 1),
                "Sales": 120.0,
                "Total Profit/Loss": 30.0,
                "Quantity Ordered": 2,
            }
        ]
    )

    first = calculate_kpis(current)
    second = calculate_kpis(current)
    assert first == second
