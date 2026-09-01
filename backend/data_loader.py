import psycopg2
import pandas as pd
import warnings
import os

def get_prophet_dataframe(
    db_user="finops_user", 
    db_password="finops_password", 
    db_host=os.environ.get("DB_HOST", "localhost"), 
    db_port="5432", 
    db_name="finops_db",
    target_metric="daily_cost_usd",
    connection_string=None
):
    """
    Connects to the PostgreSQL database, retrieves the cloud billing data,
    and formats it specifically for Meta Prophet.
    
    Meta Prophet requires:
    - 'ds': Datestamp column
    - 'y': The numeric target metric to forecast
    
    Args:
        target_metric (str): The column to forecast. Defaults to 'daily_cost_usd'.
                             Can also be 'cpu_usage_pct' or 'ram_usage_pct'.
    
    Returns:
        pd.DataFrame: A formatted pandas DataFrame ready for Prophet.
    """
    
    # Establish connection to the PostgreSQL database
    try:
        if connection_string:
            conn = psycopg2.connect(connection_string)
        else:
            conn = psycopg2.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                database=db_name
            )
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Please ensure Docker Desktop is running and you have started the database.")
        return None

    # We use a context manager (with) to ensure the connection closes automatically
    with conn:
        # Suppress the pandas UserWarning about using raw SQL connections
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            # Query all data from our table
            query = "SELECT * FROM cloud_billing;"
            df = pd.read_sql_query(query, conn)
        
    # Meta Prophet strict formatting rules:
    # 1. Rename the date column to 'ds'
    # 2. Rename the target metric column to 'y'
    df = df.rename(columns={
        'billing_date': 'ds',
        target_metric: 'y'
    })
    
    # Ensure the 'ds' column is explicitly cast to pandas datetime type
    df['ds'] = pd.to_datetime(df['ds'])
    
    # Optional: we keep the other columns (like cpu/ram usage) in the DataFrame.
    # Prophet can use them as 'extra regressors' if we choose to add them later!
    
    # Sort chronologically just to be safe
    df = df.sort_values(by='ds').reset_index(drop=True)
    
    return df
