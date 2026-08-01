"""
Database Query Functions
========================
Parameterized CRUD operations for all tables.
Every query uses ? placeholders — never string interpolation.

Usage:
    from database.queries import insert_traffic_record, get_traffic_by_location
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from database.db_connection import get_connection
from utils.logger import get_logger

logger = get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# RAW EXECUTION
# ═══════════════════════════════════════════════════════════════════════

import pandas as pd

def execute_query(query: str, params: tuple = ()) -> pd.DataFrame:
    """Execute a raw SQL query and return a pandas DataFrame."""
    try:
        with get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        logger.error(f"Raw query execution failed: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════
# LOCATIONS
# ═══════════════════════════════════════════════════════════════════════

def insert_location(
    name: str, lat: float, lon: float, road: str,
    city: str = "Chennai", speed_limit: float = 50.0,
    road_capacity: int = 500
) -> Optional[int]:
    """Insert a new location and return its ID."""
    sql = """
        INSERT OR IGNORE INTO locations
            (location_name, latitude, longitude, road_name, city, speed_limit, road_capacity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                sql, (name, lat, lon, road, city, speed_limit, road_capacity)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Insert location failed: {e}")
        return None


def get_all_locations() -> List[Dict[str, Any]]:
    """Retrieve all locations as a list of dictionaries."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM locations ORDER BY location_name"
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Get locations failed: {e}")
        return []


def get_location_by_id(location_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single location by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM locations WHERE location_id = ?", (location_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        logger.error(f"Get location by ID failed: {e}")
        return None


def get_location_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single location by name."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM locations WHERE location_name = ?", (name,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        logger.error(f"Get location by name failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# TRAFFIC DATA
# ═══════════════════════════════════════════════════════════════════════

def insert_traffic_record(record: Dict[str, Any]) -> Optional[int]:
    """Insert a single traffic observation record."""
    sql = """
        INSERT INTO traffic_data
            (location_id, timestamp, vehicle_count, average_speed,
             congestion_level, road_capacity, weather_condition, visibility,
             accident_reported, road_condition, temperature, rainfall,
             is_holiday, is_special_event)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, (
                record["location_id"], record["timestamp"],
                record["vehicle_count"], record["average_speed"],
                record["congestion_level"], record["road_capacity"],
                record["weather_condition"], record["visibility"],
                record["accident_reported"], record["road_condition"],
                record["temperature"], record["rainfall"],
                record.get("is_holiday", 0), record.get("is_special_event", 0),
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Insert traffic record failed: {e}")
        return None


def insert_traffic_records_bulk(records: List[Tuple]) -> int:
    """
    Bulk insert traffic records for performance.

    Args:
        records: List of tuples matching traffic_data column order.

    Returns:
        Number of rows inserted.
    """
    sql = """
        INSERT INTO traffic_data
            (location_id, timestamp, vehicle_count, average_speed,
             congestion_level, road_capacity, weather_condition, visibility,
             accident_reported, road_condition, temperature, rainfall,
             is_holiday, is_special_event)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        with get_connection() as conn:
            conn.executemany(sql, records)
            conn.commit()
            return len(records)
    except sqlite3.Error as e:
        logger.error(f"Bulk insert failed: {e}")
        return 0


def get_traffic_data(
    location_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    congestion_level: Optional[str] = None,
    limit: int = 10000,
) -> List[Dict[str, Any]]:
    """
    Retrieve traffic data with optional filters.

    Args:
        location_id:     Filter by location.
        start_date:      Filter by start date (ISO format).
        end_date:        Filter by end date (ISO format).
        congestion_level: Filter by congestion level.
        limit:           Maximum number of records.

    Returns:
        List of traffic records as dictionaries.
    """
    conditions = []
    params: List[Any] = []

    if location_id is not None:
        conditions.append("t.location_id = ?")
        params.append(location_id)
    if start_date:
        conditions.append("t.timestamp >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("t.timestamp <= ?")
        params.append(end_date)
    if congestion_level:
        conditions.append("t.congestion_level = ?")
        params.append(congestion_level)

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    sql = f"""
        SELECT t.*, l.location_name, l.road_name, l.latitude, l.longitude,
               l.speed_limit
        FROM traffic_data t
        JOIN locations l ON t.location_id = l.location_id
        {where_clause}
        ORDER BY t.timestamp DESC
        LIMIT ?
    """
    params.append(limit)

    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Get traffic data failed: {e}")
        return []


def get_all_traffic_data_for_training() -> List[Dict[str, Any]]:
    """Retrieve ALL traffic data joined with locations for ML training."""
    sql = """
        SELECT t.*, l.location_name, l.road_name, l.latitude, l.longitude,
               l.speed_limit
        FROM traffic_data t
        JOIN locations l ON t.location_id = l.location_id
        ORDER BY t.timestamp ASC
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql)
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Get training data failed: {e}")
        return []


def get_latest_traffic(limit: int = 50) -> List[Dict[str, Any]]:
    """Get the most recent traffic records across all locations."""
    sql = """
        SELECT t.*, l.location_name, l.road_name, l.latitude, l.longitude
        FROM traffic_data t
        JOIN locations l ON t.location_id = l.location_id
        ORDER BY t.timestamp DESC
        LIMIT ?
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Get latest traffic failed: {e}")
        return []


def get_traffic_stats() -> Dict[str, Any]:
    """Get aggregate traffic statistics."""
    sql = """
        SELECT
            COUNT(*) as total_records,
            AVG(average_speed) as avg_speed,
            AVG(vehicle_count) as avg_vehicle_count,
            SUM(CASE WHEN congestion_level = 'Severe' THEN 1 ELSE 0 END) as severe_count,
            SUM(CASE WHEN congestion_level = 'High' THEN 1 ELSE 0 END) as high_count,
            SUM(CASE WHEN accident_reported = 1 THEN 1 ELSE 0 END) as accident_count
        FROM traffic_data
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql)
            row = cursor.fetchone()
            return dict(row) if row else {}
    except sqlite3.Error as e:
        logger.error(f"Get traffic stats failed: {e}")
        return {}


