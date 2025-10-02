"""Production KPI cards component for the dashboard."""
from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

try:
    from services.analytics_service import (
        build_comparison_window,
        calculate_kpis,
    )
except ImportError:  # pragma: no cover - support `streamlit run src/app.py`
    from src.services.analytics_service import (  # type: ignore
        build_comparison_window,
        calculate_kpis,
    )

NO_DATA_MESSAGE = "No data available for the selected filters. Adjust the filters to view KPIs."


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def _format_count(value: int) -> str:
    return f"{value:,}"


def _format_delta(delta: Optional[float]) -> Optional[str]:
    if delta is None:
        return None
    return f"{delta:+.1f}%"


def _with_focus(label: str, focus: str) -> str:
    return f"{label} ? Focus" if focus == label else label


def render(
    current_df: pd.DataFrame,
    full_df: pd.DataFrame,
    *,
    metric_label: str | None = None,
) -> None:
    """Render KPI metrics with trend indicators and diagnostic captions."""
    st.subheader("KPI Summary Cards")

    if current_df is None or current_df.empty:
        st.warning(NO_DATA_MESSAGE)
        return

    comparison_df = build_comparison_window(current_df, full_df)
    comparison_df = comparison_df if not comparison_df.empty else None

    kpis = calculate_kpis(current_df, comparison_df)

    focus_label = (metric_label or "Revenue").title()
    st.caption(
        f"Highlighted metric: {focus_label} ? Rows analysed: {len(current_df):,}"
    )

    if comparison_df is not None:
        st.caption(
            "Comparison window: "
            f"{comparison_df['Order Date'].min().date()} ? {comparison_df['Order Date'].max().date()}"
        )
    else:
        st.caption("Comparison window: insufficient history for period-over-period metrics")

    card_container = st.container()
    with card_container:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label=_with_focus("Total Revenue", focus_label),
                value=_format_currency(kpis["total_revenue"]),
                delta=_format_delta(kpis.get("revenue_change")),
                help="Sum of Sales for the active selection.",
            )

        with col2:
            st.metric(
                label=_with_focus("Total Profit", focus_label),
                value=_format_currency(kpis["total_profit"]),
                delta=_format_delta(kpis.get("profit_change")),
                help="Sum of Total Profit/Loss for the active selection.",
            )

        with col3:
            st.metric(
                label="Profit Margin",
                value=f"{kpis['profit_margin']:.1f}%",
                help="Profit margin expressed as Total Profit divided by Total Revenue.",
            )

        with col4:
            st.metric(
                label="Total Orders",
                value=_format_count(int(kpis["total_orders"])),
                help="Number of orders in the filtered dataset.",
            )

    if comparison_df is None:
        st.info(
            "Period-over-period deltas require enough historical data to establish a prior window matching the current selection."
        )


__all__ = ["render"]
