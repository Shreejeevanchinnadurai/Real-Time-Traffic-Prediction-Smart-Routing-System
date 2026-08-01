-- =====================================================================
-- Traffic Prediction System — Database Schema
-- =====================================================================
-- SQLite DDL for all five core tables.
-- Run this script via: sqlite3 traffic.db < schema.sql
-- Or use db_connection.py's initialize_database() function.
-- =====================================================================

-- ── Locations Table ───────────────────────────────────────────────────
-- Stores all monitored traffic locations (intersections, landmarks).
CREATE TABLE IF NOT EXISTS locations (
    location_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name   TEXT    NOT NULL UNIQUE,
    latitude        REAL    NOT NULL,
    longitude       REAL    NOT NULL,
    road_name       TEXT    NOT NULL,
    city            TEXT    NOT NULL DEFAULT 'Chennai',
    speed_limit     REAL    NOT NULL DEFAULT 50.0,
    road_capacity   INTEGER NOT NULL DEFAULT 500
);

CREATE INDEX IF NOT EXISTS idx_locations_name ON locations(location_name);
CREATE INDEX IF NOT EXISTS idx_locations_road ON locations(road_name);

-- ── Traffic Data Table ────────────────────────────────────────────────
-- Historical and simulated traffic observations.
CREATE TABLE IF NOT EXISTS traffic_data (
    traffic_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id         INTEGER NOT NULL,
    timestamp           TEXT    NOT NULL,
    vehicle_count       INTEGER NOT NULL,
    average_speed       REAL    NOT NULL,
    congestion_level    TEXT    NOT NULL DEFAULT 'Low',
    road_capacity       INTEGER NOT NULL DEFAULT 500,
    weather_condition   TEXT    NOT NULL DEFAULT 'Clear',
    visibility          REAL    NOT NULL DEFAULT 10.0,
    accident_reported   INTEGER NOT NULL DEFAULT 0,
    road_condition      TEXT    NOT NULL DEFAULT 'Good',
    temperature         REAL    NOT NULL DEFAULT 30.0,
    rainfall            REAL    NOT NULL DEFAULT 0.0,
    is_holiday          INTEGER NOT NULL DEFAULT 0,
    is_special_event    INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (location_id) REFERENCES locations(location_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_traffic_location  ON traffic_data(location_id);
CREATE INDEX IF NOT EXISTS idx_traffic_timestamp ON traffic_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_traffic_congestion ON traffic_data(congestion_level);

-- ── Predictions Table ─────────────────────────────────────────────────
-- Stores ML-generated traffic predictions.
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id             INTEGER NOT NULL,
    prediction_time         TEXT    NOT NULL,
    predicted_vehicle_count INTEGER,
    predicted_speed         REAL,
    predicted_congestion    TEXT,
    model_name              TEXT    NOT NULL DEFAULT 'unknown',
    confidence_score        REAL,

    FOREIGN KEY (location_id) REFERENCES locations(location_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_predictions_location ON predictions(location_id);
CREATE INDEX IF NOT EXISTS idx_predictions_time     ON predictions(prediction_time);

-- ── Routes Table ──────────────────────────────────────────────────────
-- Stores computed route recommendations.
CREATE TABLE IF NOT EXISTS routes (
    route_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id           INTEGER NOT NULL,
    destination_id      INTEGER NOT NULL,
    route_distance      REAL    NOT NULL,
    estimated_duration  REAL    NOT NULL,
    congestion_score    REAL    NOT NULL DEFAULT 0.0,
    route_path          TEXT,
    route_created_at    TEXT    NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (source_id)      REFERENCES locations(location_id),
    FOREIGN KEY (destination_id) REFERENCES locations(location_id)
);

CREATE INDEX IF NOT EXISTS idx_routes_source ON routes(source_id);
CREATE INDEX IF NOT EXISTS idx_routes_dest   ON routes(destination_id);

-- ── Route History Table ───────────────────────────────────────────────
-- Logs historical route recommendations with reasoning.
CREATE TABLE IF NOT EXISTS route_history (
    history_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id                INTEGER NOT NULL,
    recommendation_reason   TEXT,
    alternatives_json       TEXT,
    created_at              TEXT    NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (route_id) REFERENCES routes(route_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_route_history_route ON route_history(route_id);

-- ── Crowdsourced Reports Table ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS crowdsourced_reports (
    report_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name     TEXT    NOT NULL,
    incident_type     TEXT    NOT NULL, -- Accident, Construction, Water Logging, Traffic Jam, Police Checking
    description       TEXT,
    timestamp         TEXT    NOT NULL DEFAULT (datetime('now')),
    upvotes           INTEGER NOT NULL DEFAULT 1,
    confidence_score  REAL    NOT NULL DEFAULT 0.75,
    status            TEXT    NOT NULL DEFAULT 'VERIFIED'
);

-- ── User Preferences Table ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_preferences (
    pref_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           TEXT    NOT NULL DEFAULT 'default_user',
    preferred_profile TEXT    NOT NULL DEFAULT 'Fastest (Traffic-Aware)',
    avoided_roads     TEXT,   -- JSON array of road names
    frequent_routes   TEXT,   -- JSON array of {source, dest}
    updated_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ── Signal Timings Table ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS signal_timings (
    signal_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    intersection_name TEXT    NOT NULL,
    current_phase     TEXT    NOT NULL DEFAULT 'GREEN',
    green_duration_s  INTEGER NOT NULL DEFAULT 45,
    predicted_queue   INTEGER NOT NULL DEFAULT 12,
    optimized_time_s  INTEGER NOT NULL DEFAULT 60,
    updated_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);

