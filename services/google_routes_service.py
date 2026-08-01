"""
Google Routes Service
=====================
Interfaces with Google Directions/Routes Web Service API to calculate
candidate driving routes, distance matrices, step maneuvering, and travel durations.
"""

import requests
from typing import Dict, List, Optional
from config.config import Config
from services.osrm_service import get_global_route as osrm_get_route
from utils.logger import get_logger

logger = get_logger(__name__)

GOOGLE_DIRECTIONS_API = "https://maps.googleapis.com/maps/api/directions/json"


def get_google_candidate_routes(
    src_lat: float, src_lon: float,
    dest_lat: float, dest_lon: float,
    alternatives: bool = True,
    travel_mode: str = "driving"
) -> List[Dict]:
    """
    Fetch candidate routes from Google Directions API.
    Returns structured route dictionary list. If API key is missing or call fails,
    falls back to OSRM engine.
    """
    api_key = Config.GOOGLE_MAPS_API_KEY
    if not api_key:
        logger.info("Google Maps API key unconfigured. Using OSRM fallback routing.")
        return osrm_get_route(src_lat, src_lon, dest_lat, dest_lon, alternatives=alternatives)

    try:
        params = {
            "origin": f"{src_lat},{src_lon}",
            "destination": f"{dest_lat},{dest_lon}",
            "mode": travel_mode.lower(),
            "alternatives": "true" if alternatives else "false",
            "key": api_key
        }
        resp = requests.get(GOOGLE_DIRECTIONS_API, params=params, timeout=7)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "OK" and data.get("routes"):
                candidate_routes = []
                for idx, r in enumerate(data["routes"]):
                    leg = r["legs"][0]
                    dist_km = leg["distance"]["value"] / 1000.0
                    dur_min = leg["duration"]["value"] / 60.0
                    
                    steps = []
                    for step in leg.get("steps", []):
                        steps.append({
                            "instruction": step.get("html_instructions", step.get("travel_mode", "Drive")),
                            "distance_km": step.get("distance", {}).get("value", 0) / 1000.0,
                            "duration_min": step.get("duration", {}).get("value", 0) / 60.0,
                            "location": [step["end_location"]["lat"], step["end_location"]["lng"]]
                        })
                        
                    candidate_routes.append({
                        "rank": idx + 1,
                        "total_distance_km": round(dist_km, 2),
                        "total_duration_min": round(dur_min, 2),
                        "google_eta_min": round(dur_min, 2),
                        "path_coords": [(src_lat, src_lon), (dest_lat, dest_lon)],
                        "steps": steps,
                        "is_recommended": (idx == 0),
                        "provider": "google"
                    })
                return candidate_routes
            else:
                logger.warning(f"Google Directions API status: {data.get('status')}. Using OSRM fallback.")
    except Exception as e:
        logger.error(f"Google Directions API request error: {e}. Using OSRM fallback.")

    return osrm_get_route(src_lat, src_lon, dest_lat, dest_lon, alternatives=alternatives)
