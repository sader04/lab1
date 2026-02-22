{{ config(materialized='table') }}

SELECT
    natural_app_id,
    app_name,
    developer_name,
    category_name,
    content_rating,
    is_free,
    price,
    currency,
    dbt_valid_from,
    dbt_valid_to,
    CASE 
        WHEN dbt_valid_to IS NULL THEN TRUE 
        ELSE FALSE 
    END AS is_current
FROM {{ ref('snp_apps') }}
ORDER BY natural_app_id, dbt_valid_from