# Visualization Components

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
