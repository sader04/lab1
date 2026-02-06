import json
import pandas as pd
from pathlib import Path

# ==============================
# Paths
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ==============================
# Configuration for C5
# ==============================
USE_CSV_APPS = True  # Use updated apps CSV
USE_CSV_REVIEWS = True  # Use dirty reviews CSV

APPS_CSV = RAW_DIR / "note_taking_ai_apps_updated.csv"
REVIEWS_CSV = RAW_DIR / "note_taking_ai_reviews_dirty.csv"

# ==============================
# Sentiment Analysis Module
# ==============================
class SentimentAnalyzer:
    def __init__(self, method='keyword'):
        self.method = method
        # Simple keyword-based sentiment dictionaries
        self.positive_words = [
            'love', 'excellent', 'amazing', 'great', 'perfect', 'awesome', 
            'fantastic', 'wonderful', 'brilliant', 'outstanding', 'superb',
            'good', 'nice', 'happy', 'pleased', 'satisfied', 'best', 'incredible'
        ]
        self.negative_words = [
            'terrible', 'worst', 'awful', 'hate', 'horrible', 'crap', 'bad',
            'disgusting', 'disappointing', 'useless', 'broken', 'crap', 'junk',
            'poor', 'sad', 'angry', 'frustrated', 'annoying', 'waste', 'sucks'
        ]
    
    def analyze_text(self, text):
        """Analyze sentiment of review text"""
        if pd.isna(text) or not isinstance(text, str):
            return {
                'score': 0, 
                'label': 'neutral',
                'positive_count': 0,
                'negative_count': 0,
                'total_sentiment_words': 0
            }
        
        text_lower = text.lower()
        pos_count = sum(1 for word in self.positive_words if word in text_lower)
        neg_count = sum(1 for word in self.negative_words if word in text_lower)
        
        # Simple sentiment scoring
        total_words = pos_count + neg_count
        if total_words == 0:
            sentiment_score = 0
            sentiment_label = 'neutral'
        elif pos_count > neg_count:
            # Stronger positive sentiment based on ratio
            sentiment_score = min(0.5 + (pos_count / total_words) * 0.5, 1.0)
            sentiment_label = 'positive'
        elif neg_count > pos_count:
            # Stronger negative sentiment based on ratio
            sentiment_score = max(-0.5 - (neg_count / total_words) * 0.5, -1.0)
            sentiment_label = 'negative'
        else:
            sentiment_score = 0
            sentiment_label = 'neutral'
        
        return {
            'score': sentiment_score,
            'label': sentiment_label,
            'positive_count': pos_count,
            'negative_count': neg_count,
            'total_sentiment_words': total_words
        }
    
    def detect_contradiction(self, text_sentiment, numeric_score):
        """Detect contradiction between text sentiment and numeric rating"""
        # Normalize numeric score to -1 to 1 scale (assuming 1-5 rating)
        if pd.isna(numeric_score):
            normalized_score = 0
        else:
            normalized_score = (numeric_score - 3) / 2  # 1->-1, 3->0, 5->1
        
        # Calculate sentiment gap
        sentiment_gap = abs(text_sentiment - normalized_score)
        
        # Contradiction detection with threshold
        is_contradiction = sentiment_gap > 0.7
        
        # Classify contradiction type
        contradiction_type = None
        if is_contradiction:
            if text_sentiment > 0.3 and normalized_score < -0.3:
                contradiction_type = 'positive_text_low_score'
            elif text_sentiment < -0.3 and normalized_score > 0.3:
                contradiction_type = 'negative_text_high_score'
            else:
                contradiction_type = 'moderate_contradiction'
        
        return {
            'sentiment_gap': sentiment_gap,
            'is_contradiction': is_contradiction,
            'contradiction_type': contradiction_type,
            'normalized_numeric_score': normalized_score
        }

