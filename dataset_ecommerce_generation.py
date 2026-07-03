import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Listes de valeurs possibles
categories = ['Clothing', 'Electronics', 'Food', 'Beauty', 'Sports', 'Furniture', 'Books', 'Toys', 'Jewelry', 'Automotive', 'Garden', 'Health', 'Music', 'Office', 'Travel']
countries = ['France', 'Germany', 'United Kingdom', 'Spain', 'Italy', 'Netherlands', 'Belgium', 'Portugal', 'Sweden', 'Norway', 'Denmark', 'Poland', 'Switzerland', 'Austria', 'Canada', 'United States', 'Australia', 'Japan', 'Brazil', 'Mexico']
channels = ['Store', 'Web', 'App', 'Marketplace', 'Social Media', 'Email', 'Phone']

# Taux de coût par catégorie (cost / revenue)
cost_rate_ranges = {
    'Electronics':  (0.70, 0.80),
    'Jewelry':      (0.70, 0.80),
    'Automotive':   (0.68, 0.78),
    'Clothing':     (0.50, 0.65),
    'Beauty':       (0.50, 0.65),
    'Sports':       (0.52, 0.65),
    'Food':         (0.45, 0.60),
    'Books':        (0.40, 0.55),
    'Toys':         (0.45, 0.58),
    'Music':        (0.42, 0.56),
    'Furniture':    (0.48, 0.62),
    'Garden':       (0.46, 0.60),
    'Health':       (0.47, 0.61),
    'Office':       (0.50, 0.63),
    'Travel':       (0.45, 0.58),
}

# Paramètres
n = 10000
start_date = datetime(2022, 1, 1)
end_date = datetime(2025, 12, 31)

# Client pool
client_pool = ["C-" + str(np.random.randint(0, 99999999)).zfill(8) for _ in range(500)]

# Génération des données
np.random.seed(42)

categories_col = np.random.choice(categories, n)
revenues = np.round(np.random.uniform(5.0, 500.0, n), 2)

unit_costs = np.array([
    round(rev * np.random.uniform(*cost_rate_ranges[cat]), 2)
    for rev, cat in zip(revenues, categories_col)
])

margins = np.round(revenues - unit_costs, 2)
margin_rates = np.round((margins / revenues) * 100, 2)

data = {
    'order_date': [start_date + timedelta(days=int(np.random.randint(0, 1460))) for _ in range(n)],
    'product_id': [cat[:3] + "-" + str(np.random.randint(0, 999999)).zfill(6) for cat in categories_col],
    'category': categories_col,
    'quantity': np.random.randint(1, 20, n),
    'revenue': revenues,
    'unit_cost': unit_costs,
    'margin': margins,
    'margin_rate': margin_rates,
    'client_id': np.random.choice(client_pool, n),
    'country': np.random.choice(countries, n),
    'channel': np.random.choice(channels, n)
}

# Export CSV
df = pd.DataFrame(data)
df.to_csv(r"C:\Users\sagot\Desktop\Portfolio_web_app\dataset_ecommerce.csv", index=False)

print(f"Dataset généré : {n} lignes exportées.")