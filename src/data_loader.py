"""Data loading utilities for the sales analytics dashboard."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import pandas as pd

try:
    import streamlit as st
except ImportError:  # pragma: no cover - Streamlit is optional during tests
    st = None  # type: ignore

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "Sales_dataset.xlsx"
CANONICAL_CSV_PATH = ROOT_DIR / "data" / "sales_data.csv"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "processed" / "sales_dataset.csv"

_COLUMN_RENAME_MAP = {
    "CUSTOMER_CODE": "Customer ID",
    "CUSTOMER_NAME": "Customer Name",
    "QUANTITY_ORDERED": "Quantity Ordered",
    "MSRP": "MSRP",
    "Estimated Cost Price (50%)": "Cost Price",
    "Selling price": "Selling Price",
    "SALES": "Sales",
    "Profit per unit": "Profit per Unit",
    "Total profit / loss": "Total Profit/Loss",
    "Status": "Status",
    "ORDER_DATE": "Order Date",
    "MONTH": "Month",
    "YEAR": "Year",
    "PRODUCT": "Product",
    "PRODUCT_CODE": "Product Code",
    "CITY": "City",
    "COUNTRY": "Country",
    "DEALSIZE": "Deal Size",
}
_NUMERIC_COLUMNS = (
    "MSRP",
    "Cost Price",
    "Selling Price",
    "Sales",
    "Profit per Unit",
    "Total Profit/Loss",
)
_INT_COLUMNS = ("Quantity Ordered", "Year")


def _cache_decorator():
    """Return the Streamlit cache decorator when available."""
    if st is None or not hasattr(st, "cache_data"):
        def _wrapper(func):
            return func
        return _wrapper
    return st.cache_data(show_spinner=False)


def _compose_rename_map(columns: Sequence[str]) -> dict[str, str]:
    """Build a mapping from raw column labels to canonical names."""
    mapping: dict[str, str] = {}
    for column in columns:
        stripped = column.strip()
        target = _COLUMN_RENAME_MAP.get(stripped, stripped)
        mapping[column] = target
    return mapping


def _apply_column_standards(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalise column labels and data types to match architecture expectations."""
    frame = frame.rename(columns=_compose_rename_map(frame.columns))

    if "Order Date" in frame.columns:
        frame["Order Date"] = pd.to_datetime(frame["Order Date"], errors="coerce")
    if "Month" in frame.columns:
        frame["Month"] = frame["Month"].astype(str)

    for column in _INT_COLUMNS:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Int64")

    for column in _NUMERIC_COLUMNS:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    return frame


def _write_csv_exports(frame: pd.DataFrame) -> None:
    """Persist canonical CSV copies used by the rest of the project."""
    CANONICAL_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(CANONICAL_CSV_PATH, index=False)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(PROCESSED_DATA_PATH, index=False)


@_cache_decorator()
def load_data(*, force_refresh: bool = False) -> pd.DataFrame:
    """Load the canonical sales dataset as a DataFrame.

    Args:
        force_refresh: When True, re-read the Excel workbook even if cached CSV exists.

    Returns:
        A DataFrame with standardised column labels and dtypes.

    Raises:
        FileNotFoundError: If neither canonical CSV nor raw Excel exists.
    """
    if not force_refresh and CANONICAL_CSV_PATH.exists():
        frame = pd.read_csv(CANONICAL_CSV_PATH, parse_dates=["Order Date"])
        return _apply_column_standards(frame)

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Expected dataset at {RAW_DATA_PATH} or {CANONICAL_CSV_PATH}."
        )

    frame = pd.read_excel(RAW_DATA_PATH)
    frame = _apply_column_standards(frame)
    _write_csv_exports(frame)
    return frame


def get_filtered_data(
    df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    countries: Optional[Sequence[str]] = None,
    status_filter: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Apply standard dashboard filters to the sales dataset."""
    filtered = df.copy()

    if "Order Date" in filtered.columns:
        filtered = filtered[
            (filtered["Order Date"] >= start_date)
            & (filtered["Order Date"] <= end_date)
        ]

    if countries:
        filtered = filtered[filtered["Country"].isin(countries)]

    if status_filter:
        filtered = filtered[filtered["Status"].isin(status_filter)]

    return filtered


def available_statuses(df: pd.DataFrame) -> Sequence[str]:
    """Return the unique status values present in the dataset."""
    if "Status" not in df:
        return tuple()
    return tuple(sorted(df["Status"].dropna().unique().tolist()))


def available_countries(df: pd.DataFrame) -> Sequence[str]:
    """Return the unique country values present in the dataset."""
    if "Country" not in df:
        return tuple()
    return tuple(sorted(df["Country"].dropna().unique().tolist()))


__all__ = [
    "RAW_DATA_PATH",
    "CANONICAL_CSV_PATH",
    "PROCESSED_DATA_PATH",
    "load_data",
    "get_filtered_data",
    "available_statuses",
    "available_countries",
]
