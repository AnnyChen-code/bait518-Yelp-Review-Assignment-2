import os
from typing import Optional, Tuple

import pandas as pd
from dateutil import parser

from .constants import VANCOUVER_CITIES, CUISINE_TYPES, CUISINE_KEYWORDS


def get_data_dir() -> str:
    """Return the directory where data files are stored."""
    env_dir = os.getenv("DATA_DIR")
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    # Prefer project-level data dir
    project_data_dir = os.path.join(os.getcwd(), "data")
    if os.path.isdir(project_data_dir):
        return project_data_dir
    # Fallback to relative path
    return "data"


def _first_existing_file(base_names: Tuple[str, ...]) -> Optional[str]:
    data_dir = get_data_dir()
    candidates = []
    for base in base_names:
        candidates.extend(
            [
                os.path.join(data_dir, f"{base}.parquet"),
                os.path.join(data_dir, f"{base}.csv"),
            ]
        )
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def _read_table(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)


def _normalize_city(value: Optional[str]) -> Optional[str]:
    if not isinstance(value, str):
        return value
    cleaned = value.strip()
    # Normalize common variants
    replacements = {
        "Vancouver, BC": "Vancouver",
        "N. Vancouver": "North Vancouver",
        "W. Vancouver": "West Vancouver",
    }
    return replacements.get(cleaned, cleaned)


def _classify_cuisine(categories_value: Optional[str]) -> str:
    if not isinstance(categories_value, str):
        return "Others"
    text = categories_value.lower()
    for cuisine, keywords in CUISINE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return cuisine
    if "restaurant" in text:
        return "Others"
    return "Others"


def _ensure_columns(df: pd.DataFrame, required: Tuple[str, ...]) -> pd.DataFrame:
    for name in required:
        if name not in df.columns:
            # Create with safe defaults
            if name in ("categories",):
                df[name] = ""
            elif name in ("stars", "review_count"):
                df[name] = 0
            else:
                df[name] = pd.NA
    return df


def load_business(errors: str = "raise") -> Optional[pd.DataFrame]:
    """Load the business table and add helper columns.

    Expected columns (best effort): id, name, city, state, latitude, longitude,
    stars, review_count, categories, is_open.
    """
    path = _first_existing_file(("business", "yelp_business", "businesses"))
    if path is None:
        if errors == "ignore":
            return None
        raise FileNotFoundError(
            "Place business.(csv|parquet) under the data directory."
        )
    df = _read_table(path)

    # Normalize expected columns
    renames = {
        "business_id": "id",
        "city_name": "city",
        "long": "longitude",
        "lat": "latitude",
        "reviews": "review_count",
        "rating": "stars",
    }
    df = df.rename(columns=renames)

    df = _ensure_columns(
        df,
        (
            "id",
            "name",
            "city",
            "state",
            "latitude",
            "longitude",
            "stars",
            "review_count",
            "categories",
            "is_open",
        ),
    )

    # Normalize values
    df["city"] = df["city"].map(_normalize_city)

    # Restaurant detection
    df["is_restaurant"] = df["categories"].astype(str).str.contains(
        "restaurant", case=False, na=False
    )

    # Cuisine classification
    df["cuisine_type"] = df["categories"].map(_classify_cuisine)

    # Flags and cleaning
    df["is_in_vancouver_area"] = df["city"].isin(VANCOUVER_CITIES)

    # Remove impossibles in geo
    if "latitude" in df.columns and "longitude" in df.columns:
        df = df[pd.to_numeric(df["latitude"], errors="coerce").notna()]
        df = df[pd.to_numeric(df["longitude"], errors="coerce").notna()]
        df["latitude"] = df["latitude"].astype(float)
        df["longitude"] = df["longitude"].astype(float)

    # Stars should be floats
    df["stars"] = pd.to_numeric(df["stars"], errors="coerce").fillna(0.0)
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce").fillna(0).astype(int)

    return df


def load_reviews(errors: str = "raise") -> Optional[pd.DataFrame]:
    path = _first_existing_file(("review", "yelp_review", "reviews"))
    if path is None:
        if errors == "ignore":
            return None
        raise FileNotFoundError(
            "Place review.(csv|parquet) under the data directory."
        )
    df = _read_table(path)
    df = df.rename(columns={"business_id": "id"})

    # Normalize
    df["stars"] = pd.to_numeric(df.get("stars"), errors="coerce").fillna(0.0)
    if "date" in df.columns:
        # Coerce to datetime
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        # Try alternative column names
        for alt in ("review_date", "created_at"):
            if alt in df.columns:
                df["date"] = pd.to_datetime(df[alt], errors="coerce")
                break
    return df


def load_users(errors: str = "raise") -> Optional[pd.DataFrame]:
    path = _first_existing_file(("user", "yelp_user", "users"))
    if path is None:
        if errors == "ignore":
            return None
        raise FileNotFoundError(
            "Place user.(csv|parquet) under the data directory."
        )
    df = _read_table(path)

    # Normalize
    df = df.rename(
        columns={
            "average_stars": "avg_stars",
            "review_count": "review_count",
            "yelping_since": "yelping_since",
        }
    )

    if "yelping_since" in df.columns:
        df["yelping_since"] = pd.to_datetime(df["yelping_since"], errors="coerce")
    if "friends" in df.columns:
        # Count friends if given as string of ids
        df["num_friends"] = df["friends"].apply(
            lambda v: 0 if not isinstance(v, str) or len(v) == 0 else len(v.split(", "))
        )
    if "fans" in df.columns:
        df["fans"] = pd.to_numeric(df["fans"], errors="coerce").fillna(0).astype(int)
    if "review_count" in df.columns:
        df["review_count"] = (
            pd.to_numeric(df["review_count"], errors="coerce").fillna(0).astype(int)
        )
    if "avg_stars" in df.columns:
        df["avg_stars"] = pd.to_numeric(df["avg_stars"], errors="coerce").fillna(0.0)

    return df


def vancouver_restaurants_only(business_df: pd.DataFrame) -> pd.DataFrame:
    filtered = business_df[
        (business_df["is_restaurant"]) & (business_df["is_in_vancouver_area"])
    ].copy()
    return filtered


def filter_by_cuisines(df: pd.DataFrame, selected: list[str]) -> pd.DataFrame:
    if not selected or set(selected) == set(CUISINE_TYPES):
        return df
    return df[df["cuisine_type"].isin(selected)].copy()
