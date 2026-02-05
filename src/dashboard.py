import pandas as pd
import plotly.express as px
import os

# Load processed data
app_kpis = pd.read_csv(os.path.join("..", "data", "processed", "app_kpis.csv"))
daily_metrics = pd.read_csv(os.path.join("..", "data", "processed", "daily_metrics.csv"))

# Ensure 'date' is datetime
daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])

# Plot 1: App ratings vs low-rating %
fig1 = px.bar(
    app_kpis,
    x='title',
    y='avg_rating',
    color='pct_low_rating',
    title="App Average Rating vs % Low Ratings",
    labels={'title': 'App', 'avg_rating': 'Avg Rating', 'pct_low_rating': '% Low Ratings (≤2)'},
    color_continuous_scale='viridis'
)
fig1.update_layout(xaxis_tickangle=-45)
fig1.show()

# Plot 2: Daily average rating over time
fig2 = px.line(
    daily_metrics,
    x='date',
    y='daily_avg_rating',
    title="Daily Average Rating Over Time"
)
fig2.update_layout(xaxis_title="Date", yaxis_title="Avg Rating")
fig2.show()
# Plot 3: Daily number of reviews over time
fig3 = px.bar(
    daily_metrics,
    x='date',
    y='daily_num_reviews',
    title="Daily Number of Reviews Over Time"
)
fig3.update_layout(xaxis_title="Date", yaxis_title="Number of Reviews")
fig3.show()
input("Press Enter to close...")