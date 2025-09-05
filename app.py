import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ---------- Load & Save ----------
def load_data():
    return pd.read_csv("inventory.csv")

def save_data(df):
    df.to_csv("inventory.csv", index=False)

def log_action(action, product, old, new):
    with open("audit_log.csv", "a") as f:
        f.write(f"{datetime.now()},{action},{product},{old},{new}\n")

# ---------- App ----------
st.set_page_config(page_title="Inventory Dashboard", layout="wide")
st.title("📦 Inventory Management Dashboard")

# Load data
df = load_data()

# ---------- File Upload ----------
uploaded = st.file_uploader("Upload Inventory (CSV/Excel)", type=["csv", "xlsx"])
if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)
    save_data(df)
    st.success("Inventory updated from uploaded file.")

# ---------- KPI Cards ----------
col1, col2, col3 = st.columns(3)
total_stock = df["Stock"].sum()
fill_rate = 0.95  # Placeholder metric
doh = round(total_stock / (df["ReorderLevel"].mean() + 1), 1)
turnover = round(total_stock / df["ReorderLevel"].sum(), 2)

col1.metric("Total Stock Units", total_stock)
col2.metric("Days on Hand (avg)", doh)
col3.metric("Inventory Turnover", turnover)

# ---------- Current Inventory ----------
st.subheader("Current Inventory")
st.dataframe(df)

# ---------- Low Stock Alerts ----------
st.subheader("Low Stock Alerts")
low_stock = df[df["Stock"] < df["ReorderLevel"]]

if not low_stock.empty:
    st.warning("⚠️ Low stock items detected!")

    # Highlight only the Stock column
    def highlight_low_stock(val):
        if val < 5:
            return 'background-color: #00008B; color: white;'  # critical = deep red
        return 'background-color: #ffcccc;'  # warning = light red

    styled = low_stock.style.applymap(highlight_low_stock, subset=['Stock'])
    st.dataframe(styled)

    # Export option
    if st.button("Export Low Stock Report"):
        low_stock.to_csv("low_stock_report.csv", index=False)
        st.success("Low stock report exported (low_stock_report.csv)")
else:
    st.success("✅ All items sufficiently stocked.")
# ---------- Charts ----------
st.subheader("Stock Analysis")

# Pie chart: stock by category
if "Category" in df.columns:
    st.write("Stock Distribution by Category")
    fig1, ax1 = plt.subplots()
    df.groupby("Category")["Stock"].sum().plot.pie(autopct="%1.1f%%", ax=ax1)
    st.pyplot(fig1)

# Bar chart: top 5 low stock items
st.write("Top 5 Low Stock Items")
fig2, ax2 = plt.subplots()
low_top5 = df.nsmallest(5, "Stock")
ax2.bar(low_top5["Product"], low_top5["Stock"], color="red")
plt.xticks(rotation=45)
st.pyplot(fig2)

# ---------- Update Stock ----------
st.subheader("Update Stock")
product = st.selectbox("Select product", df["Product"])
new_stock = st.number_input("Enter new stock level", min_value=0)
if st.button("Update Inventory"):
    old_stock = int(df.loc[df["Product"] == product, "Stock"].values[0])
    df.loc[df["Product"] == product, "Stock"] = new_stock
    save_data(df)
    log_action("UPDATE", product, old_stock, new_stock)
    st.success(f"Stock updated for {product}: {new_stock} units")

# ---------- Audit Log ----------
st.subheader("Audit Log")
try:
    log_df = pd.read_csv("audit_log.csv", names=["Time", "Action", "Product", "Old", "New"])
    st.dataframe(log_df.tail(10))
except:
    st.info("No audit log yet.")