# ==============================
# Load apps metadata (CSV for C5)
# ==============================
if USE_CSV_APPS:
    print("🔄 Using updated apps CSV (C5)")
    apps_df = pd.read_csv(APPS_CSV, quotechar='"', escapechar='\\', on_bad_lines='skip')
else:
    # fallback to JSON
    APPS_RAW = RAW_DIR / "apps_raw.json"
    with APPS_RAW.open("r", encoding="utf-8") as f:
        apps_data = json.load(f)
    apps_df = pd.DataFrame(apps_data)

# Normalize app columns (match expected names)
apps_df = apps_df.rename(columns={
    # The CSV already has the correct column names: appId, title, developer, score, ratings, installs, genre, price
    # No renaming needed, but keeping this for safety if column names change
})

# Keep only required columns (they're already in the right format)
required_app_cols = ["appId", "title", "developer", "score", "ratings", "installs", "genre", "price"]
apps_df = apps_df[[c for c in required_app_cols if c in apps_df.columns]]

# Handle missing titles
apps_df["title"] = apps_df["title"].fillna("UNKNOWN_APP")

# Clean installs - handle formats like "1,000,000+", "50,000+", "", etc.
def clean_installs(s):
    if pd.isna(s) or not isinstance(s, str) or s.strip() == "":
        return 0
    cleaned = s.replace(",", "").replace("+", "").strip()
    return int(cleaned) if cleaned.isdigit() else 0

apps_df["installs"] = apps_df["installs"].apply(clean_installs)

# Numeric conversion
apps_df["score"] = pd.to_numeric(apps_df["score"], errors="coerce")
apps_df["ratings"] = pd.to_numeric(apps_df["ratings"], errors="coerce")
apps_df["price"] = pd.to_numeric(apps_df["price"], errors="coerce").fillna(0)

# Deduplicate
apps_df = apps_df.drop_duplicates(subset=["appId"], keep="last")

# ==============================
# Load reviews (use dirty CSV)
# ==============================
if USE_CSV_REVIEWS:
    print("🔄 Using dirty reviews CSV (C5)")
    reviews_df = pd.read_csv(REVIEWS_CSV, quotechar='"', escapechar='\\', on_bad_lines='skip')
else:
    print("🔄 Using JSONL reviews (C5)")
    reviews_df = pd.read_json(REVIEWS_JSONL, lines=True, encoding="utf-8")

# ==============================
# Normalize reviews schema
# ==============================
# Rename if needed (schema drift protection)
reviews_df = reviews_df.rename(columns={
    "appId": "app_id",
    "review_id": "reviewId",
    "user_name": "userName",
    "rating": "score",
    "text": "content",
    "thumbs_up": "thumbsUpCount",
    "created_at": "at"
})

required_columns = [
    "app_id", "reviewId", "userName",
    "score", "content", "thumbsUpCount", "at"
]

reviews_df = reviews_df[[c for c in required_columns if c in reviews_df.columns]]

# Type cleaning
reviews_df["score"] = pd.to_numeric(reviews_df["score"], errors="coerce")
reviews_df["thumbsUpCount"] = pd.to_numeric(
    reviews_df.get("thumbsUpCount", 0),
    errors="coerce"
).fillna(0)
reviews_df["at"] = pd.to_datetime(reviews_df["at"], errors="coerce")

# ==============================
# Deduplication
# ==============================
if "reviewId" in reviews_df.columns:
    reviews_df = reviews_df.drop_duplicates(subset=["reviewId"], keep="last")

# ==============================
# Enrich with app_name
# ==============================
app_lookup = apps_df.set_index("appId")["title"].to_dict()

