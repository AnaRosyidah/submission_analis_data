import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="E-Commerce Analysis Dashboard", layout="wide")

st.title("📊 E-Commerce Delivery & Payment Analysis Dashboard (2017–2018)")

st.markdown("""
Dashboard ini dibuat untuk menjawab dua pertanyaan bisnis:
1. Pengaruh keterlambatan pengiriman terhadap review, nilai transaksi, dan repeat customer.
2. Perbedaan nilai transaksi dan loyalitas berdasarkan metode pembayaran.
""")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "main_data.csv")
    df = pd.read_csv(file_path)
    return df

df = load_data()

# =========================
# PREPROCESSING
# =========================
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df["year"] = df["order_purchase_timestamp"].dt.year
df["month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.header("🔎 Filter Data")

year_filter = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(df["year"].unique()),
    default=sorted(df["year"].unique())
)

month_filter = st.sidebar.multiselect(
    "Pilih Bulan",
    options=sorted(df["month"].unique()),
    default=sorted(df["month"].unique())
)

payment_filter = st.sidebar.multiselect(
    "Metode Pembayaran",
    options=df["payment_type"].unique(),
    default=df["payment_type"].unique()
)

late_filter = st.sidebar.multiselect(
    "Status Pengiriman",
    options=[0, 1],
    default=[0, 1],
    format_func=lambda x: "Tepat Waktu" if x == 0 else "Terlambat"
)

df = df[
    (df["year"].isin(year_filter)) &
    (df["month"].isin(month_filter)) &
    (df["payment_type"].isin(payment_filter)) &
    (df["is_late"].isin(late_filter))
]

# =========================
# KPI SECTION
# =========================
st.subheader("📌 Ringkasan Utama")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Order", len(df))
col2.metric("Rata-rata Review", round(df["review_score"].mean(), 2))
col3.metric("Rata-rata Delay (Hari)", round(df["delay_days"].mean(), 2))
col4.metric("Repeat Customer (%)",
            str(round(df["is_repeat_customer"].mean() * 100, 2)) + "%")

st.divider()

# ==================================================
# SECTION 1 — DELIVERY IMPACT
# ==================================================
st.header("🚚 1. Dampak Keterlambatan Pengiriman")

col1, col2 = st.columns(2)

# Proporsi Keterlambatan
with col1:
    st.subheader("Distribusi Ketepatan Pengiriman")
    fig1, ax1 = plt.subplots()
    df["is_late"].value_counts().sort_index().plot(kind="bar", ax=ax1)
    ax1.set_xticklabels(["Tepat Waktu", "Terlambat"], rotation=0)
    ax1.set_ylabel("Jumlah Order")
    st.pyplot(fig1)

# Review vs Late
with col2:
    st.subheader("Rata-rata Review Berdasarkan Status Pengiriman")
    fig2, ax2 = plt.subplots()
    df.groupby("is_late")["review_score"].mean().plot(kind="bar", ax=ax2)
    ax2.set_xticklabels(["Tepat Waktu", "Terlambat"], rotation=0)
    ax2.set_ylim(0, 5)
    ax2.set_ylabel("Rata-rata Review")
    st.pyplot(fig2)

# Repeat vs Late
st.subheader("Repeat Customer Berdasarkan Status Pengiriman")
fig3, ax3 = plt.subplots()
df.groupby("is_late")["is_repeat_customer"].mean().plot(kind="bar", ax=ax3)
ax3.set_xticklabels(["Tepat Waktu", "Terlambat"], rotation=0)
ax3.set_ylabel("Proporsi Repeat")
st.pyplot(fig3)

# Trend Review Bulanan
st.subheader("Trend Rata-rata Review per Bulan")
fig4, ax4 = plt.subplots()
df.groupby("month")["review_score"].mean().plot(ax=ax4)
plt.xticks(rotation=45)
ax4.set_ylabel("Rata-rata Review")
st.pyplot(fig4)

st.info("""
Insight:
Pesanan yang terlambat cenderung memiliki review lebih rendah
dan tingkat repeat customer yang lebih kecil dibanding pesanan tepat waktu.
""")

st.divider()

# ==================================================
# SECTION 2 — PAYMENT ANALYSIS
# ==================================================
st.header("💳 2. Analisis Metode Pembayaran")

col1, col2 = st.columns(2)

# Distribusi Payment
with col1:
    st.subheader("Distribusi Metode Pembayaran")
    fig5, ax5 = plt.subplots()
    df["payment_type"].value_counts().plot(kind="bar", ax=ax5)
    ax5.set_ylabel("Jumlah Order")
    st.pyplot(fig5)

# Avg Payment Value
with col2:
    st.subheader("Rata-rata Nilai Transaksi")
    fig6, ax6 = plt.subplots()
    df.groupby("payment_type")["payment_value"].mean().sort_values().plot(kind="bar", ax=ax6)
    ax6.set_ylabel("Rata-rata Nilai Transaksi")
    st.pyplot(fig6)

# Repeat per Payment
st.subheader("Proporsi Repeat Customer per Metode Pembayaran")
fig7, ax7 = plt.subplots()
df.groupby("payment_type")["is_repeat_customer"].mean().sort_values().plot(kind="bar", ax=ax7)
ax7.set_ylabel("Proporsi Repeat")
st.pyplot(fig7)

# Boxplot
st.subheader("Distribusi Nilai Belanja per Metode Pembayaran")
fig8, ax8 = plt.subplots()
df.boxplot(column="payment_value", by="payment_type", ax=ax8)
plt.suptitle("")
plt.xticks(rotation=45)
st.pyplot(fig8)

st.info("""
Insight:
Metode pembayaran tertentu menunjukkan rata-rata transaksi
dan tingkat loyalitas yang berbeda, sehingga dapat digunakan
untuk strategi segmentasi pelanggan.
""")

st.divider()

# =========================
# DATA PREVIEW
# =========================
st.subheader("📄 Preview Data")
st.dataframe(df.head(20))