import pandas as pd

def calculate_finops_metrics(forecast_df, provisioned_limit=1000.0, price_per_unit=0.05):
    """
    Calculate FinOps metrics based on a provisioned limit and the forecasted usage.
    
    Args:
        forecast_df (pd.DataFrame): The dataframe containing Prophet forecasts (must have 'ds' and 'yhat' columns).
        provisioned_limit (float): The hardcoded provisioned capacity limit (e.g., 1000 GB of RAM).
        price_per_unit (float): The mock cloud pricing tier (e.g., $0.05 per GB).
        
    Returns:
        pd.DataFrame: The dataframe with added FinOps metrics:
                      - 'provisioned_limit': The static limit.
                      - 'delta': (provisioned_limit - yhat) -> Positive means wasted capacity, Negative means shortage.
                      - 'financial_impact': (delta * price_per_unit) -> Dollar amount of wasted spend or shortage cost.
    """
    # Create a copy to avoid SettingWithCopyWarning
    df = forecast_df.copy()
    
    # Add the static provisioned limit
    df['provisioned_limit'] = provisioned_limit
    
    # Calculate the delta (Gap between what's provisioned and what's predicted to be used)
    df['delta'] = df['provisioned_limit'] - df['yhat']
    
    # Calculate the financial impact
    # If delta > 0, we are paying for unused capacity (wasted spend).
    # If delta < 0, we exceed our provisioned limit (projected shortage cost/overage fees).
    df['financial_impact'] = df['delta'] * price_per_unit
    
    return df
