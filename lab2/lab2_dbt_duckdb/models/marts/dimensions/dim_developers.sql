{{ config(materialized='table') }}

WITH developers AS (
    SELECT DISTINCT
        developer_id,
        developer_name,
        developer_email,
        developer_website
    FROM {{ ref('stg_playstore_apps') }}
    WHERE developer_id IS NOT NULL
)

SELECT
    -- Surrogate key
    md5(developer_id::VARCHAR) AS developer_key,
    developer_id AS natural_developer_id,
    developer_name,
    developer_email,
    developer_website,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM developers
WHERE developer_name IS NOT NULL