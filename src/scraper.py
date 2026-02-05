from google_play_scraper import app, reviews        
import json
import os
from datetime import datetime


app_ids = ['com.microsoft.office.onenote', 'notion.id', 'com.evernote']

# Save files under the workspace folder 'App Market Research/data/raw'
raw_apps_path = os.path.join("App Market Research", "data", "raw", "apps_raw.json")
raw_reviews_path = os.path.join("App Market Research", "data", "raw", "reviews_raw.json")

# Ensure the data/raw directory exists
os.makedirs(os.path.dirname(raw_apps_path), exist_ok=True)
os.makedirs(os.path.dirname(raw_reviews_path), exist_ok=True)

all_apps = []
all_reviews = []

for app_id in app_ids:
    try:
        print(f"Fetching metadata for {app_id}...")
        app_metadata = app(app_id, lang='en', country='us')
        all_apps.append(app_metadata)
        
        print(f"Fetching reviews for {app_id}...")
        app_reviews, _ = reviews(
            app_id,
            lang='en',
            country='us',
            count=100
        )
        
        # 🔑 CRITICAL: Add appId to each review so we know its source
        for r in app_reviews:
            r['appId'] = app_id  # Tag the review with its app ID
        
        all_reviews.extend(app_reviews)
        
    except Exception as e:
        print(f"Error fetching data for {app_id}: {e}")

# Save apps metadata
with open(raw_apps_path, 'w', encoding='utf-8') as f:
    json.dump(all_apps, f, ensure_ascii=False, indent=2)

# Helper to serialize datetime objects
def convert_datetime_to_string(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

# Save reviews with appId included
with open(raw_reviews_path, 'w', encoding='utf-8') as f:
    json.dump(all_reviews, f, default=convert_datetime_to_string, ensure_ascii=False, indent=2)

print(f"Ingested {len(all_apps)} apps and {len(all_reviews)} reviews")