# Sales Analytics Portfolio Dashboard Product Requirements Document (PRD)

## Goals and Background Context

### Goals
- Showcase ability to build polished analytics dashboards that communicate actionable insights for business stakeholders.
- Demonstrate fluency with Python, Streamlit, and modular analytics code in an integrated data product.
- Highlight competency in time-series forecasting and translating models into intuitive visuals.
- Convey readiness for data analyst, full-stack developer, and ML engineer responsibilities.

### Background Context
The portfolio project targets hiring managers who need proof a candidate can transform a static sales dataset into an interactive decision-support tool. Leveraging Streamlit for rapid UI delivery with embedded Python analytics modules positions the dashboard as both a polished demo and a foundation for future scaling. The emphasis on KPI storytelling, geographic exploration, and lightweight forecasting shows range across analytics, frontend presentation, and applied ML without introducing unnecessary architectural overhead for a showcase artifact.

### Problem Statement
Hiring managers often discard resumes that lack tangible examples of analytics execution, forcing candidates to overexplain skills during interviews. Without a cohesive, interactive demonstration, it is hard to validate whether the candidate can extract insights from data, design usable dashboards, and communicate results. This project addresses that gap by providing a production-quality sales analytics dashboard that surfaces business outcomes within minutes.

### Target Audience
- Hiring managers and recruiters evaluating candidates for data analyst, full-stack developer, or ML engineer roles.
- Technical interviewers who need a reproducible artifact to explore a candidate's code quality and analytical thinking.
- Portfolio reviewers on GitHub or LinkedIn scanning for polished, interactive projects.

### Success Metrics
- Achieve at least 4 of 5 positive feedback scores ("clear insight","professional polish","would demo to team") from targeted hiring manager reviews.
- Secure 3+ interview callbacks or screening invites that specifically reference the dashboard within 30 days of release.
- Demonstrate dashboard load times under 2 seconds for core views and keep reviewer drop-off below 20% per analytics logs.

### Differentiation
Unlike generic sales dashboards that focus purely on static charts, this project bundles KPI storytelling, geographic exploration, and a forecast narrative in a single streamlined experience. It demonstrates end-to-end ownership-from data preparation to deployment on Streamlit Community Cloud-making it easier for evaluators to gauge both engineering and analytical maturity without provisioning infrastructure.

### Change Log
| Date       | Version | Description                                                           | Author    |
|------------|---------|-----------------------------------------------------------------------|-----------|
| 2025-09-30 | v0.2    | Added problem statement, scope boundaries, validation, and X-functional sections | John (PM) |
| 2025-09-30 | v0.1    | Initial PRD draft from brief                                          | John (PM) |

## Requirements

### Functional
1. FR1: Provide KPI summary cards for total revenue, profit margin, and growth rate including period-over-period deltas with visual up/down indicators.
2. FR2: Deliver interactive time-series charts for sales and profit that honor user-selected date ranges and dynamically update in real time.
3. FR3: Support drill-down toggles between monthly, quarterly, and yearly views so visitors can inspect trends at multiple resolutions.
4. FR4: Render a geographic performance heatmap highlighting regional revenue density with hover tooltips that expose region-level metrics.
5. FR5: Expose a lightweight ML forecasting view that overlays baseline predictions (e.g., moving average or ARIMA) with actuals plus configurable confidence intervals.
6. FR6: Provide quick metric switching so users can pivot KPI and chart views between revenue, profit, and growth-focused perspectives.

### Non Functional
1. NFR1: Implement the experience with Streamlit for the UI layer and modular Python analytics modules (no separate FastAPI service) to demonstrate full-stack fluency.
2. NFR2: Optimize interactions so primary dashboard views respond within two seconds under portfolio demo loads and leverage caching for repeated queries.
3. NFR3: Keep data operations stateless against a bundled Kaggle sales dataset, avoiding external databases or authentication dependencies.
4. NFR4: Maintain a professional, responsive layout tuned for desktop viewing while remaining legible on tablet-sized screens.
5. NFR5: Ensure the codebase is cleanly documented, linted, and unit-tested around data transforms and forecasting logic to showcase production-readiness.
6. NFR6: Provide baseline logging and manual monitoring guidance using Streamlit Cloud logs to surface runtime errors and support demo stability.

## MVP Scope & Validation

### In Scope (MVP)
- KPI summary cards with trend indicators.
- Interactive time-series charts with interval toggles (monthly/quarterly/yearly).
- Geographic heatmap with hoverable regional performance details.
- Precomputed sales forecasting overlay with narrative explanation.
- Metric and filter controls shared across dashboard views.
- Data & Methodology page summarizing dataset provenance and modeling approach.

