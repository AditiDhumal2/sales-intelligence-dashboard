import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os

warnings.filterwarnings('ignore')

print("🚀 Starting data preparation for MSIM portfolio project...")
print("="*50)

# Check if data exists
if not os.path.exists('data/raw/superstore.csv'):
    print("❌ Error: data/raw/superstore.csv not found!")
    print("Please run: python download_kaggle_data.py")
    exit(1)

# ============ STEP 1: LOAD DATA ============
print("📖 STEP 1: Loading data...")
try:
    df = pd.read_csv('data/raw/superstore.csv')
except UnicodeDecodeError:
    print("⚠️ UTF-8 failed, trying latin-1 encoding...")
    df = pd.read_csv('data/raw/superstore.csv', encoding='latin-1')

print(f"✅ Loaded {len(df)} records with {len(df.columns)} columns")

# ============ STEP 2: DATA CLEANING ============
print("\n🧹 STEP 2: Data Cleaning...")

# 2.1 Check for missing values
print("\n📊 2.1 Missing Values Before Cleaning:")
missing_before = df.isnull().sum()
missing_before = missing_before[missing_before > 0]
if len(missing_before) > 0:
    print(missing_before)
else:
    print("✅ No missing values found!")

# 2.2 Handle missing values
print("\n🔧 2.2 Handling Missing Values...")
# Fill missing Postal Code with 0
if 'Postal Code' in df.columns:
    df['Postal Code'] = df['Postal Code'].fillna(0)
    print("   - Filled missing Postal Codes with 0")

# Fill missing City with 'Unknown'
if 'City' in df.columns:
    df['City'] = df['City'].fillna('Unknown')
    print("   - Filled missing Cities with 'Unknown'")

# Fill missing State with 'Unknown'
if 'State' in df.columns:
    df['State'] = df['State'].fillna('Unknown')
    print("   - Filled missing States with 'Unknown'")

# 2.3 Check for duplicates
print("\n📊 2.3 Checking for Duplicates...")
duplicates = df.duplicated().sum()
if duplicates > 0:
    print(f"   ⚠️ Found {duplicates} duplicate rows")
    df = df.drop_duplicates()
    print(f"   ✅ Removed {duplicates} duplicates")
else:
    print("   ✅ No duplicates found")

# 2.4 Check for invalid values
print("\n📊 2.4 Checking for Invalid Values...")

# Check negative Sales
negative_sales = (df['Sales'] < 0).sum()
if negative_sales > 0:
    print(f"   ⚠️ Found {negative_sales} rows with negative Sales")
    df['Sales'] = df['Sales'].abs()
    print("   ✅ Converted negative Sales to positive")

# Check negative Profit
negative_profit = (df['Profit'] < 0).sum()
print(f"   📊 {negative_profit} rows have negative Profit (losses)")

# Check invalid Discount (outside 0-1 range)
invalid_discount = ((df['Discount'] < 0) | (df['Discount'] > 1)).sum()
if invalid_discount > 0:
    print(f"   ⚠️ Found {invalid_discount} rows with invalid Discount")
    df['Discount'] = df['Discount'].clip(0, 1)
    print("   ✅ Clipped Discount to range 0-1")

# Check negative Quantity
negative_qty = (df['Quantity'] < 0).sum()
if negative_qty > 0:
    print(f"   ⚠️ Found {negative_qty} rows with negative Quantity")
    df['Quantity'] = df['Quantity'].abs()
    print("   ✅ Converted negative Quantity to positive")

# 2.5 Check for outliers
print("\n📊 2.5 Checking for Outliers...")
sales_q99 = df['Sales'].quantile(0.99)
profit_q99 = df['Profit'].quantile(0.99)
sales_outliers = (df['Sales'] > sales_q99).sum()
profit_outliers = (df['Profit'] > profit_q99).sum()

print(f"   📊 Sales outliers (99th percentile): {sales_outliers} rows")
print(f"   📊 Profit outliers (99th percentile): {profit_outliers} rows")

# 2.6 Data type validation
print("\n📊 2.6 Validating Data Types...")
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')

