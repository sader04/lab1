{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM read_json('data/raw/reviews_raw.jsonl', 
        format='newline_delimited',
        columns={
            'reviewId': 'VARCHAR',
            'userName': 'VARCHAR', 
            'userImage': 'VARCHAR',
            'content': 'VARCHAR',
            'score': 'VARCHAR',
            'thumbsUpCount': 'VARCHAR',
            'reviewCreatedVersion': 'VARCHAR',
            'at': 'VARCHAR',
            'replyContent': 'VARCHAR',
            'repliedAt': 'VARCHAR',
            'appVersion': 'VARCHAR',
            'appId': 'VARCHAR',
            '_extracted_at': 'VARCHAR'
        },
        ignore_errors=true
    )
),

-- Add row number to deduplicate by review_id, taking the latest extraction
deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY reviewId 
            ORDER BY _extracted_at DESC
        ) as rn
    FROM source
    WHERE reviewId IS NOT NULL
)

SELECT
    reviewId AS review_id,
    userName AS user_name,
    userImage AS user_image_url,
    content AS review_text,
    CASE WHEN score ~ '^[0-9]+$' THEN score::INTEGER ELSE NULL END AS rating,
    CASE WHEN thumbsUpCount ~ '^[0-9]+$' THEN thumbsUpCount::INTEGER ELSE 0 END AS thumbs_up_count,
    reviewCreatedVersion AS review_created_version,
    "at"::TIMESTAMP AS review_timestamp,
    replyContent AS reply_content,
    repliedAt::TIMESTAMP AS replied_at,
    appVersion AS app_version,
    appId AS app_id,
    _extracted_at::TIMESTAMP AS extracted_at,
    md5(reviewId) AS review_key,
    strftime("at"::TIMESTAMP, '%Y%m%d')::INT AS date_key
FROM deduped
WHERE rn = 1  -- Take only the most recent extraction for each review