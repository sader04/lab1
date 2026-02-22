# Lab 2: Data Pipeline with dbt & DuckDB

## Overview
This project implements an analytics-ready data pipeline for Google Play Store data using dbt (Data Build Tool) and DuckDB. The pipeline follows Kimball's dimensional modeling methodology to transform raw JSON data into a star schema optimized for analytical queries.

## Architecture

### Components
- **dbt Core**: Data transformation and testing framework
- **DuckDB**: Analytical database and execution engine
- **Python**: Data ingestion from Google Play Store API (from Lab 1)

### Pipeline Layers
1. **Raw Layer**: JSON files in `data/raw/` directory
2. **Staging Layer**: Views that clean and standardize raw data
3. **Dimension Layer**: Materialized tables for descriptive attributes
4. **Fact Layer**: Incremental table for review events
5. **Quality Layer**: dbt tests ensuring data integrity

## Project Structure
```
lab2_dbt_duckdb/
├── models/
│   ├── staging/
│   │   ├── stg_playstore_apps.sql
│   │   ├── stg_playstore_reviews.sql
│   │   └── schema.yml
│   └── marts/
│       ├── dimensions/
│       │   ├── dim_date.sql
│       │   ├── dim_developers.sql
│       │   ├── dim_categories.sql
│       │   ├── dim_apps.sql
│       │   ├── dim_apps_scd.sql
│       │   └── schema.yml
│       └── facts/
│           ├── fact_reviews.sql
│           └── schema.yml
├── snapshots/
│   └── snp_apps.sql
├── data/
│   └── raw/
│       ├── apps_raw.json
│       └── reviews_raw.jsonl
├── dbt_project.yml
└── profiles.yml
```

## Features Implemented

### 1. **Dimensional Data Modeling**
- Star schema design following Kimball methodology
- Fact table: `fact_reviews` (one row per review)
- Dimension tables: `dim_date`, `dim_developers`, `dim_categories`, `dim_apps`

### 2. **Incremental Loading**
- `fact_reviews` configured as incremental model
- Only processes new reviews based on timestamp
- Prevents duplicate processing and improves performance

### 3. **Slowly Changing Dimensions (SCD Type 2)**
- `snp_apps` snapshot tracks historical changes to app attributes
- `dim_apps_scd` provides easy access to historical and current versions
- Includes `dbt_valid_from`, `dbt_valid_to`, and `is_current` flags

### 4. **Data Quality & Testing**
- 55 data tests across all models
- Test types:
  - Uniqueness tests on primary keys
  - Not-null constraints
  - Accepted values (ratings 1-5)
  - Referential integrity (foreign key relationships)
- Custom deduplication logic in staging layer

### 5. **Key Modifications**
- Fixed UUID to VARCHAR casting for md5 hash functions
- Added deduplication using `ROW_NUMBER()` for duplicate reviews
- Adjusted date parsing for DuckDB compatibility
- Modified tests to match actual data characteristics

## Setup Instructions

### Prerequisites
- Python virtual environment (from Lab 1)
- Google Play Store raw data files

### Installation
1. Activate your virtual environment:
   ```bash
   conda activate data_eng_env  # or source data_eng_env/bin/activate
   ```

2. Install required packages:
   ```bash
   pip install duckdb dbt-core dbt-duckdb
   ```

3. Initialize dbt project (if not done):
   ```bash
   dbt init lab2_dbt_duckdb
   ```

4. Configure `profiles.yml`:
   ```yaml
   lab2:
     outputs:
       dev:
         type: duckdb
         path: dev.duckdb
         threads: 1
     target: dev
   ```

5. Copy raw data files to `data/raw/` directory

## Usage

### Run the Full Pipeline
```bash
dbt run
```

### Run Tests
```bash
dbt test
```

### Run Specific Models
```bash
dbt run --select fact_reviews
dbt run --select marts.dimensions.dim_apps_scd
dbt run --select marts.dimensions.dim_*  # All dimensions
```

### Run Snapshots
```bash
dbt snapshot
```

### Debug and Investigate
```bash
dbt show --select fact_reviews --limit 10
dbt show --select marts.dimensions.dim_apps
dbt test --select stg_playstore_reviews
```

## Testing Results
- **Total Tests**: 55
- **Passing Tests**: 55
- **Test Coverage**: All models have comprehensive tests for:
  - Primary key uniqueness
  - Foreign key relationships
  - Data type validation
  - Business rule compliance


