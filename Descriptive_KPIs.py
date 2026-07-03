#Web App streamlit to visualize e-commerce data and get AI insight to improve turnover

#Library import
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

#Streamlit browser page configuration
st.set_page_config(page_title='e-commerce-analyses', layout='wide')

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload your file (CSV or Excel)", type=["csv", "xlsx"])
if uploaded_file is not None:
    if uploaded_file.name.endswith('.xlsx'):
        st.session_state['data'] = pd.read_excel(uploaded_file)
    else:
        st.session_state['data'] = pd.read_csv(uploaded_file)
else:
    if 'data' not in st.session_state:
        st.session_state['data'] = pd.read_csv("dataset_ecommerce.csv")
data = st.session_state['data']
data['order_date'] = pd.to_datetime(data['order_date'])

#IA Chat
st.sidebar.subheader("AI Analysis")
user_question = st.sidebar.text_input("Ask a question about your data...")
chat_container = st.sidebar.container()

# Streamlit filters
st.sidebar.markdown("---")
st.sidebar.header("Filters")
last_year = data['order_date'].dt.year.max()
default_start = pd.Timestamp(f"{last_year}-01-01")
default_end = data['order_date'].max()

start = st.sidebar.date_input("Date de début", value=default_start)
end = st.sidebar.date_input("Date de fin", value=default_end)
selected_categories = st.sidebar.multiselect("Category", options=data['category'].unique(), default=data['category'].unique())
selected_countries = st.sidebar.multiselect("Country", options=data['country'].unique(), default=data['country'].unique())
selected_channels = st.sidebar.multiselect("Channel", options=data['channel'].unique(), default=data['channel'].unique())

filtered_data = data [
   (data['order_date'] >= pd.Timestamp(start)) &
   (data['order_date'] <= pd.Timestamp(end)) &
   (data['category'].isin(selected_categories)) &
   (data['country'].isin(selected_countries)) &
   (data['channel'].isin(selected_channels))
]

#Streamlit page name
st.title('E-commerce Analyses')

#Global KPIs
total_turnover = filtered_data ['revenue'].sum()
order_nb = len(filtered_data)
total_quantity = filtered_data ['quantity'].sum()
average_basket = total_turnover / order_nb
turnover_by_country = filtered_data.groupby('country')['revenue'].sum()
turnover_by_category = filtered_data.groupby('category')['revenue'].sum()
turnover_by_month = filtered_data.groupby(filtered_data['order_date'].dt.to_period('M'))['revenue'].sum().reset_index()
turnover_by_month['order_date'] = turnover_by_month['order_date'].astype(str)
quantity_by_category = filtered_data.groupby('category')['quantity'].sum()
system_prompt = f""" You are an e-commerce data analyst. Here is the store's data: 
    - Total revenue: {total_turnover}
    - Total orders: {order_nb}
    - Average basket: {average_basket}
    - turnover by country : {turnover_by_country}
    - turnover by month : {turnover_by_month}
    - turnover by category : {turnover_by_category}
    Answer concisely and with a business-oriented perspective."""
if user_question:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_question}]
    )
    chat_container.write("**You:** " + user_question)
    chat_container.write("**AI:** " + response.content[0].text)

turnover_by_channel = filtered_data.groupby('channel')['revenue'].sum()
orders_by_channel = filtered_data.groupby('channel')['revenue'].count()
avg_basket_by_channel = turnover_by_channel / orders_by_channel


# Calculation previous period
period_duration = (pd.Timestamp(end) - pd.Timestamp(start)).days
prev_start = pd.Timestamp(start) - pd.Timedelta(days=period_duration)
prev_end = pd.Timestamp(start) - pd.Timedelta(days=1)

prev_data = data[
    (data['order_date'] >= prev_start) &
    (data['order_date'] <= prev_end) &
    (data['category'].isin(selected_categories)) &
    (data['country'].isin(selected_countries)) &
    (data['channel'].isin(selected_channels))
]

prev_revenue = prev_data['revenue'].sum()
prev_average_basket = prev_data['revenue'].sum() / len(prev_data) if len(prev_data) > 0 else 0

delta_revenue = total_turnover - prev_revenue
delta_basket = average_basket - prev_average_basket
prev_orders = len(prev_data)
delta_orders = order_nb - prev_orders
prev_quantity = prev_data['quantity'].sum() if len(prev_data) > 0 else 0
delta_quantity = total_quantity - prev_quantity

# Less performing Canal
worst_channel = turnover_by_channel.idxmin()
worst_channel_revenue = turnover_by_channel.min()

