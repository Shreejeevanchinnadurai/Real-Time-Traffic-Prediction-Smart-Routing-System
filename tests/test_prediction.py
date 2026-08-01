import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from preprocessing.feature_engineering import engineer_features

def test_feature_engineering():
    # Mock raw data
    data = {
        "location_id": [1],
        "timestamp": [pd.Timestamp("2024-01-01 08:30:00")], # Morning peak
        "vehicle_count": [450],
        "average_speed": [20.0],
        "road_capacity": [500],
        "speed_limit": [50.0],
        "weather_condition": ["Clear"],
        "accident_reported": [0]
    }
    df = pd.DataFrame(data)
    
    df_engineered = engineer_features(df)
    
    assert "hour" in df_engineered.columns
    assert df_engineered.iloc[0]["hour"] == 8
    assert df_engineered.iloc[0]["is_morning_peak"] == 1
    assert df_engineered.iloc[0]["traffic_density"] == 450 / 500
    assert df_engineered.iloc[0]["speed_ratio"] == 20.0 / 50.0
