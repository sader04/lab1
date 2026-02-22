{% snapshot snp_apps %}

{{
    config(
        target_schema='snapshots',
        unique_key='natural_app_id',
        strategy='check',
        check_cols=['app_name', 'developer_name', 'category_name', 'content_rating', 'is_free', 'price'],
        invalidate_hard_deletes=True
    )
}}

SELECT
    app_id AS natural_app_id,
    app_name,
    developer_name,
    category_name,
    content_rating,
    is_free,
    price,
    currency,
    CURRENT_TIMESTAMP AS loaded_at
FROM {{ ref('stg_playstore_apps') }}

{% endsnapshot %}