# ═══════════════════════════════════════════════════════════════════════
# PREDICTIONS
# ═══════════════════════════════════════════════════════════════════════

def insert_prediction(
    location_id: int,
    predicted_vehicle_count: Optional[int],
    predicted_speed: Optional[float],
    predicted_congestion: Optional[str],
    model_name: str,
    confidence_score: Optional[float] = None,
) -> Optional[int]:
    """Store a prediction result in the database."""
    sql = """
        INSERT INTO predictions
            (location_id, prediction_time, predicted_vehicle_count,
             predicted_speed, predicted_congestion, model_name, confidence_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, (
                location_id, datetime.now().isoformat(),
                predicted_vehicle_count, predicted_speed,
                predicted_congestion, model_name, confidence_score,
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Insert prediction failed: {e}")
        return None


def get_predictions(
    location_id: Optional[int] = None, limit: int = 100
) -> List[Dict[str, Any]]:
    """Retrieve predictions with optional location filter."""
    if location_id:
        sql = """
            SELECT p.*, l.location_name, l.road_name
            FROM predictions p
            JOIN locations l ON p.location_id = l.location_id
            WHERE p.location_id = ?
            ORDER BY p.prediction_time DESC
            LIMIT ?
        """
        params: tuple = (location_id, limit)
    else:
        sql = """
            SELECT p.*, l.location_name, l.road_name
            FROM predictions p
            JOIN locations l ON p.location_id = l.location_id
            ORDER BY p.prediction_time DESC
            LIMIT ?
        """
        params = (limit,)

    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Get predictions failed: {e}")
        return []


def get_prediction_count() -> int:
    """Get total number of predictions stored."""
    try:
        with get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM predictions")
            return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f"Get prediction count failed: {e}")
        return 0


# ═══════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════

def insert_route(
    source_id: int, destination_id: int,
    distance: float, duration: float,
    congestion_score: float, route_path: str,
) -> Optional[int]:
    """Store a computed route in the database."""
    sql = """
        INSERT INTO routes
            (source_id, destination_id, route_distance,
             estimated_duration, congestion_score, route_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, (
                source_id, destination_id, distance,
                duration, congestion_score, route_path,
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Insert route failed: {e}")
        return None


def insert_route_history(
    route_id: int, reason: str, alternatives: List[Dict]
) -> Optional[int]:
    """Store route recommendation history with alternatives."""
    sql = """
        INSERT INTO route_history
            (route_id, recommendation_reason, alternatives_json)
        VALUES (?, ?, ?)
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, (
                route_id, reason, json.dumps(alternatives),
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Insert route history failed: {e}")
        return None


def get_routes(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent routes with location names."""
    sql = """
        SELECT r.*,
               s.location_name as source_name,
               d.location_name as destination_name
        FROM routes r
        JOIN locations s ON r.source_id = s.location_id
        JOIN locations d ON r.destination_id = d.location_id
        ORDER BY r.route_created_at DESC
        LIMIT ?
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Get routes failed: {e}")
        return []


def get_route_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve route recommendation history."""
    sql = """
        SELECT rh.*, r.route_distance, r.estimated_duration,
               s.location_name as source_name,
               d.location_name as destination_name
        FROM route_history rh
        JOIN routes r ON rh.route_id = r.route_id
        JOIN locations s ON r.source_id = s.location_id
        JOIN locations d ON r.destination_id = d.location_id
        ORDER BY rh.created_at DESC
        LIMIT ?
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Get route history failed: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════
# CROWDSOURCED REPORTS & USER PREFERENCES
# ═══════════════════════════════════════════════════════════════════════

def insert_crowdsourced_report(
    location_name: str, incident_type: str, description: str = ""
) -> Optional[int]:
    """Insert a crowdsourced traffic incident report."""
    sql = """
        INSERT INTO crowdsourced_reports (location_name, incident_type, description, upvotes, confidence_score)
        VALUES (?, ?, ?, 1, 0.85)
    """
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, (location_name, incident_type, description))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Insert crowdsourced report failed: {e}")
        return None

def get_recent_crowdsourced_reports(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve recent crowdsourced reports."""
    sql = "SELECT * FROM crowdsourced_reports ORDER BY timestamp DESC LIMIT ?"
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Get crowdsourced reports failed: {e}")
        return []

def get_signal_timings() -> List[Dict[str, Any]]:
    """Retrieve intersection traffic signal timing allocations."""
    sql = "SELECT * FROM signal_timings ORDER BY signal_id ASC"
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql)
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Get signal timings failed: {e}")
        return []

