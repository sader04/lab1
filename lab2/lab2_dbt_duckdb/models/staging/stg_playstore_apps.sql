{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM read_json_auto('data/raw/apps_raw.json')
)

SELECT
    appId AS app_id,
    title AS app_name,
    developer AS developer_name,
    developerId AS developer_id,
    developerEmail AS developer_email,
    developerWebsite AS developer_website,
    genre AS primary_genre,
    genreId AS primary_genre_id,
    categories,
    -- Extract category info from the categories array
    categories[1].name AS category_name,
    categories[1].id AS category_id,
    score AS rating,
    ratings AS ratings_count,
    reviews AS reviews_count,
    installs AS installs_display,
    minInstalls AS min_installs,
    realInstalls AS real_installs,
    price,
    free AS is_free,
    currency,
    contentRating AS content_rating,
    adSupported AS is_ad_supported,
    containsAds AS contains_ads,
    released AS released_date,
    lastUpdatedOn AS last_updated_display,
    updated AS updated_timestamp,
    version AS app_version,
    privacyPolicy AS privacy_policy_url,
    icon AS icon_url,
    _extracted_at AS extracted_at,
    -- Add surrogate key
    md5(appId) AS app_key
FROM source