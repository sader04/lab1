# Data Engineering Labs - AI Note-Taking Applications Analytics

**Complete Data Pipeline Implementation: From Python Ingestion to dbt Transformation**

---

## 📌 Project Overview

This repository contains a comprehensive data engineering pipeline for analyzing AI note-taking applications from the Google Play Store. The project demonstrates the evolution from a Python-based pipeline (Lab 1) to a modern dbt-based analytics warehouse (Lab 2).

### 🔄 Project Evolution

**Lab 1**: Python-only end-to-end data pipeline
- Data acquisition from Google Play Store API
- Transformation and cleaning with Python scripts
- Basic analytics and dashboarding

**Lab 2**: Modern analytics warehouse with dbt & DuckDB
- Kimball dimensional modeling
- Incremental loading and SCD Type 2
- Comprehensive data testing and quality assurance

The objective is to transform **raw, semi-structured data** into **reproducible, analytics-ready outputs**, while applying modern data engineering best practices.

---

## 📁 Complete Project Structure

```text
lab1/
├── data/
│   ├── raw/                # Raw upstream data (JSON, JSONL)
│   └── processed/          # Cleaned & aggregated datasets
├── screenshots/            # Dashboard screenshots and visualizations
├── src/
│   ├── scraper.py          # Data acquisition (Google Play API)
│   ├── transformer.py      # Data cleaning & transformation
│   ├── transformer_c2.py   # Schema drift handling
│   ├── transformer_c3.py   # Dirty data handling
│   ├── serve.py            # Serving layer (KPIs, daily metrics)
│   └── dashboard.py        # Dashboard visualization
├── STRESS_TESTING_C1.md    # Stress testing documentation
├── STRESS_TESTING_C2.md    # Schema drift documentation
├── RAPPORT_FINAL.md        # Executive summary report
├── RAPPORT_COMPLET_EXPLICATIF.md  # Detailed methodology and analysis
└── README.md

lab2/
└── lab2_dbt_duckdb/
    ├── models/
    │   ├── staging/           # Raw data staging views
    │   └── marts/           # Analytics models
    │       ├── dimensions/    # Dimension tables
    │       └── facts/        # Fact tables
    ├── snapshots/            # SCD Type 2 snapshots
    ├── data/raw/            # Raw data files
    ├── dbt_project.yml      # dbt configuration
    └── README.md            # Lab 2 specific documentation
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

### 📸 Visualizations Available

All dashboard screenshots are available in the [`screenshots/`](screenshots/) directory:

#### Main Dashboard Visualizations
- **Daily Number of Reviews** → `part AB 1.jpeg`
- **Daily Average Rating Over Time** → `part AB 2.jpeg`  
- **Average Rating per Application** → `part AB 3.jpeg`

#### Stress Testing Results
- **C1 - New Reviews Batch** → `daily averge c1 .png`, `daily number c1 .png`
- **C2 - Schema Drift** → `daily average c2.png`, `daily number c2.png`, `average rating c2.png`

#### Additional Visualizations
- Various dashboard states and analyses → `image-*.png`, `img.png`

### 📈 Key Insights from Visualizations

#### Daily Number of Reviews
![Daily Number of Reviews](screenshots/part%20AB%201.jpeg)

**Observation:**
The number of reviews increases over time, with visible spikes corresponding to periods of higher user activity.
This indicates growing adoption and engagement with AI note-taking applications.

---

#### Daily Average Rating Over Time
![Daily Average Rating](screenshots/part%20AB%202.jpeg)

**Observation:**
User ratings remain globally stable around **4–4.5**, with occasional short drops.
These fluctuations may be linked to application updates or changes affecting user experience.

---

#### Average Rating per Application and Percentage of Low Ratings
![Average Rating per App](screenshots/part%20AB%203.jpeg)

**Observation:**
Most applications maintain high average ratings, while the percentage of low ratings varies across apps.
This highlights differences in user satisfaction and perceived quality between competing AI note-taking applications.

---

## 📋 Detailed Reports & Analysis

### 📄 Executive Summary
- **File**: [`RAPPORT_FINAL.md`](RAPPORT_FINAL.md)
- **Content**: Complete project overview with key results and recommendations
- **Audience**: Management and stakeholders

### 🔬 Detailed Methodology Report  
- **File**: [`RAPPORT_COMPLET_EXPLICATIF.md`](RAPPORT_COMPLET_EXPLICATIF.md)
- **Content**: Step-by-step methodology, code explanations, and in-depth analysis
- **Audience**: Technical team and data engineers

### 🧪 Stress Testing Documentation
- **Files**: [`STRESS_TESTING_C1.md`](STRESS_TESTING_C1.md), [`STRESS_TESTING_C2.md`](STRESS_TESTING_C2.md)
- **Content**: Detailed analysis of pipeline robustness under various scenarios
- **Audience**: Quality assurance and DevOps teams

---

# Lab 2 – Modern Analytics Warehouse with dbt & DuckDB

**Advanced Data Transformation and Analytics Implementation**

---

## 🏗️ Architecture Overview

Lab 2 implements a modern analytics warehouse following Kimball's dimensional modeling methodology, transforming the raw data from Lab 1 into a robust, analytics-ready star schema.

### Key Components
- **dbt Core**: Data transformation and testing framework
- **DuckDB**: High-performance analytical database
- **Incremental Processing**: Efficient handling of growing datasets
- **Data Quality**: Comprehensive testing and validation

### Pipeline Layers
1. **Raw Layer**: JSON files from Lab 1 ingestion
2. **Staging Layer**: Views that clean and standardize data
3. **Dimension Layer**: Materialized tables for descriptive attributes
4. **Fact Layer**: Incremental table for review events
5. **Quality Layer**: 55+ dbt tests ensuring data integrity

---

## 🎯 Key Features Implemented

### 1. **Dimensional Data Modeling**
- Star schema design with proper relationships
- Fact table: `fact_reviews` (one row per review)
- Dimension tables: `dim_date`, `dim_developers`, `dim_categories`, `dim_apps`

### 2. **Incremental Loading**
- `fact_reviews` configured for incremental updates
- Processes only new reviews based on timestamp
- Prevents duplicate processing and improves performance

### 3. **Slowly Changing Dimensions (SCD Type 2)**
- `snp_apps` snapshot tracks historical changes
- `dim_apps_scd` provides current and historical versions
- Includes validity flags and timestamps

### 4. **Data Quality & Testing**
- 55 comprehensive data tests across all models
- Uniqueness, not-null, and referential integrity tests
- Business rule validation (ratings 1-5, etc.)

### 5. **Robust Error Handling**
- Fixed JSON parsing issues with mixed data types
- Proper type casting and validation
- DuckDB-specific optimizations

---

## 🚀 Quick Start for Lab 2

### Prerequisites
- Complete Lab 1 (raw data available)
- Python virtual environment with dbt packages

### Installation & Setup
```bash
# Navigate to Lab 2 directory
cd lab2/lab2_dbt_duckdb