### Out of Scope / Deferred
- Advanced forecasting models (Prophet, LSTM, ensembles).
- Customer segmentation and cohort analysis.
- Product-level or SKU drill-down dashboards.
- Automated anomaly detection or alerting workflows.
- Export capabilities (PDF, CSV) and scheduled reporting.

### MVP Validation Approach
- Share deployed dashboard with at least five hiring managers/recruiters and collect structured feedback on clarity, usefulness, and polish.
- Track interview callbacks or portfolio mentions referencing the project within 30 days of launch to confirm business impact.
- Monitor Streamlit analytics for load time (<2 seconds) and error-free sessions during demos; log remediation tasks if thresholds slip.
- Iterate copy, visuals, or interactions based on reviewer insights before promoting the project broadly.

## User Interface Design Goals

### Overall UX Vision
Deliver a sleek, data-storytelling dashboard that immediately surfaces health metrics while inviting deeper exploration. The experience should feel like a polished analytics product demo: rich visuals, intuitive structure, and smooth transitions that let recruiters or hiring managers evaluate skills without friction.

### Key Interaction Paradigms
- Card-first summary highlighting core KPIs at the top with trend arrows.
- Contextual filters (date range, metric focus) that instantly update charts.
- Tabbed or segmented layout separating time-series, geographic, and forecasting views.
- Hover tooltips and annotations that translate numbers into plain-language insights.

### Core Screens and Views
- Executive Overview (KPI cards + trend callouts)
- Time-Series Insights (line/area charts with forecasting overlay)
- Regional Performance (map heatmap with supporting table)
- Forecast Detail (model assumptions, confidence intervals, "what to watch" notes)
- Data & Methodology (brief explanation of dataset, preprocessing, forecasting approach)

### Accessibility: WCAG AA
Adopt AA-level contrast and text sizing so visualizations remain legible for varied viewers. Include alt text or captions for key charts to show accessibility intent, even if Streamlit limits full compliance.

### Branding
Modern, portfolio-appropriate theme anchored around a dark-neutral canvas with accent colors that align with sales analytics (greens for growth, reds for risk). Use consistent typography (e.g., pairing a sans-serif for body with a stronger display font for KPIs). Assumption: no existing corporate palette-confirm if you prefer a specific color system or if minimalist branding is acceptable.

### Target Device and Platforms: Web Responsive
Primary target is desktop browser (portfolio review setting) but layout should gracefully adapt to ~1024px width tablets. Mobile-specific optimization is optional given focus on hiring demos.

## Technical Assumptions

### Repository Structure: Monorepo
Single repository housing Streamlit app, analytics modules, and supporting assets to streamline portfolio sharing and onboarding.

### Service Architecture
Treat the dashboard as a Streamlit-centric application where backend logic (data prep, forecasting, analytics helpers) lives in Python modules imported directly by Streamlit. No separate FastAPI service; everything executes in-process, simplifying deployment to Streamlit Community Cloud and reducing operational overhead for a static dataset.

### Testing Requirements
Limit automated coverage to unit tests around data transformations, forecasting helpers, and any utility modules. Emphasize clarity and readability over extensive integration or end-to-end harnesses given the showcase scope.

### Additional Technical Assumptions and Requests
- Deployment target is Streamlit Community Cloud; avoid dependencies incompatible with that environment.
- CI/CD is not required; manual deploy through Streamlit is acceptable for portfolio cadence.
- Precompute or cache any ML forecasting artifacts before shipping the app; do not retrain models at runtime to keep interactions snappy.
- Dataset remains static, so code should assume immutable inputs and skip heavy refresh/ETL logic.
- Document required environment variables (if any) and manual steps for refreshing forecast artifacts.
- Use Streamlit Cloud logs for monitoring; review them after each demo session and record follow-up tasks for any errors encountered.
- Track notable technical debt via TODO comments and GitHub issues so future iterations are scoped deliberately.

## Cross-Functional Requirements

### Data Requirements
- Source dataset stored under `data/raw/` with documentation on fields (region, date, revenue, profit, etc.).
- Data treated as read-only; no user-generated content or runtime mutations.
- No data retention or purging needs because the dataset is static and bundled with the repo.
- Any schema transformations captured in preprocessing scripts with accompanying unit tests.
- Forecast artifacts versioned under `data/processed/` with timestamped filenames for traceability.

