# Cross-Functional Requirements

## Data Requirements
- Source dataset stored under `data/raw/` with documentation on fields (region, date, revenue, profit, etc.).
- Data treated as read-only; no user-generated content or runtime mutations.
- No data retention or purging needs because the dataset is static and bundled with the repo.
- Any schema transformations captured in preprocessing scripts with accompanying unit tests.
- Forecast artifacts versioned under `data/processed/` with timestamped filenames for traceability.

## Integration Requirements
- No external integrations or APIs are required for MVP; highlight this explicitly to prevent unnecessary architecture work.
- If optional future integrations (e.g., CRM imports) are explored, they will be tackled in post-MVP planning and kept out of current scope.
- Authentication is not needed; Streamlit app remains publicly accessible for review.

## Operational Requirements
- Deployment frequency: on-demand when significant improvements land; manual redeploy via Streamlit Community Cloud dashboard.
- Runtime environment: Streamlit Community Cloud with Python 3.11 target, using requirements.txt for dependencies.
- Monitoring: rely on Streamlit Cloud logs plus manual smoke checks after each publish; document troubleshooting steps in README.
- Support: maintain a simple issue template in the repository to capture bugs or enhancement requests from reviewers.
- Performance monitoring: leverage Streamlit analytics and optional logging statements to validate sub-2-second response time.
