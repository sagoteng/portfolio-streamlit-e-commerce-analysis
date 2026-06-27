# Import
import pandas as pd
import numpy as np
from  datetime import datetime, timedelta

# List of values
categories = ['Clothing', 'Electronics', 'Food', 'Beauty', 'Sports', 'Furniture', 'Books', 'Toys', 'Jewelry', 'Automotive', 'Garden', 'Health', 'Music', 'Office', 'Travel']
countries = ['France', 'Germany', 'United Kingdom', 'Spain', 'Italy', 'Netherlands', 'Belgium', 'Portugal', 'Sweden', 'Norway', 'Denmark', 'Poland', 'Switzerland', 'Austria', 'Canada', 'United States', 'Australia', 'Japan', 'Brazil', 'Mexico']
channels = ['Store', 'Web', 'App', 'Marketplace', 'Social Media', 'Email', 'Phone']

#Parameters
n = 10000
start_date = datetime(2022, 1, 1)
end_date = datetime (2025, 12, 31)
categories_col = np.random.choice(categories, n)
client_pool = ["C-" + str(np.random.randint(0,99999999)).zfill(8) for _ in range(500)] 

# Data generation
data = {
    'quantity': np.random.randint(1, 20, n),
    'revenue': np.round(np.random.uniform(5.0,500.0,n),2),
    'order_date' : [start_date + timedelta(days=int(np.random.randint(0,1460))) for _ in range(n)],
    'client_id': np.random.choice(client_pool, n),
    'product_id' : [cat[:3] + "-" + str(np.random.randint(0,999999)).zfill(6) for cat in categories_col],
    'category' : categories_col,
    'country' : np.random.choice (countries, n),
    'channel' : np.random.choice (channels, n)
}

#Export CSV
df = pd.DataFrame(data)
df.to_csv(r"C:\Users\sagot\Desktop\Portfolio_web_app\dataset_ecommerce.csv", index=False)

print(f"Dataset generated : {n} exported lines ")