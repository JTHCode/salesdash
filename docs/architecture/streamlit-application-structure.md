# Streamlit Application Structure

### Main App (`app.py`)

python

```python
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from data_loader import load_data, get_filtered_data
from components import kpi_cards, time_series, geographic_map, forecasting_viz

# Page configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
min_date = df['Order Date'].min().date()
max_date = df['Order Date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(max_date - timedelta(days=365), max_date),
    min_value=min_date,
    max_value=max_date
)

# Country filter
all_countries = sorted(df['Country'].unique())
selected_countries = st.sidebar.multiselect(
    "Countries",
    options=all_countries,
    default=None
)

# Status filter
status_options = df['Status'].unique()
selected_status = st.sidebar.multiselect(
    "Order Status",
    options=status_options,
    default=['Completed']
)

# Apply filters
filtered_df = get_filtered_data(
    df,
    pd.to_datetime(date_range[0]),
    pd.to_datetime(date_range[1]),
    selected_countries if selected_countries else None,
    selected_status if selected_status else None
)

# Dashboard title
st.title("📊 Sales Analytics Dashboard")
st.markdown("### Interactive analysis of sales performance and forecasting")

# Render components
kpi_cards.render(filtered_df, df)
st.divider()

time_series.render(filtered_df)
st.divider()

geographic_map.render(filtered_df)
st.divider()

forecasting_viz.render(filtered_df)
```
