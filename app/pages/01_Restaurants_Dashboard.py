import math
from typing import List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster

from app.utils.data_loader import (
    load_business,
    vancouver_restaurants_only,
    filter_by_cuisines,
)
from app.utils.constants import CUISINE_TYPES

st.set_page_config(page_title="Restaurants Dashboard", page_icon="🍽️", layout="wide")

st.title("Part A: Restaurants Dashboard")

business_df = load_business(errors="ignore")
if business_df is None or business_df.empty:
    st.warning("Business table not found. Place `business.csv` or `business.parquet` under `data/`.")
    st.stop()

restaurants = vancouver_restaurants_only(business_df)

st.caption("Data filtered to restaurants in the Greater Vancouver Area.")

# Cuisine filter
selected_cuisines = st.multiselect(
    "Cuisine types",
    options=CUISINE_TYPES,
    default=CUISINE_TYPES,  # default all types
)
restaurants = filter_by_cuisines(restaurants, selected_cuisines)

# Optional minimum reviews filter
min_reviews = st.slider("Minimum number of reviews", 0, int(restaurants["review_count"].max()), 0)
restaurants = restaurants[restaurants["review_count"] >= min_reviews]

# KPIs
kpi_cols = st.columns(3)
with kpi_cols[0]:
    st.metric("Total restaurants (GVA)", len(restaurants))
with kpi_cols[1]:
    st.metric("Avg. rating", f"{restaurants['stars'].mean():.2f} ⭐")
with kpi_cols[2]:
    st.metric("Median reviews", int(restaurants["review_count"].median()))

# Map setup
DEFAULT_CENTER = (49.2827, -123.1207)  # Downtown Vancouver
m = folium.Map(location=DEFAULT_CENTER, zoom_start=12, tiles="cartodbpositron")

cluster = MarkerCluster().add_to(m)

def _color_for_stars(stars: float) -> str:
    if stars >= 4.5:
        return "green"
    if stars >= 3.5:
        return "orange"
    return "red"

for _, row in restaurants.iterrows():
    if pd.isna(row.get("latitude")) or pd.isna(row.get("longitude")):
        continue
    popup = f"<b>{row.get('name','')}</b><br>⭐ {row.get('stars',0):.1f} — {row.get('review_count',0)} reviews<br>{row.get('cuisine_type','Others')}"
    folium.CircleMarker(
        location=(row["latitude"], row["longitude"]),
        radius=4,
        color=_color_for_stars(float(row.get("stars", 0))),
        fill=True,
        fill_opacity=0.7,
        popup=popup,
    ).add_to(cluster)

ret = st_folium(m, height=600, width=None, returned_objects=["bounds", "zoom", "center"])  # type: ignore

# Determine restaurants within current map bounds for adaptive chart
in_view = restaurants
bounds: Optional[dict] = ret.get("bounds") if isinstance(ret, dict) else None
if bounds:
    south, west = bounds.get("_southWest", {}).get("lat"), bounds.get("_southWest", {}).get("lng")
    north, east = bounds.get("_northEast", {}).get("lat"), bounds.get("_northEast", {}).get("lng")
    if None not in (south, west, north, east):
        in_view = restaurants[
            (restaurants["latitude"] >= south)
            & (restaurants["latitude"] <= north)
            & (restaurants["longitude"] >= west)
            & (restaurants["longitude"] <= east)
        ]

# Star distribution (adaptive to map viewport)
star_bins = (
    in_view["stars"].round(1).clip(lower=0, upper=5)
)
star_counts = star_bins.value_counts().sort_index()
fig = px.bar(
    x=star_counts.index.astype(str),
    y=star_counts.values,
    labels={"x": "Star rating", "y": "Restaurant count"},
    title="Restaurants per star rating (in current map view)",
)
st.plotly_chart(fig, use_container_width=True)

# Top 10 by popularity (review_count)
st.subheader("Top 10 restaurants by total reviews")

cols = [
    "name",
    "cuisine_type",
    "stars",
    "review_count",
    "city",
]
if not restaurants.empty:
    top10 = restaurants.sort_values("review_count", ascending=False).head(10)
    st.dataframe(top10[cols], use_container_width=True, hide_index=True)
else:
    st.info("No restaurants match the selected filters.")
