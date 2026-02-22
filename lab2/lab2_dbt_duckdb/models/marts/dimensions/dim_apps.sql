{{ config(materialized='table') }}

WITH apps AS (
    SELECT
        app_id,
        app_name,
        developer_id,
        category_id,
        content_rating,
        is_free,
        price,
        currency,
        -- Use developer_key from dim_developers
        dvlpr.developer_key,
        -- Use category_key from dim_categories
        cat.category_key
    FROM {{ ref('stg_playstore_apps') }} apps
    LEFT JOIN {{ ref('dim_developers') }} dvlpr 
        ON apps.developer_id = dvlpr.natural_developer_id
    LEFT JOIN {{ ref('dim_categories') }} cat 
        ON apps.category_id = cat.natural_category_id
)

SELECT
    -- Surrogate key
    md5(app_id::VARCHAR) AS app_key,
    app_id AS natural_app_id,
    app_name,
    developer_key,
    category_key,
    content_rating,
    is_free,
    price,
    currency,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM apps