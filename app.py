import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px

st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("startup_funding.csv")
    return df

df = load_data()

st.title("🚀 Startup Funding Analysis Dashboard")

# -----------------------------
# DATA CLEANING
# -----------------------------
st.sidebar.header("Filters")

# Remove duplicates
df.drop_duplicates(inplace=True)

# Regex Extraction (extract domain from email)
df["Email_Domain"] = df["Contact_Email"].apply(
    lambda x: re.search("@(.+)", x).group(1) if pd.notnull(x) else None
)

# Transform Funding to Millions
df["Funding_Millions"] = df["Funding_Amount"] / 1_000_000

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
industry_filter = st.sidebar.multiselect(
    "Select Industry",
    options=df["Industry"].unique(),
    default=df["Industry"].unique()
)

stage_filter = st.sidebar.multiselect(
    "Select Funding Stage",
    options=df["Funding_Stage"].unique(),
    default=df["Funding_Stage"].unique()
)

year_filter = st.sidebar.slider(
    "Select Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (2018, 2025)
)

filtered_df = df[
    (df["Industry"].isin(industry_filter)) &
    (df["Funding_Stage"].isin(stage_filter)) &
    (df["Year"].between(year_filter[0], year_filter[1]))
]

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Startups", len(filtered_df))
col2.metric("Total Funding (₹ Millions)", round(filtered_df["Funding_Millions"].sum(), 2))
col3.metric("Average Funding", round(filtered_df["Funding_Millions"].mean(), 2))
col4.metric("Top Industry", filtered_df["Industry"].mode()[0] if not filtered_df.empty else "N/A")

st.divider()

# -----------------------------
# VISUALIZATIONS
# -----------------------------

# Funding by Industry
fig1 = px.bar(
    filtered_df.groupby("Industry")["Funding_Millions"].sum().reset_index(),
    x="Industry",
    y="Funding_Millions",
    title="Funding by Industry"
)

st.plotly_chart(fig1, use_container_width=True)

# Funding Trend
fig2 = px.line(
    filtered_df.groupby("Year")["Funding_Millions"].sum().reset_index(),
    x="Year",
    y="Funding_Millions",
    title="Yearly Funding Trend"
)

st.plotly_chart(fig2, use_container_width=True)

# City-wise Funding
fig3 = px.pie(
    filtered_df,
    names="City",
    values="Funding_Millions",
    title="City-wise Funding Distribution"
)

st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# BUSINESS INSIGHTS
# -----------------------------
st.subheader("📊 Business Insights & Recommendations")

if not filtered_df.empty:
    top_industry = filtered_df.groupby("Industry")["Funding_Millions"].sum().idxmax()
    top_city = filtered_df.groupby("City")["Funding_Millions"].sum().idxmax()
    top_stage = filtered_df.groupby("Funding_Stage")["Funding_Millions"].sum().idxmax()

    st.success(f"""
    🔥 **Top Performing Industry:** {top_industry}  
    🌍 **Best Funding City:** {top_city}  
    💰 **Most Funded Stage:** {top_stage}
    """)

    st.info("""
    📌 Recommendations:
    - Focus investment in high-growth industries.
    - Expand operations in top-performing cities.
    - Investors should prioritize startups in growth stages.
    - Emerging industries show strong upward trends — early investment opportunity.
    """)
else:
    st.warning("No data available for selected filters.")

st.divider()

st.subheader("🔎 Raw Data Preview")
st.dataframe(filtered_df.head(50))
