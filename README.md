# SDG 7 Dashboard — Affordable and Clean Energy ⚡

An interactive Streamlit dashboard exploring global electricity access, renewable energy share, and CO₂ emissions (2000–2020), built for the ITS68404 Data Visualisation assignment.

## Installation

```bash
pip install streamlit pandas plotly scikit-learn scipy
```

## Setup

Place `global_energy_data.csv` in the same folder as `app.py`.

## Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Dashboard sections

| Section | Description |
|---|---|
| Global Overview | KPIs, dual-axis trend, pivot heatmap |
| Interactive Analytics | 6-chart grid with live filters |
| Ethical Bias | Standalone GDP vs CO₂ scatter |
| World Map | Animated choropleth with Play button |
| AI Predictions | RandomForest CO₂ estimator with R² and MAE |

## Tech stack

Python · Streamlit · Plotly · pandas · scikit-learn · scipy
