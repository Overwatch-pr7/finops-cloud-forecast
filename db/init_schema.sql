-- db/init_schema.sql
-- This script creates the required database schema and ingests the CSV data.

-- We set the datestyle to 'ISO, DMY' because our CSV dates are in DD-MM-YYYY format
-- (e.g., '01-01-2025' for Jan 1st). 
-- If we don't set this, PostgreSQL might confuse the month and the day.
SET datestyle = 'ISO, DMY';

-- Drop the table if it already exists so we can run this script cleanly multiple times
DROP TABLE IF EXISTS cloud_billing;

-- Create the table structure matching our CSV columns
-- We use NUMERIC for decimals to accurately represent percentages and currency
CREATE TABLE cloud_billing (
    -- Primary key can be Date since we have one record per day
    billing_date DATE PRIMARY KEY, 
    cpu_usage_pct NUMERIC(5, 2),
    ram_usage_pct NUMERIC(5, 2),
    daily_cost_usd NUMERIC(10, 2)
);

-- Use the PostgreSQL COPY command to ingest the data directly from the CSV.
-- We are mapping this to the 'cloud_billing' table.
-- DELIMITER ',' indicates a standard CSV.
-- CSV HEADER tells Postgres to skip the first row (the column names).
COPY cloud_billing(billing_date, cpu_usage_pct, ram_usage_pct, daily_cost_usd)
FROM '/data/cloud_billing_dataset.csv'
DELIMITER ','
CSV HEADER;
