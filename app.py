"""
app.py
Interactive Streamlit sales analytics dashboard.
Pulls data live from MySQL, lets the user filter by date/region/category,
and visualizes KPIs and trends with Plotly.

Run with:
    streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from db_config import get_connection

st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")


# ---------------------------------------------------------------------------
# Data loading (cached so we don't hit MySQL on every filter interaction)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=600)
def load_data() -> pd.DataFrame:
    """Pulls a flat, denormalized view of orders joined with items/products/customers."""
    query = """
        SELECT
            o.order_id,
            o.order_date,
            o.region,
            o.status,
            c.segment,
            p.product_name,
            p.category,
            oi.quantity,
            oi.unit_price,
            (oi.quantity * oi.unit_price) AS line_revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


df = load_data()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

min_date, max_date = df["order_date"].min(), df["order_date"].max()
date_range = st.sidebar.date_input("Order date range", value=(min_date, max_date),
                                    min_value=min_date, max_value=max_date)

regions = st.sidebar.multiselect("Region", options=sorted(df["region"].unique()),
                                  default=sorted(df["region"].unique()))

categories = st.sidebar.multiselect("Category", options=sorted(df["category"].unique()),
                                     default=sorted(df["category"].unique()))

statuses = st.sidebar.multiselect("Order status", options=sorted(df["status"].unique()),
                                   default=["Completed"])

if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

# Apply filters
mask = (
    (df["order_date"] >= pd.to_datetime(date_range[0]))
    & (df["order_date"] <= pd.to_datetime(date_range[1]))
    & (df["region"].isin(regions))
    & (df["category"].isin(categories))
    & (df["status"].isin(statuses))
)
filtered = df[mask]

# ---------------------------------------------------------------------------
# Header + KPI cards
# ---------------------------------------------------------------------------
st.title("📊 Sales Analytics Dashboard")
st.caption("Live data from MySQL · filters apply to every chart below")

total_revenue = filtered["line_revenue"].sum()
total_orders = filtered["order_id"].nunique()
avg_order_value = total_revenue / total_orders if total_orders else 0
total_units = filtered["quantity"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"${total_revenue:,.0f}")
k2.metric("Total Orders", f"{total_orders:,}")
k3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
k4.metric("Units Sold", f"{total_units:,}")

st.divider()

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("Revenue Trend")
    trend = (
        filtered.groupby(filtered["order_date"].dt.to_period("W"))["line_revenue"]
        .sum()
        .reset_index()
    )
    trend["order_date"] = trend["order_date"].dt.start_time
    fig_trend = px.line(trend, x="order_date", y="line_revenue",
                         labels={"order_date": "Week", "line_revenue": "Revenue ($)"},
                         markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.subheader("Revenue by Category")
    by_cat = filtered.groupby("category")["line_revenue"].sum().reset_index()
    fig_cat = px.pie(by_cat, names="category", values="line_revenue", hole=0.4)
    st.plotly_chart(fig_cat, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Revenue by Region")
    by_region = filtered.groupby("region")["line_revenue"].sum().sort_values(ascending=False).reset_index()
    fig_region = px.bar(by_region, x="region", y="line_revenue",
                         labels={"line_revenue": "Revenue ($)"}, color="region")
    st.plotly_chart(fig_region, use_container_width=True)

with col4:
    st.subheader("Top 10 Products")
    top_products = (
        filtered.groupby("product_name")["line_revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig_products = px.bar(top_products, x="line_revenue", y="product_name", orientation="h",
                           labels={"line_revenue": "Revenue ($)", "product_name": ""})
    fig_products.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_products, use_container_width=True)

st.subheader("Customer Segment Breakdown")
by_segment = filtered.groupby(["segment", "category"])["line_revenue"].sum().reset_index()
fig_segment = px.bar(by_segment, x="segment", y="line_revenue", color="category",
                      labels={"line_revenue": "Revenue ($)"}, barmode="stack")
st.plotly_chart(fig_segment, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Raw data + export
# ---------------------------------------------------------------------------
with st.expander("View filtered raw data"):
    st.dataframe(filtered, use_container_width=True)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_sales_data.csv", "text/csv")
