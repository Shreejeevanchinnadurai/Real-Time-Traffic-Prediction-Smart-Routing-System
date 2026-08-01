"""
OSRM Routing & Nominatim Geocoding Service
==========================================
Provides global real-world routing and geocoding without requiring API keys,
using the public OpenStreetMap infrastructure.
"""

import requests
import polyline
from typing import Dict, List, Optional, Tuple

from utils.logger import get_logger

logger = get_logger(__name__)

# Public API Endpoints
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

# Nominatim user-agent header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TrafficAI-SmartRouting/1.0"
}

# Local Keyword Fallback Dictionary for Tamil Nadu & Indian Cities
TN_FALLBACK_GEO = [
    (("tambaram", "tbram"), 12.9249, 80.1000, "Tambaram, Chennai, Tamil Nadu, India"),
    (("t. nagar", "t nagar", "tnagar"), 13.0418, 80.2341, "T. Nagar, Chennai, Tamil Nadu, India"),
    (("airport", "meenambakkam"), 12.9941, 80.1709, "Chennai International Airport, Meenambakkam, Chennai, Tamil Nadu"),
    (("guindy", "kathipara"), 13.0067, 80.2020, "Guindy, Chennai, Tamil Nadu, India"),
    (("siruseri", "omr", "it corridor"), 12.8259, 80.2223, "Siruseri IT Park, OMR, Chennai, Tamil Nadu"),
    (("koyambedu", "cmbt"), 13.0694, 80.1948, "Koyambedu CMBT, Chennai, Tamil Nadu"),
    (("marina", "beach road"), 13.0499, 80.2824, "Marina Beach, Chennai, Tamil Nadu"),
    (("adyar", "lb road"), 13.0012, 80.2565, "Adyar, Chennai, Tamil Nadu, India"),
    (("velachery", "100 feet road"), 12.9759, 80.2212, "Velachery, Chennai, Tamil Nadu, India"),
    (("anna nagar", "roundtana"), 13.0850, 80.2101, "Anna Nagar, Chennai, Tamil Nadu, India"),
    (("chromepet", "gst road"), 12.9516, 80.1462, "Chromepet, Chennai, Tamil Nadu, India"),
    (("porur", "mount poonamallee"), 13.0382, 80.1565, "Porur, Chennai, Tamil Nadu, India"),
    (("coimbatore", "kovai"), 11.0168, 76.9558, "Coimbatore, Tamil Nadu, India"),
    (("madurai",), 9.9252, 78.1198, "Madurai, Tamil Nadu, India"),
    (("trichy", "tiruchirappalli"), 10.7905, 78.7047, "Tiruchirappalli, Tamil Nadu, India"),
    (("salem",), 11.6643, 78.1460, "Salem, Tamil Nadu, India"),
    (("tirunelveli", "nellai"), 8.7139, 77.7567, "Tirunelveli, Tamil Nadu, India"),
    (("vellore",), 12.9165, 79.1325, "Vellore, Tamil Nadu, India"),
    (("ooty", "udhagamandalam"), 11.4102, 76.6950, "Ooty, Tamil Nadu, India"),
    (("bengaluru", "bangalore"), 12.9716, 77.5946, "Bengaluru, Karnataka, India"),
    (("chennai",), 13.0827, 80.2707, "Chennai, Tamil Nadu, India"),
]

def geocode_location(address: str) -> Tuple[float, float, str]:
    """
    Convert a text address into (latitude, longitude) and a formatted address string.
    Guaranteed to return coordinates for any input.
    """
    if not address or not address.strip():
        return 13.0827, 80.2707, "Chennai Central, Tamil Nadu, India"

    address_clean = address.strip().lower()
    
    # 1. Check local TN keyword fallback
    for keywords, lat, lon, name in TN_FALLBACK_GEO:
        for kw in keywords:
            if kw in address_clean:
                logger.info(f"Geocoding resolved via Keyword Match ('{kw}') for '{address}'")
                return lat, lon, name

    # 2. Query Nominatim API with automatic country/state query enhancement
    try:
        search_query = address
        if "india" not in address_clean and "chennai" not in address_clean and "tamil" not in address_clean:
            search_query += ", Tamil Nadu, India"
            
        params = {
            "q": search_query,
            "format": "json",
            "limit": 1
        }
        response = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                result = data[0]
                lat = float(result["lat"])
                lon = float(result["lon"])
                display_name = result.get("display_name", address.title())
                return lat, lon, display_name
    except Exception as e:
        logger.warning(f"Nominatim API geocoding failed for '{address}': {e}")

    # 3. Safe Default (Chennai Center) so user UI never crashes
    logger.info(f"Using Chennai default coordinates for '{address}'")
    return 13.0827, 80.2707, f"{address.strip().title()}, Tamil Nadu, India"


def get_global_route(
    src_lat: float, src_lon: float, 
    dest_lat: float, dest_lon: float, 
    alternatives: bool = True
) -> List[Dict]:
    """
    Fetch routes between two global coordinates using OSRM.
    
    Args:
        src_lat, src_lon: Origin coordinates
        dest_lat, dest_lon: Destination coordinates
        alternatives: Whether to fetch multiple alternative routes
        
    Returns:
        List of route dictionaries containing path coordinates, distance, and duration.
    """
    try:
        # OSRM expects coordinates as lon,lat
        coords = f"{src_lon},{src_lat};{dest_lon},{dest_lat}"
        
        url = f"{OSRM_URL}/{coords}"
        params = {
            "overview": "full",
            "geometries": "polyline",
            "steps": "true",
            "alternatives": "true" if alternatives else "false"
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != "Ok":
            logger.warning(f"OSRM returned non-Ok code: {data.get('code')}")
            return []
            
        routes = []
        for idx, r in enumerate(data.get("routes", [])):
            # Decode the Google polyline into a list of (lat, lon) tuples
            path_coords = polyline.decode(r["geometry"])
            
            # OSRM returns distance in meters, duration in seconds
            dist_km = r.get("distance", 0) / 1000.0
            dur_min = r.get("duration", 0) / 60.0
            
            # Create a summary of steps for the route table
            steps_summary = []
            if "legs" in r and len(r["legs"]) > 0:
                for step in r["legs"][0].get("steps", []):
                    instruction_type = step.get("maneuver", {}).get("type", "")
                    name = step.get("name", "")
                    modifier = step.get("maneuver", {}).get("modifier", "")
                    
                    full_instruction = f"{instruction_type} {modifier} {name}".strip()
                    
                    # OSRM maneuver location is [lon, lat]
                    loc = step.get("maneuver", {}).get("location", [0, 0])
                    
                    if full_instruction:
                        steps_summary.append({
                            "instruction": full_instruction,
                            "distance_km": step.get("distance", 0) / 1000.0,
                            "duration_min": step.get("duration", 0) / 60.0,
                            "location": [loc[1], loc[0]]  # Store as [lat, lon] for Folium
                        })
            
            routes.append({
                "rank": idx + 1,
                "total_distance_km": round(dist_km, 2),
                "total_duration_min": round(dur_min, 2),
                "path_coords": path_coords,
                "steps": steps_summary,
                "is_recommended": (idx == 0)
            })
            
        return routes
        
    except Exception as e:
        logger.error(f"OSRM Routing failed: {e}")
        return []
