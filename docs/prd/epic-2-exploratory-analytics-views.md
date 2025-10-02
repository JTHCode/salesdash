# Epic 2 Exploratory Analytics Views

## Story 2.1 Date Range & Metric Controls
As a dashboard viewer,
I want intuitive controls to adjust date ranges and choose revenue vs profit metrics,
so that subsequent charts and summaries reflect the slice I care about.

### Acceptance Criteria
1. UI presents date picker (or presets) plus metric selection toggle.
2. Selected filters flow into shared state accessed by charts and KPI cards.
3. Controls persist selections across reruns and default to a sensible recent period.
4. Unit tests verify filter handlers update state objects correctly.

## Story 2.2 Time-Series Visualization
As an analyst,
I want a time-series chart displaying sales and profit trends by selected interval,
so that I can observe momentum and identify inflection points.

### Acceptance Criteria
1. Plotly line/area chart renders aggregated values per chosen interval (monthly/quarterly/yearly).
2. Users can toggle between intervals and metric focus; chart updates immediately.
3. Hover tooltips surface period values and deltas; annotations highlight notable peaks/troughs.
4. Performance stays within two-second response thanks to cached data transformations.

## Story 2.3 Regional Performance Heatmap
As a business stakeholder,
I want a geographic heatmap showing revenue density with hoverable detail,
so that I can compare regional performance at a glance.

### Acceptance Criteria
1. Map component (Plotly choropleth or similar) displays the static dataset aggregated by region/state.
2. Hover tooltips expose revenue, profit margin, and growth for the hovered region.
3. Secondary table or card stack lists top/bottom regions matching filters.
4. Map respects selected metric and date filters.
