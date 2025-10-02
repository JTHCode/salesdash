# Sales Analytics Portfolio Dashboard - Technical Architecture

## Document Purpose

This architecture document defines the technical implementation for a portfolio showcase dashboard. It prioritizes clarity for development while avoiding unnecessary complexity for a single-developer portfolio project.

## High-Level Architecture

### System Overview

A Python-based analytics dashboard with two main components:

1.  **FastAPI Backend** - Data processing and ML forecasting API
2.  **Streamlit Frontend** - Interactive visualization dashboard

**Architecture Style:** Simple client-server with in-memory data processing

**Deployment Target:** Streamlit Community Cloud (single application deployment)

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User Browser                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP
                     ↓
┌─────────────────────────────────────────────────────────┐
│         Streamlit Application (Community Cloud)          │
│  ┌─────────────────────────────────────────────┐        │
│  │         Streamlit Frontend                  │        │
│  │  • Dashboard UI                             │        │
│  │  • Plotly Visualizations                    │        │
│  │  • User Interactions                        │        │
│  └──────────────┬──────────────────────────────┘        │
│                 │                                         │
│                 │ In-process function calls              │
│                 ↓                                         │
│  ┌─────────────────────────────────────────────┐        │
│  │         Backend Services (Embedded)         │        │
│  │  • Data Processing                          │        │
│  │  • ML Forecasting (scikit-learn)            │        │
│  │  • Caching Layer                            │        │
│  └──────────────┬──────────────────────────────┘        │
│                 │                                         │
│                 │ File I/O                               │
│                 ↓                                         │
│  ┌─────────────────────────────────────────────┐        │
│  │    Static Data (CSV in repo)                │        │
│  │  • Kaggle Sales Dataset                     │        │
│  └─────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

**Note:** For Streamlit Community Cloud deployment, FastAPI is not used as a separate service. Instead, backend logic is embedded as Python modules called directly by Streamlit components.

## Technology Stack

Category

Technology

Version

Purpose

**Language**

Python

3.11+

Primary development language

**Frontend Framework**

Streamlit

1.29+

Dashboard UI framework

**Data Processing**

Pandas

2.1+

Data manipulation

**Numerical Computing**

NumPy

1.26+

Numerical operations

**Visualization**

Plotly

5.18+

Interactive charts and maps

**ML/Forecasting**

scikit-learn

1.4+

Time series forecasting models

**Data Validation**

Pydantic

2.5+

Data models (optional)

**Caching**

streamlit.cache_data

built-in

In-memory result caching

## Data Architecture

### Data Model

Based on the provided Kaggle dataset columns:

python

```python
{
    # Customer Information
    'Customer ID': str,
    'Customer Name': str,
    
    # Order Details
    'Quantity Ordered': int,
    'Status': str,  # Completed/Cancelled/Returned
    
    # Pricing
    'MSRP': float,
    'Cost Price': float,
    'Selling Price': float,
    
    # Financial Metrics
    'Sales': float,
    'Profit per Unit': float,
    'Total Profit/Loss': float,
    
    # Time Information
    'Order Date': datetime,
    'Month': str,
    'Year': int,
    
    # Product Information
    'Product': str,
    'Product Code': str,
    
    # Geographic Information
    'City': str,
    'Country': str,
    
    # Segmentation
    'Deal Size': str  # Small/Medium/Large
}
```

### Data Flow

1.  **Data Loading** (On App Startup)
    -   CSV loaded into Pandas DataFrame
    -   Cached with `@st.cache_data` decorator
    -   Data cleaning/type conversion performed once
2.  **Data Processing** (Per User Interaction)
    -   Filter by date range, country, product, status
    -   Aggregate for KPIs (sum, mean, growth rates)
    -   Prepare for visualization (group by time period/country)
3.  **Data Consumption** (Frontend Components)
    -   Call processing functions directly
    -   Render with Plotly visualizations
    -   Cache processed results with `@st.cache_data`

## Project Structure

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

## Core Services Implementation

### 1. Data Loader (`data_loader.py`)

python

