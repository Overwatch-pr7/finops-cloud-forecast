import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from backend.data_loader import get_prophet_dataframe
from backend.ml_engine import generate_forecast
from backend.finops_calc import calculate_finops_metrics

st.set_page_config(page_title="FinOps Cloud Cost Forecaster", layout="wide")

# ==============================================================================
# ANALYTICS (POSTHOG)
# ==============================================================================
posthog_key = st.secrets.get("POSTHOG_API_KEY")
if posthog_key:
    posthog_snippet = f"""
    <script>
        !function(t,e){{var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){{function g(t,e){{var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){{t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){{var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}},u.people.toString=function(){{return u.toString(1)+".people (stub)"}},o="capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])}},e.__SV=1)}}(document,window.posthog||[]);
        posthog.init('{posthog_key}', {{api_host: 'https://us.i.posthog.com'}})
    </script>
    """
    components.html(posthog_snippet, height=0)

# ==============================================================================
# CACHED DATA FUNCTIONS
# ==============================================================================
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    db_url = st.secrets.get("DATABASE_URL")
    return get_prophet_dataframe(connection_string=db_url)

@st.cache_data(show_spinner=False)
def run_prediction(df, days):
    return generate_forecast(df, periods=days)

# ==============================================================================
# UI COMPONENTS
# ==============================================================================
st.title("FinOps Cloud Cost Forecaster")

# 2. Interactive Sidebar
st.sidebar.header("Configuration")
uploaded_file = st.sidebar.file_uploader("Upload Custom Data (CSV)", type=['csv'], help="CSV must contain 'ds' (Date) and 'y' (Usage) columns.")
forecast_horizon = st.sidebar.slider("Forecast Horizon (Days)", min_value=30, max_value=90, value=60, step=1)
provisioned_limit = st.sidebar.slider("Provisioned Capacity (GB)", min_value=500.0, max_value=2000.0, value=1000.0, step=50.0)
price_per_gb = st.sidebar.number_input("Price per GB ($)", value=0.05, step=0.01)

# 1. Health Status & Data Loading
st.markdown("### System Status")
data_source_name = "Default Mock Data"
df = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        data_source_name = f"Uploaded File: {uploaded_file.name}"
        st.success(f"Custom Data Loaded Successfully: {uploaded_file.name}")
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()
else:
    try:
        df = load_data()
        if df is not None and not df.empty:
            st.success("Database Connected & Default Data Loaded Successfully!")
        else:
            st.error("Database Connected, but no data found.")
            st.stop()
    except Exception as e:
        st.error(f"Database Connection Failed: {e}")
        st.stop()

# Validate columns for Prophet
if 'ds' not in df.columns or 'y' not in df.columns:
    st.error("Data source is missing required columns. Ensure your data has 'ds' (Date) and 'y' (Usage) columns.")
    st.stop()

# ==============================================================================
# ML ENGINE & FINOPS LOGIC
# ==============================================================================
with st.spinner("Running Machine Learning Model..."):
    # Generate Forecast
    full_forecast = run_prediction(df, days=forecast_horizon)
    # The ML Engine returns history + future. We need just the future for FinOps delta.
    future_only = full_forecast.tail(forecast_horizon)
    
    # Calculate FinOps Metrics
    finops_results = calculate_finops_metrics(future_only, provisioned_limit=provisioned_limit, price_per_unit=price_per_gb)

# ==============================================================================
# DASHBOARD VISUALIZATIONS
# ==============================================================================
st.markdown("---")
st.subheader("Cloud Usage vs. Provisioned Capacity")
st.info("**Tip:** If you use the zoom or pan tools, just **double-click** anywhere on the graph to reset the view back to default!")

# Plotly Graph 1: Historical + Forecast vs Limit
fig1 = go.Figure()

# Plot historical actuals
fig1.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines', name='Historical Usage (Actual)', line=dict(color='blue')))

# Plot forecasted trend
fig1.add_trace(go.Scatter(x=full_forecast['ds'], y=full_forecast['yhat'], mode='lines', name='Forecasted Usage', line=dict(color='orange', dash='dash')))

# Plot provisioned limit
fig1.add_trace(go.Scatter(x=full_forecast['ds'], y=[provisioned_limit]*len(full_forecast), mode='lines', name='Provisioned Limit', line=dict(color='red')))

fig1.update_layout(title=f"Cloud Usage Forecast ({data_source_name})", xaxis_title="Date", yaxis_title="Usage (GB)")
st.plotly_chart(fig1, use_container_width=True)


# Financial Impact Summary
total_wasted_capacity = finops_results[finops_results['delta'] > 0]['delta'].sum()
total_shortage = abs(finops_results[finops_results['delta'] < 0]['delta'].sum())

total_wasted_spend = finops_results[finops_results['financial_impact'] > 0]['financial_impact'].sum()
total_shortage_cost = abs(finops_results[finops_results['financial_impact'] < 0]['financial_impact'].sum())

col1, col2 = st.columns(2)
with col1:
    st.metric(label=f"Total Wasted Spend (Next {forecast_horizon} Days)", value=f"${total_wasted_spend:,.2f}")
with col2:
    st.metric(label=f"Projected Shortage Cost (Next {forecast_horizon} Days)", value=f"${total_shortage_cost:,.2f}")

st.markdown("---")
st.subheader("Wasted Capacity / Shortage Over Time (Delta)")

# Plotly Graph 2: Delta
fig2 = go.Figure()
# Color delta green if it's positive (wasted capacity) and red if it's negative (shortage)
colors = ['green' if val > 0 else 'red' for val in finops_results['delta']]

fig2.add_trace(go.Bar(
    x=finops_results['ds'], 
    y=finops_results['delta'], 
    marker_color=colors,
    name='Delta (Capacity)'
))
fig2.update_layout(title="Daily Capacity Delta (Provisioned - Predicted)", xaxis_title="Date", yaxis_title="Delta (GB)")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("### Raw FinOps Data")
st.dataframe(finops_results[['ds', 'yhat', 'provisioned_limit', 'delta', 'financial_impact']])
