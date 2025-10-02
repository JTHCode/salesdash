# Data Architecture

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
