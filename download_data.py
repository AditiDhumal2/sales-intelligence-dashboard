# download_data.py - Run this first!
import pandas as pd
import urllib.request
import os

# Create directories if they don't exist
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/enhanced', exist_ok=True)

# Download Superstore dataset
url = "https://raw.githubusercontent.com/plotly/datasets/master/superstore.csv"
urllib.request.urlretrieve(url, 'data/raw/superstore.csv')

print("✅ Dataset downloaded successfully!")
print("Now run: python data_preparation.py")