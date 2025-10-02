# Performance Optimization

### Caching Strategy

1.  **Data Loading**: Cache entire dataset load with `@st.cache_data`
2.  **Filtered Data**: Cache filtered results based on filter parameters
3.  **Analytics**: Cache KPI calculations and aggregations
4.  **Forecasting**: Cache forecast results with 1-hour TTL

### Data Size Considerations

-   Expected dataset size: < 50MB (manageable in-memory)
-   If dataset exceeds 100MB: Consider data sampling or aggregation
-   Streamlit Community Cloud: 1GB memory limit (sufficient for this use case)
