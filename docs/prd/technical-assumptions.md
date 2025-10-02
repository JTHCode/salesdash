# Technical Assumptions

## Repository Structure: Monorepo
Single repository housing Streamlit app, analytics modules, and supporting assets to streamline portfolio sharing and onboarding.

## Service Architecture
Treat the dashboard as a Streamlit-centric application where backend logic (data prep, forecasting, analytics helpers) lives in Python modules imported directly by Streamlit. No separate FastAPI service; everything executes in-process, simplifying deployment to Streamlit Community Cloud and reducing operational overhead for a static dataset.

## Testing Requirements
Limit automated coverage to unit tests around data transformations, forecasting helpers, and any utility modules. Emphasize clarity and readability over extensive integration or end-to-end harnesses given the showcase scope.

## Additional Technical Assumptions and Requests
- Deployment target is Streamlit Community Cloud; avoid dependencies incompatible with that environment.
- CI/CD is not required; manual deploy through Streamlit is acceptable for portfolio cadence.
- Precompute or cache any ML forecasting artifacts before shipping the app; do not retrain models at runtime to keep interactions snappy.
- Dataset remains static, so code should assume immutable inputs and skip heavy refresh/ETL logic.
- Document required environment variables (if any) and manual steps for refreshing forecast artifacts.
- Use Streamlit Cloud logs for monitoring; review them after each demo session and record follow-up tasks for any errors encountered.
- Track notable technical debt via TODO comments and GitHub issues so future iterations are scoped deliberately.
