# dashboard/pages/7_Anomaly_Detection.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data, detect_anomalies
import pandas as pd
import numpy as np

st.markdown("""
<style>
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #f5576c;
        background: #f5576c15;
    }
    .alert-box h4 {
        margin: 0 0 0.3rem 0;
        color: #f5576c;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🚨 Anomaly Detection</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Automatically identify unusual patterns in your business data</p>', unsafe_allow_html=True)

df = load_data()

col1, col2, col3 = st.columns(3)

with col1:
    anomaly_type = st.selectbox("Detect Anomalies In:", ["Sales", "Profit", "Orders", "Discount"])

with col2:
    threshold = st.slider("Sensitivity (Z-Score Threshold)", 1.5, 3.0, 2.0, 0.1)

with col3:
    time_aggregation = st.selectbox("Time Aggregation:", ["Daily", "Weekly", "Monthly"])

if anomaly_type == "Sales":
    column = 'Sales'
    value_label = 'Sales ($)'
elif anomaly_type == "Profit":
    column = 'Profit'
    value_label = 'Profit ($)'
elif anomaly_type == "Orders":
    column = 'Order ID'
    value_label = 'Number of Orders'
else:
    column = 'Discount'
    value_label = 'Discount (%)'

agg_freq = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}
aggregated = df.set_index('Order Date').resample(agg_freq[time_aggregation]).agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Order ID': 'count',
    'Discount': 'mean'
}).reset_index()

aggregated.columns = ['Date', 'Sales', 'Profit', 'Orders', 'Discount']

anomalies = detect_anomalies(aggregated, column=column, threshold=threshold)

st.markdown("---")
st.markdown(f"### 📊 Anomaly Detection Results for {anomaly_type}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Data Points", f"{len(aggregated):,}")

with col2:
    st.metric("Anomalies Detected", f"{len(anomalies):,}", 
              delta=f"{len(anomalies)/len(aggregated)*100:.1f}%")

with col3:
    if len(anomalies) > 0:
        avg_anomaly = anomalies[column].mean()
        avg_normal = aggregated[~aggregated.index.isin(anomalies.index)][column].mean()
        diff_pct = ((avg_anomaly - avg_normal) / avg_normal * 100) if avg_normal > 0 else 0
        st.metric("Avg Anomaly Value", f"{avg_anomaly:.0f}", 
                  delta=f"{diff_pct:.1f}% vs normal")
    else:
        st.metric("✅ No Anomalies", "Data is clean")

fig = go.Figure()

normal = aggregated[~aggregated.index.isin(anomalies.index)]
fig.add_trace(go.Scatter(x=normal['Date'], y=normal[column],
                         mode='lines+markers', name='Normal Data',
                         line=dict(color='#667eea', width=2),
                         marker=dict(color='#667eea', size=6)))

if len(anomalies) > 0:
    fig.add_trace(go.Scatter(x=anomalies['Date'], y=anomalies[column],
                             mode='markers', name='⚠️ Anomaly',
                             marker=dict(color='#f5576c', size=12, symbol='x'),
                             hovertemplate='<b>Anomaly</b><br>Date: %{x}<br>Value: %{y:,.2f}<extra></extra>'))

fig.update_layout(title=f"{anomaly_type} with Anomalies Detected",
                  xaxis_title="Date",
                  yaxis_title=value_label,
                  height=500,
                  hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

if len(anomalies) > 0:
    st.markdown("---")
    st.markdown("### 🚨 Anomaly Alerts")

    for idx, row in anomalies.head(10).iterrows():
        date = row['Date'].strftime('%Y-%m-%d')
        value = row[column]
        avg = aggregated[column].mean()
        
        if value > avg:
            direction = "↑ High"
        else:
            direction = "↓ Low"
        
        if anomaly_type == "Sales":
            alert = f"🚨 **{direction} Sales Alert:** Sales were **${value:,.2f}** on {date} vs average ${avg:,.2f}"
        elif anomaly_type == "Profit":
            alert = f"🚨 **{direction} Profit Alert:** Profit was **${value:,.2f}** on {date} vs average ${avg:,.2f}"
        elif anomaly_type == "Orders":
            alert = f"🚨 **{direction} Orders Alert:** {value:.0f} orders on {date} vs average {avg:.0f}"
        else:
            alert = f"🚨 **{direction} Discount Alert:** Discount was **{value:.1f}%** on {date} vs average {avg:.1f}%"
        
        st.markdown(f"<div class='alert-box'><h4>⚠️ Alert</h4>{alert}</div>", unsafe_allow_html=True)

    if len(anomalies) > 10:
        st.warning(f"Showing top 10 of {len(anomalies)} anomalies detected")