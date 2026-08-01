"""
Google Maps Platform Integration Tests
======================================
Tests API key loading, geocoding, Google Routes candidate generation,
Places search, fallback capabilities, and TrafficAI ML forecast integration.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from services.google_maps_service import geocode_location_google, get_google_route
from services.google_routes_service import get_google_candidate_routes
from services.google_places_service import get_nearby_places


def test_env_var_loading():
    """Verify GOOGLE_MAPS_API_KEY environment variable is configured."""
    assert Config.GOOGLE_MAPS_API_KEY != "", "GOOGLE_MAPS_API_KEY should be set in .env"
    assert Config.MAP_PROVIDER in ["google", "folium"]


def test_google_geocoding():
    """Test geocoding for Tamil Nadu locations."""
    lat, lon, display_name = geocode_location_google("T. Nagar, Chennai")
    assert lat > 0
    assert lon > 0
    assert "Chennai" in display_name or "T. Nagar" in display_name


def test_google_routes_candidate_generation():
    """Test Google Routes API candidate generation."""
    # T. Nagar to Chennai Airport
    routes = get_google_candidate_routes(13.0418, 80.2341, 12.9941, 80.1709, alternatives=True)
    assert len(routes) > 0
    
    best_route = routes[0]
    assert "total_distance_km" in best_route
    assert "total_duration_min" in best_route
    assert best_route["total_distance_km"] > 0
    assert best_route["total_duration_min"] > 0


def test_google_places_nearby():
    """Test Places POI retrieval."""
    hospitals = get_nearby_places(13.0418, 80.2341, "hospital")
    assert len(hospitals) > 0
    assert "name" in hospitals[0]
    assert "latitude" in hospitals[0]


def test_fallback_when_key_missing(monkeypatch):
    """Test graceful fallback behavior when API key is missing."""
    monkeypatch.setattr(Config, "GOOGLE_MAPS_API_KEY", "")
    
    lat, lon, name = geocode_location_google("T. Nagar, Chennai")
    assert lat > 0
    
    routes = get_google_route(13.0418, 80.2341, 12.9941, 80.1709)
    assert len(routes) > 0
