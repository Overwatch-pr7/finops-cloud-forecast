import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
import os

import streamlit as st

# Load Neon Connection String from Streamlit Secrets
NEON_CONN_STR = st.secrets.get("DATABASE_URL")

def seed_database():
    if not NEON_CONN_STR:
        print("❌ Error: DATABASE_URL not found in .streamlit/secrets.toml")
        return
    
    try:
        print("Connecting to Neon Database...")
        conn = psycopg2.connect(NEON_CONN_STR)
        cursor = conn.cursor()

        print("Dropping old table if exists...")
        cursor.execute("DROP TABLE IF EXISTS cloud_billing;")
        
        print("Creating cloud_billing table...")
        cursor.execute("""
            CREATE TABLE cloud_billing (
                billing_date DATE PRIMARY KEY, 
                cpu_usage_pct NUMERIC(5, 2),
                ram_usage_pct NUMERIC(5, 2),
                daily_cost_usd NUMERIC(10, 2)
            );
        """)

        print("Reading CSV data...")
        df = pd.read_csv("data/cloud_billing_dataset.csv")
        
        # Convert DD-MM-YYYY to YYYY-MM-DD for PostgreSQL
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y').dt.strftime('%Y-%m-%d')
        
        # Prepare data for bulk insert
        records = df.to_records(index=False)
        values = list(records)

        print("Inserting records into Neon database...")
        insert_query = """
            INSERT INTO cloud_billing (billing_date, cpu_usage_pct, ram_usage_pct, daily_cost_usd) 
            VALUES %s
        """
        execute_values(cursor, insert_query, values)
        
        conn.commit()
        print("✅ Successfully seeded the Neon database with 365 records!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    seed_database()
