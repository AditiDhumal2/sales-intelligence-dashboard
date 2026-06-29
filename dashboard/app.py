# dashboard/app.py - COMPLETE FIXED VERSION (No Double Menu)
import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
import os
import sys

warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="AI Sales Intelligence Dashboard | MSIM Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== COMPLETE CSS TO HIDE DEFAULT MENU ====================
st.markdown("""
<style>
    /* HIDE DEFAULT STREAMLIT SIDEBAR COMPLETELY */
    .st-emotion-cache-1v3fvcr {
        display: none !important;
    }
    .st-emotion-cache-1q8dd3e {
        display: none !important;
    }
    .st-emotion-cache-1lcbmhc {
        display: none !important;
    }
    .st-emotion-cache-1d391kg {
        display: none !important;
    }
    .st-emotion-cache-1r6slb0 {
        display: none !important;
    }
    .st-emotion-cache-6qob1r {
        display: none !important;
    }
    .st-emotion-cache-1wivap2 {
        display: none !important;
    }
    
    /* HIDE HAMBURGER MENU */
    #MainMenu {
        visibility: hidden !important;
    }
    .stApp > header {
        display: none !important;
    }
    header {
        visibility: hidden !important;
    }
    
    /* HIDE FOOTER */
    footer {
        visibility: hidden !important;
    }
    .stApp > footer {
        display: none !important;
    }
    
    /* HIDE DEFAULT SIDEBAR NAVIGATION TEXT */
    .css-1v3fvcr {
        display: none !important;
    }
    .css-1lcbmhc {
        display: none !important;
    }
    .css-1q8dd3e {
        display: none !important;
    }
    
    /* KEEP CUSTOM SIDEBAR VISIBLE */
    section[data-testid="stSidebar"] {
        min-width: 0px !important;
        width: 300px !important;
        background-color: #f8f9fa !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    
    /* STYLE CUSTOM RADIO BUTTONS */
    .stRadio > div {
        gap: 0.2rem !important;
    }
    .stRadio label {
        padding: 0.6rem 1rem !important;
        border-radius: 0.5rem !important;
        transition: 0.3s !important;
        cursor: pointer !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #333 !important;
        width: 100% !important;
    }
    .stRadio label:hover {
        background-color: #667eea20 !important;
    }
    .stRadio label[data-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* MAIN HEADER STYLES */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }
    .sidebar-logo {
        text-align: center;
        padding: 1rem 0;
    }
    .feature-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.3rem 0;
        border-left: 3px solid #667eea;
        font-size: 0.85rem;
        color: #333;
    }
    .footer {
        text-align: center;
        color: #999;
        padding: 1rem 0;
        font-size: 0.8rem;
        border-top: 1px solid #eee;
        margin-top: 2rem;
    }
    
    /* HIDE DEFAULT PAGE TITLE */
    .stAppDeployButton {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== CUSTOM SIDEBAR ====================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("## 📊 AI Sales Intelligence")
    st.markdown("---")
    
    # Navigation using radio buttons
    st.markdown("### 🧭 Navigation")
    
    page_options = [
        "🏠 Executive Summary",
        "🔍 Drill-Down Analysis",
        "👥 Customer Segmentation",
        "🔮 Sales Forecasting",
        "🤖 AI Business Insights",
        "💬 Natural Language Query",
        "🚨 Anomaly Detection",
        "💡 Recommendation Engine",
        "📦 Product Performance",
        "🗺️ Regional Performance",
        "🎯 Scenario Simulator",
        "📖 Data Storytelling"
    ]
    
    selected = st.radio(
        label="",
        options=page_options,
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Features Section
    st.markdown("### 🎯 Features Included")
    features = [
        "✅ 12 Analytics Modules",
        "🤖 AI-Powered Insights",
        "📈 Predictive Forecasting",
        "💬 Natural Language Query",
        "🎯 Decision Support",
        "📊 Interactive Visualizations"
    ]
    for feature in features:
        st.markdown(f"<div class='feature-box'>{feature}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(f"⏰ Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")

# ==================== PAGE ROUTING ====================
page_map = {
    "🏠 Executive Summary": "1_Executive_Summary",
    "🔍 Drill-Down Analysis": "2_Drill_Down_Analysis",
    "👥 Customer Segmentation": "3_Customer_Segmentation",
    "🔮 Sales Forecasting": "4_Sales_Forecasting",
    "🤖 AI Business Insights": "5_AI_Business_Insights",
    "💬 Natural Language Query": "6_Natural_Language_Query",
    "🚨 Anomaly Detection": "7_Anomaly_Detection",
    "💡 Recommendation Engine": "8_Recommendation_Engine",
    "📦 Product Performance": "9_Product_Performance",
    "🗺️ Regional Performance": "10_Regional_Performance",
    "🎯 Scenario Simulator": "11_Scenario_Simulator",
    "📖 Data Storytelling": "12_Data_Storytelling"
}

page_name = page_map.get(selected, "1_Executive_Summary")
page_file = f"dashboard/pages/{page_name}.py"

try:
    if os.path.exists(page_file):
        with open(page_file, 'r', encoding='utf-8') as f:
            exec(f.read())
    else:
        st.error(f"❌ Page not found: {page_file}")
        st.info("Please make sure all page files are in the 'dashboard/pages/' folder")
        
        pages_dir = "dashboard/pages"
        if os.path.exists(pages_dir):
            st.subheader("📁 Available Pages:")
            for file in sorted(os.listdir(pages_dir)):
                if file.endswith('.py'):
                    st.write(f"✅ {file}")
        else:
            st.warning("Pages folder not found. Please create 'dashboard/pages/' folder.")
            
except Exception as e:
    st.error(f"❌ Error loading page: {str(e)}")
    st.info("Please ensure all page files are properly created.")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p>📊 <strong>AI-Powered Sales Intelligence Dashboard</strong></p>
    <p style='font-size: 0.75rem; color: #bbb;'>
        Built with ❤️ | 12 Analytics Modules | AI-Powered Insights
    </p>
</div>
""", unsafe_allow_html=True)