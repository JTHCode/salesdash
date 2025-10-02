# Project Structure

```
sales-analytics-dashboard/
├── data/
│   └── sales_data.csv              # Kaggle dataset
├── src/
│   ├── __init__.py
│   ├── app.py                      # Streamlit main app (entry point)
│   ├── data_loader.py              # Data loading & caching
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analytics_service.py    # KPI calculations
│   │   └── forecasting_service.py  # ML forecasting (scikit-learn)
│   ├── components/
│   │   ├── __init__.py
│   │   ├── kpi_cards.py           # KPI display components
│   │   ├── time_series.py         # Time series charts
│   │   ├── geographic_map.py      # Plotly map component
│   │   └── forecasting_viz.py     # Forecast visualizations
│   └── utils/
│       ├── __init__.py
│       ├── data_processing.py     # Data transformation utilities
│       └── plotting.py            # Plotly chart helpers
├── tests/
│   ├── test_analytics.py
│   └── test_forecasting.py
├── requirements.txt
├── .streamlit/
│   └── config.toml                # Streamlit configuration
├── README.md
└── .gitignore
```
