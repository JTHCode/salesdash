# High-Level Architecture

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
