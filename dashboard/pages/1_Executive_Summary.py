# dashboard/pages/1_Executive_Summary.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data, load_summary, calculate_growth
import pandas as pd

st.markdown("""
<style>
    .ai-summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .ai-summary h3 {
        margin: 0 0 0.5rem 0;
    }
    .ai-summary p {
        margin: 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📊 Executive Summary</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Real-time business performance snapshot</p>', unsafe_allow_html=True)

df = load_data()
summary = load_summary()

total_revenue = df['Sales'].sum()
total_profit = df['Profit'].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
total_customers = df['Customer ID'].nunique()
total_orders = df['Order ID'].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
growth_rate = calculate_growth(df)

# AI Summary
st.markdown(f"""
<div class='ai-summary'>
    <h3>🤖 AI-Generated Executive Summary</h3>
    <p>
        Revenue is <strong>${total_revenue:,.2f}</strong> with a <strong>{profit_margin:.1f}%</strong> profit margin.
        {'📈 Revenue increased ' + f'{growth_rate:.1f}%' + ' this month, driven primarily by technology products.' if growth_rate > 0 else '📉 Revenue decreased slightly this month.'}
        Customer base stands at <strong>{total_customers:,}</strong> with average order value of <strong>${avg_order_value:,.2f}</strong>.
    </p>
</div>
""", unsafe_allow_html=True)

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Total Revenue", f"${total_revenue:,.0f}", delta=f"{growth_rate:.1f}%" if growth_rate != 0 else None)

with col2:
    st.metric("💵 Total Profit", f"${total_profit:,.0f}", delta=f"{profit_margin:.1f}% margin")

with col3:
    st.metric("👥 Customers", f"{total_customers:,}", delta=f"{total_orders:,} orders")

with col4:
    st.metric("📊 Avg Order Value", f"${avg_order_value:,.0f}")

col5, col6, col7, col8 = st.columns(4)

with col5:
    profitable_orders = (df['Profit'] > 0).sum()
    profit_pct = (profitable_orders / len(df) * 100)
    st.metric("✅ Profitable Orders", f"{profit_pct:.1f}%")

with col6:
    unique_products = df['Product ID'].nunique()
    st.metric("📦 Products Sold", f"{unique_products:,}")

with col7:
    top_region = df.groupby('Region')['Sales'].sum().idxmax()
    st.metric("🏆 Best Region", top_region)

with col8:
    top_category = df.groupby('Category')['Profit'].sum().idxmax()
    st.metric("🏆 Best Category", top_category)

# Charts
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Monthly Sales Trend")
    monthly_sales = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    monthly_sales['Order Date'] = monthly_sales['Order Date'].astype(str)
    
    fig = px.line(monthly_sales, x='Order Date', y='Sales', title="Sales Performance Over Time", markers=True)
    fig.update_layout(height=400, showlegend=False)
    fig.update_traces(line=dict(color='#667eea', width=3))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💰 Profit by Category")
    category_profit = df.groupby('Category')['Profit'].sum().sort_values(ascending=True)
    
    fig = px.bar(category_profit, x='Profit', y=category_profit.index,
                 orientation='h', title="Category Profitability",
                 color=category_profit.values, color_continuous_scale='Viridis')
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)