"""
BAIT518 Assignment 2 - Part A: Restaurants Dashboard
Interactive dashboard for Vancouver restaurants analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from data_loader import YelpDataLoader, create_sample_data

# Page configuration
st.set_page_config(
    page_title="Vancouver Restaurants Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Load and cache the data"""
    loader = YelpDataLoader()
    
    # Try to load real data first, fall back to sample data
    try:
        business_df = loader.load_business_data()
        reviews_df = loader.load_reviews_data()
        users_df = loader.load_users_data()
        
        if business_df is None:
            st.warning("Real Yelp data not found. Using sample data for demonstration.")
            business_df, reviews_df, users_df = create_sample_data()
            
            # Process sample data through the loader for consistency
            loader.business_df = business_df
            loader.reviews_df = reviews_df
            loader.users_df = users_df
            
            # Apply Vancouver filtering to sample data
            loader.business_df = loader.filter_vancouver_restaurants(business_df)
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Using sample data for demonstration.")
        business_df, reviews_df, users_df = create_sample_data()
        
        # Process sample data
        loader.business_df = business_df
        loader.reviews_df = reviews_df
        loader.users_df = users_df
        loader.business_df = loader.filter_vancouver_restaurants(business_df)
    
    return loader.business_df, loader.reviews_df, loader.users_df

def create_cuisine_filter(business_df):
    """Create cuisine type filter"""
    # Get all unique cuisines
    all_cuisines = set()
    for cuisines_list in business_df['cuisine_types']:
        all_cuisines.update(cuisines_list)
    
    all_cuisines = sorted(list(all_cuisines))
    
    # Multi-select for cuisine types
    selected_cuisines = st.sidebar.multiselect(
        "Select Cuisine Types:",
        options=all_cuisines,
        default=all_cuisines,
        help="Choose one or more cuisine types to filter restaurants"
    )
    
    return selected_cuisines

def filter_by_cuisine(business_df, selected_cuisines):
    """Filter restaurants by selected cuisine types"""
    if not selected_cuisines:
        return business_df
    
    def matches_cuisine(cuisines_list):
        return any(cuisine in selected_cuisines for cuisine in cuisines_list)
    
    filtered_df = business_df[business_df['cuisine_types'].apply(matches_cuisine)]
    return filtered_df

def create_map_visualization(business_df):
    """Create interactive map of restaurant locations"""
    # Default to downtown Vancouver center
    center_lat, center_lon = 49.2827, -123.1207
    
    # Create the map
    fig = px.scatter_mapbox(
        business_df,
        lat="latitude",
        lon="longitude",
        color="stars",
        size="review_count",
        hover_name="name",
        hover_data={
            "stars": True,
            "review_count": True,
            "latitude": False,
            "longitude": False
        },
        color_continuous_scale="Viridis",
        size_max=15,
        zoom=11,
        center={"lat": center_lat, "lon": center_lon},
        title="Restaurant Locations in Greater Vancouver"
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        height=500,
        margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )
    
    return fig

def create_star_category_plot(business_df):
    """Create plot showing number of restaurants by star category"""
    # Create star categories
    business_df_copy = business_df.copy()
    business_df_copy['star_category'] = pd.cut(
        business_df_copy['stars'], 
        bins=[0, 2, 3, 4, 5], 
        labels=['1-2 Stars', '2-3 Stars', '3-4 Stars', '4-5 Stars'],
        include_lowest=True
    )
    
    star_counts = business_df_copy['star_category'].value_counts().sort_index()
    
    fig = px.bar(
        x=star_counts.index,
        y=star_counts.values,
        title="Number of Restaurants by Star Category",
        labels={'x': 'Star Category', 'y': 'Number of Restaurants'},
        color=star_counts.values,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        showlegend=False,
        height=400
    )
    
    return fig

