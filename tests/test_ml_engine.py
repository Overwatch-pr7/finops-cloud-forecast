import sys
import os
import argparse

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_loader import get_prophet_dataframe
from backend.ml_engine import generate_forecast
from backend.finops_calc import calculate_finops_metrics

def run_ml_test(days=60):
    print("Testing ML Engine with Meta Prophet...")
    print("-" * 50)
    
    # Step 1: Load the formatted data from PostgreSQL
    print("Step 1: Loading Data")
    df = get_prophet_dataframe()
    if df is None:
        print("TEST FAILED: Data load failed. Is the database running?")
        sys.exit(1)
        
    # Step 2: Generate the forecast
    print("\nStep 2: Training and Forecasting")
    forecast = generate_forecast(df, periods=days)
    
    if forecast is None:
        print("TEST FAILED: Forecasting returned None.")
        sys.exit(1)
        
    # Step 3: Calculate FinOps Metrics
    print("\nStep 3: Calculating FinOps Metrics (Wasted Spend vs Shortage)")
    # We will pass only the future predictions (the last `days` rows) to the financial calculator
    future_forecast = forecast.tail(days)
    finops_results = calculate_finops_metrics(future_forecast, provisioned_limit=1000.0, price_per_unit=0.05)
    
    # Step 4: Display and Save Results
    print("\n" + "-" * 50)
    print("TEST PASSED: Forecast and FinOps metrics generated successfully!")
    
    # Define columns to save
    prophet_columns = ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
    finops_columns = ['ds', 'yhat', 'provisioned_limit', 'delta', 'financial_impact']
    
    # Output paths inside the data/ folder
    base_forecast_file = "data/trend_forecast.csv"
    delta_forecast_file = "data/trend_forecast_with_delta.csv"
    
    # Save the files
    future_forecast[prophet_columns].to_csv(base_forecast_file, index=False)
    finops_results[finops_columns].to_csv(delta_forecast_file, index=False)
    
    print(f"Saved the Prophet forecast to {base_forecast_file}")
    print(f"Saved the FinOps forecast to {delta_forecast_file}")
    
    print("\nPreview of the last 5 days (FinOps Metrics):")
    print(finops_results[finops_columns].tail())
    print("-" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the ML Prophet engine.")
    parser.add_argument('--days', type=int, default=60, help="Number of future days to forecast (default: 60).")
    args = parser.parse_args()
    
    run_ml_test(days=args.days)
