import pandas as pd
from pathlib import Path

# ==============================
# Paths
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

APPS_CSV = PROCESSED_DIR / "apps_catalog.csv"
REVIEWS_CSV = PROCESSED_DIR / "apps_reviews.csv"

# ==============================
# Load processed data
# ==============================
apps_df = pd.read_csv(APPS_CSV)
reviews_df = pd.read_csv(REVIEWS_CSV)

# Ensure correct types
reviews_df["score"] = pd.to_numeric(reviews_df["score"], errors="coerce")
reviews_df["at"] = pd.to_datetime(reviews_df["at"], errors="coerce")

# ==============================
# 1. App-level KPIs
# ==============================
review_stats = reviews_df.groupby("app_id").agg(
    num_reviews=("score", "count"),
    avg_rating=("score", "mean"),
    pct_low_rating=("score", lambda s: (s <= 2).mean() * 100),
).reset_index()

date_range = reviews_df.groupby("app_id")["at"].agg(
    first_review_date="min",
    latest_review_date="max",
).reset_index()

app_kpis = review_stats.merge(date_range, on="app_id", how="left")

# Join app title
app_kpis = app_kpis.merge(
    apps_df[["appId", "title"]],
    left_on="app_id",
    right_on="appId",
    how="left"
)

app_kpis = app_kpis[[
    "appId",
    "title",
    "num_reviews",
    "avg_rating",
    "pct_low_rating",
    "first_review_date",
    "latest_review_date"
]]

# Formatting
app_kpis["avg_rating"] = app_kpis["avg_rating"].round(3)
app_kpis["pct_low_rating"] = app_kpis["pct_low_rating"].round(2)

# Save
app_kpis.to_csv(PROCESSED_DIR / "app_kpis.csv", index=False)

# ==============================
# 2. Daily metrics
# ==============================
reviews_df["date"] = reviews_df["at"].dt.date

daily_metrics = reviews_df.groupby("date").agg(
    daily_num_reviews=("score", "count"),
    daily_avg_rating=("score", "mean"),
).reset_index()

daily_metrics = daily_metrics.sort_values("date")
daily_metrics["daily_avg_rating"] = daily_metrics["daily_avg_rating"].round(3)

# Save
daily_metrics.to_csv(PROCESSED_DIR / "daily_metrics.csv", index=False)

print("✅ Generated app_kpis.csv and daily_metrics.csv")
