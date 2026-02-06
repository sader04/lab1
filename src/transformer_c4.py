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
# Configuration for C4
# ==============================
USE_CSV_APPS = True  # Use updated apps CSV
USE_CSV_REVIEWS = True  # Use dirty reviews CSV

APPS_CSV = RAW_DIR / "note_taking_ai_apps_updated.csv"
REVIEWS_CSV = RAW_DIR / "note_taking_ai_reviews_dirty.csv"

# ==============================
# Load apps metadata (CSV for C4)
# ==============================
if USE_CSV_APPS:
    print("🔄 Using updated apps CSV (C4)")
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
    print("🔄 Using dirty reviews CSV (C4)")
    reviews_df = pd.read_csv(REVIEWS_CSV, quotechar='"', escapechar='\\', on_bad_lines='skip')
else:
    print("🔄 Using JSONL reviews (C4)")
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

# Final column selection
reviews_df = reviews_df[[
    "app_id", "app_name", "reviewId",
    "userName", "score", "content",
    "thumbsUpCount", "at"
]]

# ==============================
# Save processed datasets
# ==============================
apps_df.to_csv(PROCESSED_DIR / "apps_catalog_4.csv", index=False)
reviews_df.to_csv(PROCESSED_DIR / "apps_reviews_4.csv", index=False)

print(
    f"✅ C4 Transform completed: "
    f"{len(apps_df)} apps, "
    f"{len(reviews_df)} reviews"
)

