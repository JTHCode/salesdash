# Deployment Configuration

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
