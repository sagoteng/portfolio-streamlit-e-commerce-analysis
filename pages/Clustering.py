# Library import
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Page config
st.set_page_config(page_title='Customer Segmentation', layout='wide')

# Data loading
if 'data' not in st.session_state:
    st.session_state['data'] = pd.read_csv("dataset_ecommerce.csv")
data = st.session_state['data']
data['order_date'] = pd.to_datetime(data['order_date'])

# Fixed number of clusters
n_clusters = 4

# RFM Calculations
order_frequency = data.groupby('client_id')['revenue'].count()
revenue_by_client = data.groupby('client_id')['revenue'].sum()
reference_date = data['order_date'].max() + pd.Timedelta(days=1)
last_purchase = data.groupby('client_id')['order_date'].max()
recency = reference_date - last_purchase

rfm = pd.DataFrame({
    'Order Frequency': order_frequency,
    'Revenue by Client': revenue_by_client,
    'Recency': recency
})
rfm['Recency'] = rfm['Recency'].dt.days

# Normalize & cluster
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm)

cluster_labels = {
    0: '🥈 Regular',
    1: '🎯 Occasional',
    2: '👑 VIP',
    3: '⚠️ At Risk'
}

cluster_recommendations = {
    0: 'Regular customers with upsell potential. Offer loyalty rewards and cross-selling opportunities.',
    1: 'Low-engagement occasional buyers. Re-engage with targeted promotions and entry-level offers.',
    2: 'Top customers — high frequency and spend. Priority: VIP program, exclusive access, premium service.',
    3: 'Inactive customers. Launch urgent reactivation campaign with a special offer before losing them permanently.'
}

kmeans = KMeans(n_clusters=n_clusters, random_state=42)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
rfm['Label'] = rfm['Cluster'].map(cluster_labels)

# Average table
avg_all = rfm.drop(columns=['Label']).groupby('Cluster').mean().round(1)
avg_all['Label'] = avg_all.index.map(cluster_labels)
avg_all['Nb Clients'] = rfm.groupby('Cluster').size()
avg_all = avg_all[['Label', 'Nb Clients', 'Order Frequency', 'Revenue by Client', 'Recency']]
avg_all.columns = ['Segment', 'Nb Clients', 'Avg Frequency', 'Avg Revenue (€)', 'Avg Recency (days)']

# System prompt
system_prompt = f"""You are a CRM analyst addressing the management of an e-commerce company. Your tone is professional and action-oriented.

Here is the RFM customer segmentation:
{avg_all.to_string()}

Your analysis should:
- Comment on the distribution of customers across segments
- Identify priority segments
- Propose concrete marketing actions per segment
- Flag at-risk customers

Respond concisely and in a structured way."""

# AI Chat
st.sidebar.header("AI Analysis")

if 'messages_clustering' not in st.session_state:
    st.session_state['messages_clustering'] = []

user_question = st.sidebar.text_input("Ask a question about the segmentation...")
chat_container = st.sidebar.container()

if user_question:
    st.session_state['messages_clustering'].append({"role": "user", "content": user_question})
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=st.session_state['messages_clustering']
    )
    st.session_state['messages_clustering'].append({"role": "assistant", "content": response.content[0].text})

for msg in st.session_state['messages_clustering']:
    if msg['role'] == 'user':
        st.sidebar.write("**You:** " + msg['content'])
    else:
        st.sidebar.write("**AI:** " + msg['content'])

# Page title
st.title('Customer Segmentation — RFM')
st.caption("Segmentation based on Recency, Frequency and Monetary value of each customer.")

# Cluster profile cards
st.markdown("---")
st.subheader("Segment Profiles")
# Display order 
display_order = ['👑 VIP', '🥈 Regular', '🎯 Occasional', '⚠️ At Risk']
avg_all_sorted = avg_all.set_index('Segment').reindex(display_order).reset_index()

cols = st.columns(n_clusters)
for i, col in enumerate(cols):
    row = avg_all_sorted.iloc[i]
    cluster_num = avg_all[avg_all['Segment'] == row['Segment']].index[0]
    with col:
        st.markdown(f"### {row['Segment']}")
        st.metric("Nb of clients", f"{int(row['Nb Clients']):,}")
        st.metric("Avg Revenue", f"{row['Avg Revenue (€)']:,.0f} €")
        st.metric("Avg Frequency", f"{row['Avg Frequency']:.0f} orders")
        st.metric("Avg Recency", f"{row['Avg Recency (days)']:.0f} days")
        st.caption(cluster_recommendations.get(cluster_num, ""))

# Scatter plots 2D
st.markdown("---")
st.subheader("Segment Visualization")
col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(rfm, x='Revenue by Client', y='Recency',
                     color='Label', title='Revenue vs Recency',
                     labels={'Revenue by Client': 'Total Revenue (€)', 'Recency': 'Recency (days)', 'Label': 'Segment'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(rfm, x='Order Frequency', y='Revenue by Client',
                     color='Label', title='Frequency vs Revenue',
                     labels={'Order Frequency': 'Nb Orders', 'Revenue by Client': 'Total Revenue (€)', 'Label': 'Segment'})
    st.plotly_chart(fig, use_container_width=True)

# Summary table
st.markdown("---")
st.subheader("Summary Table")
st.dataframe(
    avg_all.reset_index(drop=True),
    hide_index=True,
    column_config={
        'Avg Revenue (€)': st.column_config.NumberColumn(format="€ %,.0f"),
    }
)