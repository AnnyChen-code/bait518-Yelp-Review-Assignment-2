"""
BAIT518 Assignment 2 - Part B: Review Dynamics Story Board
Analysis of review patterns and COVID-19 impact
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, date
from data_loader import YelpDataLoader, create_sample_data

# Page configuration
st.set_page_config(
    page_title="Review Dynamics Analysis",
    page_icon="📊",
    layout="wide"
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
        
        if business_df is None or reviews_df is None:
            st.warning("Real Yelp data not found. Using sample data for demonstration.")
            business_df, reviews_df, users_df = create_sample_data()
            
            # Process sample data through the loader for consistency
            loader.business_df = business_df
            loader.reviews_df = reviews_df
            loader.users_df = users_df
            
            # Apply Vancouver filtering to sample data
            loader.business_df = loader.filter_vancouver_restaurants(business_df)
            
            # Filter reviews for Vancouver businesses
            vancouver_business_ids = set(loader.business_df['business_id'])
            loader.reviews_df = reviews_df[reviews_df['business_id'].isin(vancouver_business_ids)]
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Using sample data for demonstration.")
        business_df, reviews_df, users_df = create_sample_data()
        
        # Process sample data
        loader.business_df = business_df
        loader.reviews_df = reviews_df
        loader.users_df = users_df
        loader.business_df = loader.filter_vancouver_restaurants(business_df)
        
        # Filter reviews for Vancouver businesses
        vancouver_business_ids = set(loader.business_df['business_id'])
        loader.reviews_df = reviews_df[reviews_df['business_id'].isin(vancouver_business_ids)]
    
    return loader.business_df, loader.reviews_df, loader.users_df

def prepare_time_series_data(reviews_df):
    """Prepare data for time series analysis"""
    # Ensure date column is datetime
    reviews_df['date'] = pd.to_datetime(reviews_df['date'])
    
    # Extract year and month
    reviews_df['year'] = reviews_df['date'].dt.year
    reviews_df['month'] = reviews_df['date'].dt.month
    reviews_df['year_month'] = reviews_df['date'].dt.to_period('M')
    
    return reviews_df

def create_star_distribution_over_time(reviews_df):
    """Create visualization showing star distribution changes over years"""
    
    # Group by year and star rating
    yearly_stars = reviews_df.groupby(['year', 'stars']).size().reset_index(name='count')
    
    # Calculate percentages for each year
    yearly_totals = reviews_df.groupby('year').size().reset_index(name='total')
    yearly_stars = yearly_stars.merge(yearly_totals, on='year')
    yearly_stars['percentage'] = (yearly_stars['count'] / yearly_stars['total']) * 100
    
    # Create stacked area chart
    fig = px.area(
        yearly_stars,
        x='year',
        y='percentage',
        color='stars',
        title='Star Rating Distribution Over Years',
        labels={
            'year': 'Year',
            'percentage': 'Percentage of Reviews (%)',
            'stars': 'Star Rating'
        },
        color_discrete_sequence=px.colors.sequential.RdYlGn_r
    )
    
    fig.update_layout(
        height=500,
        hovermode='x unified',
        legend_title="Star Rating"
    )
    
    return fig

def create_review_volume_over_time(reviews_df):
    """Create visualization showing review volume changes over time"""
    
    # Monthly review counts
    monthly_counts = reviews_df.groupby(reviews_df['date'].dt.to_period('M')).size().reset_index(name='review_count')
    monthly_counts['date'] = monthly_counts['date'].dt.to_timestamp()
    
    # Calculate moving average
    monthly_counts['moving_avg'] = monthly_counts['review_count'].rolling(window=6, center=True).mean()
    
    fig = go.Figure()
    
    # Add review count bars
    fig.add_trace(go.Bar(
        x=monthly_counts['date'],
        y=monthly_counts['review_count'],
        name='Monthly Reviews',
        opacity=0.7,
        marker_color='lightblue'
    ))
    
    # Add moving average line
    fig.add_trace(go.Scatter(
        x=monthly_counts['date'],
        y=monthly_counts['moving_avg'],
        mode='lines',
        name='6-Month Moving Average',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title='Review Volume Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Reviews',
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_covid_impact_analysis(reviews_df):
    """Create visualizations showing COVID-19 impact on reviews"""
    
    # Define COVID periods
    pre_covid = reviews_df[reviews_df['date'] < '2020-03-01']
    covid_start = reviews_df[(reviews_df['date'] >= '2020-03-01') & (reviews_df['date'] < '2021-01-01')]
    covid_recovery = reviews_df[reviews_df['date'] >= '2021-01-01']
    
    # Analysis 1: Review volume comparison
    periods = ['Pre-COVID\n(Before Mar 2020)', 'COVID Impact\n(Mar 2020 - Dec 2020)', 'Recovery Period\n(Jan 2021 onwards)']
    volumes = [len(pre_covid), len(covid_start), len(covid_recovery)]
    
    # Calculate monthly averages for fair comparison
    pre_covid_months = (pre_covid['date'].max() - pre_covid['date'].min()).days / 30.44
    covid_months = 10  # Mar 2020 - Dec 2020
    recovery_months = max(1, (covid_recovery['date'].max() - covid_recovery['date'].min()).days / 30.44)
    
    monthly_averages = [
        volumes[0] / max(1, pre_covid_months),
        volumes[1] / covid_months,
        volumes[2] / max(1, recovery_months)
    ]
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Bar(
        x=periods,
        y=monthly_averages,
        name='Average Monthly Reviews',
        marker_color=['green', 'red', 'orange'],
        text=[f'{val:.0f}' for val in monthly_averages],
        textposition='auto'
    ))
    
    fig1.update_layout(
        title='COVID-19 Impact: Average Monthly Review Volume',
        yaxis_title='Average Reviews per Month',
        height=400
    )
    
    # Analysis 2: Rating patterns during COVID
    def get_avg_rating(df):
        return df['stars'].mean() if len(df) > 0 else 0
    
    avg_ratings = [
        get_avg_rating(pre_covid),
        get_avg_rating(covid_start),
        get_avg_rating(covid_recovery)
    ]
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=periods,
        y=avg_ratings,
        mode='lines+markers',
        name='Average Rating',
        line=dict(color='blue', width=4),
        marker=dict(size=10)
    ))
    
    fig2.update_layout(
        title='COVID-19 Impact: Average Rating Trends',
        yaxis_title='Average Star Rating',
        yaxis=dict(range=[1, 5]),
        height=400
    )
    
    return fig1, fig2

def create_sentiment_analysis_over_time(reviews_df):
    """Analyze sentiment patterns over time using star ratings as proxy"""
    
    # Create sentiment categories
    reviews_df['sentiment'] = reviews_df['stars'].apply(lambda x: 
        'Negative' if x <= 2 else 'Neutral' if x == 3 else 'Positive'
    )
    
    # Monthly sentiment analysis
    monthly_sentiment = reviews_df.groupby([
        reviews_df['date'].dt.to_period('M'), 'sentiment'
    ]).size().unstack(fill_value=0)
    
    # Calculate percentages
    monthly_sentiment_pct = monthly_sentiment.div(monthly_sentiment.sum(axis=1), axis=0) * 100
    monthly_sentiment_pct.index = monthly_sentiment_pct.index.to_timestamp()
    
    fig = go.Figure()
    
    colors = {'Positive': 'green', 'Neutral': 'orange', 'Negative': 'red'}
    
    for sentiment in ['Positive', 'Neutral', 'Negative']:
        if sentiment in monthly_sentiment_pct.columns:
            fig.add_trace(go.Scatter(
                x=monthly_sentiment_pct.index,
                y=monthly_sentiment_pct[sentiment],
                mode='lines',
                name=sentiment,
                line=dict(color=colors[sentiment], width=3),
                stackgroup='one'
            ))
    
    fig.update_layout(
        title='Sentiment Trends Over Time (Based on Star Ratings)',
        xaxis_title='Date',
        yaxis_title='Percentage of Reviews (%)',
        height=500,
        hovermode='x unified'
    )
    
    return fig

def main():
    """Main function for review dynamics analysis"""
    
    st.title("📊 Review Dynamics Story Board")
    st.markdown("### BAIT518 Assignment 2 - Part B")
    
    # Load data
    with st.spinner("Loading review data..."):
        business_df, reviews_df, users_df = load_data()
    
    # Prepare data
    reviews_df = prepare_time_series_data(reviews_df)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", f"{len(reviews_df):,}")
    
    with col2:
        date_range = reviews_df['date'].max() - reviews_df['date'].min()
        st.metric("Time Span", f"{date_range.days} days")
    
    with col3:
        avg_rating = reviews_df['stars'].mean()
        st.metric("Average Rating", f"{avg_rating:.2f} ⭐")
    
    with col4:
        unique_businesses = reviews_df['business_id'].nunique()
        st.metric("Restaurants Reviewed", unique_businesses)
    
    # Main analysis
    st.header("📈 Review Distribution Analysis")
    
    # Star distribution over time
    st.subheader("Star Rating Distribution Changes Over Years")
    star_dist_fig = create_star_distribution_over_time(reviews_df)
    st.plotly_chart(star_dist_fig, use_container_width=True)
    
    # Key insights from star distribution
    with st.expander("💡 Key Insights from Star Distribution"):
        yearly_avg = reviews_df.groupby('year')['stars'].mean()
        best_year = yearly_avg.idxmax()
        worst_year = yearly_avg.idxmin()
        
        st.write(f"**Highest average rating year:** {best_year} ({yearly_avg[best_year]:.2f} stars)")
        st.write(f"**Lowest average rating year:** {worst_year} ({yearly_avg[worst_year]:.2f} stars)")
        
        # Calculate trend
        if len(yearly_avg) > 1:
            trend = "increasing" if yearly_avg.iloc[-1] > yearly_avg.iloc[0] else "decreasing"
            st.write(f"**Overall trend:** Ratings are {trend} over time")
    
    # Review volume analysis
    st.subheader("Review Volume Over Time")
    volume_fig = create_review_volume_over_time(reviews_df)
    st.plotly_chart(volume_fig, use_container_width=True)
    
    # COVID-19 Impact Analysis
    st.header("🦠 COVID-19 Impact Analysis")
    st.markdown("Exploring how the pandemic affected restaurant reviews in Vancouver")
    
    covid_fig1, covid_fig2 = create_covid_impact_analysis(reviews_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(covid_fig1, use_container_width=True)
    
    with col2:
        st.plotly_chart(covid_fig2, use_container_width=True)
    
    # Sentiment analysis
    st.subheader("Sentiment Trends Over Time")
    sentiment_fig = create_sentiment_analysis_over_time(reviews_df)
    st.plotly_chart(sentiment_fig, use_container_width=True)
    
    # Summary insights
    st.header("📋 Key Findings")
    
    # Calculate COVID impact metrics
    pre_covid_reviews = reviews_df[reviews_df['date'] < '2020-03-01']
    covid_reviews = reviews_df[(reviews_df['date'] >= '2020-03-01') & (reviews_df['date'] < '2021-01-01')]
    
    if len(pre_covid_reviews) > 0 and len(covid_reviews) > 0:
        pre_covid_avg = pre_covid_reviews['stars'].mean()
        covid_avg = covid_reviews['stars'].mean()
        rating_change = covid_avg - pre_covid_avg
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Most Significant Phenomenon Discovered:**
            
            The COVID-19 pandemic had a measurable impact on restaurant reviews:
            - Average rating changed by {rating_change:+.2f} stars during COVID period
            - Review volume patterns shifted significantly in March 2020
            - Recovery patterns show gradual return to pre-pandemic levels
            """)
        
        with col2:
            st.success(f"""
            **Data Quality Insights:**
            
            - Total reviews analyzed: {len(reviews_df):,}
            - Time period covered: {reviews_df['date'].min().strftime('%Y-%m-%d')} to {reviews_df['date'].max().strftime('%Y-%m-%d')}
            - Average reviews per month: {len(reviews_df) / max(1, (reviews_df['date'].max() - reviews_df['date'].min()).days / 30.44):.0f}
            """)
    
    # Data exploration section
    with st.expander("🔍 Detailed Data Exploration"):
        st.subheader("Review Distribution by Year")
        yearly_dist = reviews_df['year'].value_counts().sort_index()
        st.bar_chart(yearly_dist)
        
        st.subheader("Monthly Review Patterns")
        monthly_dist = reviews_df['month'].value_counts().sort_index()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_df = pd.DataFrame({
            'Month': [month_names[i-1] for i in monthly_dist.index],
            'Reviews': monthly_dist.values
        })
        st.bar_chart(monthly_df.set_index('Month'))

if __name__ == "__main__":
    main()