"""
Centralized Configuration Module
================================
Single source of truth for all project settings: paths, database config,
feature lists, model hyperparameters, and application constants.

Usage:
    from config.config import Config
    db_path = Config.DB_PATH
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """Helper to fetch configuration values from Streamlit secrets or OS environment."""
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)


class Config:
    """Application-wide configuration."""

    # ── Project Paths ──────────────────────────────────────────────────
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()
    DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
    DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
    MODELS_DIR = PROJECT_ROOT / "models" / "trained"
    LOG_DIR = PROJECT_ROOT / "logs"

    # ── Database Configuration ─────────────────────────────────────────
    DB_TYPE = _get_secret("DB_TYPE", "sqlite")
    DB_PATH = PROJECT_ROOT / "database" / _get_secret("DB_NAME", "traffic.db")
    DB_HOST = _get_secret("DB_HOST", "localhost")
    DB_PORT = int(_get_secret("DB_PORT", "3306"))
    DB_USER = _get_secret("DB_USER", "")
    DB_PASSWORD = _get_secret("DB_PASSWORD", "")
    DB_NAME = _get_secret("DB_NAME", "traffic.db")

    # ── Google Maps Platform Config ────────────────────────────────────
    GOOGLE_MAPS_API_KEY = _get_secret("GOOGLE_MAPS_API_KEY", "")
    MAP_PROVIDER = "google" if _get_secret("GOOGLE_MAPS_API_KEY", "") else "folium"

    # ── Synthetic Data Settings ────────────────────────────────────────
    SYNTHETIC_DAYS = int(os.getenv("SYNTHETIC_DAYS", "90"))
    SYNTHETIC_INTERVAL_HOURS = 1  # One record per location per hour

    # ── ML Feature Columns ─────────────────────────────────────────────
    # Features used during training — MUST match inference
    CLASSIFICATION_FEATURES = [
        "hour", "day_of_week", "month", "is_weekend", "is_peak_hour",
        "is_morning_peak", "is_evening_peak", "vehicle_count",
        "road_capacity", "traffic_density", "speed_ratio",
        "capacity_utilization", "weather_severity", "visibility",
        "accident_reported", "temperature", "rainfall",
        "accident_risk", "is_holiday", "is_special_event",
    ]

    REGRESSION_FEATURES = [
        "hour", "day_of_week", "month", "is_weekend", "is_peak_hour",
        "is_morning_peak", "is_evening_peak", "vehicle_count",
        "road_capacity", "traffic_density", "capacity_utilization",
        "weather_severity", "visibility", "accident_reported",
        "temperature", "rainfall", "accident_risk",
        "is_holiday", "is_special_event",
    ]

    CLASSIFICATION_TARGET = "congestion_level"
    REGRESSION_TARGET = "average_speed"

    # ── Congestion Thresholds ──────────────────────────────────────────
    CONGESTION_LEVELS = {
        "Low": 0,
        "Moderate": 1,
        "High": 2,
        "Severe": 3,
    }
    CONGESTION_LABELS = ["Low", "Moderate", "High", "Severe"]

    # ── Model File Names ───────────────────────────────────────────────
    CLASSIFICATION_MODEL_FILE = "congestion_classifier.joblib"
    REGRESSION_MODEL_FILE = "speed_regressor.joblib"
    CLASSIFICATION_PIPELINE_FILE = "classification_pipeline.joblib"
    REGRESSION_PIPELINE_FILE = "regression_pipeline.joblib"
    CLASSIFICATION_METRICS_FILE = "classification_metrics.joblib"
    REGRESSION_METRICS_FILE = "regression_metrics.joblib"
    MODEL_COMPARISON_FILE = "model_comparison.joblib"

    # ── Train/Test Split ───────────────────────────────────────────────
    TRAIN_RATIO = 0.70
    VALIDATION_RATIO = 0.15
    TEST_RATIO = 0.15

    # ── Routing Configuration ──────────────────────────────────────────
    CONGESTION_PENALTIES = {
        "Low": 1.0,
        "Moderate": 1.3,
        "High": 1.7,
        "Severe": 2.5,
    }
    INCIDENT_PENALTY = 1.5
    K_ALTERNATIVE_ROUTES = 3  # Number of alternative routes to generate

    # ── Streamlit Settings ─────────────────────────────────────────────
    PAGE_TITLE = "Traffic Intelligence System"
    PAGE_ICON = "🚦"
    LAYOUT = "wide"

    # ── Alert Thresholds ───────────────────────────────────────────────
    TRAVEL_TIME_SPIKE_FACTOR = 1.3  # 30% above average triggers alert
    CAPACITY_WARNING_THRESHOLD = 0.80  # 80% capacity triggers alert

    @classmethod
    def ensure_directories(cls) -> None:
        """Create all required directories if they don't exist."""
        for directory in [
            cls.DATA_RAW_DIR,
            cls.DATA_PROCESSED_DIR,
            cls.MODELS_DIR,
            cls.LOG_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
