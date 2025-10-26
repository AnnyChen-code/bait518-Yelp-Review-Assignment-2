import pandas as pd
import plotly.express as px
import streamlit as st

from app.utils.data_loader import load_business, load_reviews, vancouver_restaurants_only

st.set_page_config(page_title="Review Dynamics", page_icon="⭐", layout="wide")

st.title("Part B: Review Dynamics Story Board")

business_df = load_business(errors="ignore")
reviews_df = load_reviews(errors="ignore")

if business_df is None or reviews_df is None:
    st.warning("Business or review table not found. Place files under `data/`.")
    st.stop()

restaurants = vancouver_restaurants_only(business_df)[["id", "name"]]
reviews_df = reviews_df.merge(restaurants, how="inner", left_on="id", right_on="id")

if "date" not in reviews_df.columns or reviews_df["date"].isna().all():
    st.warning("Review table lacks a usable `date` column; cannot compute dynamics.")
    st.stop()

reviews_df = reviews_df.dropna(subset=["date"]).copy()
reviews_df["year"] = reviews_df["date"].dt.year
reviews_df["month"] = reviews_df["date"].dt.to_period("M").astype(str)

# 1) Distribution of review stars over years
st.subheader("Star distribution over years")
star_by_year = reviews_df.groupby(["year"]) ["stars"].value_counts().rename("count").reset_index()
fig1 = px.bar(
    star_by_year,
    x="year",
    y="count",
    color="stars",
    barmode="stack",
    title="Counts of review stars by year",
)
st.plotly_chart(fig1, use_container_width=True)

# 2) COVID-19 impact visuals
st.subheader("Impact of COVID-19 on Yelp reviews (Vancouver restaurants)")

reviews_df["year_month"] = reviews_df["date"].dt.to_period("M").dt.to_timestamp()
monthly = reviews_df.groupby("year_month").agg(
    review_count=("stars", "count"),
    avg_stars=("stars", "mean"),
).reset_index()

fig2 = px.line(
    monthly,
    x="year_month",
    y="review_count",
    title="Monthly review volume",
)
fig2.add_vline(x=pd.Timestamp("2020-03-01"), line_dash="dash", line_color="red")
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.line(
    monthly,
    x="year_month",
    y="avg_stars",
    title="Monthly average star rating",
)
fig3.add_vline(x=pd.Timestamp("2020-03-01"), line_dash="dash", line_color="red")
st.plotly_chart(fig3, use_container_width=True)

st.caption(
    "Dashed red line denotes March 2020 (COVID-19 onset)."
)

st.markdown(
    """
Use these two visuals to discuss any abrupt level shifts in review volume and
average rating around March 2020, as well as the recovery trajectory.
    """
)
