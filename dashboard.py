import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# Content
def create_monthly_orders_df(df):
    monthly_orders_df = (
        df[df['order_approved_at'].dt.year == 2017]
        .resample('M', on='order_approved_at')
        .agg({
            "order_id": "nunique",
            "price": "sum"
        })
        .reset_index()
        .rename(columns={"order_id": "order_count", 
                         "price": "revenue"})
    )

    monthly_orders_df['order_approved_at'] = pd.to_datetime(monthly_orders_df['order_approved_at'])
    
    return monthly_orders_df

def create_average_delivery_time(df):
    delivery_time = df["order_estimated_delivery_date"] - df["order_approved_at"]
    delivery_time = delivery_time.apply(lambda x: x.total_seconds() / 86400)  # Convert to days
    df["delivery_time"] = round(delivery_time, 2)  # Round to two decimal places
    
    return df['delivery_time'].mean()

def create_customer_df(df):
    customer_df = df.groupby(by="customer_city").customer_id.nunique().sort_values(ascending=False)
    return customer_df

main_data = pd.read_csv("main_data.csv")

datetime_columns = ["order_approved_at", "order_estimated_delivery_date"]
main_data.sort_values(by="order_approved_at", inplace=True)
main_data.reset_index(inplace=True)
 
for column in datetime_columns:
    main_data[column] = pd.to_datetime(main_data[column])

min_date = main_data["order_approved_at"].min()
max_date = main_data["order_approved_at"].max()

with st.sidebar:
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = main_data[(main_data["order_approved_at"] >= str(start_date)) & 
                (main_data["order_approved_at"] <= str(end_date))]

monthly_orders_df = create_monthly_orders_df(main_df)
average_delivery_time = create_average_delivery_time(main_df)
customer_df = create_customer_df(main_df)

# Header
st.title('E-commerce Dashboard')
st.text('created by Bintang Bakkara')

st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
#Tampilkan pertanyaan 2: Berapa rata-rata waktu pengiriman?
with col2:
    average_delivery_time = create_average_delivery_time(main_df.copy())
    st.metric("Rata-rata Delivery Time", f"{average_delivery_time:.2f} hari")

# Tampilkan pertanyaan 1: Apa saja sepuluh kota dengan jumlah pelanggan terbanyak?
st.text("10 Kota dengan Jumlah Pelanggan Terbanyak")
st.write(customer_df.head(10))
# Buat plot persebaran pelanggan
fig, ax = plt.subplots(figsize=(17, 8))
ax.bar(customer_df.index[:10], customer_df.head(10))
ax.set_title("Persebaran Pelanggan Berdasarkan Kota")
ax.set_xlabel("Kota")
ax.set_ylabel("Jumlah Pelanggan")
st.pyplot(fig)

#Tampilkan pertanyaan 3: Bagaimana trend pesanan selama tahun 2017?
fig, ax = plt.subplots(figsize=(17, 8))
st.text("Trend Pesanan sepanjang tahun 2017")
ax.plot(
    monthly_orders_df["order_approved_at"].dt.strftime('%B'), 
    monthly_orders_df["order_count"], 
    marker='o', 
    linewidth=2, 
    color="#72BCD4")
ax.set_title("Jumlah Order per Bulan (2017)", 
             loc="center", 
             fontsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)