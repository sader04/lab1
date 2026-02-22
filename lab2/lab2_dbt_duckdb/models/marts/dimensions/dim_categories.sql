{{ config(materialized='table') }}

WITH categories AS (
    SELECT DISTINCT
        category_id,
        category_name,
        primary_genre,
        primary_genre_id
    FROM {{ ref('stg_playstore_apps') }}
    WHERE category_id IS NOT NULL
)

SELECT
    -- Surrogate key
    md5(category_id::VARCHAR) AS category_key,
    category_id AS natural_category_id,
    category_name,
    primary_genre,
    primary_genre_id,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM categories