### Integration Requirements
- No external integrations or APIs are required for MVP; highlight this explicitly to prevent unnecessary architecture work.
- If optional future integrations (e.g., CRM imports) are explored, they will be tackled in post-MVP planning and kept out of current scope.
- Authentication is not needed; Streamlit app remains publicly accessible for review.

### Operational Requirements
- Deployment frequency: on-demand when significant improvements land; manual redeploy via Streamlit Community Cloud dashboard.
- Runtime environment: Streamlit Community Cloud with Python 3.11 target, using requirements.txt for dependencies.
- Monitoring: rely on Streamlit Cloud logs plus manual smoke checks after each publish; document troubleshooting steps in README.
- Support: maintain a simple issue template in the repository to capture bugs or enhancement requests from reviewers.
- Performance monitoring: leverage Streamlit analytics and optional logging statements to validate sub-2-second response time.

## Epic List
- Epic 1: Foundation & Data Experience - Stand up the Streamlit project structure, ingest the static sales dataset, and deliver KPI summary cards with baseline analytics.
- Epic 2: Exploratory Analytics Views - Add interactive time-series and regional visualizations with filtering controls to support exploratory data insights.
- Epic 3: Forecasting Showcase - Introduce precomputed forecasting outputs, overlay them on time-series visuals, and create narrative explanations of expected trends.

## Epic 1 Foundation & Data Experience

### Story 1.1 Streamlit Project Bootstrap
As a project maintainer,
I want a Streamlit app scaffolded with modular Python packages and preloaded dataset utilities,
so that future analytics features plug into a clean, portfolio-ready structure.

#### Acceptance Criteria
1. Repository contains a Streamlit entrypoint, modular `src` packages, and configuration for local + Streamlit Cloud execution.
2. Kaggle sales dataset is stored locally, documented, and loaded via a reusable data access helper.
3. Basic page shell renders with placeholder sections for KPI, time-series, map, and forecast areas.
4. README describes setup, local run instructions, and deployment steps to Streamlit Community Cloud.

### Story 1.2 KPI Summary Cards MVP
As a hiring manager evaluating the demo,
I want KPI tiles showing revenue, profit margin, and growth with trend indicators,
so that I can quickly gauge the dashboard's ability to surface executive insights.

#### Acceptance Criteria
1. KPI cards compute metrics from the static dataset and display formatted values.
2. Period-over-period deltas and directional arrows (up/down) render based on baseline comparison (e.g., previous period).
3. Cards update when date range inputs change (reusing placeholder controls for now).
4. Visual styling matches the UX vision (consistent colors, typography, responsive card layout).

### Story 1.3 Data Utility & Caching Layer
As a developer,
I want shared utility functions for aggregations, period comparisons, and caching,
so that downstream features can reuse optimized computations without performance regressions.

#### Acceptance Criteria
1. Utility module exposes functions for computing KPI aggregates and time-based slices with docstrings.
2. Streamlit caching (`@st.cache_data`) wraps expensive computations to keep response times under two seconds.
3. Unit tests cover KPI utility behavior using sample dataset slices.
4. KPI summary cards integrate with utilities and log key actions for debugging in Streamlit.

## Epic 2 Exploratory Analytics Views

### Story 2.1 Date Range & Metric Controls
As a dashboard viewer,
I want intuitive controls to adjust date ranges and choose revenue vs profit metrics,
so that subsequent charts and summaries reflect the slice I care about.

#### Acceptance Criteria
1. UI presents date picker (or presets) plus metric selection toggle.
2. Selected filters flow into shared state accessed by charts and KPI cards.
3. Controls persist selections across reruns and default to a sensible recent period.
4. Unit tests verify filter handlers update state objects correctly.

### Story 2.2 Time-Series Visualization
As an analyst,
I want a time-series chart displaying sales and profit trends by selected interval,
so that I can observe momentum and identify inflection points.

#### Acceptance Criteria
1. Plotly line/area chart renders aggregated values per chosen interval (monthly/quarterly/yearly).
2. Users can toggle between intervals and metric focus; chart updates immediately.
3. Hover tooltips surface period values and deltas; annotations highlight notable peaks/troughs.
4. Performance stays within two-second response thanks to cached data transformations.

### Story 2.3 Regional Performance Heatmap
As a business stakeholder,
I want a geographic heatmap showing revenue density with hoverable detail,
so that I can compare regional performance at a glance.

#### Acceptance Criteria
1. Map component (Plotly choropleth or similar) displays the static dataset aggregated by region/state.
2. Hover tooltips expose revenue, profit margin, and growth for the hovered region.
3. Secondary table or card stack lists top/bottom regions matching filters.
4. Map respects selected metric and date filters.

