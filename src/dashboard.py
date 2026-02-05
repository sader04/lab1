import pandas as pd
import plotly.express as px
from pathlib import Path

# ==============================
# Paths
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

APP_KPIS_CSV = PROCESSED_DIR / "app_kpis.csv"
DAILY_METRICS_CSV = PROCESSED_DIR / "daily_metrics.csv"

# ==============================
# Load data
# ==============================
app_kpis = pd.read_csv(APP_KPIS_CSV)
daily_metrics = pd.read_csv(DAILY_METRICS_CSV)

# Ensure correct types
daily_metrics["date"] = pd.to_datetime(daily_metrics["date"])

# ==============================
# Plot 1 — App-level KPIs
# ==============================
fig1 = px.bar(
    app_kpis,
    x="title",
    y="avg_rating",
    color="pct_low_rating",
    title="Average Rating per App and Percentage of Low Ratings",
    labels={
        "title": "Application",
        "avg_rating": "Average Rating",
        "pct_low_rating": "% Low Ratings (≤ 2)"
    },
    color_continuous_scale="viridis"
)

fig1.update_layout(xaxis_tickangle=-45)
fig1.show()

# ==============================
# Plot 2 — Rating trend over time
# ==============================
fig2 = px.line(
    daily_metrics,
    x="date",
    y="daily_avg_rating",
    title="Daily Average Rating Over Time",
    labels={
        "date": "Date",
        "daily_avg_rating": "Average Rating"
    }
)

fig2.show()

# ==============================
# Plot 3 — Review volume over time
# ==============================
fig3 = px.bar(
    daily_metrics,
    x="date",
    y="daily_num_reviews",
    title="Daily Number of Reviews",
    labels={
        "date": "Date",
        "daily_num_reviews": "Number of Reviews"
    }
)

fig3.show()
