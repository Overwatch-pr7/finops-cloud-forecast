import pandas as pd
from prophet import Prophet

def generate_forecast(df, periods=60):
    """
    Trains a Meta Prophet model on the provided historical data and 
    generates a forecast for future dates.
    
    Args:
        df (pd.DataFrame): The input dataframe containing historical data.
                           Must contain at least two columns: 'ds' (datestamp) and 'y' (target metric).
        periods (int): The number of days to forecast into the future. Defaults to 60.
        
    Returns:
        pd.DataFrame: The forecast dataframe containing predicted values ('yhat') 
                      and confidence intervals ('yhat_lower', 'yhat_upper').
    """
    if df is None or df.empty:
        print("Error: Input dataframe is empty or None. Cannot train model.")
        return None
        
    # Initialize the Prophet model
    # We can add custom seasonality later (e.g., weekly seasonality) if needed.
    # By default, Prophet handles weekly and yearly seasonality automatically if there's enough data.
    model = Prophet(
        daily_seasonality=False,
        yearly_seasonality=True,
        weekly_seasonality=True
    )
    
    print(f"Training Prophet model on {len(df)} historical records...")
    model.fit(df)
    
    # Create a dataframe for future dates
    print(f"Generating future dataframe for {periods} days...")
    future_df = model.make_future_dataframe(periods=periods, freq='D')
    
    # Predict the future!
    print("Calculating predictions...")
    forecast = model.predict(future_df)
    
    return forecast

