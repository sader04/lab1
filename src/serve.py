import os
import pandas as pd

#Define paths
processed_dir = os.path.join("LAB1", "data", "processed")
apps_csv = os.path.join(processed_dir, "apps_catalog.csv")
reviews_csv = os.path.join(processed_dir, "apps_reviews.csv")

#load processed data
apps_df = pd.read_csv(apps_csv)
reviews_df = pd.read_csv(reviews_csv)

# Ensure 'at' is datetime for date operations
reviews_df['at'] = pd.to_datetime(reviews_df['at'])

# ----------------------------
# 1. Generate app_kpis.csv
# ----------------------------
# Calculate review counts and stats per app
review_stats = reviews_df.groupby('app_id').agg(
    num_reviews=('score', 'count'),
    avg_rating=('score', 'mean'),
    pct_low_rating=('score', lambda x: (x <= 2).mean() * 100)  # percentage
).reset_index()

# Get first and latest review dates
date_range = reviews_df.groupby('app_id')['at'].agg(
    first_review_date=('min'),
    latest_review_date=('max')
).reset_index()

# Merge stats
app_kpis = review_stats.merge(date_range, on='app_id')

# Add app title from apps_df
app_kpis = app_kpis.merge(apps_df[['appId', 'title']], left_on='app_id', right_on='appId', how='left')
app_kpis = app_kpis[['appId', 'title', 'num_reviews', 'avg_rating', 'pct_low_rating', 'first_review_date', 'latest_review_date']]

# Round numeric columns for readability
app_kpis['avg_rating'] = app_kpis['avg_rating'].round(3)
app_kpis['pct_low_rating'] = app_kpis['pct_low_rating'].round(2)

# Save
app_kpis.to_csv(os.path.join(processed_dir, "app_kpis.csv"), index=False)

# -------------------------------
# 2. Generate daily_metrics.csv
# -------------------------------
# Extract date part only
reviews_df['date'] = reviews_df['at'].dt.date

# Group by date
daily_metrics = reviews_df.groupby('date').agg(
    daily_num_reviews=('score', 'count'),
    daily_avg_rating=('score', 'mean')
).reset_index()

# Sort by date
daily_metrics = daily_metrics.sort_values('date').reset_index(drop=True)

# Round average rating
daily_metrics['daily_avg_rating'] = daily_metrics['daily_avg_rating'].round(3)

# Save
daily_metrics.to_csv(os.path.join(processed_dir, "daily_metrics.csv"), index=False)

print("✅ Generated app_kpis.csv and daily_metrics.csv")