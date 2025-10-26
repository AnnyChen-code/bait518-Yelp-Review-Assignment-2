#!/usr/bin/env python3
"""
Quick demo script to test all components of the BAIT518 Assignment 2
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_data_loader():
    """Test the data loading functionality"""
    print("🔄 Testing Data Loader...")
    
    try:
        from data_loader import YelpDataLoader, create_sample_data
        
        # Test sample data generation
        business_df, reviews_df, users_df = create_sample_data()
        
        print(f"✅ Sample data generated successfully:")
        print(f"   - Businesses: {len(business_df):,}")
        print(f"   - Reviews: {len(reviews_df):,}")
        print(f"   - Users: {len(users_df):,}")
        
        # Test data loader class
        loader = YelpDataLoader()
        loader.business_df = business_df
        loader.reviews_df = reviews_df
        loader.users_df = users_df
        
        # Test Vancouver filtering
        vancouver_businesses = loader.filter_vancouver_restaurants(business_df)
        print(f"   - Vancouver restaurants: {len(vancouver_businesses):,}")
        
        # Test cuisine extraction
        cuisines = loader.get_top_cuisines()
        print(f"   - Top cuisines: {list(cuisines.keys())[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loader test failed: {str(e)}")
        return False

def test_visualizations():
    """Test that visualization modules can be imported"""
    print("\n🎨 Testing Visualization Modules...")
    
    modules_to_test = [
        ('restaurants_dashboard', 'Part A: Restaurants Dashboard'),
        ('review_dynamics', 'Part B: Review Dynamics'),
        ('user_analysis', 'Part C: User Analysis'),
        ('main_app', 'Main Application')
    ]
    
    success_count = 0
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}")
            success_count += 1
        except Exception as e:
            print(f"❌ {description}: {str(e)}")
    
    return success_count == len(modules_to_test)

def check_requirements():
    """Check if required packages are available"""
    print("\n📦 Checking Required Packages...")
    
    required_packages = [
        'pandas', 'plotly', 'streamlit', 'numpy', 
        'matplotlib', 'seaborn', 'folium'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing!")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def show_usage_instructions():
    """Show how to run the application"""
    print("\n🚀 Usage Instructions:")
    print("=" * 50)
    print("1. To run the main dashboard:")
    print("   streamlit run main_app.py")
    print()
    print("2. To run individual components:")
    print("   streamlit run restaurants_dashboard.py  # Part A")
    print("   streamlit run review_dynamics.py        # Part B") 
    print("   streamlit run user_analysis.py          # Part C")
    print()
    print("3. Access the dashboard at: http://localhost:8501")
    print()
    print("4. For real Yelp data:")
    print("   - Download from: https://www.yelp.com/dataset")
    print("   - Place JSON files in: /workspace/data/")
    print("   - Files needed:")
    print("     * yelp_academic_dataset_business.json")
    print("     * yelp_academic_dataset_review.json") 
    print("     * yelp_academic_dataset_user.json")

def main():
    """Run all tests and show instructions"""
    print("🎯 BAIT518 Assignment 2 - Vancouver Yelp Analysis")
    print("=" * 60)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if check_requirements():
        tests_passed += 1
    
    if test_data_loader():
        tests_passed += 1
        
    if test_visualizations():
        tests_passed += 1
    
    # Show results
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The application is ready to run.")
        show_usage_instructions()
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("Try running: pip install -r requirements.txt")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)