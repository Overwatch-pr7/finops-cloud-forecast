# Phase 2: PostgreSQL Setup and Data Ingestion

This document explains the steps taken to set up the PostgreSQL database and ingest the synthetic cloud billing dataset we generated in Phase 1.

## Why Docker?
We chose to use Docker for the PostgreSQL instance instead of a native Windows installation. This keeps the environment clean, prevents background services from slowing down your machine, and makes it extremely easy to tear down or recreate the database if needed.

## Steps Taken

### 1. Database Initialization Script (`db/init_schema.sql`)
We wrote a pure SQL script to handle schema creation and data ingestion.

```sql
-- Set date format because our CSV uses DD-MM-YYYY
SET datestyle = 'ISO, DMY';

DROP TABLE IF EXISTS cloud_billing;

CREATE TABLE cloud_billing (
    billing_date DATE PRIMARY KEY, 
    cpu_usage_pct NUMERIC(5, 2),
    ram_usage_pct NUMERIC(5, 2),
    daily_cost_usd NUMERIC(10, 2)
);

-- Ingest data natively using Postgres COPY
COPY cloud_billing(billing_date, cpu_usage_pct, ram_usage_pct, daily_cost_usd)
FROM '/data/cloud_billing_dataset.csv'
DELIMITER ','
CSV HEADER;
```
* **`SET datestyle`**: Fixes ambiguity in our `01-01-2025` date format.
* **`NUMERIC(5, 2)`**: Standard SQL type for decimals, ensuring we don't hit floating point issues with currency and percentages.
* **`COPY ... FROM`**: This is PostgreSQL's highly optimized bulk-loading command. It's much faster than running thousands of `INSERT` statements.

### 2. Container Startup Script (`db/run_db.ps1`)
We created a PowerShell script to automate the Docker instance creation.
* It stops any existing container named `finops-postgres`.
* It runs `postgres:15-alpine` in the background mapping port `5432` to localhost.
* It maps our `data/` folder to `/data` inside the container so the `COPY` command can find the CSV.
* It pipes our `init_schema.sql` script into the container to automatically execute it.

### 3. Automated Testing (`tests/test_db_ingestion.ps1`)
To ensure our data was ingested properly without manually querying it, we wrote a test script in a separate `tests/` folder. It runs a `SELECT COUNT(*)` and validates that all 365 rows exist.

## How to use
To spin up the database and ingest data:
1. Open PowerShell.
2. `cd db`
3. `.\run_db.ps1`

To run the test:
1. `cd ..\tests`
2. `.\test_db_ingestion.ps1`

To connect to the database from DBeaver, VSCode, or Python (later):
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `finops_db`
- **Username**: `finops_user`
- **Password**: `finops_password`
