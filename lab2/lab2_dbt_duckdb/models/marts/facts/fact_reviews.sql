{{ config(
    materialized='incremental',
    unique_key='fact_review_key'
) }}

WITH reviews AS (
    SELECT
        review_id,
        app_id,
        rating,
        thumbs_up_count,
        review_timestamp,
        date_key,
        review_key,
        DATE(review_timestamp) AS review_date
    FROM {{ ref('stg_playstore_reviews') }}
    
    {% if is_incremental() %}
    -- Only load reviews newer than the latest in the fact table
    WHERE review_timestamp > (SELECT MAX(review_timestamp) FROM {{ this }})
    {% endif %}
),

-- Get dimension keys
dimensions AS (
    SELECT
        r.review_id,
        r.rating,
        r.thumbs_up_count,
        r.review_timestamp,
        r.date_key,
        a.app_key,
        a.developer_key,
        a.category_key
    FROM reviews r
    INNER JOIN {{ ref('dim_apps') }} a 
        ON r.app_id = a.natural_app_id
    WHERE r.rating IS NOT NULL
)

SELECT
    review_id AS fact_review_key,
    date_key,
    app_key,
    developer_key,
    category_key,
    rating,
    thumbs_up_count,
    review_timestamp,
    CASE 
        WHEN rating >= 4 THEN 1 
        ELSE 0 
    END AS is_positive_review,
    CASE 
        WHEN rating <= 2 THEN 1 
        ELSE 0 
    END AS is_negative_review,
    1 AS review_count
FROM dimensions