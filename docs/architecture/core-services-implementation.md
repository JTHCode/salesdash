# Core Services Implementation

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
