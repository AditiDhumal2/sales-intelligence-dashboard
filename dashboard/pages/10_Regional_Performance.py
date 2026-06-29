# dashboard/pages/10_Regional_Performance.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data
import pandas as pd

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🗺️ Regional Performance Intelligence</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Analyze performance across regions</p>', unsafe_allow_html=True)

df = load_data()

regional_metrics = df.groupby('Region').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Order ID': 'count',
    'Customer ID': 'nunique'
}).rename(columns={'Order ID': 'Orders', 'Customer ID': 'Customers'})

regional_metrics['Margin'] = (regional_metrics['Profit'] / regional_metrics['Sales']) * 100
regional_metrics['Avg_Order'] = regional_metrics['Sales'] / regional_metrics['Orders']

st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    best_region_sales = regional_metrics['Sales'].idxmax()
    st.metric("🏆 Best Region (Sales)", best_region_sales)

with col2:
    best_region_profit = regional_metrics['Profit'].idxmax()
    st.metric("🏆 Best Region (Profit)", best_region_profit)

with col3:
    best_region_margin = regional_metrics['Margin'].idxmax()
    st.metric("🏆 Best Region (Margin)", best_region_margin)

with col4:
    total_region_sales = regional_metrics['Sales'].sum()
    st.metric("💰 Total Regional Sales", f"${total_region_sales:,.0f}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Sales by Region")
    fig = px.bar(regional_metrics, x=regional_metrics.index, y='Sales',
                title="Regional Sales Performance",
                color='Sales', color_continuous_scale='Viridis')
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Profit Margin by Region")
    fig = px.bar(regional_metrics, x=regional_metrics.index, y='Margin',
                title="Regional Profit Margins",
                color='Margin', color_continuous_scale='RdYlGn')
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("📊 State Performance Analysis")

state_metrics = df.groupby('State').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).reset_index()

state_metrics['Margin'] = (state_metrics['Profit'] / state_metrics['Sales']) * 100
state_metrics = state_metrics.sort_values('Sales', ascending=False)

col1, col2 = st.columns(2)

with col1:
    top_states = state_metrics.head(10)
    fig = px.bar(top_states, x='Sales', y='State', orientation='h',
                title="Top 10 States by Sales",
                color='Profit', color_continuous_scale='Viridis')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.treemap(state_metrics, path=['State'], values='Sales',
                    title="Sales Distribution by State",
                    color='Profit', color_continuous_scale='RdYlGn')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("🏙️ City Performance")

selected_region = st.selectbox("Select Region", ['All'] + sorted(df['Region'].unique()))

if selected_region != 'All':
    city_df = df[df['Region'] == selected_region]
else:
    city_df = df

city_metrics = city_df.groupby('City').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).reset_index()

city_metrics['Margin'] = (city_metrics['Profit'] / city_metrics['Sales']) * 100
top_cities = city_metrics.nlargest(10, 'Sales')

st.dataframe(top_cities.style.format({
    'Sales': '${:,.2f}',
    'Profit': '${:,.2f}',
    'Margin': '{:.1f}%'
}), use_container_width=True)

st.markdown("---")
st.subheader("📊 Regional Performance Comparison")

regions_radar = regional_metrics.copy()
regions_radar['Sales_Pct'] = (regions_radar['Sales'] / regions_radar['Sales'].sum()) * 100
regions_radar['Profit_Pct'] = (regions_radar['Profit'] / regions_radar['Profit'].sum()) * 100
regions_radar['Customers_Pct'] = (regions_radar['Customers'] / regions_radar['Customers'].sum()) * 100

fig = go.Figure()

for region in regions_radar.index:
    fig.add_trace(go.Scatterpolar(
        r=[regions_radar.loc[region, 'Sales_Pct'], 
           regions_radar.loc[region, 'Profit_Pct'],
           regions_radar.loc[region, 'Margin'],
           regions_radar.loc[region, 'Avg_Order'] / 1000,
           regions_radar.loc[region, 'Customers_Pct']],
        theta=['Sales %', 'Profit %', 'Margin %', 'Avg Order (K)', 'Customers %'],
        fill='toself',
        name=region
    ))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    title="Regional Performance Comparison",
    height=500
)
st.plotly_chart(fig, use_container_width=True)