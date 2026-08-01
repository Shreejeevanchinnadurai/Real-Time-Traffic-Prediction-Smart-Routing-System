"""
Google Maps Platform Integration Service
=========================================
Wraps Google Maps Geocoding API, Directions API, and Places API.
Includes automatic fallback to OpenStreetMap/OSRM when API key is unconfigured.
"""

import time
import requests
from typing import Dict, List, Optional, Tuple
from config.config import Config
from services.osrm_service import geocode_location as osrm_geocode, get_global_route as osrm_get_route
from utils.helpers import decode_google_polyline
from utils.logger import get_logger

logger = get_logger(__name__)

GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GOOGLE_DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
GOOGLE_DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


def geocode_location_google(address: str) -> Tuple[float, float, str]:
    """
    Geocode an address using Google Geocoding API if key is present,
    falling back to OSRM/Tamil Nadu local matcher.
    """
    api_key = Config.GOOGLE_MAPS_API_KEY
    if not api_key:
        return osrm_geocode(address)

    try:
        params = {"address": address, "key": api_key}
        resp = requests.get(GOOGLE_GEOCODE_URL, params=params, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "OK" and data.get("results"):
                res = data["results"][0]
                loc = res["geometry"]["location"]
                return float(loc["lat"]), float(loc["lng"]), res.get("formatted_address", address)
    except Exception as e:
        logger.warning(f"Google Geocoding failed for '{address}': {e}. Falling back to OSRM.")

    return osrm_geocode(address)


def get_google_route(src_lat: float, src_lon: float, dest_lat: float, dest_lon: float, alternatives: bool = True) -> List[Dict]:
    """
    Fetch live driving routes using Google Directions API with real-time traffic delay estimates
    and overview polyline decoding.
    """
    api_key = Config.GOOGLE_MAPS_API_KEY
    if not api_key:
        return osrm_get_route(src_lat, src_lon, dest_lat, dest_lon, alternatives=alternatives)

    try:
        params = {
            "origin": f"{src_lat},{src_lon}",
            "destination": f"{dest_lat},{dest_lon}",
            "mode": "driving",
            "departure_time": "now",
            "traffic_model": "best_guess",
            "alternatives": "true" if alternatives else "false",
            "key": api_key
        }
        resp = requests.get(GOOGLE_DIRECTIONS_URL, params=params, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "OK" and data.get("routes"):
                routes = []
                for idx, r in enumerate(data["routes"]):
                    leg = r["legs"][0]
                    dist_km = leg["distance"]["value"] / 1000.0
                    base_dur_min = leg["duration"]["value"] / 60.0
                    
                    # Extract duration in traffic if available
                    dur_in_traffic = leg.get("duration_in_traffic", {}).get("value")
                    dur_min = (dur_in_traffic / 60.0) if dur_in_traffic else base_dur_min
                    traffic_delay_min = max(0.0, dur_min - base_dur_min)

                    steps_summary = []
                    for step in leg.get("steps", []):
                        steps_summary.append({
                            "instruction": step.get("html_instructions", step.get("travel_mode", "Drive")),
                            "distance_km": step.get("distance", {}).get("value", 0) / 1000.0,
                            "duration_min": step.get("duration", {}).get("value", 0) / 60.0,
                            "location": [step["end_location"]["lat"], step["end_location"]["lng"]]
                        })

                    # Decode overview polyline coordinates
                    poly_str = r.get("overview_polyline", {}).get("points", "")
                    path_coords = decode_google_polyline(poly_str)
                    if not path_coords:
                        path_coords = [(src_lat, src_lon), (dest_lat, dest_lon)]

                    routes.append({
                        "rank": idx + 1,
                        "total_distance_km": round(dist_km, 2),
                        "total_duration_min": round(dur_min, 2),
                        "base_duration_min": round(base_dur_min, 2),
                        "traffic_delay_min": round(traffic_delay_min, 2),
                        "path_coords": path_coords,
                        "steps": steps_summary,
                        "summary": r.get("summary", f"Route {idx+1}"),
                        "is_recommended": (idx == 0)
                    })
                return routes
    except Exception as e:
        logger.warning(f"Google Directions API failed: {e}. Falling back to OSRM.")

    return osrm_get_route(src_lat, src_lon, dest_lat, dest_lon, alternatives=alternatives)


def get_google_matrix_traffic(origins: List[str], destinations: List[str]) -> Optional[Dict]:
    """
    Query Google Distance Matrix API with live traffic data across multiple origin/destination corridors.
    """
    api_key = Config.GOOGLE_MAPS_API_KEY
    if not api_key:
        return None

    try:
        params = {
            "origins": "|".join(origins),
            "destinations": "|".join(destinations),
            "mode": "driving",
            "departure_time": "now",
            "traffic_model": "best_guess",
            "key": api_key
        }
        resp = requests.get(GOOGLE_DISTANCE_MATRIX_URL, params=params, timeout=8)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.warning(f"Google Distance Matrix API call failed: {e}")

    return None
