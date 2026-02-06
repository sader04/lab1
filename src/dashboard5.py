import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# ==============================
# Paths
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

APP_KPIS_CSV = PROCESSED_DIR / "app_kpis_5.csv"
DAILY_METRICS_CSV = PROCESSED_DIR / "daily_metrics_5.csv"
CONTRADICTIONS_CSV = PROCESSED_DIR / "sentiment_contradictions_5.csv"
SUMMARY_CSV = PROCESSED_DIR / "sentiment_summary_5.csv"

# ==============================
# Load data
# ==============================
app_kpis = pd.read_csv(APP_KPIS_CSV)
daily_metrics = pd.read_csv(DAILY_METRICS_CSV)
contradictions = pd.read_csv(CONTRADICTIONS_CSV)
summary = pd.read_csv(SUMMARY_CSV)

# Ensure correct types
daily_metrics["date"] = pd.to_datetime(daily_metrics["date"])
contradictions["at"] = pd.to_datetime(contradictions["at"])

# ==============================
# Plot 1 — App Sentiment vs Rating Analysis
# ==============================
fig1 = px.scatter(
    app_kpis,
    x="avg_rating",
    y="avg_sentiment_score",
    size="contradiction_rate",
    color="title",
    title="App Rating vs Sentiment Score (Bubble Size = Contradiction Rate)",
    labels={
        "avg_rating": "Average Rating (1-5)",
        "avg_sentiment_score": "Average Sentiment Score (-1 to 1)",
        "title": "Application",
        "contradiction_rate": "Contradiction Rate (%)"
    },
    hover_name="title",
    hover_data=["num_reviews", "total_contradictions", "contradiction_rate"]
)
fig1.update_layout(xaxis_title="Average Rating", yaxis_title="Average Sentiment Score")
fig1.show()

# ==============================
# Plot 2 — Contradiction Rate by App
# ==============================
fig2 = px.bar(
    app_kpis.sort_values("contradiction_rate", ascending=False),
    x="title",
    y="contradiction_rate",
    title="Sentiment-Rating Contradiction Rate by App",
    labels={
        "title": "Application",
        "contradiction_rate": "Contradiction Rate (%)"
    },
    color="contradiction_rate",
    color_continuous_scale="reds"
)
fig2.update_layout(xaxis_tickangle=-45, xaxis_title="Application", yaxis_title="Contradiction Rate (%)")
fig2.show()

# ==============================
# Plot 3 — Daily Sentiment Trends
# ==============================
fig3 = make_subplots(
    rows=2, cols=1,
    subplot_titles=("Daily Average Rating vs Sentiment", "Daily Contradiction Rate"),
    vertical_spacing=0.15
)

# Rating vs Sentiment over time
fig3.add_trace(
    go.Scatter(
        x=daily_metrics["date"],
        y=daily_metrics["daily_avg_rating"],
        name="Avg Rating",
        line=dict(color="blue"),
        yaxis="y1"
    ),
    row=1, col=1
)

fig3.add_trace(
    go.Scatter(
        x=daily_metrics["date"],
        y=daily_metrics["daily_avg_sentiment"],
        name="Avg Sentiment",
        line=dict(color="green"),
        yaxis="y1"
    ),
    row=1, col=1
)

# Contradiction rate over time
fig3.add_trace(
    go.Bar(
        x=daily_metrics["date"],
        y=daily_metrics["daily_contradiction_rate"],
        name="Contradiction Rate",
        marker_color="red",
        yaxis="y2"
    ),
    row=2, col=1
)

fig3.update_layout(
    title="Daily Sentiment and Contradiction Trends",
    height=600,
    showlegend=True
)
fig3.update_xaxes(title_text="Date", row=2, col=1)
fig3.update_yaxes(title_text="Score", row=1, col=1)
fig3.update_yaxes(title_text="Contradiction Rate (%)", row=2, col=1)

fig3.show()