```python
import streamlit as st
import pandas as pd
from datetime import datetime

@st.cache_data
def load_data():
    """Load and prepare the sales dataset."""
    df = pd.read_csv('data/sales_data.csv')
    
    # Data type conversions
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year'] = df['Year'].astype(int)
    df['Quantity Ordered'] = df['Quantity Ordered'].astype(int)
    
    # Ensure numeric columns
    numeric_cols = ['MSRP', 'Cost Price', 'Selling Price', 
                    'Sales', 'Profit per Unit', 'Total Profit/Loss']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter out cancelled/returned orders for main analysis
    # (can be toggled via UI filter)
    return df

@st.cache_data
def get_filtered_data(df, start_date, end_date, 
                      countries=None, status_filter=None):
    """Filter dataset based on user selections."""
    filtered = df.copy()
    
    # Date filter
    filtered = filtered[
        (filtered['Order Date'] >= start_date) & 
        (filtered['Order Date'] <= end_date)
    ]
    
    # Country filter
    if countries:
        filtered = filtered[filtered['Country'].isin(countries)]
    
    # Status filter
    if status_filter:
        filtered = filtered[filtered['Status'].isin(status_filter)]
    
    return filtered
```

### 2. Analytics Service (`analytics_service.py`)

python

```python
import pandas as pd
import numpy as np
from typing import Dict, List

@st.cache_data
def calculate_kpis(df: pd.DataFrame, 
                   comparison_df: pd.DataFrame = None) -> Dict:
    """Calculate key performance indicators."""
    
    kpis = {
        'total_revenue': df['Sales'].sum(),
        'total_profit': df['Total Profit/Loss'].sum(),
        'profit_margin': (df['Total Profit/Loss'].sum() / 
                         df['Sales'].sum() * 100) if df['Sales'].sum() > 0 else 0,
        'total_orders': len(df),
        'avg_order_value': df['Sales'].mean(),
    }
    
    # Period-over-period comparison
    if comparison_df is not None and len(comparison_df) > 0:
        prev_revenue = comparison_df['Sales'].sum()
        prev_profit = comparison_df['Total Profit/Loss'].sum()
        
        kpis['revenue_change'] = (
            ((kpis['total_revenue'] - prev_revenue) / prev_revenue * 100)
            if prev_revenue > 0 else 0
        )
        kpis['profit_change'] = (
            ((kpis['total_profit'] - prev_profit) / prev_profit * 100)
            if prev_profit > 0 else 0
        )
    
    return kpis

@st.cache_data
def get_time_series_data(df: pd.DataFrame, 
                         period: str = 'M') -> pd.DataFrame:
    """Aggregate data by time period.
    
    Args:
        period: 'D' (daily), 'W' (weekly), 'M' (monthly), 'Q' (quarterly)
    """
    df_copy = df.copy()
    df_copy.set_index('Order Date', inplace=True)
    
    aggregated = df_copy.resample(period).agg({
        'Sales': 'sum',
        'Total Profit/Loss': 'sum',
        'Quantity Ordered': 'sum'
    }).reset_index()
    
    # Calculate profit margin
    aggregated['Profit Margin'] = (
        aggregated['Total Profit/Loss'] / aggregated['Sales'] * 100
    )
    
    return aggregated

@st.cache_data
def get_geographic_data(df: pd.DataFrame) -> List[Dict]:
    """Aggregate data by country."""
    geo_data = df.groupby('Country').agg({
        'Sales': 'sum',
        'Total Profit/Loss': 'sum',
        'Customer ID': 'nunique',
        'Quantity Ordered': 'sum'
    }).reset_index()
    
    geo_data['Profit Margin'] = (
        geo_data['Total Profit/Loss'] / geo_data['Sales'] * 100
    )
    
    geo_data.rename(columns={
        'Customer ID': 'Unique Customers'
    }, inplace=True)
    
    return geo_data.to_dict('records')

@st.cache_data
def get_product_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze product performance."""
    product_data = df.groupby('Product').agg({
        'Sales': 'sum',
        'Total Profit/Loss': 'sum',
        'Quantity Ordered': 'sum'
    }).reset_index()
    
    product_data['Profit Margin'] = (
        product_data['Total Profit/Loss'] / product_data['Sales'] * 100
    )
    
    return product_data.sort_values('Sales', ascending=False)

@st.cache_data
def get_deal_size_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze by deal size segments."""
    deal_data = df.groupby('Deal Size').agg({
        'Sales': 'sum',
        'Total Profit/Loss': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()
    
    return deal_data
```

