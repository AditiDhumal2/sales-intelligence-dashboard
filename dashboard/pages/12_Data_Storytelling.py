# dashboard/pages/12_Data_Storytelling.py
import streamlit as st
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data
import pandas as pd

st.markdown("""
<style>
    .story-section {
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .story-section h3 {
        color: #667eea;
        margin-top: 0;
    }
    .key-finding {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .finding-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📖 Data Storytelling</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Key business findings and actionable insights</p>', unsafe_allow_html=True)

df = load_data()

total_sales = df['Sales'].sum()
total_profit = df['Profit'].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

category_analysis = df.groupby('Category').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).reset_index()
category_analysis['Margin'] = (category_analysis['Profit'] / category_analysis['Sales']) * 100

best_category = category_analysis.loc[category_analysis['Profit'].idxmax()]
worst_category = category_analysis.loc[category_analysis['Profit'].idxmin()]

region_analysis = df.groupby('Region').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).reset_index()
region_analysis['Margin'] = (region_analysis['Profit'] / region_analysis['Sales']) * 100

best_region = region_analysis.loc[region_analysis['Sales'].idxmax()]
worst_region = region_analysis.loc[region_analysis['Sales'].idxmin()]

if 'Segment' in df.columns:
    segment_counts = df['Segment'].value_counts()
else:
    segment_counts = None

top_product = df.groupby('Product Name')['Profit'].sum().idxmax() if len(df) > 0 else "N/A"

st.markdown("### 🎯 Executive Summary")

st.markdown(f"""
<div class='story-section'>
    <h3>📊 Business Overview</h3>
    <p>
        Our business generated <strong>${total_sales:,.2f}</strong> in revenue with 
        <strong>${total_profit:,.2f}</strong> in profit, achieving a <strong>{profit_margin:.1f}%</strong> 
        profit margin. The customer base consists of <strong>{df['Customer ID'].nunique():,}</strong> 
        customers who placed <strong>{df['Order ID'].nunique():,}</strong> orders.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📈 Key Business Findings")

st.markdown(f"""
<div class='key-finding'>
    <span class='finding-number'>1</span>
    <strong>Category Performance:</strong>
    <br>{best_category['Category']} category drives most profit with <strong>${best_category['Profit']:,.2f}</strong> 
    and a {best_category['Margin']:.1f}% margin. {worst_category['Category']} category has lower margins at 
    {worst_category['Margin']:.1f}% and requires strategic review.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='key-finding'>
    <span class='finding-number'>2</span>
    <strong>Regional Performance:</strong>
    <br>{best_region['Region']} region leads with <strong>${best_region['Sales']:,.2f}</strong> in sales 
    and {best_region['Margin']:.1f}% margin.
</div>
""", unsafe_allow_html=True)

if segment_counts is not None:
    st.markdown(f"""
    <div class='key-finding'>
        <span class='finding-number'>3</span>
        <strong>Customer Insights:</strong>
        <br>{segment_counts.index[0]} segment represents the largest customer group with {segment_counts.iloc[0]:,} customers.
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class='key-finding'>
    <span class='finding-number'>4</span>
    <strong>Product Performance:</strong>
    <br>Top product: <strong>{top_product[:50]}</strong> generates significant profit. 
    Average order value is <strong>${df['Sales'].sum() / df['Order ID'].nunique():,.2f}</strong>.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='key-finding'>
    <span class='finding-number'>5</span>
    <strong>Profitability Analysis:</strong>
    <br>Overall profit margin is {profit_margin:.1f}%. 
    {f'Healthy margins indicate strong business performance.' if profit_margin > 20 else 'Opportunity exists to improve margins.'}
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📊 Visual Summary")

col1, col2 = st.columns(2)

with col1:
    fig = px.pie(category_analysis, values='Profit', names='Category', 
                 title="Profit Distribution by Category", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(region_analysis, x='Region', y='Sales', 
                title="Sales by Region", color='Region')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 💡 Strategic Recommendations")

recommendations = [
    f"📌 **Category Strategy:** Focus resources on {best_category['Category']} category",
    f"📌 **Regional Expansion:** Apply successful {best_region['Region']} region strategies to other regions",
    f"📌 **Customer Retention:** {'Launch retention campaign' if segment_counts and segment_counts.get('At-Risk Customer', 0) > 0 else 'Continue building customer loyalty'}",
    f"📌 **Product Portfolio:** Optimize product mix - focus on high-margin products",
    f"📌 **Pricing Optimization:** {'Maintain current pricing strategy' if profit_margin > 20 else 'Review pricing for margin improvement'}"
]

for rec in recommendations:
    st.info(rec)

st.markdown("---")
st.markdown("### 🎯 Conclusion")

st.markdown("""
<div class='story-section'>
    <p>
    This analysis reveals a business with <strong>strong revenue</strong> and <strong>healthy profit margins</strong>, 
    driven primarily by <strong>technology products</strong> in the <strong>West region</strong>. 
    The customer base is diverse with significant opportunities for <strong>targeted marketing</strong> and 
    <strong>retention strategies</strong>.
    </p>
    <p style='margin-top: 1rem; color: #667eea; font-weight: 600;'>
    💡 Key Takeaway: Data-driven decisions lead to better business outcomes.
    </p>
</div>
""", unsafe_allow_html=True)