# ==============================
# Plot 4 — Contradiction Type Distribution
# ==============================
if 'contradiction_type' in contradictions.columns:
    contradiction_types = contradictions['contradiction_type'].value_counts()
    
    fig4 = px.pie(
        values=contradiction_types.values,
        names=contradiction_types.index,
        title="Types of Sentiment-Rating Contradictions",
        color_discrete_map={
            'positive_text_low_score': 'lightcoral',
            'negative_text_high_score': 'lightblue',
            'moderate_contradiction': 'lightgray'
        }
    )
    fig4.show()

# ==============================
# Plot 5 — Sentiment Distribution by Rating Category
# ==============================
if 'rating_category' in contradictions.columns and 'sentiment_strength' in contradictions.columns:
    sentiment_by_rating = contradictions.groupby(['rating_category', 'sentiment_strength']).size().unstack(fill_value=0)
    
    fig5 = px.bar(
        sentiment_by_rating.reset_index().melt(id_vars=['rating_category'], var_name='sentiment', value_name='count'),
        x="rating_category",
        y="count",
        color="sentiment",
        title="Sentiment Distribution Within Rating Categories (Contradictions Only)",
        labels={
            "rating_category": "Rating Category",
            "count": "Number of Contradictions",
            "sentiment": "Sentiment Strength"
        },
        barmode="group"
    )
    fig5.update_layout(xaxis_title="Rating Category", yaxis_title="Number of Contradictions")
    fig5.show()

# ==============================
# Plot 6 — Key Metrics Summary
# ==============================
fig6 = go.Figure()

# Create summary metrics display
metrics_data = [
    f"Total Reviews: {summary['total_reviews'].iloc[0]:,}",
    f"Contradiction Rate: {summary['contradiction_rate_pct'].iloc[0]:.1f}%",
    f"Avg Sentiment: {summary['avg_sentiment_score'].iloc[0]:.2f}",
    f"Avg Rating: {summary['avg_rating'].iloc[0]:.2f}",
    f"Sentiment Gap: {summary['avg_sentiment_gap'].iloc[0]:.2f}",
    f"Positive Reviews: {summary['positive_reviews_pct'].iloc[0]:.1f}%",
    f"Negative Reviews: {summary['negative_reviews_pct'].iloc[0]:.1f}%",
    f"Apps w/ Contradictions: {summary['apps_with_contradictions'].iloc[0]}/{summary['total_apps'].iloc[0]}"
]

fig6.add_trace(
    go.Table(
        header=dict(values=["Key Metrics"], fill_color="lightblue"),
        cells=dict(values=[metrics_data], fill_color="lightgray")
    )
)

fig6.update_layout(
    title="Sentiment Analysis Summary Metrics",
    height=400
)

fig6.show()

# ==============================
# Print Summary Statistics
# ==============================
print("✅ C5 Sentiment Dashboard completed - showing 6 visualizations")
print(f"\n📊 Sentiment Analysis Summary:")
print(f"   - Total Reviews Analyzed: {summary['total_reviews'].iloc[0]:,}")
print(f"   - Contradictions Found: {summary['total_contradictions'].iloc[0]:,} ({summary['contradiction_rate_pct'].iloc[0]:.1f}%)")
print(f"   - Average Sentiment Score: {summary['avg_sentiment_score'].iloc[0]:.2f} (-1 to 1)")
print(f"   - Average Rating: {summary['avg_rating'].iloc[0]:.2f} (1 to 5)")
print(f"   - Sentiment-Rating Gap: {summary['avg_sentiment_gap'].iloc[0]:.2f}")
print(f"   - Apps with Contradictions: {summary['apps_with_contradictions'].iloc[0]} out of {summary['total_apps'].iloc[0]}")

if len(contradictions) > 0:
    print(f"\n🔍 Top Contradiction Examples:")
    sample_contradictions = contradictions.nlargest(3, 'sentiment_rating_gap')[['app_name', 'content', 'score', 'text_sentiment_label', 'contradiction_type']]
    for _, row in sample_contradictions.iterrows():
        print(f"   - {row['app_name']}: \"{row['content'][:50]}...\" (Rating: {row['score']}, Sentiment: {row['text_sentiment_label']}, Type: {row['contradiction_type']})")

input("\nPress Enter to close...")
