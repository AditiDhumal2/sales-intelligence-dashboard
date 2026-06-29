# dashboard/pages/6_Natural_Language_Query.py
import streamlit as st
import plotly.express as px
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data
import pandas as pd

st.markdown("""
<style>
    .user-msg {
        background: #667eea20;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .bot-msg {
        background: #764ba220;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #764ba2;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💬 Natural Language Query</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Ask questions about your business data in plain English</p>', unsafe_allow_html=True)

df = load_data()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm your AI data assistant. Ask me anything about your sales data!"}
    ]

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"<div class='user-msg'>🧑 <strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'>🤖 <strong>AI:</strong> {message['content']}</div>", unsafe_allow_html=True)

user_query = st.text_input("Ask a question about your data:", placeholder="e.g., Which product generated the highest profit?")

def process_query(query, df):
    query_lower = query.lower()
    response = ""
    
    product_match = re.search(r'product|item', query_lower)
    category_match = re.search(r'category', query_lower)
    region_match = re.search(r'region|state|city', query_lower)
    
    if "highest" in query_lower and "profit" in query_lower:
        if product_match:
            top_product = df.groupby('Product Name')['Profit'].sum().idxmax()
            top_profit = df.groupby('Product Name')['Profit'].sum().max()
            response = f"🏆 The product that generated the highest profit is **{top_product[:50]}** with a profit of **${top_profit:,.2f}**."
            
            top_products = df.groupby('Product Name')['Profit'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(top_products, x=top_products.values, y=top_products.index, 
                        orientation='h', title="Top 10 Products by Profit")
            st.plotly_chart(fig, use_container_width=True)
        elif category_match:
            top_cat = df.groupby('Category')['Profit'].sum().idxmax()
            top_cat_profit = df.groupby('Category')['Profit'].sum().max()
            response = f"🏆 The category with the highest profit is **{top_cat}** with **${top_cat_profit:,.2f}** in profit."
    
    elif "highest" in query_lower and "sales" in query_lower:
        top_product = df.groupby('Product Name')['Sales'].sum().idxmax()
        top_sales = df.groupby('Product Name')['Sales'].sum().max()
        response = f"📈 The product with the highest sales is **{top_product[:50]}** with **${top_sales:,.2f}** in sales."
        
        top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(top_products, x=top_products.values, y=top_products.index, 
                    orientation='h', title="Top 10 Products by Sales")
        st.plotly_chart(fig, use_container_width=True)
    
    elif "region" in query_lower and ("sales" in query_lower or "performance" in query_lower):
        regional = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
        response = "📊 Here are regional sales figures:\n"
        for region, sales in regional.items():
            response += f"• {region}: ${sales:,.2f}\n"
        
        fig = px.bar(regional, x=regional.index, y='Sales', 
                    title="Sales by Region", color=regional.values,
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    elif "category" in query_lower:
        cat_profit = df.groupby('Category')['Profit'].sum().sort_values(ascending=False)
        response = "📦 Category performance:\n"
        for cat, profit in cat_profit.items():
            response += f"• {cat}: ${profit:,.2f} profit\n"
        
        fig = px.bar(cat_profit, x=cat_profit.index, y='Profit', 
                    title="Profit by Category", color=cat_profit.values,
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    elif "customer" in query_lower:
        total_customers = df['Customer ID'].nunique()
        if 'Segment' in df.columns:
            segments = df['Segment'].value_counts()
            response = f"👥 We have **{total_customers:,}** customers.\n\n**Segments:**\n"
            for seg, count in segments.items():
                response += f"• {seg}: {count:,} customers\n"
        else:
            response = f"👥 We have **{total_customers:,}** customers."
    
    elif "total" in query_lower and "sales" in query_lower:
        total = df['Sales'].sum()
        response = f"💰 Total sales: **${total:,.2f}**"
    
    elif "total" in query_lower and "profit" in query_lower:
        total = df['Profit'].sum()
        response = f"💵 Total profit: **${total:,.2f}**"
    
    elif "margin" in query_lower:
        margin = (df['Profit'].sum() / df['Sales'].sum()) * 100
        response = f"📊 Overall profit margin: **{margin:.1f}%**"
    
    else:
        response = "🤔 I understand questions about sales, profit, products, customers, regions, and categories. Try asking:\n\n• Which product generated the highest profit?\n• Show sales by region\n• What's the total revenue?\n• How many customers do we have?"

    return response

if st.button("Send", type="primary") and user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.spinner("🤔 Thinking..."):
        response = process_query(user_query, df)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()

st.markdown("---")
st.markdown("### 🚀 Try These Questions:")

quick_questions = [
    "Which product generated the highest profit?",
    "Show sales by region",
    "What's the total revenue?",
    "How many customers do we have?"
]

cols = st.columns(2)
for idx, q in enumerate(quick_questions):
    with cols[idx % 2]:
        if st.button(q, key=f"quick_{idx}"):
            st.session_state.messages.append({"role": "user", "content": q})
            with st.spinner("🤔 Thinking..."):
                response = process_query(q, df)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if st.button("🗑️ Clear Chat", type="secondary"):
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Chat cleared! Ask me anything about your sales data!"}
    ]
    st.rerun()