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
# Configuration
# ==============================
USE_CSV_BATCH = True
# False → normal pipeline (JSONL)
# True  → C3 New Reviews Batch (CSV)
APPS_RAW = RAW_DIR / "apps_raw.json"
REVIEWS_CSV = RAW_DIR / "note_taking_ai_reviews_dirty.csv"  




# ==============================
# Load apps metadata (JSON)
# ==============================
with APPS_RAW.open("r", encoding="utf-8") as f:
    apps_data = json.load(f)

apps_df = pd.DataFrame(apps_data)

apps_df = apps_df[[
    "appId", "title", "developer",
    "score", "ratings", "installs",
    "genre", "price"
]]

apps_df["score"] = pd.to_numeric(apps_df["score"], errors="coerce")
apps_df["ratings"] = pd.to_numeric(apps_df["ratings"], errors="coerce")

apps_df = apps_df.drop_duplicates(subset=["appId"], keep="last")

# ==============================
# Load reviews (JSONL or CSV)
# ==============================
# ==============================
# Load reviews (explicit source selection)
# ==============================
if USE_CSV_BATCH:
    if not REVIEWS_CSV.exists():
        raise FileNotFoundError(
            "C1 expects CSV batch as sole reviews source"
        )
    print("🔄 Using CSV reviews batch (C1)")
    reviews_df = pd.read_csv(REVIEWS_CSV)
else:
    if not REVIEWS_JSONL.exists():
        raise FileNotFoundError(
            "JSONL reviews file not found"
        )
    print("🔄 Using JSONL reviews")
    reviews_df = pd.read_json(
        REVIEWS_JSONL,
        lines=True,
        encoding="utf-8"
    )


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
    reviews_df = reviews_df.drop_duplicates(
        subset=["reviewId"],
        keep="last"
    )

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

reviews_df = reviews_df[[
    "app_id", "app_name", "reviewId",
    "userName", "score", "content",
    "thumbsUpCount", "at"
]]

# ==============================
# Save processed datasets
# ==============================
apps_df.to_csv(
    PROCESSED_DIR / "apps_catalog_3.csv",
    index=False
)

reviews_df.to_csv(
    PROCESSED_DIR / "apps_reviews_3.csv",
    index=False
)

print(
    f"✅ C3 Transform completed: "
    f"{len(apps_df)} apps, "
    f"{len(reviews_df)} reviews"
)
