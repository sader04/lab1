from google_play_scraper import search, app, reviews, Sort
import json
from pathlib import Path
from datetime import datetime

# ==============================
# Configuration
# ==============================
QUERY = "ai note taking"
N_APPS = 20
REVIEWS_PER_PAGE = 200

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

APPS_PATH = RAW_DIR / "apps_raw.json"
REVIEWS_PATH = RAW_DIR / "reviews_raw.jsonl"   #  JSONL (append-safe)

# ==============================
# 1. Search apps by query
# ==============================
results = search(
    QUERY,
    lang="en",
    country="us",
    n_hits=N_APPS
)

app_ids = [r["appId"] for r in results]
print(f"Found {len(app_ids)} apps for query '{QUERY}'")

# ==============================
# 2. Extract apps metadata
# ==============================
all_apps = []

for app_id in app_ids:
    try:
        print(f"Fetching metadata for {app_id}")
        meta = app(app_id, lang="en", country="us")
        meta["_extracted_at"] = datetime.utcnow().isoformat()
        all_apps.append(meta)
    except Exception as e:
        print(f"[ERROR] App metadata {app_id}: {e}")

# Save apps metadata (JSON)
with APPS_PATH.open("w", encoding="utf-8") as f:
    json.dump(all_apps, f, ensure_ascii=False, indent=2)

# ==============================
# 3. Extract reviews with pagination + append
# ==============================
with REVIEWS_PATH.open("a", encoding="utf-8") as f:
    for app_id in app_ids:
        print(f"Fetching reviews for {app_id}")
        continuation_token = None
        page_count = 0
        max_pages = 5  # Safety limit (e.g., 5 * 200 = 1000 reviews max per app)

        while page_count < max_pages:
            try:
                result, continuation_token = reviews(
                    app_id,
                    lang="en",
                    country="us",
                    sort=Sort.NEWEST,
                    count=REVIEWS_PER_PAGE,
                    continuation_token=continuation_token
                )
                #stop if no more reviews
                if not result:
                    print(f"  → No more reviews for {app_id}")
                    break

                print(f"  → Fetched {len(result)} reviews (page {page_count + 1})")
                for r in result:
                    r["appId"] = app_id
                    r["_extracted_at"] = datetime.utcnow().isoformat()
                    f.write(json.dumps(r, default=str, ensure_ascii=False) + "\n")
                
                #break if no more pages
                if continuation_token is None:
                    print(f"  → End of reviews for {app_id}")
                    break
                
                page_count += 1

            except Exception as e:
                print(f"[ERROR] Reviews {app_id}: {e}")
                break

print("✅ Ingestion completed (apps JSON + reviews JSONL)")
