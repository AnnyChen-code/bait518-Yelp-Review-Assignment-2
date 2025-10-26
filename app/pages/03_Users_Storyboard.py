import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from app.utils.data_loader import load_users

st.set_page_config(page_title="Users Story Board", page_icon="👤", layout="wide")

st.title("Part C: Users Story Board")

users_df = load_users(errors="ignore")
if users_df is None or users_df.empty:
    st.warning("User table not found. Place `user.csv` or `user.parquet` under `data/`.")
    st.stop()

# Derived features
if "yelping_since" in users_df.columns:
    users_df["account_age_years"] = (
        (pd.Timestamp.today() - users_df["yelping_since"]).dt.days / 365.25
    )
else:
    users_df["account_age_years"] = np.nan

# 1) Distribution of user review counts
st.subheader("Distribution of user review counts")
fig1 = px.histogram(users_df, x="review_count", nbins=50, title="Histogram of review counts per user")
st.plotly_chart(fig1, use_container_width=True)

# 2) Relationship between fans and average stars (or review_count as fallback)
st.subheader("Do more popular users (fans) rate differently?")
y_axis = "avg_stars" if "avg_stars" in users_df.columns else "review_count"
fig2 = px.scatter(
    users_df,
    x="fans" if "fans" in users_df.columns else "num_friends",
    y=y_axis,
    trendline="ols",
    labels={"x": "Fans" if "fans" in users_df.columns else "Friends", "y": y_axis.replace("_", " ").title()},
    title=(
        "Fans vs Average Stars" if y_axis == "avg_stars" else "Fans vs Review Count"
    ),
)
st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "These charts can reveal heavy-tailed behavior (power users) and whether popularity ties to rating style."
)
