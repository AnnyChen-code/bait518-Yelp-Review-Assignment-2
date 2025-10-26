# BAIT518 – Yelp Assignment 2 (Streamlit Dashboard)

This repository contains a Streamlit app implementing the three parts of the assignment:

- Restaurants Dashboard (Part A)
- Review Dynamics Story Board (Part B)
- Users Story Board (Part C)

## Quick start

1. Create a Python environment (3.10+ recommended) and install dependencies:
   
   ```bash
   pip install -r requirements.txt
   ```

2. Place your data files in the `data/` folder at the project root. Accepted names and formats:
   - `business.csv` or `business.parquet`
   - `review.csv` or `review.parquet`
   - `user.csv` or `user.parquet`

   Alternative file base names are also detected (e.g., `yelp_business`, `businesses`, `reviews`, `users`).

3. Run the app:
   
   ```bash
   streamlit run streamlit_app.py
   ```

   Or run a specific page directly:
   
   ```bash
   streamlit run app/Home.py
   ```

## Data expectations

The loader is tolerant to column name variants. Ideal columns:

- Business: `id`, `name`, `city`, `state`, `latitude`, `longitude`, `stars`, `review_count`, `categories`, `is_open`
- Review: `id` (business_id), `stars`, `date`
- User: `review_count`, `avg_stars`, `yelping_since`, `friends`, `fans`

Only Greater Vancouver Area restaurants are used in the dashboards. If your dataset is the full Yelp corpus, the app filters down automatically.

## Pages

- Part A: KPIs, interactive Folium map (zoom to Vancouver), star distribution synced to map viewport, Top-10 by reviews, cuisine-type filter (Indian/Chinese/Thai/…/Others).
- Part B: Star distribution by year, COVID-19 impact visuals with a vertical line at March 2020 for monthly review volume and average stars.
- Part C: Users storyboard with histogram of review counts and scatter of popularity (fans/friends) vs ratings (avg_stars) with trendline.

## Notes

- Set `DATA_DIR` environment variable if your files aren’t under `data/`.
- CSV and Parquet are supported (Parquet is faster/lower memory).