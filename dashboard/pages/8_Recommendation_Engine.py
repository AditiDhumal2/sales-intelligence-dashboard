# dashboard/pages/8_Recommendation_Engine.py
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
    .rec-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .priority-high { border-left-color: #f5576c; }
    .priority-medium { border-left-color: #f6d365; }
    .priority-low { border-left-color: #4facfe; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💡 Recommendation Engine</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">AI-powered business recommendations for action</p>', unsafe_allow_html=True)

df = load_data()

total_sales = df['Sales'].sum()
total_profit = df['Profit'].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

category_analysis = df.groupby('Category').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Quantity': 'sum' if 'Quantity' in df.columns else lambda x: len(x)
}).reset_index()

if 'Quantity' not in df.columns:
    category_analysis['Quantity'] = df.groupby('Category').size().values

category_analysis['Margin'] = (category_analysis['Profit'] / category_analysis['Sales']) * 100
best_category = category_analysis.loc[category_analysis['Profit'].idxmax()]
worst_category = category_analysis.loc[category_analysis['Profit'].idxmin()]

product_analysis = df.groupby('Product Name').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Quantity': 'sum' if 'Quantity' in df.columns else 'count'
}).reset_index()

if 'Quantity' not in df.columns:
    product_analysis['Quantity'] = df.groupby('Product Name').size().values

product_analysis['Margin'] = (product_analysis['Profit'] / product_analysis['Sales']) * 100
top_products = product_analysis.nlargest(10, 'Profit')
slow_products = product_analysis.nsmallest(10, 'Quantity')

region_analysis = df.groupby('Region').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).reset_index()
region_analysis['Margin'] = (region_analysis['Profit'] / region_analysis['Sales']) * 100

best_region = region_analysis.loc[region_analysis['Sales'].idxmax()]
worst_region = region_analysis.loc[region_analysis['Sales'].idxmin()]

st.markdown("### 🎯 Top Recommendations")

st.markdown(f"""
<div class='rec-card priority-high'>
    <strong>📦 Category Strategy Recommendation</strong><br>
    <strong>Action:</strong> Increase inventory and marketing investment in <strong>{best_category['Category']}</strong> category.<br>
    <strong>Why:</strong> Generates <strong>${best_category['Profit']:,.2f}</strong> profit with <strong>{best_category['Margin']:.1f}%</strong> margin.<br>
    <strong>Priority:</strong> 🔴 High
</div>
""", unsafe_allow_html=True)

if worst_category['Margin'] < 15:
    st.markdown(f"""
    <div class='rec-card priority-high'>
        <strong>💰 Pricing Strategy Recommendation</strong><br>
        <strong>Action:</strong> Review pricing and discount structure for <strong>{worst_category['Category']}</strong> category.<br>
        <strong>Why:</strong> Current margin is only <strong>{worst_category['Margin']:.1f}%</strong> (below target).<br>
        <strong>Priority:</strong> 🔴 High
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class='rec-card priority-medium'>
    <strong>📍 Regional Strategy Recommendation</strong><br>
    <strong>Action:</strong> Expand successful strategies from <strong>{best_region['Region']}</strong> to other regions.<br>
    <strong>Why:</strong> {best_region['Region']} achieves <strong>{best_region['Margin']:.1f}%</strong> margin.<br>
    <strong>Priority:</strong> 🟡 Medium
</div>
""", unsafe_allow_html=True)

if 'Segment' in df.columns:
    segment_counts = df['Segment'].value_counts()
    at_risk = segment_counts.get('At-Risk Customer', 0)
    
    if at_risk > 0:
        st.markdown(f"""
        <div class='rec-card priority-high'>
            <strong>👥 Customer Retention Recommendation</strong><br>
            <strong>Action:</strong> Launch targeted retention campaign for <strong>{at_risk}</strong> at-risk customers.<br>
            <strong>Why:</strong> Retaining customers is 5x cheaper than acquiring new ones.<br>
            <strong>Priority:</strong> 🔴 High
        </div>
        """, unsafe_allow_html=True)

avg_discount = df['Discount'].mean() if 'Discount' in df.columns else 0
if avg_discount > 0.15:
    st.markdown(f"""
    <div class='rec-card priority-medium'>
        <strong>🎯 Discount Strategy Recommendation</strong><br>
        <strong>Action:</strong> Optimize discount levels across categories.<br>
        <strong>Current:</strong> Average discount is <strong>{avg_discount:.1%}</strong>.<br>
        <strong>Priority:</strong> 🟡 Medium
    </div>
    """, unsafe_allow_html=True)