### 3. Forecasting Service (`forecasting_service.py`)

python

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, Tuple

@st.cache_data(ttl=3600)
def moving_average_forecast(historical_data: pd.Series, 
                            periods: int = 12,
                            window: int = 3) -> Dict:
    """Simple moving average forecast."""
    
    # Calculate moving average
    ma = historical_data.rolling(window=window).mean()
    last_ma = ma.iloc[-1]
    
    # Generate forecast (simple: use last MA value)
    forecast_values = [last_ma] * periods
    
    # Calculate confidence interval (simple: ±10% of forecast)
    std = historical_data.std()
    confidence_lower = [val - std for val in forecast_values]
    confidence_upper = [val + std for val in forecast_values]
    
    # Generate future dates
    last_date = historical_data.index[-1]
    freq = pd.infer_freq(historical_data.index) or 'MS'
    forecast_dates = pd.date_range(
        start=last_date, 
        periods=periods + 1, 
        freq=freq
    )[1:]
    
    return {
        'historical_dates': historical_data.index.tolist(),
        'historical_values': historical_data.values.tolist(),
        'forecast_dates': forecast_dates.tolist(),
        'forecast_values': forecast_values,
        'confidence_lower': confidence_lower,
        'confidence_upper': confidence_upper,
        'method': f'Moving Average (window={window})'
    }

@st.cache_data(ttl=3600)
def linear_regression_forecast(historical_data: pd.Series,
                               periods: int = 12) -> Dict:
    """Linear regression forecast using scikit-learn."""
    
    # Prepare data
    X = np.arange(len(historical_data)).reshape(-1, 1)
    y = historical_data.values
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate predictions
    future_X = np.arange(len(historical_data), 
                        len(historical_data) + periods).reshape(-1, 1)
    forecast_values = model.predict(future_X)
    
    # Calculate residuals for confidence interval
    residuals = y - model.predict(X)
    std_residual = np.std(residuals)
    
    # Confidence intervals (±2 standard deviations)
    confidence_lower = forecast_values - (2 * std_residual)
    confidence_upper = forecast_values + (2 * std_residual)
    
    # Generate future dates
    last_date = historical_data.index[-1]
    freq = pd.infer_freq(historical_data.index) or 'MS'
    forecast_dates = pd.date_range(
        start=last_date,
        periods=periods + 1,
        freq=freq
    )[1:]
    
    return {
        'historical_dates': historical_data.index.tolist(),
        'historical_values': historical_data.values.tolist(),
        'forecast_dates': forecast_dates.tolist(),
        'forecast_values': forecast_values.tolist(),
        'confidence_lower': confidence_lower.tolist(),
        'confidence_upper': confidence_upper.tolist(),
        'method': 'Linear Regression',
        'r_squared': model.score(X, y)
    }
```

## Streamlit Application Structure

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

## Visualization Components

### KPI Cards Component (`components/kpi_cards.py`)

python

```python
import streamlit as st
from services.analytics_service import calculate_kpis
from datetime import timedelta

def render(current_df, full_df):
    """Render KPI cards with period-over-period comparison."""
    
    # Get comparison period (previous period of same length)
    if len(current_df) > 0:
        current_start = current_df['Order Date'].min()
        current_end = current_df['Order Date'].max()
        period_length = (current_end - current_start).days
        
        prev_start = current_start - timedelta(days=period_length)
        prev_end = current_start - timedelta(days=1)
        
        comparison_df = full_df[
            (full_df['Order Date'] >= prev_start) &
            (full_df['Order Date'] <= prev_end)
        ]
    else:
        comparison_df = None
    
    kpis = calculate_kpis(current_df, comparison_df)
    
    # Display KPIs in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${kpis['total_revenue']:,.0f}",
            f"{kpis.get('revenue_change', 0):.1f}%" if 'revenue_change' in kpis else None
        )
    
    with col2:
        st.metric(
            "Total Profit",
            f"${kpis['total_profit']:,.0f}",
            f"{kpis.get('profit_change', 0):.1f}%" if 'profit_change' in kpis else None
        )
    
    with col3:
        st.metric(
            "Profit Margin",
            f"{kpis['profit_margin']:.1f}%"
        )
    
    with col4:
        st.metric(
            "Total Orders",
            f"{kpis['total_orders']:,}"
        )
