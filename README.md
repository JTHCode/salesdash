# Sales Analytics Portfolio Dashboard

An interactive Streamlit dashboard that showcases sales analytics capabilities across KPI reporting, exploratory visualisation, and lightweight forecasting. The project is designed as a portfolio piece for data-focused roles and emphasises clean engineering practices, reproducibility, and storytelling with data.

---

## Project Highlights
- End-to-end demo of data ingestion, transformation, visualisation, and forecasting in a single, deployable app.
- Streamlit UI that surfaces executive KPIs, time-series trends, regional performance, and forecast narratives.
- Modular Python codebase with clearly separated services, components, and utilities for easy extension.
- Static Kaggle dataset packaged with the repository for quick setup and deterministic results.

---

## Repository Structure
```
salesdash/
??? data/
?   ??? raw/
?   ?   ??? Sales_dataset.xlsx        # Kaggle source workbook
?   ??? processed/                    # Generated CSV caches
?   ??? sales_data.csv                # Canonical CSV emitted on first load
??? src/
?   ??? app.py                        # Streamlit entrypoint
?   ??? data_loader.py                # Data ingestion + caching helpers
?   ??? components/                   # UI building blocks (placeholders in Story 1.1)
?   ??? services/                     # Analytics / business logic modules
?   ??? utils/                        # Shared utilities (plotting, etc.)
??? tests/
?   ??? __init__.py
?   ??? test_analytics.py             # Data loader smoke tests
?   ??? test_forecasting.py           # Placeholder for future forecasts
??? .streamlit/
?   ??? config.toml                   # Theme + layout configuration
??? requirements.txt                  # Python dependencies
??? README.md
```

---

## Tech Stack
| Layer           | Tooling                     | Notes                                    |
|-----------------|-----------------------------|------------------------------------------|
| Language        | Python 3.11+                | Primary development language             |
| Frontend        | Streamlit 1.29+             | Rapid dashboard UI                       |
| Data Processing | pandas 2.1, numpy 1.26      | In-memory analytics                      |
| Visualisation   | Plotly 5.18                 | Interactive charts and maps              |
| Forecasting     | scikit-learn 1.4            | Baseline time-series models (future)     |
| Excel Support   | openpyxl 3.1                | Kaggle workbook ingestion                |
| Testing         | pytest 7.4                  | Unit / smoke test scaffold               |

---

## Getting Started
1. **Clone and enter the repository**
   ```bash
   git clone <repo-url> salesdash
   cd salesdash
   ```
2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   source .venv/bin/activate  # macOS/Linux
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Verify data availability**
   - Ensure `data/raw/Sales_dataset.xlsx` exists (already staged).
   - The first call to `load_data()` generates `data/sales_data.csv` and a processed copy under `data/processed/`.

---

## Running the Dashboard
```bash
streamlit run src/app.py
```
The placeholder app confirms that:
- Dataset loading succeeds and generates canonical CSV caches.
- Sidebar filters (date range, countries, status) drive the filtered view.
- KPI, time-series, geographic, and forecasting sections render placeholders that future stories will replace with production components.

## Offline Forecast Pipeline
The forecasting workflow runs offline so the Streamlit app can reuse cached results without retraining.

1. `python -m src.services.forecasting_service` regenerates the artifact at `data/processed/forecast_sales.csv`.
2. The pipeline aggregates monthly `Sales`, applies a rolling moving-average model (default 3-month window) for a 12-interval horizon and records 95% confidence bounds plus training metadata.
3. Output columns include actual and forecast rows alongside `method`, `horizon`, `confidence_level`, `evaluation_metric`, `evaluation_value`, and training window timestamps for downstream validation.
4. Consumers should call `services.load_forecast_results(force_refresh=True)` or rerun the generator via `python -m src.services.forecasting_service` before visualisation updates, then run `pytest -k forecasting` and `streamlit run src/app.py` for manual verification.

---

## Smoke Testing
1. **Streamlit smoke test**
   ```bash
   streamlit run src/app.py
   ```
   - Verify the caption summarises row counts.
   - Adjust filters to confirm the layout updates without errors.
2. **Unit tests**
   ```bash
   pytest
   ```
   The analytics smoke tests validate `load_data()` and `get_filtered_data()` behaviour and confirm canonical CSV exports.

---

## Deployment Guide (Streamlit Community Cloud)
1. Push the repository to GitHub.
2. In Streamlit Community Cloud, create a new app pointing to `src/app.py`.
3. Select Python 3.11 and ensure `requirements.txt` is referenced.
4. After deployment, smoke test the filters and confirm logs show successful dataset loading.

Because the dataset ships with the repository, no additional secrets or storage configuration is required for the MVP scope.

---

## Data Handling and Caching
- Source: Kaggle sales dataset bundled under `data/raw/`.
- `src/data_loader.py` standardises column names, publishes CSV caches, and exposes helpers:
  - `load_data()` returns the canonical DataFrame with caching via `st.cache_data`.
  - `get_filtered_data()` applies date, country, and status filters used by the Streamlit UI.
  - `available_countries()` and `available_statuses()` surface unique filter values.
- Caching keeps initial load performant for portfolio reviewers.

---

## Roadmap
- [ ] Build KPI summary cards with period-over-period comparisons.
- [ ] Implement interactive time-series charts (monthly/quarterly/yearly toggles).
- [ ] Add geographic heatmap and supporting regional insights.
- [ ] Integrate precomputed forecasting results with narrative guidance.
- [ ] Expand test coverage for analytics utilities and forecasting pipelines.
- [ ] Polish UX (responsive layout, accessibility tweaks, brand theming).

Refer to the Product Requirements Document (`docs/prd/`) for full epics and story sequencing.

---

## Contributing
Feel free to open issues or submit pull requests that improve documentation, add analytics features, or enhance testing. Please keep stories small and reference the corresponding PRD acceptance criteria.

---

## Support
For bugs or enhancement ideas:
- Open an issue describing the challenge and expected outcome.
- Include screenshots or Streamlit log excerpts when applicable.

Happy analysing!



