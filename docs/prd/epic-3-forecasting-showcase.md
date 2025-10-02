# Epic 3 Forecasting Showcase

## Story 3.1 Forecast Pipeline Preparation
As a data scientist,
I want a script/notebook that trains a simple forecasting model and exports predictions,
so that the Streamlit app can load ready-made forecasts without runtime retraining.

### Acceptance Criteria
1. Offline artifact (script or notebook) loads the static dataset, trains a moving average or ARIMA model, and writes forecast results to disk (CSV/JSON).
2. Documentation explains model choice, horizon, and evaluation metrics.
3. Forecast artifact checked into repo under a `data/processed` path with reproducible instructions.
4. Unit tests cover forecast loader function to ensure schema consistency.

## Story 3.2 Forecast Visualization & Narrative
As a hiring manager,
I want to see forecast vs actual charts with confidence ranges and narrative takeaways,
so that I understand the candidate's ability to communicate predictive insights.

### Acceptance Criteria
1. Time-series chart overlays actuals with forecasted values and shaded confidence interval.
2. Toggle controls allow users to switch forecast horizon or metric (where applicable).
3. Text narrative block summarizes "what the forecast suggests" and recommended focus points.
4. Chart and narrative update according to global filters while using precomputed forecasts (no on-the-fly training).

## Story 3.3 Data & Methodology Transparency
As a stakeholder,
I want a concise section describing data provenance, preprocessing, and modeling assumptions,
so that I trust the analytics presented in the dashboard.

### Acceptance Criteria
1. Dedicated "Data & Methodology" view outlines dataset origin, transformations, and forecasting setup in plain language.
2. Links to underlying scripts/notebooks (if public) or repo paths are included.
3. Highlights that dataset is static and forecasts are precomputed; clarifies limitations.
4. Section styling matches rest of dashboard and is accessible from navigation or footer.
