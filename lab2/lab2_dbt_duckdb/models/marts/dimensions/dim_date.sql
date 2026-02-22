{{ config(materialized='table') }}

WITH date_spine AS (
    -- Get min and max dates from reviews
    SELECT 
        MIN(DATE(review_timestamp)) AS min_date,
        MAX(DATE(review_timestamp)) AS max_date
    FROM {{ ref('stg_playstore_reviews') }}
),

-- Generate all dates between min and max
dates AS (
    SELECT 
        UNNEST(generate_series(
            (SELECT min_date FROM date_spine)::DATE,
            (SELECT max_date FROM date_spine)::DATE,
            INTERVAL 1 DAY
        )) AS date_day
)

SELECT
    -- Surrogate key in YYYYMMDD format
    CAST(strftime(date_day, '%Y%m%d') AS INTEGER) AS date_key,
    date_day AS full_date,
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(MONTH FROM date_day) AS month,
    EXTRACT(DAY FROM date_day) AS day,
    strftime(date_day, '%B') AS month_name,
    strftime(date_day, '%A') AS day_of_week,
    EXTRACT(WEEK FROM date_day) AS week_of_year,
    EXTRACT(QUARTER FROM date_day) AS quarter,
    CASE 
        WHEN EXTRACT(DOW FROM date_day) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END AS is_weekend,
    -- Add more attributes as needed
    strftime(date_day, '%Y-%m') AS year_month
FROM dates
ORDER BY date_day