# dashboard/pages/2_Drill_Down_Analysis.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data
import pandas as pd

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🔍 Interactive Drill-Down Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Explore data at different levels of granularity</p>', unsafe_allow_html=True)

df = load_data()

# Time Drill-Down
st.markdown("### 📅 Time Drill-Down")

col1, col2, col3 = st.columns(3)

with col1:
    years = ['All'] + sorted(df['Year'].unique())
    selected_year = st.selectbox("Year", years, key="year_drill")

with col2:
    if selected_year != 'All':
        quarters = ['All'] + sorted(df[df['Year'] == selected_year]['Quarter'].unique())
    else:
        quarters = ['All'] + sorted(df['Quarter'].unique())
    selected_quarter = st.selectbox("Quarter", quarters, key="quarter_drill")

with col3:
    if selected_year != 'All' and selected_quarter != 'All':
        months = ['All'] + sorted(df[(df['Year'] == selected_year) & (df['Quarter'] == selected_quarter)]['Month'].unique())
    elif selected_year != 'All':
        months = ['All'] + sorted(df[df['Year'] == selected_year]['Month'].unique())
    else:
        months = ['All'] + sorted(df['Month'].unique())
    selected_month = st.selectbox("Month", months, key="month_drill")

# Apply time filters
filtered_df = df.copy()
if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['Year'] == selected_year]
if selected_quarter != 'All':
    filtered_df = filtered_df[filtered_df['Quarter'] == selected_quarter]
if selected_month != 'All':
    filtered_df = filtered_df[filtered_df['Month'] == selected_month]

# Geography Drill-Down
st.markdown("### 🌍 Geography Drill-Down")

col1, col2, col3 = st.columns(3)

with col1:
    regions = ['All'] + sorted(df['Region'].unique())
    selected_region = st.selectbox("Region", regions, key="region_drill")

with col2:
    if selected_region != 'All':
        states = ['All'] + sorted(df[df['Region'] == selected_region]['State'].unique())
    else:
        states = ['All'] + sorted(df['State'].unique())
    selected_state = st.selectbox("State", states, key="state_drill")

with col3:
    if selected_state != 'All':
        cities = ['All'] + sorted(df[df['State'] == selected_state]['City'].unique())
    elif selected_region != 'All':
        cities = ['All'] + sorted(df[df['Region'] == selected_region]['City'].unique())
    else:
        cities = ['All'] + sorted(df['City'].unique())
    selected_city = st.selectbox("City", cities, key="city_drill")

if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
if selected_state != 'All':
    filtered_df = filtered_df[filtered_df['State'] == selected_state]
if selected_city != 'All':
    filtered_df = filtered_df[filtered_df['City'] == selected_city]

# Product Drill-Down
st.markdown("### 📦 Product Drill-Down")

col1, col2, col3 = st.columns(3)

with col1:
    categories = ['All'] + sorted(filtered_df['Category'].unique())
    selected_category = st.selectbox("Category", categories, key="cat_drill")

with col2:
    if selected_category != 'All':
        subcategories = ['All'] + sorted(filtered_df[filtered_df['Category'] == selected_category]['Sub-Category'].unique())
    else:
        subcategories = ['All'] + sorted(filtered_df['Sub-Category'].unique())
    selected_subcategory = st.selectbox("Sub-Category", subcategories, key="subcat_drill")

with col3:
    if selected_subcategory != 'All':
        products = ['All'] + sorted(filtered_df[filtered_df['Sub-Category'] == selected_subcategory]['Product Name'].unique())
    elif selected_category != 'All':
        products = ['All'] + sorted(filtered_df[filtered_df['Category'] == selected_category]['Product Name'].unique())
    else:
        products = ['All'] + sorted(filtered_df['Product Name'].unique())
    selected_product = st.selectbox("Product", products, key="prod_drill")

if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]
if selected_subcategory != 'All':
    filtered_df = filtered_df[filtered_df['Sub-Category'] == selected_subcategory]
if selected_product != 'All':
    filtered_df = filtered_df[filtered_df['Product Name'] == selected_product]

# Results
st.markdown("---")
st.markdown("### 📊 Drill-Down Results")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Sales Performance")
    monthly = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    monthly['Order Date'] = monthly['Order Date'].astype(str)
    fig = px.line(monthly, x='Order Date', y='Sales', markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💵 Profit Analysis")
    plot_data = filtered_df.groupby('Category')['Profit'].sum()
    fig = px.pie(values=plot_data.values, names=plot_data.index, hole=0.3)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(filtered_df.head(100), use_container_width=True)
st.caption(f"Showing {len(filtered_df)} records after drill-down")