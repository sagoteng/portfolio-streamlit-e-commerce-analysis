# E-Commerce Analysis Dashboard

An interactive multi-page web application built with Streamlit for analyzing e-commerce sales data, featuring descriptive analytics, customer segmentation, revenue forecasting and integrated AI chat (Claude).

🔗 **[Live Demo](https://portfolio-app-e-commerce-analysis.streamlit.app)**

---

## Overview

This project demonstrates a full data analysis pipeline applied to an e-commerce context, from data generation to AI-powered insights. It is designed as a portfolio project and can also serve as a starting point for teams needing a structured test dataset and analysis framework.

---

## Features

### 📊 Descriptive KPIs
- Key metrics: Total Revenue, Number of Orders, Total Quantity Sold, Average Basket
- Interactive sidebar filters: date range, product category, country, sales channel
- Visualizations: revenue trends over time, breakdown by country, category, and channel
- AI-powered chat assistant (Claude API) for business-oriented data interpretation

### 👥 Customer Segmentation (RFM + KMeans)
- RFM scoring: Recency, Frequency, Monetary value per customer
- KMeans clustering with adjustable number of segments (2 to 4)
- Cluster profiles labeled as VIP, Regular, Occasional, At Risk
- AI chat assistant for segment analysis and recommendations

### 📈 Revenue Forecasting (Prophet)
- Monthly revenue forecast for 2026 based on 4 years of historical data
- Confidence intervals (upper and lower bounds)
- Monthly forecast table with formatted values

---

## Dataset

The dataset is fully simulated using `dataset_ecommerce_generation.py` and contains **10,000 orders** across **500 unique customers** over the period **2022–2025**.

| Column | Description |
|---|---|
| `order_date` | Order date (2022–2025) |
| `product_id` | Product identifier (category prefix + 6-digit ID) |
| `category` | Product category (15 categories) |
| `quantity` | Units ordered (1–20) |
| `revenue` | Order revenue in € (5–500) |
| `client_id` | Customer identifier (C- + 8-digit ID) |
| `country` | Customer country (20 countries) |
| `channel` | Sales channel (Store, Web, App, Marketplace, Social Media, Email, Phone) |

> The data generation script can be reused to create custom test datasets by adjusting parameters such as the number of orders, date range, or product catalog.

---

## Tech Stack

| Tool | Usage |
|---|---|
| Python | Core language |
| Streamlit | Web application framework |
| Pandas | Data manipulation |
| Plotly | Interactive visualizations |
| Scikit-learn | KMeans clustering |
| Prophet | Time series forecasting |
| Anthropic API | AI-powered chat analysis |

---

## Project Structure

```
portfolio-streamlit-e-commerce-analysis/
├── Descriptive_KPIs.py          # Main page - KPIs and visualizations
├── pages/
│   ├── Clustering.py            # Customer segmentation page
│   └── Forecasting.py           # Revenue forecasting page
├── dataset_ecommerce_generation.py  # Simulated data generator
├── dataset_ecommerce.csv        # Generated dataset
├── requirements.txt             # Python dependencies
└── .streamlit/
    └── config.toml              # App theme configuration
```

---

## Installation

```bash
git clone https://github.com/sagoteng/portfolio-streamlit-e-commerce-analysis.git
cd portfolio-streamlit-e-commerce-analysis
pip install -r requirements.txt
```

Create a `.env` file with your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

Run the app:
```bash
streamlit run Descriptive_KPIs.py
```

---

## Author

**Enguerrand** — Data Analyst  
[GitHub](https://github.com/sagoteng)
