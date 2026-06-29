# dashboard/pages/9_Product_Performance.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data
import pandas as pd

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📦 Product Performance Analytics</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Track and analyze product performance</p>', unsafe_allow_html=True)

df = load_data()

col1, col2, col3 = st.columns(3)

with col1:
    categories = ['All'] + sorted(df['Category'].unique())
    selected_category = st.selectbox("Category", categories)

with col2:
    if selected_category != 'All':
        subcategories = ['All'] + sorted(df[df['Category'] == selected_category]['Sub-Category'].unique())
    else:
        subcategories = ['All'] + sorted(df['Sub-Category'].unique())
    selected_subcategory = st.selectbox("Sub-Category", subcategories)

with col3:
    sort_by = st.selectbox("Sort By", ["Sales", "Profit", "Margin", "Quantity"])

filtered_df = df.copy()
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]
if selected_subcategory != 'All':
    filtered_df = filtered_df[filtered_df['Sub-Category'] == selected_subcategory]

product_metrics = filtered_df.groupby('Product Name').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Quantity': 'sum' if 'Quantity' in df.columns else 'count'
}).reset_index()

if 'Quantity' not in df.columns:
    product_metrics['Quantity'] = filtered_df.groupby('Product Name').size().values

product_metrics['Margin'] = (product_metrics['Profit'] / product_metrics['Sales']) * 100
product_metrics['Avg_Price'] = product_metrics['Sales'] / product_metrics['Quantity']
product_metrics = product_metrics.sort_values(sort_by, ascending=False)

st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_products = len(product_metrics)
    st.metric("Total Products", f"{total_products:,}")

with col2:
    st.metric("Total Sales", f"${product_metrics['Sales'].sum():,.0f}")

with col3:
    st.metric("Total Profit", f"${product_metrics['Profit'].sum():,.0f}")

with col4:
    avg_margin = product_metrics['Margin'].mean()
    st.metric("Avg Margin", f"{avg_margin:.1f}%")

st.markdown("---")
st.subheader("🏆 Product Rankings")

tab1, tab2, tab3, tab4 = st.tabs(["Top Sales", "Top Profit", "Top Margin", "Slow Movers"])

with tab1:
    top_sales = product_metrics.nlargest(10, 'Sales')[['Product Name', 'Sales', 'Profit', 'Margin']]
    fig = px.bar(top_sales, x='Sales', y='Product Name', orientation='h',
                title="Top 10 Products by Sales",
                color='Profit', color_continuous_scale='Viridis')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_sales.style.format({
        'Sales': '${:,.2f}',
        'Profit': '${:,.2f}',
        'Margin': '{:.1f}%'
    }), use_container_width=True)

with tab2:
    top_profit = product_metrics.nlargest(10, 'Profit')[['Product Name', 'Profit', 'Sales', 'Margin']]
    fig = px.bar(top_profit, x='Profit', y='Product Name', orientation='h',
                title="Top 10 Products by Profit",
                color='Margin', color_continuous_scale='Viridis')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_profit.style.format({
        'Profit': '${:,.2f}',
        'Sales': '${:,.2f}',
        'Margin': '{:.1f}%'
    }), use_container_width=True)

with tab3:
    top_margin = product_metrics.nlargest(10, 'Margin')[['Product Name', 'Margin', 'Sales', 'Profit']]
    fig = px.bar(top_margin, x='Margin', y='Product Name', orientation='h',
                title="Top 10 Products by Margin",
                color='Profit', color_continuous_scale='Viridis')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_margin.style.format({
        'Margin': '{:.1f}%',
        'Sales': '${:,.2f}',
        'Profit': '${:,.2f}'
    }), use_container_width=True)

with tab4:
    slow_movers = product_metrics.nsmallest(10, 'Quantity')[['Product Name', 'Quantity', 'Sales', 'Profit']]
    fig = px.bar(slow_movers, x='Quantity', y='Product Name', orientation='h',
                title="Slow Moving Products (By Quantity)",
                color='Sales', color_continuous_scale='Reds')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(slow_movers.style.format({
        'Sales': '${:,.2f}',
        'Profit': '${:,.2f}'
    }), use_container_width=True)

st.markdown("---")
st.subheader("📊 Product Performance Matrix")

fig = px.scatter(product_metrics, x='Sales', y='Profit', 
                size='Quantity', hover_name='Product Name',
                color='Margin', color_continuous_scale='Viridis',
                title="Product Performance Matrix (Sales vs Profit)",
                labels={'Sales': 'Sales ($)', 'Profit': 'Profit ($)'})
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)