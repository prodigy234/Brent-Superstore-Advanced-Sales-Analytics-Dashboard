import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# -----------------------------------------------
# LOAD DATA
# -----------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("superstore_synthetic.csv")
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    return df

df = load_data()

# -----------------------------------------------
# SIDEBAR FILTERS
# -----------------------------------------------
st.sidebar.header("🔍 Filter Data")
regions = st.sidebar.multiselect("Select Region(s):", options=df['Region'].unique(), default=df['Region'].unique())
categories = st.sidebar.multiselect("Select Category(ies):", options=df['Category'].unique(), default=df['Category'].unique())

df_filtered = df[df['Region'].isin(regions) & df['Category'].isin(categories)]

# -----------------------------------------------
# HEADER
# -----------------------------------------------
st.title("📊 Advanced Sales Analytics Dashboard")
st.markdown("### Brent Superstore Sales Data")

# -----------------------------------------------
# KPIs
# -----------------------------------------------
total_sales = round(df_filtered['Sales'].sum(), 2)
total_profit = round(df_filtered['Profit'].sum(), 2)
total_orders = df_filtered['Order ID'].nunique()

download_summary = pd.DataFrame({
    'Metric': ['Total Sales', 'Total Profit', 'Total Orders'],
    'Value': [total_sales, total_profit, total_orders]
})

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Total Orders", total_orders)

# -----------------------------------------------
# SALES TREND
# -----------------------------------------------
st.subheader("📈 Sales Trend Over Time")
daily_sales = df_filtered.groupby('Order Date')['Sales'].sum().reset_index()
fig1 = px.line(daily_sales, x='Order Date', y='Sales', title='Daily Sales')
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------------------------
# SALES BY CATEGORY
# -----------------------------------------------
st.subheader("🛍️ Sales by Category and Sub-Category")
cat_sales = df_filtered.groupby(['Category', 'Sub-Category'])['Sales'].sum().reset_index()
fig2 = px.bar(cat_sales, x='Sub-Category', y='Sales', color='Category', title='Sales by Category')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------
# PROFIT BY REGION
# -----------------------------------------------
st.subheader("🌍 Profit by Region")
region_profit = df_filtered.groupby('Region')['Profit'].sum().reset_index()
fig3 = px.pie(region_profit, values='Profit', names='Region', title='Profit Distribution by Region')
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------------------------
# CUSTOMER SEGMENT ANALYSIS
# -----------------------------------------------
st.subheader("👤 Customer Segment Performance")
seg_profit = df_filtered.groupby('Segment')[['Sales', 'Profit']].sum().reset_index()
fig4 = px.bar(seg_profit, x='Segment', y=['Sales', 'Profit'], barmode='group', title='Segment-Wise Sales and Profit')
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------------------
# TOP PRODUCTS
# -----------------------------------------------
st.subheader("🏆 Top 10 Products by Sales")
top_products = df_filtered.groupby('Sub-Category')['Sales'].sum().nlargest(10).reset_index()
fig5 = px.bar(top_products, x='Sales', y='Sub-Category', orientation='h', title='Top 10 Products')
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------------------------
# LOSS-MAKING PRODUCTS
# -----------------------------------------------
st.subheader("❌ Loss-Making Products")
loss_products = df_filtered[df_filtered['Profit'] < 0]
loss_summary = loss_products.groupby('Sub-Category')[['Sales', 'Profit']].sum().sort_values(by='Profit').reset_index()
st.dataframe(loss_summary.head(10))

# -----------------------------------------------
# DISCOUNT IMPACT
# -----------------------------------------------
st.subheader("💸 Discount Impact on Profit")
fig6 = px.scatter(df_filtered, x='Discount', y='Profit', color='Category', title='Profit vs Discount')
st.plotly_chart(fig6, use_container_width=True)

# -----------------------------------------------
# DOWNLOAD INSIGHTS
# -----------------------------------------------
def convert_df_to_excel(df_summary, filename="insight_summary.xlsx"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_summary.to_excel(writer, sheet_name='KPIs', index=False)
        loss_summary.to_excel(writer, sheet_name='Loss Makers', index=False)
        region_profit.to_excel(writer, sheet_name='Profit by Region', index=False)
        top_products.to_excel(writer, sheet_name='Top Products', index=False)
    processed_data = output.getvalue()
    return processed_data

excel_data = convert_df_to_excel(download_summary)
st.download_button(
    label="📥 Download Summary as Excel",
    data=excel_data,
    file_name='sales_summary_report.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

# -----------------------------------------------
# RAW DATA
# -----------------------------------------------
with st.expander("🔍 View Raw Data"):
    st.dataframe(df_filtered)

st.markdown("---")
st.markdown("✅ Created with Python + Streamlit | 📬 Gbenga Kajola")
