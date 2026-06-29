# dashboard/pages/11_Scenario_Simulator.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data
import pandas as pd
import numpy as np

st.markdown("""
<style>
    .sim-box {
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🎯 Scenario Simulator</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Model business scenarios and their impact</p>', unsafe_allow_html=True)

df = load_data()

current_sales = df['Sales'].sum()
current_profit = df['Profit'].sum()
current_margin = (current_profit / current_sales * 100) if current_sales > 0 else 0
current_customers = df['Customer ID'].nunique()

st.markdown("### 📊 Scenario Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    discount_change = st.slider("Discount Change (%)", -50, 50, 0, 5)

with col2:
    price_change = st.slider("Price Change (%)", -30, 30, 0, 5)

with col3:
    marketing_budget = st.slider("Marketing Budget ($)", 0, 100000, 50000, 5000)

st.markdown("### 🔧 Advanced Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    price_elasticity = st.slider("Price Elasticity", -3.0, -0.5, -1.5, 0.1)

with col2:
    discount_elasticity = st.slider("Discount Elasticity", -2.0, 2.0, 0.8, 0.1)

with col3:
    marketing_roi = st.slider("Marketing ROI", 1.0, 10.0, 5.0, 0.5)

price_volume_impact = (price_change / 100) * price_elasticity
price_margin_impact = -(price_change / 100) * 0.8
discount_volume_impact = (discount_change / 100) * discount_elasticity
discount_margin_impact = -(discount_change / 100) * 0.5
marketing_sales_impact = (marketing_budget - 50000) * marketing_roi

total_volume_change = price_volume_impact + discount_volume_impact
total_margin_change = discount_margin_impact - (price_change / 100) * 0.8

projected_sales = current_sales * (1 + total_volume_change) + marketing_sales_impact
projected_profit = projected_sales * ((current_margin + total_margin_change) / 100)
profit_change = projected_profit - current_profit

st.markdown("---")
st.markdown("### 📈 Simulation Results")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Sales", f"${current_sales:,.0f}")
    st.metric("Projected Sales", f"${projected_sales:,.0f}", 
             delta=f"{(projected_sales/current_sales - 1)*100:.1f}%")

with col2:
    st.metric("Current Profit", f"${current_profit:,.0f}")
    st.metric("Projected Profit", f"${projected_profit:,.0f}", 
             delta=f"${profit_change:,.0f}")

with col3:
    st.metric("Current Margin", f"{current_margin:.1f}%")
    new_margin = (projected_profit / projected_sales) * 100 if projected_sales > 0 else 0
    st.metric("Projected Margin", f"{new_margin:.1f}%", 
             delta=f"{new_margin - current_margin:.1f}%")

with col4:
    roi = (profit_change / max(marketing_budget - 50000, 1)) * 100 if marketing_budget != 50000 else 0
    st.metric("Marketing ROI", f"{roi:.0f}%")

st.markdown("---")
st.subheader("🎯 Recommendation")

if profit_change > 100000:
    st.success(f"""
    ✅ **Highly Recommended Scenario!**
    
    This scenario would increase profit by **${profit_change:,.0f}** ({ (profit_change/current_profit)*100:.1f}% increase).
    Consider implementing these changes immediately.
    """)
elif profit_change > 0:
    st.info(f"""
    💡 **Recommended Scenario**
    
    This scenario would increase profit by **${profit_change:,.0f}** ({ (profit_change/current_profit)*100:.1f}% increase).
    """)
else:
    st.warning(f"""
    ⚠️ **Not Recommended Scenario**
    
    This scenario would decrease profit by **${abs(profit_change):,.0f}** ({ (profit_change/current_profit)*100:.1f}% decrease).
    """)

st.markdown("---")
st.subheader("📊 Sensitivity Analysis")

sensitivity_data = []
for pct in [-20, -10, 0, 10, 20]:
    volume = (pct / 100) * price_elasticity
    sales_impact = current_sales * (1 + volume)
    profit_impact = sales_impact * (current_margin / 100)
    sensitivity_data.append({
        'Price Change (%)': pct,
        'Volume Impact (%)': volume * 100,
        'Sales Impact ($)': sales_impact - current_sales,
        'Profit Impact ($)': profit_impact - current_profit
    })

sensitivity_df = pd.DataFrame(sensitivity_data)

fig = go.Figure()
fig.add_trace(go.Scatter(x=sensitivity_df['Price Change (%)'], 
                         y=sensitivity_df['Sales Impact ($)'],
                         mode='lines+markers', name='Sales Impact',
                         line=dict(color='#667eea', width=3)))
fig.add_trace(go.Scatter(x=sensitivity_df['Price Change (%)'], 
                         y=sensitivity_df['Profit Impact ($)'],
                         mode='lines+markers', name='Profit Impact',
                         line=dict(color='#f5576c', width=3)))

fig.update_layout(title="Sensitivity Analysis: Price Change Impact",
                  xaxis_title="Price Change (%)",
                  yaxis_title="Impact ($)",
                  height=400,
                  hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)