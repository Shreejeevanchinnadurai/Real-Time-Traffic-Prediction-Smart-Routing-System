"""
Traffic Service
===============
Business logic for interacting with traffic data. Fetches latest data,
aggregates conditions for routing, and checks for alerts.
"""

from typing import Dict, List, Any
from datetime import datetime

from database.queries import get_latest_traffic, get_traffic_data
from utils.logger import get_logger

logger = get_logger(__name__)


def get_current_traffic_conditions() -> Dict[str, Dict]:
    """
    Get the most recent traffic observation for every location to use in routing.
    
    Returns:
        Dictionary mapping location_name -> traffic data dict.
    """
    # Fetch a sufficient number of recent records to get at least one per location
    recent_records = get_latest_traffic(limit=100)
    
    conditions = {}
    for record in recent_records:
        loc_name = record["location_name"]
        if loc_name not in conditions:
            # We only want the most recent record per location
            conditions[loc_name] = {
                "average_speed": record["average_speed"],
                "congestion_level": record["congestion_level"],
                "accident_reported": bool(record["accident_reported"]),
                "road_condition": record["road_condition"],
            }
    
    return conditions


def generate_alerts() -> List[Dict[str, Any]]:
    """
    Analyze recent traffic data and generate active alerts.
    
    Returns:
        List of alert dictionaries.
    """
    alerts = []
    recent_traffic = get_latest_traffic(limit=50) # Get recent snapshot
    
    processed_locations = set()
    
    for record in recent_traffic:
        loc_name = record["location_name"]
        
        # Only process the most recent record per location
        if loc_name in processed_locations:
            continue
        processed_locations.add(loc_name)
        
        # Alert 1: Severe Congestion
        if record["congestion_level"] == "Severe":
            alerts.append({
                "type": "Severe Congestion",
                "location": loc_name,
                "message": f"Severe congestion detected on {record['road_name']}. Speed: {record['average_speed']} km/h.",
                "level": "error"
            })
            
        # Alert 2: Accident
        if record["accident_reported"]:
            alerts.append({
                "type": "Accident",
                "location": loc_name,
                "message": f"Accident reported near {loc_name} on {record['road_name']}.",
                "level": "error"
            })
            
        # Alert 3: High Capacity Warning
        capacity_util = record["vehicle_count"] / record["road_capacity"] if record["road_capacity"] > 0 else 0
        if capacity_util > 0.85 and record["congestion_level"] != "Severe":
             alerts.append({
                "type": "Heavy Traffic",
                "location": loc_name,
                "message": f"Heavy traffic volume approaching capacity on {record['road_name']}.",
                "level": "warning"
            })
             
    return alerts