```

### Geographic Map Component (`components/geographic_map.py`)

python

```python
import streamlit as st
import plotly.express as px
from services.analytics_service import get_geographic_data

def render(filtered_df):
    """Render geographic performance heatmap."""
    
    st.subheader("🗺️ Geographic Performance")
    
    geo_data = get_geographic_data(filtered_df)
    
    if not geo_data:
        st.warning("No data available for selected filters")
        return
    
    # Create choropleth map
    import plotly.graph_objects as go
    
    fig = go.Figure(data=go.Choropleth(
        locations=[d['Country'] for d in geo_data],
        z=[d['Sales'] for d in geo_data],
        locationmode='country names',
        colorscale='Blues',
        colorbar_title="Sales ($)",
        text=[f"{d['Country']}<br>Sales: ${d['Sales']:,.0f}<br>Profit: ${d['Total Profit/Loss']:,.0f}<br>Margin: {d['Profit Margin']:.1f}%" 
              for d in geo_data],
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title='Sales by Country',
        height=500,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    with st.expander("📋 View Geographic Data Table"):
        import pandas as pd
        df_geo = pd.DataFrame(geo_data)
        st.dataframe(
            df_geo.style.format({
                'Sales': '${:,.0f}',
                'Total Profit/Loss': '${:,.0f}',
                'Profit Margin': '{:.2f}%'
            }),
            use_container_width=True
        )
```

## Deployment Configuration

### Streamlit Configuration (`.streamlit/config.toml`)

toml

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

### Requirements File (`requirements.txt`)

```
streamlit==1.29.0
pandas==2.1.4
numpy==1.26.3
plotly==5.18.0
scikit-learn==1.4.0
openpyxl==3.1.2
```

## Performance Optimization

### Caching Strategy

1.  **Data Loading**: Cache entire dataset load with `@st.cache_data`
2.  **Filtered Data**: Cache filtered results based on filter parameters
3.  **Analytics**: Cache KPI calculations and aggregations
4.  **Forecasting**: Cache forecast results with 1-hour TTL

### Data Size Considerations

-   Expected dataset size: < 50MB (manageable in-memory)
-   If dataset exceeds 100MB: Consider data sampling or aggregation
-   Streamlit Community Cloud: 1GB memory limit (sufficient for this use case)

## Error Handling

python

```python
# Example error handling pattern
try:
    kpis = calculate_kpis(filtered_df)
    render_kpis(kpis)
except ValueError as e:
    st.error(f"Data processing error: {str(e)}")
except Exception as e:
    st.error("An unexpected error occurred. Please refresh the page.")
    st.exception(e)  # Only in development
```

## Testing Strategy

### Local Testing

bash

```bash
# Run streamlit locally
streamlit run src/app.py

# Test with different date ranges and filters
# Verify all visualizations render correctly
# Check forecast accuracy with known data
```

### Unit Tests (pytest)

python

```python
# tests/test_analytics.py
def test_calculate_kpis():
    # Test KPI calculations with sample data
    pass

def test_time_series_aggregation():
    # Test time series grouping
    pass
```

## Deployment Steps

### 1. Prepare Repository

bash

```bash
# Ensure clean structure
git add .
git commit -m "Portfolio dashboard ready for deployment"
git push origin main
```

### 2. Streamlit Community Cloud Setup

1.  Go to share.streamlit.io
2.  Connect GitHub repository
3.  Select `src/app.py` as main file
4.  Deploy

### 3. Post-Deployment

-   Test all features on deployed URL
-   Add deployment URL to README
-   Include in portfolio

## Post-MVP Enhancements (V2+)

### Advanced ML (scikit-learn only)

-   Polynomial regression for non-linear trends
-   Random Forest for multi-variate forecasting
-   K-means clustering for customer segmentation
-   Isolation Forest for anomaly detection

### Additional Features

-   PDF report generation (reportlab)
-   CSV export of filtered data
-   Seasonal decomposition analysis
-   Customer cohort analysis