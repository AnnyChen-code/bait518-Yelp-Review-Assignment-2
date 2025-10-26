"""
BAIT518 Assignment 2 - Part C: Users Story Board
Analysis of user behavior patterns and interesting insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from data_loader import YelpDataLoader, create_sample_data

# Page configuration
st.set_page_config(
    page_title="User Behavior Analysis",
    page_icon="👥",
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
        
        if business_df is None or reviews_df is None or users_df is None:
            st.warning("Real Yelp data not found. Using sample data for demonstration.")
            business_df, reviews_df, users_df = create_sample_data()
            
            # Process sample data through the loader for consistency
            loader.business_df = business_df
            loader.reviews_df = reviews_df
            loader.users_df = users_df
            
            # Apply Vancouver filtering to sample data
            loader.business_df = loader.filter_vancouver_restaurants(business_df)
            
            # Filter reviews and users for Vancouver businesses
            vancouver_business_ids = set(loader.business_df['business_id'])
            loader.reviews_df = reviews_df[reviews_df['business_id'].isin(vancouver_business_ids)]
            vancouver_user_ids = set(loader.reviews_df['user_id'])
            loader.users_df = users_df[users_df['user_id'].isin(vancouver_user_ids)]
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Using sample data for demonstration.")
        business_df, reviews_df, users_df = create_sample_data()
        
        # Process sample data
        loader.business_df = business_df
        loader.reviews_df = reviews_df
        loader.users_df = users_df
        loader.business_df = loader.filter_vancouver_restaurants(business_df)
        
        # Filter reviews and users for Vancouver businesses
        vancouver_business_ids = set(loader.business_df['business_id'])
        loader.reviews_df = reviews_df[reviews_df['business_id'].isin(vancouver_business_ids)]
        vancouver_user_ids = set(loader.reviews_df['user_id'])
        loader.users_df = users_df[users_df['user_id'].isin(vancouver_user_ids)]
    
    return loader.business_df, loader.reviews_df, loader.users_df

def prepare_user_data(users_df, reviews_df):
    """Prepare and enrich user data with additional metrics"""
    
    # Ensure date columns are datetime
    reviews_df['date'] = pd.to_datetime(reviews_df['date'])
    users_df['yelping_since'] = pd.to_datetime(users_df['yelping_since'])
    
    # Calculate user tenure (years on Yelp)
    current_date = reviews_df['date'].max()
    users_df['tenure_years'] = (current_date - users_df['yelping_since']).dt.days / 365.25
    
    # Calculate additional metrics from reviews
    user_review_stats = reviews_df.groupby('user_id').agg({
        'stars': ['mean', 'std', 'count'],
        'date': ['min', 'max'],
        'business_id': 'nunique'
    }).round(2)
    
    # Flatten column names
    user_review_stats.columns = [
        'avg_rating_given', 'rating_std', 'vancouver_review_count',
        'first_vancouver_review', 'last_vancouver_review', 'unique_restaurants_visited'
    ]
    
    # Calculate review frequency (reviews per year in Vancouver)
    user_review_stats['vancouver_review_span_years'] = (
        user_review_stats['last_vancouver_review'] - user_review_stats['first_vancouver_review']
    ).dt.days / 365.25
    user_review_stats['vancouver_review_span_years'] = user_review_stats['vancouver_review_span_years'].fillna(0)
    user_review_stats['reviews_per_year_vancouver'] = (
        user_review_stats['vancouver_review_count'] / 
        user_review_stats['vancouver_review_span_years'].replace(0, 1)
    ).round(2)
    
    # Merge with user data
    enriched_users = users_df.merge(user_review_stats, left_on='user_id', right_index=True, how='left')
    
    # Fill NaN values
    enriched_users = enriched_users.fillna(0)
    
    # Create user categories
    enriched_users['user_category'] = pd.cut(
        enriched_users['review_count'],
        bins=[0, 10, 50, 200, float('inf')],
        labels=['Casual (1-10)', 'Regular (11-50)', 'Active (51-200)', 'Power User (200+)']
    )
    
    # Create engagement score
    enriched_users['engagement_score'] = (
        enriched_users['review_count'] * 0.4 +
        enriched_users['useful'] * 0.3 +
        enriched_users['fans'] * 0.2 +
        enriched_users['unique_restaurants_visited'] * 0.1
    ).round(2)
    
    return enriched_users

def create_user_engagement_analysis(users_df):
    """Visualization 1: User Engagement Patterns"""
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'User Categories Distribution',
            'Engagement Score vs Review Count',
            'User Tenure vs Activity Level',
            'Rating Behavior Patterns'
        ),
        specs=[[{"type": "xy"}, {"type": "xy"}],
               [{"type": "xy"}, {"type": "xy"}]]
    )
    
    # 1. User categories pie chart
    category_counts = users_df['user_category'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=category_counts.index,
            values=category_counts.values,
            name="User Categories"
        ),
        row=1, col=1
    )
    
    # 2. Engagement score vs review count scatter
    fig.add_trace(
        go.Scatter(
            x=users_df['review_count'],
            y=users_df['engagement_score'],
            mode='markers',
            name='Users',
            marker=dict(
                size=8,
                color=users_df['tenure_years'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Tenure (Years)")
            ),
            text=users_df['user_category'],
            hovertemplate='Reviews: %{x}<br>Engagement: %{y}<br>Category: %{text}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Tenure vs activity scatter
    fig.add_trace(
        go.Scatter(
            x=users_df['tenure_years'],
            y=users_df['reviews_per_year_vancouver'],
            mode='markers',
            name='Activity Rate',
            marker=dict(size=6, color='orange', opacity=0.6),
            hovertemplate='Tenure: %{x:.1f} years<br>Reviews/Year: %{y:.1f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. Rating behavior histogram
    fig.add_trace(
        go.Histogram(
            x=users_df['avg_rating_given'],
            nbinsx=20,
            name='Rating Distribution',
            marker_color='lightblue',
            opacity=0.7
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800,
        title_text="User Engagement Patterns Analysis",
        showlegend=False
    )
    
    # Update axis labels
    fig.update_xaxes(title_text="Review Count", row=1, col=2)
    fig.update_yaxes(title_text="Engagement Score", row=1, col=2)
    fig.update_xaxes(title_text="Tenure (Years)", row=2, col=1)
    fig.update_yaxes(title_text="Reviews per Year", row=2, col=1)
    fig.update_xaxes(title_text="Average Rating Given", row=2, col=2)
    fig.update_yaxes(title_text="Number of Users", row=2, col=2)
    
    return fig

def create_user_loyalty_analysis(users_df, reviews_df):
    """Visualization 2: User Loyalty and Restaurant Exploration Patterns"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Restaurant Exploration vs Review Volume',
            'User Loyalty Segments',
            'Review Consistency Over Time',
            'Social Influence (Fans vs Useful Votes)'
        )
    )
    
    # 1. Restaurant exploration scatter
    fig.add_trace(
        go.Scatter(
            x=users_df['vancouver_review_count'],
            y=users_df['unique_restaurants_visited'],
            mode='markers',
            name='Users',
            marker=dict(
                size=users_df['tenure_years'] * 2,
                color=users_df['avg_rating_given'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Avg Rating Given", x=0.45)
            ),
            hovertemplate='Reviews: %{x}<br>Restaurants: %{y}<br>Avg Rating: %{marker.color:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add diagonal line for reference (1:1 ratio)
    max_reviews = users_df['vancouver_review_count'].max()
    fig.add_trace(
        go.Scatter(
            x=[0, max_reviews],
            y=[0, max_reviews],
            mode='lines',
            name='1:1 Ratio',
            line=dict(dash='dash', color='red'),
            showlegend=False
        ),
        row=1, col=1
    )
    
    # 2. User loyalty segments (exploration ratio)
    users_df['exploration_ratio'] = users_df['unique_restaurants_visited'] / users_df['vancouver_review_count'].replace(0, 1)
    users_df['loyalty_segment'] = pd.cut(
        users_df['exploration_ratio'],
        bins=[0, 0.3, 0.7, 1.0],
        labels=['Loyal (Return Visitors)', 'Balanced', 'Explorers']
    )
    
    loyalty_counts = users_df['loyalty_segment'].value_counts()
    fig.add_trace(
        go.Bar(
            x=loyalty_counts.index,
            y=loyalty_counts.values,
            name='Loyalty Segments',
            marker_color=['green', 'orange', 'blue'],
            text=loyalty_counts.values,
            textposition='auto'
        ),
        row=1, col=2
    )
    
    # 3. Review consistency (rating standard deviation)
    fig.add_trace(
        go.Histogram(
            x=users_df['rating_std'],
            nbinsx=15,
            name='Rating Consistency',
            marker_color='purple',
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # 4. Social influence scatter
    fig.add_trace(
        go.Scatter(
            x=users_df['useful'],
            y=users_df['fans'],
            mode='markers',
            name='Social Metrics',
            marker=dict(
                size=np.log1p(users_df['review_count']) * 2,
                color='red',
                opacity=0.6
            ),
            hovertemplate='Useful Votes: %{x}<br>Fans: %{y}<br>Reviews: %{marker.size}<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800,
        title_text="User Loyalty and Exploration Patterns",
        showlegend=False
    )
    
    # Update axis labels
    fig.update_xaxes(title_text="Vancouver Reviews", row=1, col=1)
    fig.update_yaxes(title_text="Unique Restaurants", row=1, col=1)
    fig.update_xaxes(title_text="Loyalty Segment", row=1, col=2)
    fig.update_yaxes(title_text="Number of Users", row=1, col=2)
    fig.update_xaxes(title_text="Rating Standard Deviation", row=2, col=1)
    fig.update_yaxes(title_text="Number of Users", row=2, col=1)
    fig.update_xaxes(title_text="Useful Votes Received", row=2, col=2)
    fig.update_yaxes(title_text="Number of Fans", row=2, col=2)
    
    return fig

def create_user_insights_summary(users_df):
    """Generate key insights about user patterns"""
    
    insights = {}
    
    # Basic stats
    insights['total_users'] = len(users_df)
    insights['avg_reviews_per_user'] = users_df['vancouver_review_count'].mean()
    insights['avg_restaurants_per_user'] = users_df['unique_restaurants_visited'].mean()
    insights['avg_tenure'] = users_df['tenure_years'].mean()
    
    # User categories
    insights['user_categories'] = users_df['user_category'].value_counts().to_dict()
    
    # Loyalty analysis
    insights['loyalty_segments'] = users_df['loyalty_segment'].value_counts().to_dict()
    
    # Power users (top 10%)
    top_10_percent = int(len(users_df) * 0.1)
    power_users = users_df.nlargest(top_10_percent, 'engagement_score')
    insights['power_user_contribution'] = {
        'users_pct': 10,
        'reviews_pct': (power_users['vancouver_review_count'].sum() / users_df['vancouver_review_count'].sum()) * 100,
        'restaurants_pct': (power_users['unique_restaurants_visited'].sum() / users_df['unique_restaurants_visited'].sum()) * 100
    }
    
    # Rating behavior
    insights['avg_rating_given'] = users_df['avg_rating_given'].mean()
    insights['rating_consistency'] = users_df['rating_std'].mean()
    
    return insights

def main():
    """Main function for user analysis"""
    
    st.title("👥 User Behavior Analysis")
    st.markdown("### BAIT518 Assignment 2 - Part C")
    
    # Load data
    with st.spinner("Loading user data..."):
        business_df, reviews_df, users_df = load_data()
    
    # Prepare enriched user data
    with st.spinner("Analyzing user patterns..."):
        enriched_users = prepare_user_data(users_df, reviews_df)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", f"{len(enriched_users):,}")
    
    with col2:
        avg_reviews = enriched_users['vancouver_review_count'].mean()
        st.metric("Avg Reviews per User", f"{avg_reviews:.1f}")
    
    with col3:
        avg_restaurants = enriched_users['unique_restaurants_visited'].mean()
        st.metric("Avg Restaurants Visited", f"{avg_restaurants:.1f}")
    
    with col4:
        avg_tenure = enriched_users['tenure_years'].mean()
        st.metric("Avg User Tenure", f"{avg_tenure:.1f} years")
    
    # Visualization 1: User Engagement Patterns
    st.header("📊 Visualization 1: User Engagement Patterns")
    engagement_fig = create_user_engagement_analysis(enriched_users)
    st.plotly_chart(engagement_fig, use_container_width=True)
    
    with st.expander("💡 Insights from User Engagement Analysis"):
        category_dist = enriched_users['user_category'].value_counts()
        most_common = category_dist.index[0]
        st.write(f"**Most common user type:** {most_common} ({category_dist.iloc[0]} users)")
        
        high_engagement = enriched_users[enriched_users['engagement_score'] > enriched_users['engagement_score'].quantile(0.9)]
        st.write(f"**Top 10% most engaged users:** Average {high_engagement['review_count'].mean():.0f} total reviews")
        
        avg_rating = enriched_users['avg_rating_given'].mean()
        st.write(f"**Average rating given by users:** {avg_rating:.2f} stars")
    
    # Visualization 2: User Loyalty and Exploration
    st.header("🔍 Visualization 2: User Loyalty and Restaurant Exploration")
    loyalty_fig = create_user_loyalty_analysis(enriched_users, reviews_df)
    st.plotly_chart(loyalty_fig, use_container_width=True)
    
    with st.expander("💡 Insights from Loyalty Analysis"):
        loyalty_dist = enriched_users['loyalty_segment'].value_counts()
        most_common_loyalty = loyalty_dist.index[0]
        st.write(f"**Most common user behavior:** {most_common_loyalty} ({loyalty_dist.iloc[0]} users)")
        
        explorers = enriched_users[enriched_users['loyalty_segment'] == 'Explorers']
        if len(explorers) > 0:
            st.write(f"**Explorer users:** Visit {explorers['unique_restaurants_visited'].mean():.1f} restaurants on average")
        
        loyal_users = enriched_users[enriched_users['loyalty_segment'] == 'Loyal (Return Visitors)']
        if len(loyal_users) > 0:
            st.write(f"**Loyal users:** Average {loyal_users['vancouver_review_count'].mean():.1f} reviews per restaurant")
    
    # Key Findings Summary
    st.header("🎯 Key Findings & Interesting Patterns")
    
    insights = create_user_insights_summary(enriched_users)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Most Interesting Pattern #1: The 80/20 Rule")
        power_contribution = insights['power_user_contribution']
        st.info(f"""
        **Power User Phenomenon:**
        
        The top 10% most engaged users contribute disproportionately to the platform:
        - **{power_contribution['reviews_pct']:.1f}%** of all Vancouver restaurant reviews
        - **{power_contribution['restaurants_pct']:.1f}%** of restaurant discoveries
        - This follows the classic Pareto principle in user-generated content
        """)
        
        # Power user characteristics
        top_10_percent = int(len(enriched_users) * 0.1)
        power_users = enriched_users.nlargest(top_10_percent, 'engagement_score')
        
        st.write("**Power User Characteristics:**")
        st.write(f"- Average tenure: {power_users['tenure_years'].mean():.1f} years")
        st.write(f"- Average reviews: {power_users['review_count'].mean():.0f}")
        st.write(f"- Average restaurants visited: {power_users['unique_restaurants_visited'].mean():.0f}")
    
    with col2:
        st.subheader("🎭 Most Interesting Pattern #2: User Loyalty Spectrum")
        
        loyalty_pcts = enriched_users['loyalty_segment'].value_counts(normalize=True) * 100
        
        st.success(f"""
        **Restaurant Exploration Behavior:**
        
        Users fall into distinct behavioral patterns:
        - **{loyalty_pcts.get('Loyal (Return Visitors)', 0):.1f}%** are Loyal (return to same restaurants)
        - **{loyalty_pcts.get('Balanced', 0):.1f}%** are Balanced (mix of new and repeat visits)
        - **{loyalty_pcts.get('Explorers', 0):.1f}%** are Explorers (constantly try new places)
        
        This reveals different dining personalities and platform usage patterns.
        """)
        
        # Rating consistency insight
        consistent_users = enriched_users[enriched_users['rating_std'] < 0.5]
        st.write(f"**Rating Consistency:** {len(consistent_users)} users ({len(consistent_users)/len(enriched_users)*100:.1f}%) are very consistent in their ratings (std < 0.5)")
    
    # Additional Analysis
    st.header("📈 Additional User Behavior Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Social influence analysis
        social_users = enriched_users[enriched_users['fans'] > 0]
        st.metric(
            "Users with Fans", 
            f"{len(social_users):,}",
            delta=f"{len(social_users)/len(enriched_users)*100:.1f}% of all users"
        )
        
        if len(social_users) > 0:
            avg_fans = social_users['fans'].mean()
            st.write(f"Average fans per social user: {avg_fans:.1f}")
    
    with col2:
        # Review frequency analysis
        active_reviewers = enriched_users[enriched_users['reviews_per_year_vancouver'] > 12]  # More than 1 per month
        st.metric(
            "Very Active Reviewers", 
            f"{len(active_reviewers):,}",
            delta=f">1 review/month in Vancouver"
        )
    
    with col3:
        # Rating generosity
        generous_raters = enriched_users[enriched_users['avg_rating_given'] > 4.0]
        st.metric(
            "Generous Raters", 
            f"{len(generous_raters):,}",
            delta=f"Avg rating > 4.0 stars"
        )
    
    # Data quality and methodology
    with st.expander("📊 Data Quality & Methodology"):
        st.write("**Analysis Methodology:**")
        st.write("- User engagement score combines review count, useful votes, fans, and restaurant diversity")
        st.write("- Loyalty segments based on exploration ratio (unique restaurants / total reviews)")
        st.write("- Power users defined as top 10% by engagement score")
        st.write("- All analysis focused on Vancouver restaurant reviews only")
        
        st.write(f"**Data Coverage:**")
        st.write(f"- Users analyzed: {len(enriched_users):,}")
        st.write(f"- Total Vancouver reviews: {enriched_users['vancouver_review_count'].sum():,}")
        st.write(f"- Unique restaurants covered: {enriched_users['unique_restaurants_visited'].sum():,}")
        st.write(f"- Average user tenure: {enriched_users['tenure_years'].mean():.1f} years")

if __name__ == "__main__":
    main()