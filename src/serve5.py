import pandas as pd
from pathlib import Path

# ==============================
# Paths
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

APPS_CSV = PROCESSED_DIR / "apps_catalog_5.csv"
REVIEWS_CSV = PROCESSED_DIR / "apps_reviews_5.csv"

# ==============================
# Load processed data
# ==============================
apps_df = pd.read_csv(APPS_CSV)
reviews_df = pd.read_csv(REVIEWS_CSV)

# Ensure 'at' is datetime for date operations
reviews_df['at'] = pd.to_datetime(reviews_df['at'])

# ==============================
# 1. Generate app_kpis_5.csv (Enhanced with sentiment)
# ==============================
# Basic review stats per app
review_stats = reviews_df.groupby('app_id').agg(
    num_reviews=('score', 'count'),
    avg_rating=('score', 'mean'),
    pct_low_rating=('score', lambda x: (x <= 2).mean() * 100),
    avg_sentiment_score=('text_sentiment_score', 'mean'),
    pct_positive_sentiment=('text_sentiment_label', lambda x: (x == 'positive').mean() * 100),
    pct_negative_sentiment=('text_sentiment_label', lambda x: (x == 'negative').mean() * 100),
    total_contradictions=('is_contradiction', 'sum'),
    contradiction_rate=('is_contradiction', lambda x: x.mean() * 100),
    avg_sentiment_gap=('sentiment_rating_gap', 'mean'),
    total_positive_words=('positive_word_count', 'sum'),
    total_negative_words=('negative_word_count', 'sum')
).reset_index()

# Get first and latest review dates
date_range = reviews_df.groupby('app_id')['at'].agg(
    first_review_date=('min'),
    latest_review_date=('max')
).reset_index()

# Contradiction type breakdown
contradiction_types = reviews_df[reviews_df['is_contradiction'] == True].groupby(['app_id', 'contradiction_type']).size().unstack(fill_value=0)
contradiction_types.columns = [f"contradiction_{col}" for col in contradiction_types.columns]

# Merge all stats
app_kpis = review_stats.merge(date_range, on='app_id')
if not contradiction_types.empty:
    app_kpis = app_kpis.merge(contradiction_types, left_on='app_id', right_index=True, how='left')

# Add app title from apps_df
app_kpis = app_kpis.merge(apps_df[['appId', 'title']], left_on='app_id', right_on='appId', how='left')

# Select and reorder columns
base_columns = ['appId', 'title', 'num_reviews', 'avg_rating', 'pct_low_rating', 
                'avg_sentiment_score', 'pct_positive_sentiment', 'pct_negative_sentiment',
                'total_contradictions', 'contradiction_rate', 'avg_sentiment_gap',
                'total_positive_words', 'total_negative_words', 'first_review_date', 
                'latest_review_date']

# Add contradiction type columns if they exist
contradiction_columns = [col for col in app_kpis.columns if col.startswith('contradiction_')]
final_columns = base_columns + contradiction_columns

app_kpis = app_kpis[[col for col in final_columns if col in app_kpis.columns]]

# Round numeric columns for readability
numeric_cols = ['avg_rating', 'pct_low_rating', 'avg_sentiment_score', 
                'pct_positive_sentiment', 'pct_negative_sentiment', 'contradiction_rate', 
                'avg_sentiment_gap']
for col in numeric_cols:
    if col in app_kpis.columns:
        app_kpis[col] = app_kpis[col].round(3)

# Save
app_kpis.to_csv(PROCESSED_DIR / "app_kpis_5.csv", index=False)

# ================================
# 2. Generate daily_metrics_5.csv (Enhanced with sentiment)
# ================================
# Extract date part only
reviews_df['date'] = reviews_df['at'].dt.date

# Group by date
daily_metrics = reviews_df.groupby('date').agg(
    daily_num_reviews=('score', 'count'),
    daily_avg_rating=('score', 'mean'),
    daily_avg_sentiment=('text_sentiment_score', 'mean'),
    daily_contradictions=('is_contradiction', 'sum'),
    daily_contradiction_rate=('is_contradiction', lambda x: x.mean() * 100),
    daily_positive_pct=('text_sentiment_label', lambda x: (x == 'positive').mean() * 100),
    daily_negative_pct=('text_sentiment_label', lambda x: (x == 'negative').mean() * 100),
    daily_sentiment_gap=('sentiment_rating_gap', 'mean')
).reset_index()

