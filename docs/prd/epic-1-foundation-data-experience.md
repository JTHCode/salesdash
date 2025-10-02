# Epic 1 Foundation & Data Experience

## Story 1.1 Streamlit Project Bootstrap
As a project maintainer,
I want a Streamlit app scaffolded with modular Python packages and preloaded dataset utilities,
so that future analytics features plug into a clean, portfolio-ready structure.

### Acceptance Criteria
1. Repository contains a Streamlit entrypoint, modular `src` packages, and configuration for local + Streamlit Cloud execution.
2. Kaggle sales dataset is stored locally, documented, and loaded via a reusable data access helper.
3. Basic page shell renders with placeholder sections for KPI, time-series, map, and forecast areas.
4. README describes setup, local run instructions, and deployment steps to Streamlit Community Cloud.

## Story 1.2 KPI Summary Cards MVP
As a hiring manager evaluating the demo,
I want KPI tiles showing revenue, profit margin, and growth with trend indicators,
so that I can quickly gauge the dashboard's ability to surface executive insights.

### Acceptance Criteria
1. KPI cards compute metrics from the static dataset and display formatted values.
2. Period-over-period deltas and directional arrows (up/down) render based on baseline comparison (e.g., previous period).
3. Cards update when date range inputs change (reusing placeholder controls for now).
4. Visual styling matches the UX vision (consistent colors, typography, responsive card layout).

## Story 1.3 Data Utility & Caching Layer
As a developer,
I want shared utility functions for aggregations, period comparisons, and caching,
so that downstream features can reuse optimized computations without performance regressions.

### Acceptance Criteria
1. Utility module exposes functions for computing KPI aggregates and time-based slices with docstrings.
2. Streamlit caching (`@st.cache_data`) wraps expensive computations to keep response times under two seconds.
3. Unit tests cover KPI utility behavior using sample dataset slices.
4. KPI summary cards integrate with utilities and log key actions for debugging in Streamlit.
