"""
Prediction Service
==================
Business logic layer for predictions. Validates input, engineers features,
calls the ML models, and saves results to the database.

Usage:
    from services.prediction_service import get_traffic_prediction
"""

from typing import Any, Dict, Optional
import pandas as pd
from datetime import datetime

from models.predict import predict_full
from database.queries import insert_prediction, execute_query
from utils.logger import get_logger
from preprocessing.feature_engineering import engineer_features

logger = get_logger(__name__)


def get_traffic_stats() -> Dict[str, Any]:
    """
    Returns high-level traffic stats for the Dashboard KPIs.
    """
    try:
        # Simple aggregated query from recent traffic data
        query = "SELECT AVG(average_speed) as avg_speed, SUM(accident_reported) as accident_count, COUNT(*) as total_records FROM traffic_data"
        df = execute_query(query)
        
        # Query for severe congestion count
        query_severe = "SELECT COUNT(*) as severe_count FROM traffic_data WHERE average_speed < 20"
        df_severe = execute_query(query_severe)
        
        if not df.empty and not df_severe.empty:
            return {
                "avg_speed": df.iloc[0]["avg_speed"] or 0.0,
                "accident_count": df.iloc[0]["accident_count"] or 0,
                "total_records": df.iloc[0]["total_records"] or 0,
                "severe_count": df_severe.iloc[0]["severe_count"] or 0,
            }
        return {"avg_speed": 0, "accident_count": 0, "total_records": 0, "severe_count": 0}
    except Exception as e:
        logger.error(f"Failed to fetch traffic stats: {e}")
        return {"avg_speed": 0, "accident_count": 0, "total_records": 0, "severe_count": 0}



def get_traffic_prediction(
    location_id: int,
    location_name: str,
    timestamp: datetime,
    vehicle_count: int,
    road_capacity: int,
    speed_limit: float,
    weather_condition: str,
    temperature: float,
    visibility: float,
    rainfall: float,
    accident_reported: int,
    is_holiday: int,
    is_special_event: int,
    lag_vehicle_count: int = 0,
    lag_average_speed: float = 0.0,
    rolling_vehicle_count_3h: float = 0.0,
    rolling_average_speed_3h: float = 0.0,
) -> Optional[Dict[str, Any]]:
    """
    Generate traffic prediction and store it in the database.

    Args:
        Input features matching the required inputs for the models.

    Returns:
        Dictionary with prediction results, or None on failure.
    """
    try:
        # 1. Construct raw input data frame
        raw_data = {
            "timestamp": [timestamp],
            "vehicle_count": [vehicle_count],
            "road_capacity": [road_capacity],
            "speed_limit": [speed_limit],
            "weather_condition": [weather_condition],
            "temperature": [temperature],
            "visibility": [visibility],
            "rainfall": [rainfall],
            "accident_reported": [accident_reported],
            "is_holiday": [is_holiday],
            "is_special_event": [is_special_event],
            # Pass pre-computed lags if available, else feature_engineering will fill default
            "lag_vehicle_count": [lag_vehicle_count] if lag_vehicle_count else [vehicle_count],
            "lag_average_speed": [lag_average_speed] if lag_average_speed else [speed_limit],
            "rolling_vehicle_count_3h": [rolling_vehicle_count_3h] if rolling_vehicle_count_3h else [vehicle_count],
            "rolling_average_speed_3h": [rolling_average_speed_3h] if rolling_average_speed_3h else [speed_limit],
            "location_id": [location_id], # Needed for lag grouping in feature_engineering if multiple rows, but safe to include
        }
        df_raw = pd.DataFrame(raw_data)

        # 2. Engineer features
        df_features = engineer_features(df_raw)
        
        # 3. Convert to dict for predict_full
        input_features = df_features.iloc[0].to_dict()
        
        # 4. Get Prediction
        result = predict_full(input_features)

        # 5. Store in database
        prediction_id = insert_prediction(
            location_id=location_id,
            predicted_vehicle_count=None,  # We are not predicting volume in this setup, only congestion/speed
            predicted_speed=result["predicted_speed"],
            predicted_congestion=result["predicted_congestion"],
            model_name=result["model_name"],
            confidence_score=result["confidence_score"],
        )

        if prediction_id:
            result["prediction_id"] = prediction_id
            logger.info(f"Saved prediction {prediction_id} for location {location_id}")
        else:
            logger.warning("Failed to save prediction to database")

        return result

    except Exception as e:
        logger.error(f"Prediction service failed: {e}")
        return None