# Sort by date
daily_metrics = daily_metrics.sort_values('date').reset_index(drop=True)

# Round numeric columns
round_cols = ['daily_avg_rating', 'daily_avg_sentiment', 'daily_contradiction_rate', 
              'daily_positive_pct', 'daily_negative_pct', 'daily_sentiment_gap']
for col in round_cols:
    if col in daily_metrics.columns:
        daily_metrics[col] = daily_metrics[col].round(3)

# Save
daily_metrics.to_csv(PROCESSED_DIR / "daily_metrics_5.csv", index=False)

# ================================
# 3. Generate sentiment_contradictions_5.csv (Detailed analysis)
# ================================
# Create detailed contradiction dataset
contradictions_df = reviews_df[reviews_df['is_contradiction'] == True].copy()

# Add additional analysis columns
contradictions_df['rating_category'] = pd.cut(
    contradictions_df['score'], 
    bins=[0, 2, 3, 5], 
    labels=['Low', 'Medium', 'High'],
    include_lowest=True
)

contradictions_df['sentiment_strength'] = pd.cut(
    contradictions_df['text_sentiment_score'],
    bins=[-1, -0.3, 0.3, 1],
    labels=['Negative', 'Neutral', 'Positive'],
    include_lowest=True
)

# Select relevant columns for contradiction analysis
contradiction_columns = [
    'app_id', 'app_name', 'reviewId', 'userName', 'score', 'rating_category',
    'content', 'text_sentiment_score', 'text_sentiment_label', 'sentiment_strength',
    'sentiment_rating_gap', 'contradiction_type', 'normalized_numeric_score',
    'positive_word_count', 'negative_word_count', 'at'
]

contradictions_df = contradictions_df[[col for col in contradiction_columns if col in contradictions_df.columns]]

# Save detailed contradictions
contradictions_df.to_csv(PROCESSED_DIR / "sentiment_contradictions_5.csv", index=False)

# ================================
# 4. Generate sentiment_summary_5.csv (High-level overview)
# ==============================
# Create summary statistics
summary_stats = {
    'total_reviews': [len(reviews_df)],
    'total_contradictions': [reviews_df['is_contradiction'].sum()],
    'contradiction_rate_pct': [(reviews_df['is_contradiction'].sum() / len(reviews_df)) * 100],
    'avg_sentiment_score': [reviews_df['text_sentiment_score'].mean()],
    'avg_rating': [reviews_df['score'].mean()],
    'avg_sentiment_gap': [reviews_df['sentiment_rating_gap'].mean()],
    'positive_reviews_pct': [(reviews_df['text_sentiment_label'] == 'positive').mean() * 100],
    'negative_reviews_pct': [(reviews_df['text_sentiment_label'] == 'negative').mean() * 100],
    'neutral_reviews_pct': [(reviews_df['text_sentiment_label'] == 'neutral').mean() * 100],
    'apps_with_contradictions': [reviews_df[reviews_df['is_contradiction'] == True]['app_id'].nunique()],
    'total_apps': [reviews_df['app_id'].nunique()]
}

summary_df = pd.DataFrame(summary_stats)

# Round numeric columns
for col in summary_df.columns:
    if summary_df[col].dtype in ['float64', 'int64']:
        summary_df[col] = summary_df[col].round(2)

summary_df.to_csv(PROCESSED_DIR / "sentiment_summary_5.csv", index=False)

print("✅ Generated enhanced C5 datasets:")
print(f"   - app_kpis_5.csv ({len(app_kpis)} apps with sentiment metrics)")
print(f"   - daily_metrics_5.csv ({len(daily_metrics)} days with sentiment trends)")
print(f"   - sentiment_contradictions_5.csv ({len(contradictions_df)} detailed contradictions)")
print(f"   - sentiment_summary_5.csv (overall sentiment statistics)")

# Print key insights
print(f"\n📊 Key Sentiment Insights:")
print(f"   - Overall contradiction rate: {summary_df['contradiction_rate_pct'].iloc[0]:.1f}%")
print(f"   - Average sentiment score: {summary_df['avg_sentiment_score'].iloc[0]:.2f}")
print(f"   - Average rating: {summary_df['avg_rating'].iloc[0]:.2f}")
print(f"   - Sentiment-rating gap: {summary_df['avg_sentiment_gap'].iloc[0]:.2f}")
print(f"   - Apps with contradictions: {summary_df['apps_with_contradictions'].iloc[0]}/{summary_df['total_apps'].iloc[0]}")
