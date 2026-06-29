# dashboard/pages/5_AI_Business_Insights.py
import streamlit as st
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data
import pandas as pd
import numpy as np

st.markdown("""
<style>
    .insight-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.2rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .alert-card {
        background: linear-gradient(135deg, #f093fb15 0%, #f5576c15 100%);
        padding: 1.2rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #f5576c;
    }
    .success-card {
        background: linear-gradient(135deg, #4facfe15 0%, #00f2fe15 100%);
        padding: 1.2rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4facfe;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🤖 AI Business Insights</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Automatically generated business intelligence from your data</p>', unsafe_allow_html=True)

df = load_data()

total_sales = df['Sales'].sum()
total_profit = df['Profit'].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

category_analysis = df.groupby('Category').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).reset_index()
category_analysis['Profit_Margin'] = (category_analysis['Profit'] / category_analysis['Sales']) * 100

best_category = category_analysis.loc[category_analysis['Profit'].idxmax()]
worst_category = category_analysis.loc[category_analysis['Profit'].idxmin()]

region_analysis = df.groupby('Region').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).reset_index()
best_region = region_analysis.loc[region_analysis['Sales'].idxmax()]
worst_region = region_analysis.loc[region_analysis['Sales'].idxmin()]

monthly = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
monthly.columns = ['Month', 'Sales']
if len(monthly) >= 2:
    growth = ((monthly['Sales'].iloc[-1] - monthly['Sales'].iloc[-2]) / monthly['Sales'].iloc[-2]) * 100
else:
    growth = 0

product_profit = df.groupby('Product Name')['Profit'].sum()
top_product = product_profit.idxmax() if len(product_profit) > 0 else "N/A"
worst_product = product_profit.idxmin() if len(product_profit) > 0 else "N/A"

if 'Segment' in df.columns:
    segment_counts = df['Segment'].value_counts()
    top_segment = segment_counts.index[0] if len(segment_counts) > 0 else "N/A"
    at_risk_segment = segment_counts.get('At-Risk Customer', 0)
else:
    top_segment = "N/A"
    at_risk_segment = 0

st.markdown("### 🎯 Key Business Insights")

if growth > 0:
    st.markdown(f"""
    <div class='success-card'>
        <strong>📈 Revenue Growth:</strong> Revenue increased by <strong>{growth:.1f}%</strong> this month, 
        driven primarily by <strong>{best_category['Category']}</strong> products in the <strong>{best_region['Region']}</strong> region.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class='alert-card'>
        <strong>📉 Revenue Decline:</strong> Revenue decreased by <strong>{abs(growth):.1f}%</strong> this month. 
        Consider reviewing pricing strategy for <strong>{worst_category['Category']}</strong> products.
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class='insight-card'>
    <strong>📦 Category Performance:</strong>
    <br><strong>{best_category['Category']}</strong> drives most profit (${best_category['Profit']:,.2f}) with 
    <strong>{best_category['Profit_Margin']:.1f}%</strong> margin.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='insight-card'>
    <strong>📍 Regional Performance:</strong>
    <br><strong>{best_region['Region']}</strong> contributes <strong>{(best_region['Sales']/total_sales*100):.1f}%</strong> 
    of revenue with <strong>{(best_region['Profit']/total_profit*100):.1f}%</strong> of profit.
</div>
""", unsafe_allow_html=True)

if at_risk_segment > 0:
    st.markdown(f"""
    <div class='alert-card'>
        <strong>⚠️ Customer Risk Alert:</strong>
        <br><strong>{at_risk_segment}</strong> customers are at risk of churning. 
        Recommend immediate retention campaign.
    </div>
    """, unsafe_allow_html=True)

if profit_margin > 20:
    st.markdown(f"""
    <div class='success-card'>
        <strong>✅ Strong Profitability:</strong> Overall profit margin is <strong>{profit_margin:.1f}%</strong>, 
        well above industry average.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class='alert-card'>
        <strong>⚠️ Margin Improvement Needed:</strong> Profit margin is <strong>{profit_margin:.1f}%</strong>, 
        below target. Review discounts and costs.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("🎯 Executive Recommendations")

recommendations = [
    f"📌 **Priority 1:** Focus marketing efforts on {best_category['Category']} category - it's your profit engine",
    f"📌 **Priority 2:** Investigate {worst_category['Category']} category - margins are below acceptable levels",
    f"📌 **Priority 3:** Expand successful strategies from {best_region['Region']} region to underperforming regions",
    f"📌 **Priority 4:** {'Launch retention campaign for at-risk customers' if at_risk_segment > 0 else 'Continue building customer loyalty programs'}",
    f"📌 **Priority 5:** {'Optimize discount strategy for low-margin products' if profit_margin < 20 else 'Maintain current pricing strategy'}"
]

for rec in recommendations:
    st.info(rec)