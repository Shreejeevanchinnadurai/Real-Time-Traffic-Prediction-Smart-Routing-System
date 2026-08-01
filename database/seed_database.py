"""
Database Seeder — Synthetic Traffic Data Generator
===================================================
Populates the database with:
  1. 20 Chennai locations with real lat/lng coordinates
  2. 90 days of hourly synthetic traffic observations (~43,200 records)

The generator creates REALISTIC traffic patterns:
  - Peak-hour volume spikes (7-10 AM, 4:30-8 PM)
  - Speed inversely correlated with volume
  - Weather impacts on speed and visibility
  - Weekend vs weekday patterns
  - Accident probability influenced by weather/volume
  - Holiday effects

Usage:
    python -m database.seed_database
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from database.db_connection import get_connection, initialize_database
from database.queries import insert_location, insert_traffic_records_bulk
from utils.constants import WEATHER_CONDITIONS, ROAD_CONDITIONS, WEATHER_SEVERITY_MAP
from utils.helpers import get_congestion_label, safe_divide
from utils.logger import get_logger

logger = get_logger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# CHENNAI LOCATIONS — Real coordinates, realistic road properties
# ═══════════════════════════════════════════════════════════════════════

CHENNAI_LOCATIONS = [
    # (name, lat, lon, road_name, speed_limit, road_capacity)
    ("Sholinganallur",    12.9010, 80.2279, "OMR (IT Corridor)",       60, 600),
    ("T. Nagar",          13.0418, 80.2341, "Usman Road",              40, 400),
    ("Anna Nagar",        13.0850, 80.2101, "2nd Avenue",              50, 500),
    ("Adyar",             13.0067, 80.2572, "Adyar Bridge Road",       50, 450),
    ("Guindy",            13.0067, 80.2206, "Mount Road (Anna Salai)", 50, 550),
    ("Velachery",         12.9815, 80.2180, "Velachery Main Road",     50, 500),
    ("Tambaram",          12.9249, 80.1000, "GST Road",                60, 550),
    ("Porur",             13.0382, 80.1562, "Mount Poonamallee Road",  50, 500),
    ("Perambur",          13.1187, 80.2328, "Perambur High Road",      40, 400),
    ("Mylapore",          13.0368, 80.2676, "Kutchery Road",           40, 350),
    ("Egmore",            13.0732, 80.2609, "Poonamallee High Road",   50, 500),
    ("Chromepet",         12.9516, 80.1441, "GST Road (South)",        60, 550),
    ("Nungambakkam",      13.0569, 80.2425, "Nungambakkam High Road",  40, 400),
    ("Thiruvanmiyur",     12.9830, 80.2594, "East Coast Road",         60, 500),
    ("Madhavaram",        13.1488, 80.2298, "NH-5 (Grand Northern Trunk)", 60, 600),
    ("Koyambedu",         13.0694, 80.1948, "Jawaharlal Nehru Road",   50, 550),
    ("Vadapalani",        13.0524, 80.2123, "Arcot Road",              50, 500),
    ("Besant Nagar",      13.0002, 80.2667, "Besant Nagar Beach Road", 40, 350),
    ("Aminjikarai",       13.0696, 80.2263, "Nelson Manickam Road",    40, 400),
    ("Pallavaram",        12.9675, 80.1505, "Pallavaram-Thoraipakkam Road", 50, 450),
]


# ═══════════════════════════════════════════════════════════════════════
# HOLIDAYS / SPECIAL EVENTS (for the 90-day window)
# ═══════════════════════════════════════════════════════════════════════

def _get_holidays(start_date: datetime) -> set:
    """Generate a set of holiday dates within the 90-day window."""
    holidays = set()
    for day_offset in [0, 14, 25, 45, 60, 75]:  # ~6 holidays in 90 days
        holidays.add((start_date + timedelta(days=day_offset)).date())
    return holidays


def _get_special_events(start_date: datetime) -> set:
    """Generate a set of special event dates (cricket matches, festivals)."""
    events = set()
    for day_offset in [7, 20, 35, 50, 70, 85]:
        events.add((start_date + timedelta(days=day_offset)).date())
    return events


# ═══════════════════════════════════════════════════════════════════════
# TRAFFIC SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════

def _get_weather_for_hour(hour: int, day_seed: int) -> tuple:
    """
    Generate weather conditions based on day seed and hour.
    Returns (weather, temperature, rainfall, visibility).
    """
    random.seed(day_seed * 100 + hour)

    # Base temperature (Chennai: 25-38°C)
    if 6 <= hour <= 10:
        base_temp = random.uniform(26, 30)
    elif 11 <= hour <= 15:
        base_temp = random.uniform(32, 38)
    elif 16 <= hour <= 20:
        base_temp = random.uniform(29, 34)
    else:
        base_temp = random.uniform(25, 29)

    # Weather probability varies by season (simplified)
    weather_roll = random.random()
    if weather_roll < 0.50:
        weather = "Clear"
        rainfall = 0.0
        visibility = random.uniform(8, 10)
    elif weather_roll < 0.70:
        weather = "Cloudy"
        rainfall = 0.0
        visibility = random.uniform(6, 9)
    elif weather_roll < 0.85:
        weather = "Light Rain"
        rainfall = random.uniform(1, 10)
        visibility = random.uniform(4, 7)
        base_temp -= random.uniform(2, 5)
    elif weather_roll < 0.95:
        weather = "Heavy Rain"
        rainfall = random.uniform(10, 50)
        visibility = random.uniform(1, 4)
        base_temp -= random.uniform(4, 8)
    else:
        weather = "Fog"
        rainfall = 0.0
        visibility = random.uniform(0.5, 3)

    return weather, round(base_temp, 1), round(rainfall, 1), round(visibility, 1)


def _generate_vehicle_count(
    hour: int, road_capacity: int, is_weekend: bool,
    is_holiday: bool, is_special_event: bool, location_idx: int,
) -> int:
    """
    Generate realistic vehicle count based on time-of-day patterns.

    Peak hours (weekday):   70-100% of capacity
    Off-peak:               20-50% of capacity
    Late night (10 PM-6 AM): 10-25% of capacity
    Weekends:               60% of weekday levels
    """
    # Base multiplier by hour (realistic traffic curve)
    hourly_pattern = {
        0: 0.12, 1: 0.08, 2: 0.06, 3: 0.05, 4: 0.06, 5: 0.10,
        6: 0.25, 7: 0.55, 8: 0.80, 9: 0.85, 10: 0.65, 11: 0.55,
        12: 0.50, 13: 0.55, 14: 0.55, 15: 0.60, 16: 0.70, 17: 0.90,
        18: 0.95, 19: 0.80, 20: 0.55, 21: 0.40, 22: 0.28, 23: 0.18,
    }

    multiplier = hourly_pattern.get(hour, 0.40)

    # Weekend adjustment
    if is_weekend:
        if 10 <= hour <= 20:
            multiplier *= 0.70  # Weekend daytime: less commuter traffic
        else:
            multiplier *= 0.60  # Weekend off-peak

    # Holiday: behaves like weekend
    if is_holiday and not is_weekend:
        multiplier *= 0.65

    # Special event: more traffic during event hours
    if is_special_event and 16 <= hour <= 22:
        multiplier *= 1.3

    # Add per-location variation (some roads are busier)
    location_factor = 0.85 + (location_idx % 5) * 0.06

    count = int(road_capacity * multiplier * location_factor)

    # Add noise (±10%)
    noise = random.uniform(-0.10, 0.10)
    count = max(5, int(count * (1 + noise)))

    return min(count, int(road_capacity * 1.15))  # Cap at 115% capacity


def _compute_speed(
    vehicle_count: int, road_capacity: int, speed_limit: float,
    weather: str, accident: bool,
) -> float:
    """
    Compute realistic average speed based on traffic conditions.

    As volume approaches capacity, speed degrades following a BPR-like curve.
    Weather and accidents apply additional penalties.
    """
    # Volume-to-capacity ratio
    vc_ratio = safe_divide(vehicle_count, road_capacity, 0.5)

    # BPR (Bureau of Public Roads) speed-flow relationship
    # speed = free_flow_speed / (1 + alpha * (v/c)^beta)
    alpha = 0.15
    beta = 4.0
    speed = speed_limit / (1 + alpha * (vc_ratio ** beta))

    # Weather penalty
    weather_penalties = {
        "Clear": 1.0,
        "Cloudy": 0.95,
        "Light Rain": 0.80,
        "Heavy Rain": 0.60,
        "Fog": 0.65,
    }
    speed *= weather_penalties.get(weather, 1.0)

    # Accident penalty
    if accident:
        speed *= 0.55  # Significant speed reduction

    # Add noise (±5%)
    speed *= random.uniform(0.95, 1.05)

    # Clamp to realistic range
    return round(max(3.0, min(speed, speed_limit)), 1)


def _should_accident_occur(
    vehicle_count: int, road_capacity: int, weather: str, hour: int
) -> bool:
    """
    Determine if an accident should be simulated.
    Base probability ~3%, increased by poor weather and high volume.
    """
    base_prob = 0.03
    vc_ratio = safe_divide(vehicle_count, road_capacity, 0.5)

    # High traffic increases accident risk
    if vc_ratio > 0.8:
        base_prob += 0.04
    elif vc_ratio > 0.6:
        base_prob += 0.02

    # Weather increases risk
    weather_risk = {
        "Clear": 0.0, "Cloudy": 0.01,
        "Light Rain": 0.03, "Heavy Rain": 0.06, "Fog": 0.05,
    }
    base_prob += weather_risk.get(weather, 0.0)

    # Night hours slightly higher risk
    if hour < 6 or hour > 22:
        base_prob += 0.02

    return random.random() < base_prob


def _get_road_condition(weather: str) -> str:
    """Determine road condition based on weather."""
    if weather in ("Heavy Rain",):
        return random.choice(["Fair", "Poor", "Fair"])
    elif weather == "Light Rain":
        return random.choice(["Good", "Fair", "Fair"])
    elif weather == "Fog":
        return random.choice(["Good", "Fair"])
    else:
        roll = random.random()
        if roll < 0.80:
            return "Good"
        elif roll < 0.95:
            return "Fair"
        else:
            return "Poor"


# ═══════════════════════════════════════════════════════════════════════
# MAIN SEEDER
# ═══════════════════════════════════════════════════════════════════════

def seed_locations() -> None:
    """Insert all Chennai locations into the database."""
    logger.info("Seeding locations...")
    for name, lat, lon, road, speed_limit, capacity in CHENNAI_LOCATIONS:
        insert_location(name, lat, lon, road, "Chennai", speed_limit, capacity)
    logger.info(f"Seeded {len(CHENNAI_LOCATIONS)} locations.")


def seed_traffic_data(days: int = None) -> None:
    """
    Generate and insert synthetic traffic data.

    Args:
        days: Number of days to generate (default from Config).
    """
    if days is None:
        days = Config.SYNTHETIC_DAYS

    start_date = datetime.now() - timedelta(days=days)
    holidays = _get_holidays(start_date)
    special_events = _get_special_events(start_date)

    logger.info(f"Generating {days} days of traffic data for {len(CHENNAI_LOCATIONS)} locations...")

    all_records = []
    total_hours = days * 24

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        is_weekend = current_date.weekday() >= 5
        is_holiday = current_date.date() in holidays
        is_special_event = current_date.date() in special_events
        day_seed = current_date.toordinal()

        for hour in range(24):
            timestamp = current_date.replace(hour=hour, minute=0, second=0)
            weather, temp, rainfall, visibility = _get_weather_for_hour(hour, day_seed)
            road_condition = _get_road_condition(weather)

            for loc_idx, (name, lat, lon, road, speed_limit, capacity) in enumerate(CHENNAI_LOCATIONS):
                # Use deterministic seed for reproducibility but add location variation
                random.seed(day_seed * 10000 + hour * 100 + loc_idx + 42)

                vehicle_count = _generate_vehicle_count(
                    hour, capacity, is_weekend, is_holiday, is_special_event, loc_idx
                )

                accident = _should_accident_occur(vehicle_count, capacity, weather, hour)

                avg_speed = _compute_speed(
                    vehicle_count, capacity, speed_limit, weather, accident
                )

                # Determine congestion level from computed metrics
                speed_ratio = safe_divide(avg_speed, speed_limit, 0.5)
                capacity_util = safe_divide(vehicle_count, capacity, 0.5)
                congestion = get_congestion_label(speed_ratio, capacity_util)

                record = (
                    loc_idx + 1,  # location_id (1-indexed)
                    timestamp.isoformat(),
                    vehicle_count,
                    avg_speed,
                    congestion,
                    capacity,
                    weather,
                    visibility,
                    int(accident),
                    road_condition,
                    temp,
                    rainfall,
                    int(is_holiday),
                    int(is_special_event),
                )
                all_records.append(record)

        # Insert in daily batches for efficiency
        if (day_offset + 1) % 10 == 0 or day_offset == days - 1:
            logger.info(
                f"  Progress: Day {day_offset + 1}/{days} "
                f"({len(all_records)} records buffered)"
            )

    # Bulk insert all records
    logger.info(f"Inserting {len(all_records)} traffic records into database...")
    inserted = insert_traffic_records_bulk(all_records)
    logger.info(f"Successfully inserted {inserted} traffic records.")


def seed_database() -> None:
    """Full database seeding: initialize schema → locations → traffic data."""
    logger.info("=" * 60)
    logger.info("STARTING DATABASE SEEDING")
    logger.info("=" * 60)

    # Step 1: Initialize schema
    initialize_database()

    # Step 2: Check if already seeded
    from database.db_connection import get_table_counts
    counts = get_table_counts()
    if counts.get("traffic_data", 0) > 0:
        logger.info(
            f"Database already has {counts['traffic_data']} traffic records. "
            f"Skipping seed."
        )
        return

    # Step 3: Seed locations
    seed_locations()

    # Step 4: Generate and insert traffic data
    seed_traffic_data()

    # Final report
    counts = get_table_counts()
    logger.info("=" * 60)
    logger.info("SEEDING COMPLETE")
    for table, count in counts.items():
        logger.info(f"  {table}: {count} rows")
    logger.info("=" * 60)


# ── Entry Point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    Config.ensure_directories()
    seed_database()