def create_top_restaurants_table(business_df):
    """Create table of top 10 restaurants by popularity (review count)"""
    top_restaurants = business_df.nlargest(10, 'review_count')[
        ['name', 'stars', 'review_count', 'cuisine_types']
    ].copy()
    
    # Format cuisine types for display
    top_restaurants['cuisines'] = top_restaurants['cuisine_types'].apply(
        lambda x: ', '.join(x) if isinstance(x, list) else str(x)
    )
    
    # Rename columns for display
    display_df = top_restaurants[['name', 'stars', 'review_count', 'cuisines']].copy()
    display_df.columns = ['Restaurant Name', 'Star Rating', 'Number of Reviews', 'Cuisine Types']
    
    # Add ranking
    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
    
    return display_df

def main():
    """Main dashboard function"""
    st.title("🍽️ Vancouver Restaurants Dashboard")
    st.markdown("### BAIT518 Assignment 2 - Part A")
    
    # Load data
    with st.spinner("Loading restaurant data..."):
        business_df, reviews_df, users_df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_cuisines = create_cuisine_filter(business_df)
    
    # Filter data based on selections
    filtered_business_df = filter_by_cuisine(business_df, selected_cuisines)
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Restaurants", 
            len(filtered_business_df),
            delta=f"{len(filtered_business_df) - len(business_df)} from all"
        )
    
    with col2:
        avg_rating = filtered_business_df['stars'].mean()
        st.metric("Average Rating", f"{avg_rating:.2f} ⭐")
    
    with col3:
        total_reviews = filtered_business_df['review_count'].sum()
        st.metric("Total Reviews", f"{total_reviews:,}")
    
    with col4:
        unique_cuisines = len(set().union(*filtered_business_df['cuisine_types']))
        st.metric("Cuisine Types", unique_cuisines)
    
    # Main content area
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Map visualization
        st.subheader("Restaurant Locations")
        map_fig = create_map_visualization(filtered_business_df)
        st.plotly_chart(map_fig, use_container_width=True)
        
        # Star category plot
        st.subheader("Restaurants by Star Category")
        star_fig = create_star_category_plot(filtered_business_df)
        st.plotly_chart(star_fig, use_container_width=True)
    
    with col_right:
        # Top 10 restaurants
        st.subheader("Top 10 Most Popular Restaurants")
        st.caption("Ranked by number of reviews")
        
        top_restaurants = create_top_restaurants_table(filtered_business_df)
        st.dataframe(
            top_restaurants,
            use_container_width=True,
            hide_index=True,
            height=400
        )
    
    # Additional insights
    st.subheader("📊 Data Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cuisine distribution
        all_cuisines = []
        for cuisines_list in filtered_business_df['cuisine_types']:
            all_cuisines.extend(cuisines_list)
        
        cuisine_counts = pd.Series(all_cuisines).value_counts().head(10)
        
        fig_cuisine = px.pie(
            values=cuisine_counts.values,
            names=cuisine_counts.index,
            title="Top 10 Cuisine Types Distribution"
        )
        st.plotly_chart(fig_cuisine, use_container_width=True)
    
    with col2:
        # Rating vs Review Count scatter
        fig_scatter = px.scatter(
            filtered_business_df,
            x='review_count',
            y='stars',
            title='Rating vs Number of Reviews',
            labels={'review_count': 'Number of Reviews', 'stars': 'Star Rating'},
            opacity=0.6
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Data summary
    with st.expander("📋 Data Summary"):
        st.write("**Dataset Overview:**")
        st.write(f"- Total restaurants in Greater Vancouver: {len(business_df):,}")
        st.write(f"- Restaurants matching current filters: {len(filtered_business_df):,}")
        st.write(f"- Average rating: {filtered_business_df['stars'].mean():.2f} stars")
        st.write(f"- Rating range: {filtered_business_df['stars'].min():.1f} - {filtered_business_df['stars'].max():.1f} stars")
        st.write(f"- Total reviews: {filtered_business_df['review_count'].sum():,}")
        
        if len(selected_cuisines) < len(set().union(*business_df['cuisine_types'])):
            st.write(f"- Filtered by cuisine types: {', '.join(selected_cuisines)}")

if __name__ == "__main__":
    main()