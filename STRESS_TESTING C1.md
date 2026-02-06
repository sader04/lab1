

# C.1 — New Reviews Batch

## How many changes were required in your code to support this new batch?

Supporting the new reviews batch required **very limited changes** to the pipeline.
Specifically, a configuration switch (`USE_CSV_BATCH`) was added in the transformation layer to explicitly select the upstream reviews source (JSONL or CSV).

In addition, a lightweight schema normalization step was introduced to handle potential column name differences between input formats.

No changes were required in the serving layer (`serve.py`) or in the dashboard code, demonstrating that downstream components are decoupled from upstream ingestion formats and that the pipeline follows a modular design with a clear separation of concerns.

---

## Is your pipeline clearly performing a full refresh, or does this behavior remain implicit?

The pipeline is **effectively performing a full refresh** on every execution.
Each run fully reloads the selected upstream dataset, recomputes all transformations from scratch, and overwrites the processed output files without preserving any previous state.

This behavior is **partially explicit**. The use of a configuration flag (`USE_CSV_BATCH`) makes the choice of the upstream source explicit and enforces a clean rebuild by failing early if the expected input file is missing.

However, the full-refresh behavior itself is not formally modeled as an explicit pipeline mode. There is no notion of incremental processing, batch identifiers, or historical state management, which means the full-refresh assumption remains an implicit design choice rather than an explicit contract.

---

## Pipeline outputs with CSV batch (C1)

![C1 Daily Rating](screenshots/daily%20averge%20c1%20.png)

The daily average rating time series is computed over a short time window due to the limited size of the CSV batch, making the metric more sensitive to individual reviews.

![C1 Daily Rating](screenshots/daily%20number%20c1%20.png)

The daily number of reviews shows a very limited temporal distribution, highlighting the impact of reduced data volume on downstream analytics and visualizations.

---

## How are duplicate reviews handled?

Duplicate reviews are handled during the **transformation step** using the review identifier (`reviewId`).
If multiple records share the same `reviewId`, only the most recent occurrence is retained, while the others are discarded.

This deduplication logic ensures consistent aggregates but relies on the implicit assumption that `reviewId` is stable and uniquely identifies a review across upstream batches.

---

## What happens to reviews that reference applications not present in the applications dataset?

Reviews that reference application identifiers not present in the applications metadata dataset are **not discarded**.
During the enrichment step, the application name cannot be resolved and is therefore set to a default value (`"UNKNOWN_APP"`).

This allows the pipeline to continue processing without failing, but it also highlights an implicit assumption of referential integrity between reviews and applications that is not explicitly enforced or validated.