# Automatic app ID matching function
def find_app_name(app_id):
    # First try exact match
    if app_id in app_lookup:
        return app_lookup[app_id]
    
    # Extract key parts of app ID for matching
    app_parts = app_id.lower().replace('.ai', '').replace('.com', '').split('.')
    app_keywords = [part for part in app_parts if len(part) > 2]
    
    # Try to find best match among known apps
    best_match = None
    best_score = 0
    
    for known_id, title in app_lookup.items():
        known_parts = known_id.lower().replace('.ai', '').replace('.com', '').split('.')
        known_keywords = [part for part in known_parts if len(part) > 2]
        
        # Calculate similarity score
        score = 0
        for app_kw in app_keywords:
            for known_kw in known_keywords:
                if app_kw == known_kw:
                    score += 3  # Exact keyword match
                elif app_kw in known_kw or known_kw in app_kw:
                    score += 1  # Partial match
        
        # Bonus for domain similarity
        if any(part in known_id.lower() for part in app_parts):
            score += 2
            
        if score > best_score and score >= 3:  # Minimum threshold
            best_score = score
            best_match = title
    
    return best_match if best_match else "UNKNOWN_APP"

reviews_df["app_name"] = reviews_df["app_id"].apply(find_app_name)

# ==============================
# NEW: Sentiment Analysis & Contradiction Detection
# ==============================
print("🔄 Adding sentiment analysis (C5)")

# Initialize sentiment analyzer
sentiment_analyzer = SentimentAnalyzer(method='keyword')

# Apply sentiment analysis to each review
sentiment_results = reviews_df['content'].apply(sentiment_analyzer.analyze_text)

# Extract sentiment metrics into separate columns
reviews_df['text_sentiment_score'] = sentiment_results.apply(lambda x: x['score'])
reviews_df['text_sentiment_label'] = sentiment_results.apply(lambda x: x['label'])
reviews_df['positive_word_count'] = sentiment_results.apply(lambda x: x['positive_count'])
reviews_df['negative_word_count'] = sentiment_results.apply(lambda x: x['negative_count'])
reviews_df['total_sentiment_words'] = sentiment_results.apply(lambda x: x['total_sentiment_words'])

# Apply contradiction detection
contradiction_results = reviews_df.apply(
    lambda row: sentiment_analyzer.detect_contradiction(row['text_sentiment_score'], row['score']),
    axis=1
)

# Extract contradiction metrics
reviews_df['sentiment_rating_gap'] = contradiction_results.apply(lambda x: x['sentiment_gap'])
reviews_df['is_contradiction'] = contradiction_results.apply(lambda x: x['is_contradiction'])
reviews_df['contradiction_type'] = contradiction_results.apply(lambda x: x['contradiction_type'])
reviews_df['normalized_numeric_score'] = contradiction_results.apply(lambda x: x['normalized_numeric_score'])

# Final column selection
reviews_df = reviews_df[[
    "app_id", "app_name", "reviewId", "userName", "score", "content",
    "thumbsUpCount", "at", "text_sentiment_score", "text_sentiment_label",
    "positive_word_count", "negative_word_count", "total_sentiment_words",
    "sentiment_rating_gap", "is_contradiction", "contradiction_type",
    "normalized_numeric_score"
]]

# ==============================
# Save processed datasets
# ==============================
apps_df.to_csv(PROCESSED_DIR / "apps_catalog_5.csv", index=False)
reviews_df.to_csv(PROCESSED_DIR / "apps_reviews_5.csv", index=False)

# Print summary statistics
total_reviews = len(reviews_df)
contradictions = reviews_df['is_contradiction'].sum()
contradiction_rate = (contradictions / total_reviews) * 100 if total_reviews > 0 else 0

print(
    f"✅ C5 Transform completed: "
    f"{len(apps_df)} apps, "
    f"{total_reviews} reviews"
)
print(f"📊 Sentiment Analysis Summary:")
print(f"   - Total contradictions detected: {contradictions} ({contradiction_rate:.1f}%)")
print(f"   - Positive reviews: {(reviews_df['text_sentiment_label'] == 'positive').sum()}")
print(f"   - Negative reviews: {(reviews_df['text_sentiment_label'] == 'negative').sum()}")
print(f"   - Neutral reviews: {(reviews_df['text_sentiment_label'] == 'neutral').sum()}")
