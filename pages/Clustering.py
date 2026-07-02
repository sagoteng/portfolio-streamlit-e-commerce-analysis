#Library import
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

#Data loading
if 'data' not in st.session_state:
    st.session_state['data'] = pd.read_csv("dataset_ecommerce.csv")
data = st.session_state['data']
data['order_date'] = pd.to_datetime(data['order_date'])

#Calculate clustering metrics
order_frequency = data.groupby('client_id')['revenue'].count()
revenue_by_client = data.groupby('client_id')['revenue'].sum()
reference_date = data['order_date'].max() + pd.Timedelta(days=1)
last_purchase = data.groupby('client_id')['order_date'].max()
recency = reference_date - last_purchase

#Assemble clustering metrics into a DataFrame
rfm = pd.DataFrame({'Order Frequency':order_frequency,'Revenue by Client':revenue_by_client,'Recency':recency})

#Convert recency in number of days
rfm['Recency'] = rfm['Recency'].dt.days

#Normalize Data
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm)

#Dictionnary
cluster_labels = {
    0: '2. Regular',
    1: '3. Occasional',
    2: '1. VIP',
    3: '4. At risk'
}

#KMeans Clustering + Streamlit slider
n_clusters = st.slider("Number of clusters", min_value=2, max_value=4, value=4)
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
rfm['Label'] = rfm['Cluster'].map(cluster_labels)

#Streamlit page name
st.title('Clustering')

#Streamlit display
    #Header Clustering
st.markdown("---")
st.subheader("Clustering")
fig = px.scatter_3d(rfm, x='Order Frequency',y='Revenue by Client', z='Recency',color='Cluster')
st.plotly_chart(fig)

avg_all = rfm.drop(columns=['Label']).groupby('Cluster').mean()
avg_all['Label'] = avg_all.index.map(cluster_labels)

    #Average clustering
st.markdown("---")
st.subheader("Average Clustering table")
st.dataframe(avg_all.reset_index(),
                 hide_index=True,
                )

# IA implementation
st.markdown("---")
st.subheader("AI Analysis")

system_prompt = f"""You are an e-commerce data analyst specialized in customer segmentation.
Here is the RFM clustering data:
{avg_all.to_string()}
Cluster labels: {cluster_labels}
Answer concisely and with a business-oriented perspective."""

user_question = st.chat_input("Ask a question about your data...")

if user_question:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_question}]
    )
    st.chat_message("user").write(user_question)
    st.chat_message("assistant").write(response.content[0].text)