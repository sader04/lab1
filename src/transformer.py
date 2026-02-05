import json
import os
import pandas as pd

# Define paths
raw_apps_path = os.path.join("LAB1", "data", "raw", "apps_raw.json")
raw_reviews_path = os.path.join("LAB1", "data", "raw", "reviews_raw.json")
processed_dir = os.path.join("LAB1", "data", "processed")

# Ensure output directory exists
os.makedirs(processed_dir, exist_ok=True)

# Load raw data
with open(raw_apps_path, 'r', encoding='utf-8') as f:
    apps_data = json.load(f)

with open(raw_reviews_path, 'r', encoding='utf-8') as f:
    reviews_data = json.load(f)

# Helper: clean installs string (e.g., "10,000,000+" → 10000000)
def clean_installs(installs_str):
    if not isinstance(installs_str, str):
        return 0
    cleaned = installs_str.replace(",", "").rstrip("+")
    return int(cleaned) if cleaned.isdigit() else 0

# Clean app data
for app in apps_data:
    app['installs'] = clean_installs(app.get('installs', '0'))

# Build appId → title lookup
app_lookup = {app['appId']: app['title'] for app in apps_data}

# Enrich reviews with app_id and app_name
enriched_reviews = []
for review in reviews_data:
    app_id = review.get('appId')
    if app_id in app_lookup:
        enriched_reviews.append({
            'app_id': app_id,
            'app_name': app_lookup[app_id],
            'reviewId': review.get('reviewId'),
            'userName': review.get('userName'),
            'score': review.get('score'),
            'content': review.get('content', ''),
            'thumbsUpCount': review.get('thumbsUpCount', 0),
            'at': review.get('at')  # Keep as ISO string; parse later if needed
        })
    else:
        print(f"Warning: Review with appId '{app_id}' has no matching app metadata — skipped.")

# Convert to DataFrames
apps_df = pd.DataFrame(apps_data)
reviews_df = pd.DataFrame(enriched_reviews)

# Select only required columns in specified order
apps_df = apps_df[['appId', 'title', 'developer', 'score', 'ratings', 'installs', 'genre', 'price']]
reviews_df = reviews_df[['app_id', 'app_name', 'reviewId', 'userName', 'score', 'content', 'thumbsUpCount', 'at']]

# Save to CSV
apps_df.to_csv(os.path.join(processed_dir, "apps_catalog.csv"), index=False, encoding='utf-8')
reviews_df.to_csv(os.path.join(processed_dir, "apps_reviews.csv"), index=False, encoding='utf-8')

print(f"✅ Transformed {len(apps_df)} apps and {len(reviews_df)} reviews into CSV files.")