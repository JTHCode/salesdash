"""Analytics utilities for KPI aggregation and reusable time-series helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd

try:
    import streamlit as st
except ImportError:  # pragma: no cover - streamlit is optional in tests
    st = None  # type: ignore


def _cache_decorator():
    """Return the Streamlit cache decorator when available."""
    if st is None or not hasattr(st, "cache_data"):
        def _identity(func):
            return func

        return _identity
    return st.cache_data(show_spinner=False)


@dataclass(frozen=True)
class KpiResult:
    """Container for KPI values used in the dashboard."""

    total_revenue: float
    total_profit: float
    profit_margin: float
    total_orders: int
    avg_order_value: float
    revenue_change: Optional[float]
    profit_change: Optional[float]

    def as_dict(self) -> Dict[str, Any]:
        """Return the KPI values as a serialisable dictionary."""
        return {
            "total_revenue": self.total_revenue,
            "total_profit": self.total_profit,
            "profit_margin": self.profit_margin,
            "total_orders": self.total_orders,
            "avg_order_value": self.avg_order_value,
            "revenue_change": self.revenue_change,
            "profit_change": self.profit_change,
        }


def _safe_divide(numerator: float, denominator: float) -> float:
    """Return numerator / denominator guarding against zero."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _percentage_change(current: float, previous: float) -> Optional[float]:
    """Compute the percentage change, returning None when undefined."""
    if previous == 0 or previous is None:
        return None
    return ((current - previous) / previous) * 100


@_cache_decorator()
def build_comparison_window(
    current_df: pd.DataFrame,
    full_df: pd.DataFrame,
) -> pd.DataFrame:
    """Return a prior-period slice that matches the current selection window.

    The result is cached so repeated interactions with identical filters reuse the
    same computation without recomputing the window boundaries from scratch.
    """
    if (
        current_df is None
        or current_df.empty
        or "Order Date" not in current_df
        or full_df is None
        or full_df.empty
        or "Order Date" not in full_df
    ):
        return pd.DataFrame()

    current_start = current_df["Order Date"].min()
    current_end = current_df["Order Date"].max()
    if pd.isna(current_start) or pd.isna(current_end):
        return pd.DataFrame()

    period_days = max((current_end - current_start).days + 1, 1)
    prev_end = current_start - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=period_days - 1)

    mask = (full_df["Order Date"] >= prev_start) & (full_df["Order Date"] <= prev_end)
    comparison = full_df.loc[mask]
    return comparison.reset_index(drop=True)


@_cache_decorator()
def aggregate_time_series(
    df: pd.DataFrame,
    period: str = "MS",
) -> pd.DataFrame:
    """Aggregate sales data by the requested resampling period.

    Args:
        df: Dataset to aggregate. Must include an ``Order Date`` column.
        period: Pandas-compatible resample frequency code (e.g. ``"W"`` or ``"Q"``).

    Returns:
        A DataFrame grouped by the period with revenue, profit, quantity, and
        derived profit margin columns. Empty frame if source data is missing.
    """
    if df is None or df.empty or "Order Date" not in df:
        return pd.DataFrame()

    copy = df[["Order Date", "Sales", "Total Profit/Loss", "Quantity Ordered"]].copy()
    copy["Order Date"] = pd.to_datetime(copy["Order Date"], errors="coerce")
    copy = copy.dropna(subset=["Order Date"]).set_index("Order Date")

    aggregated = copy.resample(period).agg(
        {
            "Sales": "sum",
            "Total Profit/Loss": "sum",
            "Quantity Ordered": "sum",
        }
    )
    aggregated = aggregated.reset_index()

    aggregated["Profit Margin"] = aggregated.apply(
        lambda row: _safe_divide(row["Total Profit/Loss"], row["Sales"]) * 100
        if row["Sales"]
        else 0.0,
        axis=1,
    )
    return aggregated


@_cache_decorator()
def get_geographic_data(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Aggregate sales metrics by country for geographic visualizations."""
    if df is None or df.empty or "Country" not in df:
        return []

    aggregations: dict[str, str] = {}
    if "Sales" in df.columns:
        aggregations["Sales"] = "sum"
    if "Total Profit/Loss" in df.columns:
        aggregations["Total Profit/Loss"] = "sum"
    if "Customer ID" in df.columns:
        aggregations["Customer ID"] = "nunique"
    if "Quantity Ordered" in df.columns:
        aggregations["Quantity Ordered"] = "sum"

    if not aggregations:
        return []

    geo = (
        df.groupby("Country")
        .agg(aggregations)
        .reset_index()
    )

    if "Sales" in geo.columns and "Total Profit/Loss" in geo.columns:
        geo["Profit Margin"] = geo.apply(
            lambda row: _safe_divide(row["Total Profit/Loss"], row["Sales"]) * 100
            if row["Sales"]
            else 0.0,
            axis=1,
        )
    else:
        geo["Profit Margin"] = 0.0

    return geo.to_dict("records")


@_cache_decorator()
def calculate_kpis(
    current_df: pd.DataFrame,
    comparison_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """Calculate KPI metrics for the current selection and cached for reuse."""
    if current_df is None or current_df.empty:
        empty_result = KpiResult(
            total_revenue=0.0,
            total_profit=0.0,
            profit_margin=0.0,
            total_orders=0,
            avg_order_value=0.0,
            revenue_change=None,
            profit_change=None,
        )
        return empty_result.as_dict()

    total_revenue = float(current_df.get("Sales", pd.Series(dtype="float")).sum())
    total_profit = float(current_df.get("Total Profit/Loss", pd.Series(dtype="float")).sum())
    total_orders = int(len(current_df))
    avg_order_value = float(_safe_divide(total_revenue, total_orders) if total_orders else 0.0)
    profit_margin = float(_safe_divide(total_profit, total_revenue) * 100 if total_revenue else 0.0)

    revenue_change = None
    profit_change = None
    if comparison_df is not None and not comparison_df.empty:
        prev_revenue = float(comparison_df.get("Sales", pd.Series(dtype="float")).sum())
        prev_profit = float(comparison_df.get("Total Profit/Loss", pd.Series(dtype="float")).sum())
        revenue_change = _percentage_change(total_revenue, prev_revenue)
        profit_change = _percentage_change(total_profit, prev_profit)

    result = KpiResult(
        total_revenue=total_revenue,
        total_profit=total_profit,
        profit_margin=profit_margin,
        total_orders=total_orders,
        avg_order_value=avg_order_value,
        revenue_change=revenue_change,
        profit_change=profit_change,
    )
    return result.as_dict()


__all__ = [
    "KpiResult",
    "aggregate_time_series",
    "build_comparison_window",
    "calculate_kpis",
    "get_geographic_data",
]