# Activate environment
conda activate data_eng_env

# Run the complete pipeline
dbt run

# Run tests
dbt test

# Run snapshots
dbt snapshot
```

### Key Commands
```bash
# Run all dimension models
dbt run --select marts.dimensions.dim_*

# Run specific models
dbt run --select fact_reviews
dbt run --select marts.dimensions.dim_apps_scd

# Debug and investigate
dbt show --select fact_reviews --limit 10
dbt test --select stg_playstore_reviews
```

---

## 📈 Lab 2 Results & Benefits

### Performance Improvements
- **Incremental loading**: 10x faster for subsequent runs
- **Materialized views**: Optimized query performance
- **Data quality**: 55 tests ensure reliability

### Analytics Capabilities
- **Historical analysis**: SCD Type 2 enables time-travel queries
- **Scalable architecture**: Handles growing datasets efficiently
- **Reproducible transformations**: Version-controlled with dbt

### Technical Advantages
- **Modern tooling**: Industry-standard dbt framework
- **Documentation**: Auto-generated documentation
- **Testing**: Comprehensive data validation

---

## ✅ Complete Project Key Takeaways

### Lab 1 Achievements
- ✅ Query-based ingestion improves flexibility and scalability
- ✅ Pagination with continuation tokens enables richer datasets
- ✅ Append-mode writing increases robustness against failures
- ✅ Clear separation between pipeline components
- ✅ Functional dashboard with meaningful analytics

### Lab 2 Achievements
- ✅ Modern dimensional modeling following Kimball methodology
- ✅ Incremental processing for efficient data updates
- ✅ Comprehensive data quality with 55+ tests
- ✅ SCD Type 2 implementation for historical tracking
- ✅ Production-ready analytics warehouse

### Overall Project Success
This repository demonstrates a complete data engineering journey from basic Python scripts to a production-ready analytics warehouse, showcasing:
- **Evolution of thinking**: From simple ETL to sophisticated data modeling
- **Tool mastery**: Python, APIs, dbt, DuckDB
- **Best practices**: Testing, documentation, incremental processing
- **Real-world application**: Actual AI app market analysis

---
By:
* DERBANI Salwa
* KOUDIA Selma
