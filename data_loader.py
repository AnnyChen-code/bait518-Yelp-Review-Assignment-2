"""
Yelp Dataset Loader and Preprocessor
This module handles loading and preprocessing of Yelp dataset JSON files
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
import re

class YelpDataLoader:
    def __init__(self, data_dir="/workspace/data/"):
        self.data_dir = data_dir
        self.business_df = None
        self.reviews_df = None
        self.users_df = None
        
    def load_json_to_dataframe(self, filepath):
        """
        Load JSON lines file to pandas DataFrame
        Yelp dataset uses JSON lines format (one JSON object per line)
        """
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    data.append(json.loads(line.strip()))
            return pd.DataFrame(data)
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return None
        except Exception as e:
            print(f"Error loading {filepath}: {str(e)}")
            return None
    
    def load_business_data(self, filename="yelp_academic_dataset_business.json"):
        """Load and preprocess business data"""
        filepath = self.data_dir + filename
        print(f"Loading business data from {filepath}...")
        
        self.business_df = self.load_json_to_dataframe(filepath)
        
        if self.business_df is not None:
            # Filter for restaurants in Vancouver area
            self.business_df = self.filter_vancouver_restaurants(self.business_df)
            print(f"Loaded {len(self.business_df)} Vancouver restaurants")
            
        return self.business_df
    
    def load_reviews_data(self, filename="yelp_academic_dataset_review.json"):
        """Load and preprocess reviews data"""
        filepath = self.data_dir + filename
        print(f"Loading reviews data from {filepath}...")
        
        self.reviews_df = self.load_json_to_dataframe(filepath)
        
        if self.reviews_df is not None:
            # Convert date column to datetime
            self.reviews_df['date'] = pd.to_datetime(self.reviews_df['date'])
            
            # Filter reviews for Vancouver businesses only
            if self.business_df is not None:
                vancouver_business_ids = set(self.business_df['business_id'])
                self.reviews_df = self.reviews_df[
                    self.reviews_df['business_id'].isin(vancouver_business_ids)
                ]
            
            print(f"Loaded {len(self.reviews_df)} reviews for Vancouver restaurants")
            
        return self.reviews_df
    
    def load_users_data(self, filename="yelp_academic_dataset_user.json"):
        """Load and preprocess users data"""
        filepath = self.data_dir + filename
        print(f"Loading users data from {filepath}...")
        
        self.users_df = self.load_json_to_dataframe(filepath)
        
        if self.users_df is not None:
            # Filter users who have reviewed Vancouver restaurants
            if self.reviews_df is not None:
                vancouver_user_ids = set(self.reviews_df['user_id'])
                self.users_df = self.users_df[
                    self.users_df['user_id'].isin(vancouver_user_ids)
                ]
            
            print(f"Loaded {len(self.users_df)} users who reviewed Vancouver restaurants")
            
        return self.users_df
    
    def filter_vancouver_restaurants(self, business_df):
        """
        Filter businesses to include only restaurants in Greater Vancouver area
        """
        # Vancouver coordinates (approximate bounding box)
        # Greater Vancouver: roughly 49.0°N to 49.4°N, -123.3°W to -122.5°W
        vancouver_bounds = {
            'lat_min': 49.0,
            'lat_max': 49.4,
            'lon_min': -123.3,
            'lon_max': -122.5
        }
        
        # Filter by location
        location_filter = (
            (business_df['latitude'] >= vancouver_bounds['lat_min']) &
            (business_df['latitude'] <= vancouver_bounds['lat_max']) &
            (business_df['longitude'] >= vancouver_bounds['lon_min']) &
            (business_df['longitude'] <= vancouver_bounds['lon_max'])
        )
        
        # Filter by categories (restaurants only)
        restaurant_keywords = ['Restaurant', 'Food', 'Dining', 'Cafe', 'Bar', 'Pizza', 'Chinese', 'Italian', 'Indian', 'Japanese', 'Thai', 'Mexican', 'American', 'Canadian', 'French', 'Greek', 'Korean', 'Vietnamese']
        
        def is_restaurant(categories):
            if pd.isna(categories) or categories is None:
                return False
            categories_str = str(categories).lower()
            return any(keyword.lower() in categories_str for keyword in restaurant_keywords)
        
        restaurant_filter = business_df['categories'].apply(is_restaurant)
        
        # Combine filters
        filtered_df = business_df[location_filter & restaurant_filter].copy()
        
        # Add cuisine type extraction
        if 'cuisine_types' not in filtered_df.columns:
            filtered_df['cuisine_types'] = filtered_df['categories'].apply(self.extract_cuisine_types)
        
        return filtered_df
    
    def extract_cuisine_types(self, categories_str):
        """Extract cuisine types from categories string"""
        if pd.isna(categories_str) or categories_str is None:
            return ['Other']
        
        categories_lower = str(categories_str).lower()
        
        cuisine_mapping = {
            'chinese': 'Chinese',
            'italian': 'Italian', 
            'indian': 'Indian',
            'japanese': 'Japanese',
            'thai': 'Thai',
            'mexican': 'Mexican',
            'american': 'American',
            'canadian': 'Canadian',
            'french': 'French',
            'greek': 'Greek',
            'korean': 'Korean',
            'vietnamese': 'Vietnamese'
        }
        
        found_cuisines = []
        for keyword, cuisine in cuisine_mapping.items():
            if keyword in categories_lower:
                found_cuisines.append(cuisine)
        
        return found_cuisines if found_cuisines else ['Other']
    
    def get_summary_stats(self):
        """Get summary statistics of loaded data"""
        stats = {}
        
        if self.business_df is not None:
            stats['total_restaurants'] = len(self.business_df)
            stats['avg_rating'] = self.business_df['stars'].mean()
            stats['top_cuisines'] = self.get_top_cuisines()
        
        if self.reviews_df is not None:
            stats['total_reviews'] = len(self.reviews_df)
            stats['date_range'] = {
                'start': self.reviews_df['date'].min(),
                'end': self.reviews_df['date'].max()
            }
            stats['rating_distribution'] = self.reviews_df['stars'].value_counts().to_dict()
        
        if self.users_df is not None:
            stats['total_users'] = len(self.users_df)
            stats['avg_user_reviews'] = self.users_df['review_count'].mean()
        
        return stats
    
    def get_top_cuisines(self, top_n=10):
        """Get top N cuisine types by restaurant count"""
        if self.business_df is None:
            return []
        
        # Flatten cuisine types and count
        all_cuisines = []
        for cuisines_list in self.business_df['cuisine_types']:
            all_cuisines.extend(cuisines_list)
        
        cuisine_counts = pd.Series(all_cuisines).value_counts()
        return cuisine_counts.head(top_n).to_dict()

# Example usage and data structure creation
def create_sample_data():
    """Create sample data for testing when actual Yelp data is not available"""
    
    # Sample business data
    sample_businesses = []
    vancouver_lats = np.random.uniform(49.1, 49.3, 100)
    vancouver_lons = np.random.uniform(-123.2, -122.7, 100)
    
    cuisines = ['Chinese', 'Italian', 'Indian', 'Japanese', 'Thai', 'American', 'Canadian', 'French', 'Greek', 'Korean']
    
    for i in range(100):
        selected_cuisine = np.random.choice(cuisines)
        business = {
            'business_id': f'business_{i}',
            'name': f'Restaurant {i}',
            'latitude': vancouver_lats[i],
            'longitude': vancouver_lons[i],
            'stars': np.random.uniform(2.0, 5.0),
            'review_count': np.random.randint(10, 500),
            'categories': f"Restaurants, {selected_cuisine}, Food",
            'cuisine_types': [selected_cuisine],
            'city': 'Vancouver',
            'state': 'BC'
        }
        sample_businesses.append(business)
    
    # Sample reviews data
    sample_reviews = []
    for i in range(1000):
        review = {
            'review_id': f'review_{i}',
            'user_id': f'user_{np.random.randint(0, 200)}',
            'business_id': f'business_{np.random.randint(0, 100)}',
            'stars': np.random.randint(1, 6),
            'date': pd.Timestamp('2018-01-01') + pd.Timedelta(days=np.random.randint(0, 2000)),
            'text': f'Sample review text {i}',
            'useful': np.random.randint(0, 10),
            'funny': np.random.randint(0, 5),
            'cool': np.random.randint(0, 5)
        }
        sample_reviews.append(review)
    
    # Sample users data
    sample_users = []
    for i in range(200):
        user = {
            'user_id': f'user_{i}',
            'name': f'User {i}',
            'review_count': np.random.randint(1, 100),
            'yelping_since': pd.Timestamp('2010-01-01') + pd.Timedelta(days=np.random.randint(0, 4000)),
            'useful': np.random.randint(0, 50),
            'funny': np.random.randint(0, 30),
            'cool': np.random.randint(0, 40),
            'fans': np.random.randint(0, 20),
            'average_stars': np.random.uniform(2.0, 5.0)
        }
        sample_users.append(user)
    
    return pd.DataFrame(sample_businesses), pd.DataFrame(sample_reviews), pd.DataFrame(sample_users)

if __name__ == "__main__":
    # Create sample data for testing
    print("Creating sample data for testing...")
    business_df, reviews_df, users_df = create_sample_data()
    
    print(f"Sample data created:")
    print(f"- Businesses: {len(business_df)}")
    print(f"- Reviews: {len(reviews_df)}")
    print(f"- Users: {len(users_df)}")