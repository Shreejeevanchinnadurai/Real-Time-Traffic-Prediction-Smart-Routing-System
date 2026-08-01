"""
Google Places Service
====================
Provides location autocomplete, place search, and nearby POI search
(Hospitals, Fuel Stations, Parking, ATMs, Transit Hubs) using Google Places API.
"""

import requests
from typing import Dict, List
from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

GOOGLE_PLACES_NEARBY_API = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


def get_nearby_places(
    lat: float, lon: float,
    place_type: str = "hospital",
    radius_meters: int = 5000
) -> List[Dict]:
    """
    Search nearby places around coordinates using Google Places API.
    If API key is missing or call fails, returns local preset POIs.
    """
    api_key = Config.GOOGLE_MAPS_API_KEY
    if not api_key:
        return _get_fallback_pois(place_type)

    try:
        params = {
            "location": f"{lat},{lon}",
            "radius": radius_meters,
            "type": place_type.lower(),
            "key": api_key
        }
        resp = requests.get(GOOGLE_PLACES_NEARBY_API, params=params, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "OK":
                places = []
                for p in data.get("results", []):
                    loc = p.get("geometry", {}).get("location", {})
                    places.append({
                        "name": p.get("name"),
                        "latitude": loc.get("lat"),
                        "longitude": loc.get("lng"),
                        "vicinity": p.get("vicinity", ""),
                        "rating": p.get("rating", "N/A"),
                        "type": place_type
                    })
                return places
    except Exception as e:
        logger.warning(f"Google Places API failed: {e}. Returning default POIs.")

    return _get_fallback_pois(place_type)


def _get_fallback_pois(place_type: str) -> List[Dict]:
    """Fallback local POIs for Tamil Nadu."""
    if "hospital" in place_type.lower():
        return [
            {"name": "Apollo Hospital, Greams Road", "latitude": 13.0603, "longitude": 80.2512, "vicinity": "Greams Road, Chennai", "rating": 4.6},
            {"name": "MIOT International Hospital", "latitude": 13.0232, "longitude": 80.1772, "vicinity": "Manapakkam, Chennai", "rating": 4.5},
            {"name": "Fortis Malar Hospital", "latitude": 13.0061, "longitude": 80.2575, "vicinity": "Adyar, Chennai", "rating": 4.4}
        ]
    elif "gas_station" in place_type.lower() or "fuel" in place_type.lower() or "petrol" in place_type.lower():
        return [
            {"name": "Indian Oil Petrol Station", "latitude": 13.0401, "longitude": 80.2322, "vicinity": "T. Nagar, Chennai", "rating": 4.2},
            {"name": "HP Fuel Station", "latitude": 12.9642, "longitude": 80.2451, "vicinity": "OMR Perungudi, Chennai", "rating": 4.3}
        ]
    else:
        return [
            {"name": "Koyambedu CMBT Bus Terminus", "latitude": 13.0694, "longitude": 80.1948, "vicinity": "Koyambedu, Chennai", "rating": 4.4},
            {"name": "Guindy Metro Station", "latitude": 13.0076, "longitude": 80.2030, "vicinity": "Guindy, Chennai", "rating": 4.5}
        ]
