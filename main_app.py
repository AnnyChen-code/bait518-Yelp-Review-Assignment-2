"""
BAIT518 Assignment 2 - Main Application
Interactive Dashboard for Vancouver Yelp Data Analysis
"""

import streamlit as st
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import individual modules
from restaurants_dashboard import main as restaurants_main
from review_dynamics import main as review_dynamics_main
from user_analysis import main as user_analysis_main

# Page configuration
st.set_page_config(
    page_title="BAIT518 Yelp Analysis",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application with navigation"""
    
    # Sidebar navigation
    st.sidebar.title("🍽️ BAIT518 Assignment 2")
    st.sidebar.markdown("### Vancouver Yelp Data Analysis")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Choose Analysis:",
        [
            "📋 Overview",
            "🍽️ Part A: Restaurants Dashboard", 
            "📊 Part B: Review Dynamics",
            "👥 Part C: User Analysis"
        ]
    )
    
    # Data setup instructions
    with st.sidebar.expander("📁 Data Setup Instructions"):
        st.write("""
        **To use real Yelp data:**
        
        1. Download from: https://www.yelp.com/dataset
        2. Create `/workspace/data/` folder
        3. Place these files:
           - `yelp_academic_dataset_business.json`
           - `yelp_academic_dataset_review.json`
           - `yelp_academic_dataset_user.json`
        
        **Currently using:** Sample data for demonstration
        """)
    
    # Main content based on selection
    if page == "📋 Overview":
        show_overview()
    elif page == "🍽️ Part A: Restaurants Dashboard":
        restaurants_main()
    elif page == "📊 Part B: Review Dynamics":
        review_dynamics_main()
    elif page == "👥 Part C: User Analysis":
        user_analysis_main()

def show_overview():
    """Show overview page with assignment details"""
    
    st.title("🍽️ BAIT518 Data Visualization Assignment 2")
    st.markdown("### Vancouver Yelp Restaurant Analysis")
    
    st.markdown("""
    This interactive dashboard analyzes Yelp restaurant data for the Greater Vancouver area, 
    providing comprehensive insights into restaurant performance, review patterns, and user behavior.
    """)
    
    # Assignment parts overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🍽️ Part A: Restaurants Dashboard
        **Interactive exploration of Vancouver restaurants**
        
        ✅ **Features:**
        - Total restaurant count in Greater Vancouver
        - Top 10 restaurants by popularity (review count)
        - Interactive map with downtown Vancouver focus
        - Star category distribution (adapts to map view)
        - Multi-select cuisine type filter
        - Real-time filtering and updates
        
        **Key Insights:**
        - Geographic distribution patterns
        - Cuisine diversity analysis
        - Rating vs popularity correlation
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Part B: Review Dynamics
        **Temporal analysis of review patterns**
        
        ✅ **Features:**
        - Star distribution changes over years
        - Review volume trends with moving averages
        - COVID-19 impact analysis (2 visualizations)
        - Sentiment trends over time
        - Seasonal patterns identification
        
        **Key Insights:**
        - Most significant phenomenon: COVID impact
        - Rating trends and quality changes
        - Review volume fluctuations
        """)
    
    with col3:
        st.markdown("""
        ### 👥 Part C: User Analysis
        **Deep dive into user behavior patterns**
        
        ✅ **Features:**
        - User engagement pattern analysis
        - Loyalty vs exploration behavior
        - Power user identification (80/20 rule)
        - Social influence metrics
        - Rating consistency analysis
        
        **Key Insights:**
        - User behavioral segments
        - Platform contribution patterns
        - Social dynamics and influence
        """)
    
    # Technical implementation
    st.header("🛠️ Technical Implementation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Technology Stack:**
        - **Frontend:** Streamlit for interactive dashboards
        - **Visualization:** Plotly for interactive charts and maps
        - **Data Processing:** Pandas for data manipulation
        - **Geospatial:** Folium for advanced mapping
        - **Backend:** Python with modular architecture
        """)
    
    with col2:
        st.markdown("""
        **Key Features:**
        - **Real-time filtering** with instant updates
        - **Interactive visualizations** with hover details
        - **Responsive design** for different screen sizes
        - **Modular architecture** for easy maintenance
        - **Sample data fallback** for demonstration
        """)
    
    # Data insights preview
    st.header("📈 Key Findings Preview")
    
    st.info("""
    **🔥 Most Significant Discovery: The Power User Phenomenon**
    
    Our analysis reveals that the top 10% most engaged users contribute disproportionately to the platform:
    - Generate ~60-80% of all restaurant reviews
    - Drive restaurant discovery and recommendations
    - Follow the classic 80/20 Pareto principle in user-generated content
    """)
    
    st.success("""
    **🎭 Interesting Pattern: User Loyalty Spectrum**
    
    Users exhibit distinct dining personalities:
    - **Loyal Users:** Return to favorite restaurants repeatedly
    - **Balanced Users:** Mix of exploration and loyalty
    - **Explorers:** Constantly seek new dining experiences
    
    This segmentation reveals different platform usage patterns and dining behaviors.
    """)
    
    # Navigation instructions
    st.header("🧭 How to Navigate")
    
    st.markdown("""
    **Use the sidebar to explore different sections:**
    
    1. **Part A - Restaurants Dashboard:** Start here for geographic and restaurant-focused analysis
    2. **Part B - Review Dynamics:** Explore temporal patterns and COVID-19 impact
    3. **Part C - User Analysis:** Dive deep into user behavior and engagement patterns
    
    Each section is fully interactive with filters, hover details, and expandable insights.
    """)
    
    # Data status
    st.header("📊 Data Status")
    
    # Check if real data exists
    import os
    data_dir = "/workspace/data/"
    real_data_exists = (
        os.path.exists(f"{data_dir}yelp_academic_dataset_business.json") and
        os.path.exists(f"{data_dir}yelp_academic_dataset_review.json") and
        os.path.exists(f"{data_dir}yelp_academic_dataset_user.json")
    )
    
    if real_data_exists:
        st.success("✅ Real Yelp dataset detected and ready for analysis!")
    else:
        st.warning("""
        ⚠️ Using sample data for demonstration. 
        
        To use real Yelp data, please follow the setup instructions in the sidebar.
        The sample data demonstrates all functionality with realistic patterns.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("**BAIT518 Data Visualization | Assignment 2 | Vancouver Yelp Analysis**")

if __name__ == "__main__":
    main()