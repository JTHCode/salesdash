# Testing Strategy

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
