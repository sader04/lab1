


Feedback:
- You are limiting the possibilities of your code as you list the apps to search for, use a query term rather than app id.

- Use continuation tokens in reviews so you can get as much data as possible. Remember, more data, richer analyses in downstream tasks

- It’s good to separate layers’ logic in code files. Kudos on that.

- Think about writing with **append** in the loop for retrieving reviews with pagination; it is always better to prevent data loss if code crashes

- Please add a screenshot of your dashboard to the readmefile

---



# Lab 1 – Python-only Data Pipeline

**Product Analytics – AI Note-Taking Applications**

---

## 📌 Project Overview

This project implements a **Python-only end-to-end data pipeline** following the main stages of the data engineering lifecycle:

* Data acquisition & ingestion
* Data transformation & cleaning
* Serving layer (analytics-ready datasets)
* Lightweight dashboarding

The objective is to transform **raw, semi-structured data** into **reproducible, analytics-ready outputs**, while applying good data engineering practices such as modularity, robustness, and reproducibility.

---

## 📁 Project Structure

```text
lab1/
├── data/
│   ├── raw/                # Raw upstream data (JSON, JSONL)
│   └── processed/          # Cleaned & aggregated datasets
├── screenshots/            # Dashboard screenshots (README)
├── src/
│   ├── scraper.py          # Data acquisition (Google Play API)
│   ├── transformer.py      # Data cleaning & transformation (A & B)
│   ├── transformer_c2.py   # Schema drift handling (C2)
│   ├── transformer_c3.py   # Dirty & inconsistent data handling (C3)
│   ├── serve.py            # Serving layer (KPIs, daily metrics)
│   └── dashboard.py        # Dashboard visualization
├── STRESS_TESTING_C1.md    # Stress testing – New reviews batch (C1)
├── STRESS_TESTING_C2.md    # Stress testing – Schema drift (C2)
└── README.md
```

---

## 🧱 Part A – Environment Setup

* Python version: **3.7+**
* Dedicated virtual environment (`.venv`)
* Dependencies installed incrementally
* Pipeline executed using Python scripts (no notebooks)

This setup ensures isolation of dependencies and reproducibility of results.

---

## 🔗 Part B – End-to-End Data Pipeline

### Data Sources

The pipeline focuses on **AI note-taking applications** available on the Google Play Store.

Two datasets are collected:

* **Applications metadata**

  * Application identifier
  * Title, developer, genre
  * Ratings, installs, price

* **User reviews**

  * Review text
  * Rating score
  * Timestamp
  * User information

Raw data is ingested **as-is** and stored in the `data/raw/` directory.

---

### Data Acquisition & Ingestion

Applications are retrieved using a **query-based search** (`"ai note taking"`) rather than a predefined list of application IDs.
This approach improves scalability and allows the pipeline to automatically adapt to new applications entering the market.

For reviews:

* Pagination is handled using **continuation tokens**
* Reviews are collected until no more pages are available
* Data is written in **append mode (JSONL)** to prevent data loss if execution stops unexpectedly

This design enables the collection of larger datasets, resulting in richer downstream analyses.

---

### Data Transformation

Raw semi-structured data is transformed into clean, tabular datasets:

* Nested fields are flattened
* Numeric values are type-casted
* Timestamps are normalized
* Duplicate reviews are removed
* Data is enriched with application metadata when possible

Cleaned datasets are written to `data/processed/` and can be regenerated from scratch.

---

### Serving Layer

The pipeline produces analytics-ready datasets:

* **Application-level KPIs**

  * Number of reviews
  * Average rating
  * Percentage of low ratings
  * First and most recent review dates

* **Daily metrics**

  * Daily number of reviews
  * Daily average rating

These outputs are designed for reporting and visualization purposes.

---

## 📊 Dashboard Results – Part A & B

### Daily Number of Reviews

![Daily Number of Reviews](screenshots/part%20AB%201.jpeg)

**Observation:**
The number of reviews increases over time, with visible spikes corresponding to periods of higher user activity.
This indicates growing adoption and engagement with AI note-taking applications.

---

### Daily Average Rating Over Time

![Daily Average Rating](screenshots/part%20AB%202.jpeg)

**Observation:**
User ratings remain globally stable around **4–4.5**, with occasional short drops.
These fluctuations may be linked to application updates or changes affecting user experience.

---

### Average Rating per Application and Percentage of Low Ratings

![Average Rating per App](screenshots/part%20AB%203.jpeg)

**Observation:**
Most applications maintain high average ratings, while the percentage of low ratings varies across apps.
This highlights differences in user satisfaction and perceived quality between competing AI note-taking applications.

---

## ✅ Key Takeaways (Part A & B)

* Query-based ingestion improves flexibility and scalability
* Pagination with continuation tokens enables richer datasets
* Append-mode writing increases robustness against failures
* Clear separation between ingestion, transformation, serving, and visualization logic
* Dashboard screenshots confirm that the pipeline produces usable and interpretable analytics outputs

