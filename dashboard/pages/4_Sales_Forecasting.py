# dashboard/pages/4_Sales_Forecasting.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data
import pandas as pd
import numpy as np
from datetime import timedelta

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🔮 Sales Forecasting</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Predict future sales with confidence intervals</p>', unsafe_allow_html=True)

df = load_data()

daily_sales = df.groupby('Order Date')['Sales'].sum().reset_index()
daily_sales = daily_sales.set_index('Order Date').resample('D').sum().fillna(0).reset_index()
daily_sales.columns = ['Date', 'Sales']

daily_sales['MA7'] = daily_sales['Sales'].rolling(window=7).mean()
daily_sales['MA30'] = daily_sales['Sales'].rolling(window=30).mean()

st.subheader("📊 Historical Sales with Moving Averages")

fig = go.Figure()
fig.add_trace(go.Scatter(x=daily_sales['Date'], y=daily_sales['Sales'], 
                         mode='lines', name='Actual Sales', 
                         line=dict(color='gray', width=1)))
fig.add_trace(go.Scatter(x=daily_sales['Date'], y=daily_sales['MA7'], 
                         mode='lines', name='7-Day MA', 
                         line=dict(color='#667eea', width=2)))
fig.add_trace(go.Scatter(x=daily_sales['Date'], y=daily_sales['MA30'], 
                         mode='lines', name='30-Day MA', 
                         line=dict(color='#764ba2', width=2)))

fig.update_layout(title="Sales Trend with Moving Averages",
                  xaxis_title="Date",
                  yaxis_title="Sales ($)",
                  height=400,
                  hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("📈 30-Day Sales Forecast")

col1, col2, col3 = st.columns(3)

with col1:
    forecast_days = st.slider("Forecast Days", 7, 90, 30)

with col2:
    confidence_interval = st.slider("Confidence Interval", 80, 99, 95) / 100

with col3:
    seasonality = st.selectbox("Seasonality", ["Daily", "Weekly", "Monthly"])

last_date = daily_sales['Date'].max()
recent_30_avg = daily_sales['Sales'].tail(30).mean()
recent_7_avg = daily_sales['Sales'].tail(7).mean()
growth_rate = (recent_7_avg / recent_30_avg - 1) if recent_30_avg > 0 else 0

forecast_dates = [last_date + timedelta(days=x) for x in range(1, forecast_days + 1)]
base_forecast = recent_7_avg * (1 + growth_rate * np.arange(1, forecast_days + 1) / 30)

if seasonality == "Weekly":
    seasonal_pattern = 1 + 0.2 * np.sin(np.arange(forecast_days) * 2 * np.pi / 7)
elif seasonality == "Monthly":
    seasonal_pattern = 1 + 0.15 * np.sin(np.arange(forecast_days) * 2 * np.pi / 30)
else:
    seasonal_pattern = 1 + 0.05 * np.sin(np.arange(forecast_days) * 2 * np.pi / 1)

forecast_values = base_forecast * seasonal_pattern

z_score = {0.80: 1.28, 0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
z = z_score.get(confidence_interval, 1.96)
std_dev = daily_sales['Sales'].tail(30).std()

forecast_upper = forecast_values + z * std_dev
forecast_lower = forecast_values - z * std_dev

forecast_df = pd.DataFrame({
    'Date': forecast_dates,
    'Forecast': forecast_values,
    'Upper': forecast_upper,
    'Lower': forecast_lower
})

fig = go.Figure()
fig.add_trace(go.Scatter(x=daily_sales['Date'], y=daily_sales['Sales'],
                         mode='lines', name='Historical',
                         line=dict(color='#667eea', width=2)))
fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecast'],
                         mode='lines+markers', name='Forecast',
                         line=dict(color='#f5576c', width=3, dash='dash')))
fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Upper'],
                         mode='lines', name=f'Upper ({confidence_interval*100:.0f}%)',
                         line=dict(color='rgba(245,87,108,0.3)', width=0),
                         showlegend=False))
fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Lower'],
                         mode='lines', name=f'Lower ({confidence_interval*100:.0f}%)',
                         fill='tonexty',
                         line=dict(color='rgba(245,87,108,0.3)', width=0),
                         fillcolor='rgba(245,87,108,0.2)'))

fig.update_layout(title=f"{forecast_days}-Day Sales Forecast with {confidence_interval*100:.0f}% Confidence",
                  xaxis_title="Date",
                  yaxis_title="Sales ($)",
                  height=500,
                  hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Forecast Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_forecast = forecast_values.sum()
    st.metric("Total Forecasted", f"${total_forecast:,.0f}")

with col2:
    avg_daily = forecast_values.mean()
    st.metric("Avg Daily Forecast", f"${avg_daily:,.0f}")

with col3:
    max_forecast = forecast_values.max()
    st.metric("Peak Day", f"${max_forecast:,.0f}")

with col4:
    growth_pct = ((forecast_values[-1] / forecast_values[0] - 1) * 100)
    st.metric("Growth Trend", f"{growth_pct:.1f}%")