# Check for invalid dates
invalid_dates = df['Order Date'].isna().sum()
if invalid_dates > 0:
    print(f"   ⚠️ Found {invalid_dates} invalid Order Dates")
    df = df.dropna(subset=['Order Date'])
    print(f"   ✅ Removed rows with invalid dates")

# ============ STEP 3: FEATURE ENGINEERING ============
print("\n🔧 STEP 3: Feature Engineering...")

# Convert dates
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

# Calculate business metrics
df['Shipping_Days'] = (df['Ship Date'] - df['Order Date']).dt.days
df['Profit_Margin'] = (df['Profit'] / df['Sales']) * 100
df['Is_Profitable'] = df['Profit'] > 0
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month
df['Quarter'] = df['Order Date'].dt.quarter
df['Year_Month'] = df['Order Date'].dt.strftime('%Y-%m')

print("   ✅ Added Shipping_Days column")
print("   ✅ Added Profit_Margin column")
print("   ✅ Added Is_Profitable column")
print("   ✅ Added Year, Month, Quarter columns")
print("   ✅ Added Year_Month column")

# ============ STEP 4: CUSTOMER SEGMENTATION (RFM) ============
print("\n📊 STEP 4: Performing RFM Analysis...")

# Calculate RFM metrics
customer_data = df.groupby('Customer ID').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Order Date': 'max',
    'Order ID': 'count'
}).rename(columns={
    'Order ID': 'Frequency',
    'Order Date': 'Last_Purchase'
})

customer_data['Monetary'] = customer_data['Sales']
customer_data['Recency'] = (df['Order Date'].max() - customer_data['Last_Purchase']).dt.days

# RFM Scoring
try:
    customer_data['R_Score'] = pd.qcut(customer_data['Recency'], 4, labels=['4', '3', '2', '1'])
    customer_data['F_Score'] = pd.qcut(customer_data['Frequency'].rank(method='first'), 4, labels=['1', '2', '3', '4'])
    customer_data['M_Score'] = pd.qcut(customer_data['Monetary'], 4, labels=['1', '2', '3', '4'])
except Exception as e:
    print(f"⚠️ RFM scoring issue, using default: {e}")
    customer_data['R_Score'] = '3'
    customer_data['F_Score'] = '3'
    customer_data['M_Score'] = '3'

# Assign segments
def get_segment(row):
    try:
        r = int(row['R_Score'])
        f = int(row['F_Score'])
        m = int(row['M_Score'])
        
        if r >= 3 and f >= 3 and m >= 3:
            return 'VIP Customer'
        elif r >= 3 and f >= 2:
            return 'Loyal Customer'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At-Risk Customer'
        elif r <= 2 and f >= 2:
            return 'At-Risk Customer'
        elif r <= 2:
            return 'Lost Customer'
        else:
            return 'Active Customer'
    except:
        return 'Active Customer'

customer_data['Segment'] = customer_data.apply(get_segment, axis=1)

# Add Segment to main dataframe
segment_dict = customer_data['Segment'].to_dict()
df['Segment'] = df['Customer ID'].map(segment_dict)
df['Segment'] = df['Segment'].fillna('Active Customer')

print(f"✅ Segment column added successfully!")
print(f"   Unique segments: {df['Segment'].nunique()}")
print(f"   Segment distribution:\n{df['Segment'].value_counts()}")

# ============ STEP 5: SAVE CLEANED DATA ============
print("\n💾 STEP 5: Saving Cleaned Data...")

# Save processed data
df.to_csv('data/processed/superstore_enhanced.csv', index=False)

# Generate summary
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
print(f"Final Records: {len(df):,}")
print(f"Total Revenue: ${summary['Total Revenue']:,.2f}")
print(f"Total Profit: ${summary['Total Profit']:,.2f}")
print(f"Profit Margin: {summary['Profit Margin']:.1f}%")
print(f"Total Customers: {summary['Total Customers']:,}")
print(f"Total Orders: {summary['Total Orders']:,}")
print(f"Avg Order Value: ${summary['Avg Order Value']:,.2f}")

print("\n📊 Customer Segments:")
print(df['Segment'].value_counts())

print("\n✅ Ready to launch dashboard!")
print("Run: streamlit run dashboard/app.py")