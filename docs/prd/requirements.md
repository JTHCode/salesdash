# Requirements

## Functional
1. FR1: Provide KPI summary cards for total revenue, profit margin, and growth rate including period-over-period deltas with visual up/down indicators.
2. FR2: Deliver interactive time-series charts for sales and profit that honor user-selected date ranges and dynamically update in real time.
3. FR3: Support drill-down toggles between monthly, quarterly, and yearly views so visitors can inspect trends at multiple resolutions.
4. FR4: Render a geographic performance heatmap highlighting regional revenue density with hover tooltips that expose region-level metrics.
5. FR5: Expose a lightweight ML forecasting view that overlays baseline predictions (e.g., moving average or ARIMA) with actuals plus configurable confidence intervals.
6. FR6: Provide quick metric switching so users can pivot KPI and chart views between revenue, profit, and growth-focused perspectives.

## Non Functional
1. NFR1: Implement the experience with Streamlit for the UI layer and modular Python analytics modules (no separate FastAPI service) to demonstrate full-stack fluency.
2. NFR2: Optimize interactions so primary dashboard views respond within two seconds under portfolio demo loads and leverage caching for repeated queries.
3. NFR3: Keep data operations stateless against a bundled Kaggle sales dataset, avoiding external databases or authentication dependencies.
4. NFR4: Maintain a professional, responsive layout tuned for desktop viewing while remaining legible on tablet-sized screens.
5. NFR5: Ensure the codebase is cleanly documented, linted, and unit-tested around data transforms and forecasting logic to showcase production-readiness.
6. NFR6: Provide baseline logging and manual monitoring guidance using Streamlit Cloud logs to surface runtime errors and support demo stability.