## Epic 3 Forecasting Showcase

### Story 3.1 Forecast Pipeline Preparation
As a data scientist,
I want a script/notebook that trains a simple forecasting model and exports predictions,
so that the Streamlit app can load ready-made forecasts without runtime retraining.

#### Acceptance Criteria
1. Offline artifact (script or notebook) loads the static dataset, trains a moving average or ARIMA model, and writes forecast results to disk (CSV/JSON).
2. Documentation explains model choice, horizon, and evaluation metrics.
3. Forecast artifact checked into repo under a `data/processed` path with reproducible instructions.
4. Unit tests cover forecast loader function to ensure schema consistency.

### Story 3.2 Forecast Visualization & Narrative
As a hiring manager,
I want to see forecast vs actual charts with confidence ranges and narrative takeaways,
so that I understand the candidate's ability to communicate predictive insights.

#### Acceptance Criteria
1. Time-series chart overlays actuals with forecasted values and shaded confidence interval.
2. Toggle controls allow users to switch forecast horizon or metric (where applicable).
3. Text narrative block summarizes "what the forecast suggests" and recommended focus points.
4. Chart and narrative update according to global filters while using precomputed forecasts (no on-the-fly training).

### Story 3.3 Data & Methodology Transparency
As a stakeholder,
I want a concise section describing data provenance, preprocessing, and modeling assumptions,
so that I trust the analytics presented in the dashboard.

#### Acceptance Criteria
1. Dedicated "Data & Methodology" view outlines dataset origin, transformations, and forecasting setup in plain language.
2. Links to underlying scripts/notebooks (if public) or repo paths are included.
3. Highlights that dataset is static and forecasts are precomputed; clarifies limitations.
4. Section styling matches rest of dashboard and is accessible from navigation or footer.

## Checklist Results Report
**Date:** 2025-09-30  
**Checklist:** PM Requirements Checklist (comprehensive run)

| Category | Status | Notes |
| --- | --- | --- |
| 1. Problem Definition & Context | PASS | Problem statement, audience, success metrics, and differentiation are now explicit. |
| 2. MVP Scope Definition | PASS | In-scope, out-of-scope, and validation approach captured with rationale tied to goals. |
| 3. User Experience Requirements | PARTIAL | High-level direction defined; user flows, detailed error states, and feedback loops still pending. |
| 4. Functional Requirements | PASS | FR list maps to MVP features with clear numbering and scope. |
| 5. Non-Functional Requirements | PASS | Performance, documentation, and monitoring expectations articulated. |
| 6. Epic & Story Structure | PASS | Epics sequential with well-formed stories and acceptance criteria sized for AI execution. |
| 7. Technical Guidance | PASS | Repository, runtime, monitoring cadence, and technical debt handling documented. |
| 8. Cross-Functional Requirements | PASS | Data, integration, and operational considerations documented for architect handoff. |
| 9. Clarity & Communication | PARTIAL | Structure is clear, but user journey diagrams and stakeholder communication plan still outstanding. |

**Executive Summary**  
Overall completeness ~85%. MVP scope is confirmed as "just right" with supporting guardrails, and the document is ready for architectural planning once UX detail artifacts are produced.

**Top Issues by Priority**  
- HIGH: Document primary user flows (from landing through forecast exploration) and outline error/empty-state handling.
- MEDIUM: Add a lightweight stakeholder/communication plan plus glossary/terminology cues for non-technical reviewers.
- LOW: Include visual aids (information architecture diagram or screen map) to reinforce narrative flow.

**MVP Scope Assessment**  
Scope remains focused on demonstrating analytics craftsmanship without stretching into advanced ML or reporting. Keep the metric switching feature only if implementation effort stays manageable; otherwise, downgrade to a future enhancement.

**Technical Readiness**  
Technical constraints, deployment plan, and monitoring expectations are now documented. Key risk is ensuring Streamlit Community Cloud performance holds once visuals and forecasts are integrated; track load times during development and update caching strategy if needed.

**Recommendations**  
1. Produce user flow sketches or bullet-sequenced journeys and define error-state messaging for filtering and data load issues.  
2. Capture a stakeholder alignment note (e.g., self, mentors/reviewers) with cadence for sharing PRD updates.  
3. Add optional visual diagram illustrating dashboard layout to aid UX/Architect collaboration.  
4. Retain the checklist section for future runs; re-run after UX collateral and stakeholder plan are added to confirm full readiness.

## Next Steps

### UX Expert Prompt
TBD

### Architect Prompt
TBD

