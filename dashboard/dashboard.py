import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="E-Commerce Analysis Dashboard", layout="wide")

# =========================
# SIMPLE STICKY HEADER (STABLE)
# =========================
st.markdown("""
<style>
.sticky-header {
    position: sticky;
    top: 0;
    background-color: white;
    padding: 15px 0px;
    font-size: 24px;
    font-weight: 600;
    z-index: 1000;
    border-bottom: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="sticky-header">📊 E-Commerce Delivery & Payment Psychology Dashboard</div>', unsafe_allow_html=True)



# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "main_data.csv")
    return pd.read_csv(file_path)

df = load_data()

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.header("🔎 Filter Data")

payment_filter = st.sidebar.multiselect(
    "Pilih Metode Pembayaran",
    options=df["payment_type"].unique(),
    default=df["payment_type"].unique()
)

late_filter = st.sidebar.multiselect(
    "Status Pengiriman",
    options=[0,1],
    default=[0,1],
    format_func=lambda x: "Tepat Waktu" if x == 0 else "Terlambat"
)

df = df[
    (df["payment_type"].isin(payment_filter)) &
    (df["is_late"].isin(late_filter))
]

# =========================
# KPI SECTION
# =========================
st.subheader("📌 Ringkasan Data")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Order", len(df))
col2.metric("Rata-rata Review", round(df["review_score"].mean(),2))
col3.metric("Rata-rata Delay (hari)", round(df["delay_days"].mean(),2))
col4.metric("Repeat Customer (%)", 
            str(round(df["is_repeat_customer"].mean()*100,2))+"%")

st.divider()

# ==================================================
# SECTION 1 — DELIVERY ANALYSIS
# ==================================================
st.header("🚚 Delivery Performance Analysis")

col1, col2 = st.columns(2)

# Proporsi Keterlambatan
with col1:
    st.subheader("Proporsi Keterlambatan")
    fig1, ax1 = plt.subplots()
    df["is_late"].value_counts().plot(kind="bar", ax=ax1)
    ax1.set_xticklabels(["Tepat Waktu","Terlambat"], rotation=0)
    ax1.set_ylabel("Jumlah Order")
    st.pyplot(fig1)

# Review vs Keterlambatan
with col2:
    st.subheader("Rata-rata Review")
    fig2, ax2 = plt.subplots()
    df.groupby("is_late")["review_score"].mean().plot(kind="bar", ax=ax2)
    ax2.set_xticklabels(["Tepat Waktu","Terlambat"], rotation=0)
    ax2.set_ylim(0,5)
    st.pyplot(fig2)

# Distribusi Delay
st.subheader("Distribusi Delay Days")
fig3, ax3 = plt.subplots()
df["delay_days"].hist(bins=50, ax=ax3)
ax3.set_xlabel("Hari Keterlambatan")
st.pyplot(fig3)

# Payment vs Late
st.subheader("Proporsi Terlambat per Metode Pembayaran")
fig4, ax4 = plt.subplots()
df.groupby("payment_type")["is_late"].mean().sort_values().plot(kind="bar", ax=ax4)
ax4.set_ylabel("Proporsi Terlambat")
st.pyplot(fig4)

st.divider()

# ==================================================
# SECTION 2 — PAYMENT PSYCHOLOGY
# ==================================================
st.header("💳 Payment Psychology Analysis")

col1, col2 = st.columns(2)

# Distribusi Payment
with col1:
    st.subheader("Distribusi Metode Pembayaran")
    fig5, ax5 = plt.subplots()
    df["payment_type"].value_counts().plot(kind="bar", ax=ax5)
    st.pyplot(fig5)

# Avg Payment Value
with col2:
    st.subheader("Rata-rata Nilai Belanja")
    fig6, ax6 = plt.subplots()
    df.groupby("payment_type")["payment_value"].mean().sort_values().plot(kind="bar", ax=ax6)
    st.pyplot(fig6)

# Loyalitas
st.subheader("Proporsi Repeat Customer")
fig7, ax7 = plt.subplots()
df.groupby("payment_type")["is_repeat_customer"].mean().sort_values().plot(kind="bar", ax=ax7)
ax7.set_ylabel("Proporsi Repeat")
st.pyplot(fig7)

# Boxplot Payment
st.subheader("Distribusi Nilai Belanja per Metode Pembayaran")
fig8, ax8 = plt.subplots()
df.boxplot(column="payment_value", by="payment_type", ax=ax8)
plt.suptitle("")
st.pyplot(fig8)

st.divider()

# =========================
# DATA PREVIEW
# =========================
st.subheader("📄 Preview Data")
st.dataframe(df.head(20))
