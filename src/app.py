"""Streamlit entry point for the sales analytics dashboard prototype."""
from __future__ import annotations

try:
    import streamlit as st
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Streamlit is required to run this dashboard. Install dependencies with `python -m pip install -r requirements.txt` and launch using `streamlit run src/app.py`."
    ) from exc

try:
    from data_loader import (
        available_countries,
        available_statuses,
        get_filtered_data,
        load_data,
    )
    from components import filter_controls, forecasting_viz, geographic_map, kpi_cards, time_series
except ImportError:  # pragma: no cover - fallback when running `python src/app.py`
    from src.data_loader import (  # type: ignore
        available_countries,
        available_statuses,
        get_filtered_data,
        load_data,
    )
    from src.components import (  # type: ignore
        filter_controls,
        forecasting_viz,
        geographic_map,
        kpi_cards,
        time_series,
    )


def main() -> None:
    """Application entry point."""
    st.set_page_config(
        page_title="Sales Analytics Portfolio Dashboard",
        layout="wide",
        page_icon="chart",
        initial_sidebar_state="expanded",
    )

    st.title("Sales Analytics Portfolio Dashboard")
    st.markdown("### Interactive analysis of sales performance and forecasting")

    data = load_data()
    filters = filter_controls.render(
        data,
        country_options=available_countries(data),
        status_options=available_statuses(data),
    )

    filtered = get_filtered_data(
        data,
        start_date=filters.start_date,
        end_date=filters.end_date,
        countries=list(filters.countries) if filters.countries else None,
        status_filter=list(filters.statuses) if filters.statuses else None,
    )

    st.caption(
        f"Showing {len(filtered):,} rows from {len(data):,} total orders between {filters.start_date.date()} and {filters.end_date.date()}."
    )
    st.caption(f"Primary metric: {filters.metric_label} (column `{filters.metric_column}`)")

    kpi_cards.render(filtered, data, metric_label=filters.metric_label)
    st.divider()

    time_series.render(filtered, metric_column=filters.metric_column)
    st.divider()

    geographic_map.render(
        filtered,
        metric_column=filters.metric_column,
        metric_label=filters.metric_label,
    )
    st.divider()

    forecasting_viz.render(filtered)

    st.sidebar.markdown("---")
    st.sidebar.info(
        "KPI summary cards are live. Upcoming stories will replace the remaining placeholder visuals with production components."
    )


if __name__ == "__main__":  # pragma: no cover - CLI execution convenience
    main()
