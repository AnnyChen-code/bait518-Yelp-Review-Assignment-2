import os
import streamlit as st
import pandas as pd

from app.utils.data_loader import (
    get_data_dir,
    load_business,
    load_reviews,
    load_users,
)

st.set_page_config(
    page_title="BAIT518 Assignment 2 – Yelp Dashboards",
    page_icon="🍴",
    layout="wide",
)

st.title("BAIT518 Assignment 2 – Yelp Dashboards")

st.markdown(
    """
This Streamlit app contains three parts:

- Restaurants Dashboard (Part A)
- Review Dynamics Story Board (Part B)
- Users Story Board (Part C)

Use the sidebar to navigate to each page. Place your data files in the `data` folder.
    """
)

with st.expander("Data quick status", expanded=True):
    data_dir = get_data_dir()
    st.write("Data directory:", f"`{data_dir}`")

    business_df = load_business(errors="ignore")
    reviews_df = load_reviews(errors="ignore")
    users_df = load_users(errors="ignore")

    cols = st.columns(3)
    with cols[0]:
        st.metric("Businesses loaded", value=(0 if business_df is None else len(business_df)))
    with cols[1]:
        st.metric("Reviews loaded", value=(0 if reviews_df is None else len(reviews_df)))
    with cols[2]:
        st.metric("Users loaded", value=(0 if users_df is None else len(users_df)))

    if (business_df is None) or (reviews_df is None) or (users_df is None):
        st.info(
            "Place `business`, `review`, and `user` tables as CSV or Parquet in the data folder.\n"
            "Accepted filenames: `business.(csv|parquet)`, `review.(csv|parquet)`, `user.(csv|parquet)`.\n"
            "Large Yelp datasets are OK – only Vancouver-area rows are used in pages."
        )

st.markdown(
    """
### How to run locally
1. Install requirements: `pip install -r requirements.txt`
2. Start the app: `streamlit run app/Home.py`
3. Add your data tables to the `data` directory.
    """
)
