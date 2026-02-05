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
# True  → C1 New Reviews Batch (CSV)
APPS_RAW = RAW_DIR / "apps_raw.json"
REVIEWS_JSONL = RAW_DIR / "reviews_raw.jsonl"
REVIEWS_CSV = RAW_DIR / "note_taking_ai_reviews_batch2.csv"
#REVIEWS_CSV = RAW_DIR / "note_taking_ai_reviews_schema_drift.csv"




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

reviews_df["app_name"] = reviews_df["app_id"].map(app_lookup)
reviews_df["app_name"] = reviews_df["app_name"].fillna("UNKNOWN_APP")

reviews_df = reviews_df[[
    "app_id", "app_name", "reviewId",
    "userName", "score", "content",
    "thumbsUpCount", "at"
]]

# ==============================
# Save processed datasets
# ==============================
apps_df.to_csv(
    PROCESSED_DIR / "apps_catalog.csv",
    index=False
)

reviews_df.to_csv(
    PROCESSED_DIR / "apps_reviews.csv",
    index=False
)

print(
    f"✅ C1 Transform completed: "
    f"{len(apps_df)} apps, "
    f"{len(reviews_df)} reviews"
)
