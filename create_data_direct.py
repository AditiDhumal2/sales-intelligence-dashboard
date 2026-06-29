# create_data_direct.py - Complete working dataset creator
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

print("🚀 Creating Superstore dataset directly...")
print("This will create a realistic sales dataset for your dashboard")

# Create directories
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/enhanced', exist_ok=True)

# Set random seed for reproducibility
np.random.seed(42)

# Number of records
n_records = 10000

# Generate dates (2015-2018)
start_date = datetime(2015, 1, 1)
end_date = datetime(2018, 12, 31)
date_range = (end_date - start_date).days

print("📅 Generating dates...")
order_dates = [start_date + timedelta(days=np.random.randint(0, date_range)) for _ in range(n_records)]

# Define product catalog
categories = ['Technology', 'Furniture', 'Office Supplies']
sub_categories = {
    'Technology': ['Phones', 'Computers', 'Accessories', 'Software'],
    'Furniture': ['Chairs', 'Tables', 'Desks', 'Bookcases'],
    'Office Supplies': ['Paper', 'Pens', 'Binders', 'Storage']
}

# Generate product names
products = []
for cat in categories:
    for sub in sub_categories[cat]:
        for i in range(15):
            products.append(f"{sub} {np.random.choice(['Pro', 'Basic', 'Deluxe', 'Premium', 'Standard'])}")

print("📦 Generating sales data...")

# Generate data
data = {
    'Row ID': range(1, n_records + 1),
    'Order ID': [f'US-{np.random.randint(10000, 99999)}-{np.random.choice([2015,2016,2017,2018])}' for _ in range(n_records)],
    'Order Date': order_dates,
    'Ship Date': [d + timedelta(days=np.random.randint(1, 7)) for d in order_dates],
    'Ship Mode': np.random.choice(['Standard Class', 'Second Class', 'First Class', 'Same Day'], n_records, p=[0.5, 0.2, 0.2, 0.1]),
    'Customer ID': [f'CG-{np.random.randint(1000, 9999)}' for _ in range(n_records)],
    'Customer Name': [f'Customer_{np.random.randint(1, 800)}' for _ in range(n_records)],
    'Segment': np.random.choice(['Consumer', 'Corporate', 'Home Office'], n_records, p=[0.5, 0.3, 0.2]),
    'Country': 'United States',
    'City': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Diego', 'Dallas', 'Austin', 'Seattle'], n_records),
    'State': np.random.choice(['California', 'Texas', 'New York', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio', 'Georgia', 'North Carolina', 'Michigan'], n_records),
    'Region': np.random.choice(['West', 'East', 'Central', 'South'], n_records, p=[0.3, 0.3, 0.2, 0.2]),
    'Category': np.random.choice(categories, n_records, p=[0.35, 0.30, 0.35]),
    'Product Name': np.random.choice(products, n_records),
}

# Create DataFrame
df = pd.DataFrame(data)

# Add Sub-Category based on Product Name
df['Sub-Category'] = df['Product Name'].apply(lambda x: x.split()[0])

# Generate Sales (realistic distribution)
df['Sales'] = np.random.gamma(shape=2, scale=150, size=n_records)
df['Sales'] = df['Sales'].clip(lower=5, upper=2000)

# Generate Quantity
df['Quantity'] = np.random.choice([1, 2, 3, 4, 5], n_records, p=[0.4, 0.3, 0.15, 0.1, 0.05])

# Generate Discount
df['Discount'] = np.random.choice([0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4], n_records, p=[0.6, 0.15, 0.1, 0.05, 0.04, 0.03, 0.03])

# Calculate Profit (realistic business logic)
# Profit = Sales * (margin) - discount impact
base_margin = np.random.uniform(0.15, 0.35, n_records)
category_margin = {'Technology': 0.30, 'Furniture': 0.20, 'Office Supplies': 0.25}
df['Profit_Margin_Pct'] = df['Category'].map(category_margin) * base_margin
df['Profit'] = df['Sales'] * df['Profit_Margin_Pct'] * (1 - df['Discount'] * 1.5)
df['Profit'] = df['Profit'].clip(lower=-100, upper=500)

# Create Product ID
df['Product ID'] = df.apply(lambda row: f"{row['Category'][:2]}-{row['Sub-Category'][:3]}-{np.random.randint(100,999)}", axis=1)

# Create Postal Code
df['Postal Code'] = np.random.choice([10001, 90210, 60601, 77001, 85001, 94101, 19101, 75201], n_records)

print("💾 Saving to CSV...")

# Save to CSV
df.to_csv('data/raw/superstore.csv', index=False)

print(f"\n✅ Dataset created successfully!")
print(f"📊 Shape: {len(df):,} rows, {len(df.columns)} columns")
print(f"📋 Columns: {', '.join(df.columns[:10])}...")

print(f"\n💰 Total Sales: ${df['Sales'].sum():,.2f}")
print(f"💵 Total Profit: ${df['Profit'].sum():,.2f}")
print(f"📈 Profit Margin: {(df['Profit'].sum()/df['Sales'].sum())*100:.1f}%")

print(f"\n📊 Sales by Category:")
print(df.groupby('Category')['Sales'].sum().apply(lambda x: f"${x:,.2f}"))

print(f"\n📍 Sales by Region:")
print(df.groupby('Region')['Sales'].sum().apply(lambda x: f"${x:,.2f}"))

print("\n" + "="*50)
print("✅ DATA CREATION COMPLETE!")
print("="*50)
print("\n📋 Sample data (first 5 rows):")
print(df.head())
print("\n🎯 Next step: Run 'python data_preparation.py'")