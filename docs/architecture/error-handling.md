# Error Handling

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
