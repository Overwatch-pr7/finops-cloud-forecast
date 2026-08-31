import sys
import os
import argparse

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_loader import get_prophet_dataframe
from backend.ml_engine import generate_forecast

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
        
    # Step 3: Display results
    print("\n" + "-" * 50)
    print("TEST PASSED: Forecast generated successfully!")
    print(f"\nLast 5 days of the {days}-day future forecast:")
    
    # We select the most relevant columns to show the user
    # 'ds' (Date), 'yhat' (Predicted value), 'yhat_lower' (Lower bound), 'yhat_upper' (Upper bound)
    columns_to_show = ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
    
    # Output to CSV for the user to see the entire future forecast
    output_file = f"forecast_output_{days}_days.csv"
    future_forecast = forecast[columns_to_show].tail(days)
    future_forecast.to_csv(output_file, index=False)
    print(f"Saved the full {days}-day forecast to {output_file} so you can view all rows!")
    
    print("\nPreview of the last 5 days:")
    print(future_forecast.tail())
    print("-" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the ML Prophet engine.")
    parser.add_argument('--days', type=int, default=60, help="Number of future days to forecast (default: 60).")
    args = parser.parse_args()
    
    run_ml_test(days=args.days)
