# dashboard/utils/data_loader.py - Complete Data Loading Utilities
import pandas as pd
import streamlit as st
import numpy as np
import os

@st.cache_data
def load_data():
    """Load and cache the enhanced dataset"""
    try:
        df = pd.read_csv('data/processed/superstore_enhanced.csv')
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        return df
    except FileNotFoundError:
        try:
            df = pd.read_csv('data/raw/superstore.csv')
            df['Order Date'] = pd.to_datetime(df['Order Date'])
            return df
        except FileNotFoundError:
            st.error("❌ Data files not found!")
            st.info("Please run the following commands first:")
            st.code("""
python create_data_direct.py
python data_preparation.py
            """)
            st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

@st.cache_data
def load_summary():
    """Load business summary data"""
    try:
        return pd.read_csv('data/enhanced/business_summary.csv').iloc[0]
    except:
        return None

@st.cache_data
def get_customer_segments(df):
    """Perform RFM analysis and return customer segments"""
    current_date = df['Order Date'].max()
    
    rfm = df.groupby('Customer ID').agg({
        'Order Date': lambda x: (current_date - x.max()).days,
        'Order ID': 'count',
        'Sales': 'sum',
        'Profit': 'sum'
    }).rename(columns={
        'Order Date': 'Recency',
        'Order ID': 'Frequency',
        'Sales': 'Monetary',
        'Profit': 'Profit'
    })
    
    try:
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=['4', '3', '2', '1'])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=['1', '2', '3', '4'])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=['1', '2', '3', '4'])
    except ValueError:
        rfm['R_Score'] = '3'
        rfm['F_Score'] = '3'
        rfm['M_Score'] = '3'
    
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    def get_segment(row):
        try:
            r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])
            if r >= 4 and f >= 4 and m >= 4:
                return 'VIP Customer'
            elif r >= 3 and f >= 3:
                return 'Loyal Customer'
            elif r <= 2 and f >= 3:
                return 'At-Risk Customer'
            elif r <= 2:
                return 'Lost Customer'
            else:
                return 'Active Customer'
        except:
            return 'Active Customer'
    
    rfm['Segment'] = rfm.apply(get_segment, axis=1)
    rfm['Customer Lifetime Value'] = rfm['Monetary'] * 1.5
    return rfm

@st.cache_data
def calculate_growth(df):
    """Calculate sales growth metrics"""
    monthly = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    monthly.columns = ['Month', 'Sales']
    
    if len(monthly) >= 2:
        growth = ((monthly['Sales'].iloc[-1] - monthly['Sales'].iloc[-2]) / 
                  monthly['Sales'].iloc[-2]) * 100
        return growth
    return 0.0

@st.cache_data
def detect_anomalies(df, column='Sales', threshold=2):
    """Detect anomalies using Z-score method"""
    mean = df[column].mean()
    std = df[column].std()
    
    if std == 0:
        return pd.DataFrame()
    
    z_scores = (df[column] - mean) / std
    anomalies = df[abs(z_scores) > threshold]
    return anomalies

@st.cache_data
def get_top_performers(df, metric='Sales', n=10):
    """Get top performers by a given metric"""
    if metric not in df.columns:
        return pd.Series()
    
    if metric == 'Profit':
        return df.groupby('Product Name')['Profit'].sum().sort_values(ascending=False).head(n)
    elif metric == 'Sales':
        return df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(n)
    else:
        return df.groupby('Product Name')[metric].sum().sort_values(ascending=False).head(n)

@st.cache_data
def get_regional_summary(df):
    """Get regional performance summary"""
    regional = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'count',
        'Customer ID': 'nunique'
    }).rename(columns={'Order ID': 'Orders', 'Customer ID': 'Customers'})
    
    regional['Margin'] = (regional['Profit'] / regional['Sales']) * 100
    regional['Avg_Order'] = regional['Sales'] / regional['Orders']
    return regional

@st.cache_data
def get_category_summary(df):
    """Get category performance summary"""
    category = df.groupby('Category').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'count'
    }).rename(columns={'Order ID': 'Orders'})
    
    category['Margin'] = (category['Profit'] / category['Sales']) * 100
    category['Avg_Order'] = category['Sales'] / category['Orders']
    return category

def prepare_time_series(df, freq='D'):
    """Prepare time series data for forecasting"""
    ts = df.groupby('Order Date')['Sales'].sum().reset_index()
    ts = ts.set_index('Order Date').resample(freq).sum().fillna(0).reset_index()
    ts.columns = ['Date', 'Sales']
    return ts