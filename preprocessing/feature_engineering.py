"""
Feature Engineering Module
==========================
Generates derived features that improve ML model performance.
Each feature is documented with its rationale.

Usage:
    from preprocessing.feature_engineering import engineer_features
    df_features = engineer_features(df_clean)
"""

import pandas as pd
import numpy as np
from utils.logger import get_logger
from utils.constants import WEATHER_SEVERITY_MAP
from utils.helpers import safe_divide

logger = get_logger(__name__)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate all engineered features from cleaned traffic data.

    Args:
        df: Cleaned DataFrame with timestamp, vehicle_count, average_speed, etc.

    Returns:
        DataFrame with additional feature columns.
    """
    df = df.copy()
    logger.info(f"Starting feature engineering on {len(df)} rows")

    # Ensure timestamp is datetime
    if "timestamp" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # ── Temporal Features ─────────────────────────────────────────────
    # Hour of day: Captures daily traffic patterns (rush hours vs night)
    if "timestamp" in df.columns:
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek  # 0=Mon, 6=Sun
        df["month"] = df["timestamp"].dt.month
        df["day_of_month"] = df["timestamp"].dt.day
    elif "hour" not in df.columns:
        logger.warning("No timestamp column found; temporal features may be missing")

    # Weekend flag: Weekend traffic patterns differ significantly from weekday
    if "day_of_week" in df.columns:
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Peak hour flags: Peak periods have 2-3x the traffic volume
    if "hour" in df.columns:
        df["is_morning_peak"] = df["hour"].between(7, 9).astype(int)
        df["is_evening_peak"] = (
            (df["hour"].between(17, 19)) |
            ((df["hour"] == 16) & True)  # Simplified: include hour 16
        ).astype(int)
        df["is_peak_hour"] = (
            (df["is_morning_peak"] == 1) | (df["is_evening_peak"] == 1)
        ).astype(int)

    # ── Traffic Density Features ──────────────────────────────────────
    # Traffic density: How "full" the road is — key predictor of congestion
    if "vehicle_count" in df.columns and "road_capacity" in df.columns:
        df["traffic_density"] = df.apply(
            lambda row: safe_divide(row["vehicle_count"], row["road_capacity"], 0.0),
            axis=1,
        )
        # Capacity utilization (same as density but capped at 1.0 for percentage use)
        df["capacity_utilization"] = df["traffic_density"].clip(upper=1.5)

    # Speed ratio: How degraded current speed is vs free-flow
    if "average_speed" in df.columns and "speed_limit" in df.columns:
        df["speed_ratio"] = df.apply(
            lambda row: safe_divide(row["average_speed"], row["speed_limit"], 0.5),
            axis=1,
        )
    elif "average_speed" in df.columns:
        # Fallback: use default speed limit of 50
        df["speed_ratio"] = df["average_speed"] / 50.0

    # ── Weather Features ──────────────────────────────────────────────
    # Weather severity: Ordinal encoding — worse weather → higher number → slower traffic
    if "weather_condition" in df.columns:
        df["weather_severity"] = df["weather_condition"].map(WEATHER_SEVERITY_MAP).fillna(0)

    # ── Accident Risk ─────────────────────────────────────────────────
    # Combined incident severity: accident + weather amplification
    if "accident_reported" in df.columns and "weather_severity" in df.columns:
        df["accident_risk"] = df["accident_reported"] * (1 + df["weather_severity"])
    elif "accident_reported" in df.columns:
        df["accident_risk"] = df["accident_reported"].astype(float)

    # ── Lag Features (Temporal Autocorrelation) ───────────────────────
    # Previous hour's metrics — traffic is highly autocorrelated
    if "timestamp" in df.columns and "location_id" in df.columns:
        df = df.sort_values(["location_id", "timestamp"])

        # Group by location for lag computation
        for col in ["vehicle_count", "average_speed"]:
            if col in df.columns:
                lag_col = f"lag_{col}"
                df[lag_col] = df.groupby("location_id")[col].shift(1)
                df[lag_col] = df[lag_col].fillna(df[col].median())

        # Rolling 3-hour averages — smoothed trend
        for col in ["vehicle_count", "average_speed"]:
            if col in df.columns:
                roll_col = f"rolling_{col}_3h"
                df[roll_col] = (
                    df.groupby("location_id")[col]
                    .transform(lambda x: x.rolling(window=3, min_periods=1).mean())
                )

    # ── Ensure Holiday/Event Columns ──────────────────────────────────
    if "is_holiday" not in df.columns:
        df["is_holiday"] = 0
    if "is_special_event" not in df.columns:
        df["is_special_event"] = 0

    logger.info(f"Feature engineering complete. Columns: {len(df.columns)}")
    return df


def get_feature_descriptions() -> dict:
    """Return descriptions of all engineered features for documentation."""
    return {
        "hour": "Hour of day (0-23). Captures daily traffic rhythms.",
        "day_of_week": "Day of week (0=Mon, 6=Sun). Weekday vs weekend patterns.",
        "month": "Month of year. Seasonal traffic variations.",
        "is_weekend": "Binary: 1 if Saturday/Sunday. Traffic is 30-40% lower.",
        "is_peak_hour": "Binary: 1 during rush hours (7-10 AM, 5-8 PM).",
        "is_morning_peak": "Binary: 1 during morning rush (7-10 AM).",
        "is_evening_peak": "Binary: 1 during evening rush (5-8 PM).",
        "traffic_density": "vehicle_count / road_capacity. Core congestion indicator.",
        "speed_ratio": "average_speed / speed_limit. How degraded speed is.",
        "capacity_utilization": "Same as density, capped at 1.5. Road saturation metric.",
        "weather_severity": "Ordinal: Clear=0, Cloudy=1, Light Rain=2, Heavy Rain=3, Fog=4.",
        "accident_risk": "accident × (1 + weather_severity). Combined incident severity.",
        "lag_vehicle_count": "Previous hour's vehicle count. Temporal autocorrelation.",
        "lag_average_speed": "Previous hour's speed. Speed momentum.",
        "rolling_vehicle_count_3h": "3-hour rolling average of vehicle count.",
        "rolling_average_speed_3h": "3-hour rolling average of speed.",
    }
