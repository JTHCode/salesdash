"""Unit tests for geographic map utilities."""
from __future__ import annotations

from typing import Any

import pandas as pd
from plotly.graph_objects import Figure

from src.components import geographic_map


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Country": ["United States", "Canada", "Mexico", "Brazil", "United Kingdom"],
            "Sales": [5000, 2500, 1500, 2000, 3000],
            "Total Profit/Loss": [1500, 600, 300, 500, 900],
            "Profit Margin": [30.0, 24.0, 20.0, 25.0, 30.0],
        }
    )


def test_fetch_geo_frame_returns_dataframe(monkeypatch) -> None:
    sample = _sample_frame()
    monkeypatch.setattr(geographic_map, "get_geographic_data", lambda df: sample.to_dict("records"))
    frame = geographic_map._fetch_geo_frame(sample)
    assert isinstance(frame, pd.DataFrame)
    assert not frame.empty
    assert set(frame.columns) >= {"Country", "Sales", "Total Profit/Loss", "Profit Margin"}


def test_build_map_produces_choropleth(monkeypatch) -> None:
    geo_frame = _sample_frame()
    state = geographic_map.GeographicState(metric_column="Sales", metric_label="Revenue")
    fig = geographic_map._build_map(geo_frame, state)
    assert isinstance(fig, Figure)
    assert fig.data and fig.data[0].type == "choropleth"
    assert fig.layout.title.text.startswith("Revenue")


def test_render_ranking_table_formats_currency(monkeypatch) -> None:
    geo_frame = _sample_frame()
    state = geographic_map.GeographicState(metric_column="Sales", metric_label="Revenue")
    # Use a Streamlit stub to avoid actual rendering
    monkeypatch.setattr(geographic_map.st, "columns", lambda n: (geographic_map.st, geographic_map.st))
    monkeypatch.setattr(geographic_map.st, "dataframe", lambda *args, **kwargs: None)
    monkeypatch.setattr(geographic_map.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(geographic_map.st, "subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr(geographic_map.st, "info", lambda *args, **kwargs: None)
    geographic_map._render_ranking_table(geo_frame, state)

