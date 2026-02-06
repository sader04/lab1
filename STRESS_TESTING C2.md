
# C.2 — Schema Drift in Reviews

## Which parts of your pipeline rely on hard-coded column names?

The pipeline relies on hard-coded column names primarily in the **reviews transformation layer**.
This dependency is explicit in the schema normalization step, where upstream fields are mapped to a canonical schema using a fixed renaming dictionary (e.g. `review_id → reviewId`, `rating → score`, `review_time → at`, `review_text → content`).

Additionally, the final schema enforcement step explicitly defines the expected output columns and their default values, ensuring a stable downstream schema regardless of upstream variations.

Downstream components (serving layer and dashboard) rely exclusively on this canonical schema and do not depend on the original upstream column names.

---

## Pipeline outputs after schema drift

![C2 Daily Rating](screenshots/daily%20number%20c2.png)

The daily number of reviews remains computable after schema normalization, confirming that timestamp fields are correctly mapped despite upstream structural changes.

![C2 Daily Rating](screenshots/daily%20average%20%20c2.png)

The daily average rating time series remains interpretable, showing that rating values were successfully normalized and aggregated after schema drift.

![C2 Daily Rating](screenshots/average%20%20rating%20%20c2.png)

Application-level average ratings can still be computed, demonstrating that schema normalization and enrichment steps successfully isolate downstream analytics from upstream column name changes.

---

## Does the pipeline fail explicitly, or does it produce incorrect results silently?

The pipeline does **not fail explicitly** when encountering schema drift.
Instead, it continues execution defensively through schema normalization, type coercion, and final schema enforcement.

If upstream fields are missing or renamed in unexpected ways, default values are automatically injected (e.g. `UNKNOWN_APP`, `UNKNOWN_USER`, `NaT`).
While this prevents runtime failures, it can also lead to **silent data degradation**, where analytical results remain computable but may be partially incomplete or less accurate.

---

## How localized or widespread are the required code changes?

The required code changes to support schema drift are **highly localized**.
All adaptations are confined to the **reviews transformation step**, including schema normalization, defensive type handling, heuristic application name resolution, and final schema enforcement.

No changes were required in the applications metadata ingestion, the serving layer aggregations, or the dashboard code.

This confirms a strong separation of concerns and demonstrates that the pipeline structure effectively isolates upstream schema instability from downstream analytics.


