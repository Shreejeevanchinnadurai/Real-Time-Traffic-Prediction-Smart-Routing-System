"""
Helper Utilities
================
Shared utility functions for date/time operations, coordinate validation,
formatting, and geographic distance calculations.
"""

import math
from datetime import datetime
from typing import Optional, Tuple


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    using the Haversine formula.

    Args:
        lat1, lon1: Coordinates of point 1 (degrees).
        lat2, lon2: Coordinates of point 2 (degrees).

    Returns:
        Distance in kilometers.
    """
    R = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def is_valid_coordinate(lat: float, lon: float) -> bool:
    """Check if latitude and longitude are within valid ranges."""
    return -90 <= lat <= 90 and -180 <= lon <= 180


def is_peak_hour(hour: int, minute: int = 0) -> bool:
    """Check if the given time falls within peak traffic hours."""
    morning_peak = 7 <= hour < 10
    evening_peak = (hour == 16 and minute >= 30) or (17 <= hour < 20)
    return morning_peak or evening_peak


def is_morning_peak(hour: int) -> bool:
    """Check if the given hour falls within morning peak (7-10 AM)."""
    return 7 <= hour < 10


def is_evening_peak(hour: int, minute: int = 0) -> bool:
    """Check if the given hour falls within evening peak (4:30-8 PM)."""
    return (hour == 16 and minute >= 30) or (17 <= hour < 20)


def format_duration(minutes: float) -> str:
    """
    Format duration in minutes to a human-readable string.

    Examples:
        format_duration(95.5) -> "1h 36m"
        format_duration(25.3) -> "25m"
    """
    if minutes < 1:
        return "< 1m"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def format_distance(km: float) -> str:
    """Format distance in km to a human-readable string."""
    if km < 1:
        return f"{int(km * 1000)}m"
    return f"{km:.1f} km"


def get_congestion_label(speed_ratio: float, capacity_util: float) -> str:
    """
    Determine congestion level based on speed ratio and capacity utilization.

    Args:
        speed_ratio:   average_speed / speed_limit (0.0 to 1.0+).
        capacity_util: vehicle_count / road_capacity (0.0 to 1.0+).

    Returns:
        One of: "Low", "Moderate", "High", "Severe".
    """
    if speed_ratio > 0.75 and capacity_util < 0.4:
        return "Low"
    elif speed_ratio > 0.50 or capacity_util < 0.65:
        if speed_ratio > 0.50 and capacity_util < 0.65:
            return "Moderate"
    if speed_ratio < 0.25 or capacity_util > 0.85:
        return "Severe"
    return "High"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division that returns default value when denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def parse_timestamp(ts: str) -> Optional[datetime]:
    """Parse a timestamp string in ISO format."""
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def decode_google_polyline(polyline_str: str) -> list[tuple[float, float]]:
    """
    Decodes a Google Maps encoded polyline string into a list of (lat, lon) tuples.
    Standard Google Polyline Algorithm format.
    """
    if not polyline_str:
        return []

    index, lat, lng = 0, 0, 0
    coordinates = []
    length = len(polyline_str)

    while index < length:
        # Latitude shift decoding
        shift, result = 0, 0
        while True:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        delta_lat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += delta_lat

        # Longitude shift decoding
        shift, result = 0, 0
        while True:
            if index >= length:
                break
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        delta_lng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += delta_lng

        coordinates.append((lat / 1e5, lng / 1e5))

    return coordinates


def calculate_fuel_and_emissions(distance_km: float, duration_minutes: float, avg_speed_kmh: float) -> tuple[float, float, float]:
    """
    Calculate estimated fuel consumption (L), CO2 emissions (kg), and Eco Score (0-100).

    Args:
        distance_km: Route distance in km.
        duration_minutes: Route time in minutes.
        avg_speed_kmh: Average travel speed.

    Returns:
        (fuel_liters, co2_kg, eco_score)
    """
    # Base fuel efficiency (7 L / 100 km at optimal speed ~ 60 km/h)
    base_l_per_100km = 7.0
    
    # Speed efficiency factor (stop-and-go low speed < 20 km/h uses ~40% more fuel)
    if avg_speed_kmh < 20:
        speed_factor = 1.45
    elif avg_speed_kmh < 40:
        speed_factor = 1.15
    elif avg_speed_kmh <= 70:
        speed_factor = 1.0
    else:
        speed_factor = 1.25 # High speed drag
        
    fuel_liters = round((distance_km / 100.0) * base_l_per_100km * speed_factor, 2)
    # Gasoline produces ~2.31 kg CO2 per liter burned
    co2_kg = round(fuel_liters * 2.31, 2)
    
    # Eco Score: 100 is best, penalize low speed and excess fuel
    raw_score = 100 - (speed_factor - 1.0) * 50 - min(fuel_liters * 5, 30)
    eco_score = max(30.0, min(round(raw_score, 1), 98.0))
    
    return fuel_liters, co2_kg, eco_score

