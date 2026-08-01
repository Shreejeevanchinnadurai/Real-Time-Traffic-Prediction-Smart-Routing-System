"""
Application Constants
=====================
Enumerations, color maps, weather types, road conditions, and display
strings used throughout the application.
"""

# ── Weather Conditions ─────────────────────────────────────────────────
WEATHER_CONDITIONS = ["Clear", "Cloudy", "Light Rain", "Heavy Rain", "Fog"]
WEATHER_SEVERITY_MAP = {
    "Clear": 0,
    "Cloudy": 1,
    "Light Rain": 2,
    "Heavy Rain": 3,
    "Fog": 4,
}

# ── Road Conditions ────────────────────────────────────────────────────
ROAD_CONDITIONS = ["Good", "Fair", "Poor", "Under Construction"]
ROAD_CONDITION_PENALTY = {
    "Good": 1.0,
    "Fair": 1.1,
    "Poor": 1.3,
    "Under Construction": 1.6,
}

# ── Congestion Color Map (for maps and charts) ────────────────────────
CONGESTION_COLORS = {
    "Low": "#2ecc71",        # Green
    "Moderate": "#f39c12",   # Yellow/Orange
    "High": "#e67e22",       # Orange
    "Severe": "#e74c3c",     # Red
}

CONGESTION_ICONS = {
    "Low": "✅",
    "Moderate": "⚠️",
    "High": "🔶",
    "Severe": "🔴",
}

# ── Route Line Colors ─────────────────────────────────────────────────
ROUTE_COLORS = ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6", "#f39c12"]

# ── Peak Hour Definitions ─────────────────────────────────────────────
MORNING_PEAK_START = 7
MORNING_PEAK_END = 10
EVENING_PEAK_START_HOUR = 16
EVENING_PEAK_START_MINUTE = 30
EVENING_PEAK_END = 20

# ── Speed Limits (km/h) by road type ──────────────────────────────────
DEFAULT_SPEED_LIMIT = 50
HIGHWAY_SPEED_LIMIT = 80
RESIDENTIAL_SPEED_LIMIT = 30

# ── Display Strings ────────────────────────────────────────────────────
APP_TITLE = "🚦 Traffic Intelligence System"
APP_SUBTITLE = "Real-Time Traffic Prediction & Smart Routing"
PAGE_ICON = "🚦"
SIMULATED_LABEL = "⚡ Simulated Real-Time Traffic Feed"

# ── Days of Week ───────────────────────────────────────────────────────
DAYS_OF_WEEK = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]
