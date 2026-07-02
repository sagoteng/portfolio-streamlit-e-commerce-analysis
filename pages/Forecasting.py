# Library import
import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet

# Page config
st.set_page_config(page_title='Forecasting', layout='wide')

# Data loading
if 'data' not in st.session_state:
    st.session_state['data'] = pd.read_csv("dataset_ecommerce.csv")
data = st.session_state['data']
data['order_date'] = pd.to_datetime(data['order_date'])

# Prepare data for Prophet
turnover_by_month = data.groupby(data['order_date'].dt.to_period('M'))['revenue'].sum().reset_index()
turnover_by_month['order_date'] = turnover_by_month['order_date'].dt.to_timestamp()
prophet_df = turnover_by_month.rename(columns={'order_date': 'ds', 'revenue': 'y'})

# Train Prophet model
model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
model.fit(prophet_df)

# Forecast 12 months
future = model.make_future_dataframe(periods=12, freq='MS')
forecast = model.predict(future)

# Streamlit display
st.title('Revenue Forecasting')
st.markdown("---")
st.subheader("2026 Revenue Forecast")

# Merge actual vs forecast
fig = px.line()
fig.add_scatter(x=prophet_df['ds'], y=prophet_df['y'], name='Actual', line=dict(color='#4a5568'))
fig.add_scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast', line=dict(color='#a0aec0', dash='dash'))
fig.add_scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='Upper bound', line=dict(color='lightgrey', dash='dot'))
fig.add_scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='Lower bound', line=dict(color='lightgrey', dash='dot'))
st.plotly_chart(fig, use_container_width=True)

# Forecast table 2026 only
st.markdown("---")
st.subheader("Monthly Forecast Table")
forecast_2026 = forecast[forecast['ds'].dt.year == 2026][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].reset_index(drop=True)
forecast_2026.columns = ['Month', 'Forecast', 'Lower Bound', 'Upper Bound']
forecast_2026['Month'] = forecast_2026['Month'].dt.strftime('%B %Y')
st.dataframe(
    forecast_2026,
    hide_index=True,
    column_config={
        'Forecast': st.column_config.NumberColumn(format="€ %,.2f"),
        'Lower Bound': st.column_config.NumberColumn(format="€ %,.2f"),
        'Upper Bound': st.column_config.NumberColumn(format="€ %,.2f"),
    }
)