# FinOps Cloud Cost Forecaster

This project uses Machine Learning (Meta Prophet) to predict future cloud computing costs based on historical logs, and calculates the financial impact of under-provisioned or over-provisioned cloud resources. 

The architecture is built on PostgreSQL, Python, and features an interactive Streamlit dashboard deployed on the cloud.

---

## 🏗️ Project Architecture & Phases

### Phase 1: Project Setup & Structure
We established the base architecture for a scalable, containerized microservices application.
* **`requirements.txt`**: Specifies the Python dependencies for the ML engine, leaning on Conda for heavy C++ reliant libraries like Prophet.
* **`docker-compose.yml`**: The orchestration file that manages the PostgreSQL database container and the ML engine container, linking them via an internal network.

### Phase 2: Database Initialization
We set up a robust PostgreSQL database to store historical cloud computing cost records.
* **`db/init_schema.sql`**: A SQL script that automatically runs when the database container starts. It creates the schema for cloud logs and generates 365 days of mock historical cloud cost data.
* **`data/`**: A persistent volume mapping that ensures the database survives container restarts.

### Phase 3: Machine Learning Engine
We implemented Meta Prophet to learn seasonality (e.g. costs drop on weekends) and forecast future usage.
* **`Dockerfile`**: A custom Linux image based on Miniconda. It resolves complex C++ compilation bugs by fetching pre-compiled binaries for Prophet and Numpy directly from Conda Forge.
* **`backend/data_loader.py`**: Connects to the PostgreSQL database, queries the historical data, and formats it strictly to meet Meta Prophet's dataframe requirements (`ds` for dates, `y` for target metric).
* **`backend/ml_engine.py`**: Initializes the Prophet model, fits it to the historical data, and generates an array of future predictions (default 60 days).

### Phase 4: FinOps Cloud Logic
We established a baseline for cloud provisioning to calculate actionable financial metrics.
* **`backend/finops_calc.py`**: Compares the ML model's forecasted usage against a hardcoded "Provisioned Capacity" limit. It calculates the delta to identify wasted capacity or shortages, and multiplies that by a mock pricing tier to project the exact dollar amount of wasted spend or overage fees.
* **`tests/test_ml_engine.py`**: The main testing script that orchestrates the entire pipeline from DB loading, to forecasting, to FinOps calculations. It outputs the final metrics to a CSV file (`finops_forecast_output_60_days.csv`).

### Phase 5: Streamlit FinOps Dashboard
We built a monolithic, interactive web application using Streamlit to visualize the backend ML processes.
* **`app.py`**: The main frontend application. It features an interactive sidebar to dynamically adjust the Forecast Horizon, Provisioned Capacity, and Pricing. It also allows users to upload custom CSV data (bypassing the database) and uses Plotly to render beautiful interactive graphs of the FinOps predictions.

### Phase 6: Cloud Deployment & Web Analytics
We migrated the application from a local Docker environment to a fully managed cloud ecosystem.
* **`scripts/seed_neon_db.py`**: A utility script used to migrate our mock CSV data into a remote serverless Neon.tech PostgreSQL database.
* **`packages.txt` & `requirements.txt`**: Configured specifically for Streamlit Community Cloud (Debian) to ensure the C++ dependencies for Prophet compile successfully on the cloud servers.
* **`.streamlit/secrets.toml`**: Implemented a secure secrets manager to protect the Neon Database URI and the **PostHog** API keys used for web analytics tracking.

---

*Inspired by the FinOps Foundation's Cloud Cost Forecasting guidelines: https://www.finops.org/wg/cloud-cost-forecasting/*
