# dashboard/pages/3_Customer_Segmentation.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data, get_customer_segments
import pandas as pd
import numpy as np

st.markdown("""
<style>
    .segment-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        text-align: center;
        color: white;
    }
    .vip { background: linear-gradient(135deg, #f093fb, #f5576c); }
    .loyal { background: linear-gradient(135deg, #4facfe, #00f2fe); }
    .at-risk { background: linear-gradient(135deg, #f6d365, #fda085); }
    .lost { background: linear-gradient(135deg, #a8c0ff, #3f2b96); }
    .active { background: linear-gradient(135deg, #89f7fe, #66a6ff); }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">👥 Customer Segmentation (RFM Analysis)</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Identify and understand different customer segments for targeted marketing</p>', unsafe_allow_html=True)

df = load_data()
rfm = get_customer_segments(df)

st.subheader("📊 Customer Segment Distribution")

segment_counts = rfm['Segment'].value_counts()

col1, col2, col3, col4, col5 = st.columns(5)

segment_colors = {
    'VIP Customer': '#f5576c',
    'Loyal Customer': '#4facfe',
    'Active Customer': '#66a6ff',
    'At-Risk Customer': '#fda085',
    'Lost Customer': '#3f2b96'
}

for idx, (segment, count) in enumerate(segment_counts.items()):
    with [col1, col2, col3, col4, col5][idx]:
        st.markdown(f"""
        <div class='segment-card {segment.lower().replace(' ', '-')}'>
            <div style='font-size: 1.5rem; font-weight: 700;'>{count}</div>
            <div style='font-size: 0.8rem;'>{segment}</div>
        </div>
        """, unsafe_allow_html=True)

st.subheader("📈 RFM Score Distribution")

rfm_heatmap = rfm.groupby(['R_Score', 'F_Score']).size().unstack(fill_value=0)
fig = px.imshow(rfm_heatmap, 
                title="RFM Heatmap (Recency vs Frequency)",
                labels=dict(x="Frequency Score", y="Recency Score", color="Customers"),
                color_continuous_scale='Viridis')
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

st.subheader("💎 Segment Details")

col1, col2 = st.columns(2)

with col1:
    segment_metrics = rfm.groupby('Segment').agg({
        'Monetary': ['mean', 'sum'],
        'Frequency': 'mean',
        'Recency': 'mean'
    }).round(2)
    
    segment_metrics.columns = ['Avg Spend', 'Total Spend', 'Avg Frequency', 'Avg Recency']
    st.dataframe(segment_metrics.style.format({
        'Avg Spend': '${:,.2f}',
        'Total Spend': '${:,.2f}',
        'Avg Frequency': '{:.1f}',
        'Avg Recency': '{:.0f} days'
    }), use_container_width=True)

with col2:
    st.subheader("💰 Customer Lifetime Value (CLV)")
    clv_by_segment = rfm.groupby('Segment')['Customer Lifetime Value'].mean().sort_values(ascending=False)
    
    fig = px.bar(clv_by_segment, 
                 x=clv_by_segment.index, 
                 y='Customer Lifetime Value',
                 title="Average CLV by Segment",
                 color=clv_by_segment.values,
                 color_continuous_scale='Viridis')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🏆 Top 10 VIP Customers")
top_customers = rfm.nlargest(10, 'Monetary')[['Monetary', 'Frequency', 'Recency', 'Segment', 'Customer Lifetime Value']]

st.dataframe(top_customers.style.format({
    'Monetary': '${:,.2f}',
    'Customer Lifetime Value': '${:,.2f}',
    'Recency': '{:.0f} days'
}), use_container_width=True)

st.subheader("🎯 Segment-Based Recommendations")

recommendations = {
    'VIP Customer': "🎁 Offer exclusive rewards, early access to new products, and personalized service",
    'Loyal Customer': "💝 Implement loyalty program, referral bonuses, and cross-sell opportunities",
    'Active Customer': "📧 Increase engagement with targeted email campaigns and product recommendations",
    'At-Risk Customer': "⚠️ Re-engagement campaigns with special offers and personalized outreach",
    'Lost Customer': "🔄 Reactivation campaigns with win-back offers and survey feedback"
}

for segment, recommendation in recommendations.items():
    if segment in segment_counts.index:
        st.info(f"**{segment}:** {recommendation}")