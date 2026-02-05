import json
import pandas as pd
from pathlib import Path

print("🔄 Using schema-drift CSV (C2)")

# ==============================
# Paths
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

APPS_RAW = RAW_DIR / "apps_raw.json"
REVIEWS_CSV = RAW_DIR / "note_taking_ai_reviews_schema_drift.csv"

# ==============================
# Load apps metadata
# ==============================
with APPS_RAW.open("r", encoding="utf-8") as f:
    apps_data = json.load(f)

apps_df = pd.DataFrame(apps_data)[[
    "appId", "title", "developer",
    "score", "ratings", "installs",
    "genre", "price"
]]

apps_df["score"] = pd.to_numeric(apps_df["score"], errors="coerce")
apps_df["ratings"] = pd.to_numeric(apps_df["ratings"], errors="coerce")
apps_df = apps_df.drop_duplicates(subset=["appId"], keep="last")

# ==============================
# Load schema-drift reviews
# ==============================
reviews_df = pd.read_csv(REVIEWS_CSV)

# ==============================
# Schema normalization (C2 core)
# ==============================
reviews_df = reviews_df.rename(columns={
    "appId": "app_id",
    "review_id": "reviewId",
    "username": "userName",
    "rating": "score",
    "review_text": "content",
    "likes": "thumbsUpCount",
    "review_time": "at"
})

# ==============================
# Type cleaning
# ==============================
reviews_df["score"] = pd.to_numeric(reviews_df["score"], errors="coerce")

if "thumbsUpCount" in reviews_df.columns:
    reviews_df["thumbsUpCount"] = pd.to_numeric(
        reviews_df["thumbsUpCount"], errors="coerce"
    ).fillna(0)
else:
    reviews_df["thumbsUpCount"] = 0

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

reviews_df["app_name"] = reviews_df["app_id"].map(app_lookup)
reviews_df["app_name"] = reviews_df["app_name"].fillna("UNKNOWN_APP")

# ==============================
# Final schema enforcement (defensive)
# ==============================
FINAL_COLUMNS = {
    "app_id": pd.NA,
    "app_name": "UNKNOWN_APP",
    "reviewId": pd.NA,
    "userName": "UNKNOWN_USER",
    "score": pd.NA,
    "content": "",
    "thumbsUpCount": 0,
    "at": pd.NaT
}

for col, default in FINAL_COLUMNS.items():
    if col not in reviews_df.columns:
        reviews_df[col] = default

reviews_df = reviews_df[list(FINAL_COLUMNS.keys())]

# ==============================
# Save processed data
# ==============================
apps_df.to_csv(PROCESSED_DIR / "apps_catalog.csv", index=False)
reviews_df.to_csv(PROCESSED_DIR / "apps_reviews.csv", index=False)

print(
    f"✅ C2 Transform completed: "
    f"{len(apps_df)} apps, "
    f"{len(reviews_df)} reviews"
)