# Loss of speed of a category
prev_turnover_by_category = prev_data.groupby('category')['revenue'].sum()
category_growth = ((turnover_by_category - prev_turnover_by_category) / prev_turnover_by_category * 100).dropna()
worst_category = category_growth.idxmin()
worst_category_growth = category_growth.min()


#Streamlit display

    #Header main KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Turnover", f"{total_turnover:,.2f} €",delta=f"{delta_revenue:+,.2f} €")
col2.metric("Number of orders", f"{order_nb:,}",delta=f"{delta_orders:+}")
col3.metric(label="Total quantity", value=f"{total_quantity:,}",delta=f"{delta_quantity:+}")
col4.metric("Average basket", f"{average_basket:,.2f} €",delta=f"{delta_basket:+,.2f} €")

# Alerts
st.markdown("---")
st.subheader("⚠️ Alerts")

if delta_revenue < 0:
    st.error(f"⚠️ Revenue down vs previous period: {delta_revenue:,.2f} €")
else:
    st.success(f"✅ Revenue up vs previous period: +{delta_revenue:,.2f} €")

if delta_basket < 0:
    st.warning(f"⚠️ Average basket down vs previous period: {delta_basket:,.2f} €")
else:
    st.success(f"✅ Average basket up vs previous period: +{delta_basket:,.2f} €")

st.warning(f"⚠️ Lowest performing channel: {worst_channel} ({worst_channel_revenue:,.2f} €)")

if worst_category_growth < -10:
    st.error(f"⚠️ Category in sharp decline: {worst_category} ({worst_category_growth:.1f}% vs previous period)")
elif worst_category_growth < 0:
    st.warning(f"⚠️ Category in decline: {worst_category} ({worst_category_growth:.1f}% vs previous period)")    
 #Turnover by month
st.markdown("---")
st.subheader("Turnover by Month")
fig = px.line(turnover_by_month, x = 'order_date', y = 'revenue',color_discrete_sequence=["#4a5568"])
st.plotly_chart(fig)

    #Turnover by country
st.markdown("---")
st.subheader("Turnover by Country")
col1, col2 = st.columns(2)
with col1:
    st.dataframe(turnover_by_country.reset_index().rename(columns={'country': 'Country', 'revenue': 'Turnover'}),
                 hide_index=True,
                 column_config={
                    'Turnover': st.column_config.NumberColumn(format="€ %,.2f")
                })
with col2:
    fig = px.pie(data, names='country',values='revenue')
    st.plotly_chart(fig)

    #Turnover by category
st.markdown("---")
st.subheader("Turnover by Category")
col1, col2 = st.columns(2)
with col1:
    st.dataframe(turnover_by_category.reset_index().rename(columns={'category': 'Category', 'revenue': 'Turnover'}),
                 hide_index=True,
                 column_config={
                    'Turnover': st.column_config.NumberColumn(format="€ %,.2f")
                })
with col2:
    fig = px.bar(turnover_by_category.reset_index(), x ='category', y='revenue', color_discrete_sequence=["#4a5568"])
    st.plotly_chart(fig)

    #Quantity by category
st.markdown("---")
st.subheader("Quantity by Category")
col1, col2 = st.columns(2)
with col1:
    st.dataframe(quantity_by_category.reset_index().rename(columns={'category': 'Category', 'quantity': 'Quantity'}),
                 hide_index=True,
                 )
with col2:
    fig = px.bar(quantity_by_category.reset_index(), x ='category', y='quantity', color_discrete_sequence=["#4a5568"])
    st.plotly_chart(fig)

#Turnover by channel
st.markdown("---")
st.subheader("Performance by Channel")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Turnover by Channel**")
    fig = px.bar(turnover_by_channel.reset_index(), x='channel', y='revenue',color_discrete_sequence=["#4a5568"])
    fig.update_traces(hovertemplate='%{x}<br>€ %{y:,.2f}')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Orders by Channel**")
    fig = px.bar(orders_by_channel.reset_index(), x='channel', y='revenue',color_discrete_sequence=["#4a5568"])
    fig.update_traces(hovertemplate='%{x}<br>%{y}')
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("**Average Basket by Channel**")
    avg_basket_df = avg_basket_by_channel.reset_index()
    avg_basket_df.columns = ['channel', 'avg_basket']
    fig = px.bar(avg_basket_df, x='channel', y='avg_basket',color_discrete_sequence=["#4a5568"])
    fig.update_traces(hovertemplate='%{x}<br>€ %{y:,.2f}')
    st.plotly_chart(fig, use_container_width=True)