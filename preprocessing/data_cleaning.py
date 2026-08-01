"""
Data Cleaning Module
====================
Handles missing values, duplicates, type coercion, invalid data,
and outlier treatment for traffic datasets.

Usage:
    from preprocessing.data_cleaning import clean_traffic_data
    df_clean = clean_traffic_data(df_raw)
"""

import pandas as pd
import numpy as np
from utils.logger import get_logger
from utils.constants import WEATHER_CONDITIONS, ROAD_CONDITIONS

logger = get_logger(__name__)


def clean_traffic_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw traffic data from the database.

    Steps:
        1. Remove exact duplicate rows
        2. Coerce data types
        3. Handle missing values
        4. Fix invalid coordinates
        5. Clamp invalid speeds and counts
        6. Standardize categorical values
        7. Remove outliers (IQR method on vehicle_count and average_speed)

    Args:
        df: Raw DataFrame from database query.

    Returns:
        Cleaned DataFrame ready for feature engineering.
    """
    initial_rows = len(df)
    logger.info(f"Starting data cleaning: {initial_rows} rows")

    # ── 1. Remove Duplicates ──────────────────────────────────────────
    df = df.drop_duplicates()
    logger.info(f"  After dedup: {len(df)} rows (removed {initial_rows - len(df)})")

    # ── 2. Parse Timestamp ────────────────────────────────────────────
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        null_ts = df["timestamp"].isna().sum()
        if null_ts > 0:
            logger.warning(f"  Dropped {null_ts} rows with invalid timestamps")
            df = df.dropna(subset=["timestamp"])

    # ── 3. Coerce Numeric Types ───────────────────────────────────────
    numeric_cols = [
        "vehicle_count", "average_speed", "road_capacity",
        "visibility", "temperature", "rainfall", "speed_limit",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    int_cols = ["accident_reported", "is_holiday", "is_special_event"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # ── 4. Handle Missing Values ──────────────────────────────────────
    # Fill numeric with median
    for col in numeric_cols:
        if col in df.columns and df[col].isna().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.info(f"  Filled {col} missing values with median: {median_val:.2f}")

    # Fill categorical with mode
    categorical_cols = ["weather_condition", "road_condition", "congestion_level"]
    for col in categorical_cols:
        if col in df.columns and df[col].isna().any():
            mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(mode_val)

    # ── 5. Validate Coordinates ───────────────────────────────────────
    if "latitude" in df.columns and "longitude" in df.columns:
        valid_coords = (
            df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)
        )
        invalid_count = (~valid_coords).sum()
        if invalid_count > 0:
            logger.warning(f"  Found {invalid_count} rows with invalid coordinates")
            df = df[valid_coords]

    # ── 6. Clamp Invalid Speeds and Counts ────────────────────────────
    if "average_speed" in df.columns:
        df["average_speed"] = df["average_speed"].clip(lower=0, upper=150)

    if "vehicle_count" in df.columns:
        df["vehicle_count"] = df["vehicle_count"].clip(lower=0).astype(int)

    if "visibility" in df.columns:
        df["visibility"] = df["visibility"].clip(lower=0, upper=50)

    if "temperature" in df.columns:
        df["temperature"] = df["temperature"].clip(lower=-10, upper=55)

    if "rainfall" in df.columns:
        df["rainfall"] = df["rainfall"].clip(lower=0, upper=200)

    # ── 7. Standardize Categorical Values ─────────────────────────────
    if "weather_condition" in df.columns:
        valid_weather = set(WEATHER_CONDITIONS)
        df.loc[~df["weather_condition"].isin(valid_weather), "weather_condition"] = "Clear"

    if "road_condition" in df.columns:
        valid_road = set(ROAD_CONDITIONS)
        df.loc[~df["road_condition"].isin(valid_road), "road_condition"] = "Good"

    # ── 8. Remove Extreme Outliers (IQR) ──────────────────────────────
    for col in ["vehicle_count", "average_speed"]:
        if col in df.columns:
            Q1 = df[col].quantile(0.01)
            Q3 = df[col].quantile(0.99)
            IQR = Q3 - Q1
            lower = Q1 - 3 * IQR
            upper = Q3 + 3 * IQR
            outliers = ~df[col].between(lower, upper)
            outlier_count = outliers.sum()
            if outlier_count > 0:
                df = df[~outliers]
                logger.info(f"  Removed {outlier_count} outliers from {col}")

    # ── 9. Reset Index ────────────────────────────────────────────────
    df = df.reset_index(drop=True)

    logger.info(f"Cleaning complete: {len(df)} rows (from {initial_rows})")
    return df
