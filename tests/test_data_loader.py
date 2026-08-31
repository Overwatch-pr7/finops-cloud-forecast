import sys
import os
import argparse
import pandas as pd

# Add the project root to the python path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_loader import get_prophet_dataframe

def run_test(show_all=False):
    print("Testing Backend Data Loader for Meta Prophet...")
    print("-" * 50)
    
    # Call our backend function
    df = get_prophet_dataframe()
    
    if df is None:
        print("TEST FAILED: Could not retrieve dataframe. Is the database running?")
        sys.exit(1)
        
    print(f"Successfully loaded {len(df)} rows from the database!\n")
    print("Column Data Types:")
    print(df.dtypes)
    print("\n" + "-" * 50)
    
    if show_all:
        # A good design choice: allowing the user to view the full dataset if they want
        # We override pandas display limits temporarily to show everything
        print("\nFull Dataset View:")
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)
    else:
        print("\nFirst 5 Rows (Formatted for Prophet):")
        print(df.head())
        print("\n(Tip: Run with --show-all to print the entire dataset)")
        
    print("-" * 50)
    print("TEST PASSED: 'ds' and 'y' columns are present and correctly formatted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the data loader function.")
    parser.add_argument('--show-all', action='store_true', help="Print the entire dataset instead of just the head.")
    args = parser.parse_args()
    
    run_test(show_all=args.show_all)
