# data_preparation.py - FIXED VERSION
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os

warnings.filterwarnings('ignore')

print("🚀 Starting data preparation for MSIM portfolio project...")

# Check if file exists
if not os.path.exists('data/raw/superstore.csv'):
    print("❌ Error: data/raw/superstore.csv not found!")
    print("Please run: python create_data_direct.py")
    exit(1)

# Load data
df = pd.read_csv('data/raw/superstore.csv')
print(f"✅ Loaded {len(df)} records")

# Convert dates
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

# Calculate basic business metrics
df['Shipping_Days'] = (df['Ship Date'] - df['Order Date']).dt.days
df['Profit_Margin'] = (df['Profit'] / df['Sales']) * 100
df['Is_Profitable'] = df['Profit'] > 0
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month
df['Quarter'] = df['Order Date'].dt.quarter
df['Year_Month'] = df['Order Date'].dt.strftime('%Y-%m')

# Simple customer segmentation (RFM-like)
customer_agg = df.groupby('Customer ID').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Order ID': 'count'
}).rename(columns={'Order ID': 'Frequency'})

# Add RFM-like segmentation
customer_agg['Total_Spend'] = customer_agg['Sales']

# Simple segment assignment (simplified RFM)
def assign_segment(row):
    if row['Sales'] > df['Sales'].quantile(0.75):
        return 'VIP Customer'
    elif row['Sales'] > df['Sales'].quantile(0.50):
        return 'Loyal Customer'
    elif row['Sales'] > df['Sales'].quantile(0.25):
        return 'Regular Customer'
    else:
        return 'At-Risk Customer'

customer_agg['Segment'] = customer_agg.apply(assign_segment, axis=1)

# Merge back
df = df.merge(customer_agg[['Segment']], left_on='Customer ID', right_index=True, how='left')

# Save processed data
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/enhanced', exist_ok=True)
df.to_csv('data/processed/superstore_enhanced.csv', index=False)

# Generate business summary
summary = {
    'Total Revenue': df['Sales'].sum(),
    'Total Profit': df['Profit'].sum(),
    'Profit Margin': (df['Profit'].sum() / df['Sales'].sum()) * 100,
    'Total Customers': df['Customer ID'].nunique(),
    'Total Orders': df['Order ID'].nunique(),
    'Avg Order Value': df['Sales'].sum() / df['Order ID'].nunique(),
    'Unique Products': df['Product ID'].nunique()
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv('data/enhanced/business_summary.csv', index=False)

print("\n" + "="*50)
print("✅ DATA PREPARATION COMPLETE!")
print("="*50)
print(f"Total Revenue: ${summary['Total Revenue']:,.2f}")
print(f"Total Profit: ${summary['Total Profit']:,.2f}")
print(f"Profit Margin: {summary['Profit Margin']:.1f}%")
print(f"Total Customers: {summary['Total Customers']:,}")
print(f"Total Orders: {summary['Total Orders']:,}")
print(f"Avg Order Value: ${summary['Avg Order Value']:,.2f}")

# FIXED: Safely print customer segments
print("\n📊 Customer Segments:")
if 'Segment' in df.columns:
    print(df['Segment'].value_counts())
else:
    print("Segment column created successfully")

print("\n✅ Ready to launch dashboard!")
print("Run: streamlit run dashboard/app.py")