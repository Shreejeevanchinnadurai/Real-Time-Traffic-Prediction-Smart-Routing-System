"""
Preprocessing Pipeline
======================
Combines data cleaning and feature engineering into a single reusable
pipeline. Also provides sklearn-compatible Pipeline objects that are
saved alongside trained models to ensure training/inference consistency.

Usage:
    from preprocessing.preprocessing_pipeline import (
        build_full_dataset,
        create_classification_pipeline,
        create_regression_pipeline,
    )
"""

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder

from preprocessing.data_cleaning import clean_traffic_data
from preprocessing.feature_engineering import engineer_features
from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


def build_full_dataset() -> pd.DataFrame:
    """
    Load traffic data from database, clean it, and engineer features.
    Returns a fully prepared DataFrame ready for model training.

    Returns:
        Preprocessed DataFrame with all features and targets.
    """
    from database.queries import get_all_traffic_data_for_training

    logger.info("Building full dataset from database...")

    # Step 1: Load from DB
    raw_records = get_all_traffic_data_for_training()
    if not raw_records:
        logger.error("No traffic data found in database!")
        raise ValueError("No traffic data in database. Run seed_database.py first.")

    df = pd.DataFrame(raw_records)
    logger.info(f"Loaded {len(df)} records from database")

    # Step 2: Clean
    df = clean_traffic_data(df)

    # Step 3: Engineer features
    df = engineer_features(df)

    # Step 4: Encode congestion level for classification
    congestion_map = Config.CONGESTION_LEVELS
    df["congestion_encoded"] = df["congestion_level"].map(congestion_map)

    # Drop any rows with NaN in critical columns
    critical_cols = Config.CLASSIFICATION_FEATURES + [Config.CLASSIFICATION_TARGET]
    available_cols = [c for c in critical_cols if c in df.columns]
    df = df.dropna(subset=available_cols)

    logger.info(f"Final dataset: {len(df)} rows × {len(df.columns)} columns")
    return df


def prepare_classification_data(df: pd.DataFrame):
    """
    Prepare data for congestion classification.

    Uses chronological splitting (oldest 70% train, 15% val, 15% test).

    Returns:
        (X_train, X_val, X_test, y_train, y_val, y_test, feature_names)
    """
    # Ensure sorted by timestamp
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp").reset_index(drop=True)

    # Select features that exist in the dataframe
    features = [f for f in Config.CLASSIFICATION_FEATURES if f in df.columns]
    target = "congestion_encoded"

    if target not in df.columns:
        congestion_map = Config.CONGESTION_LEVELS
        df[target] = df[Config.CLASSIFICATION_TARGET].map(congestion_map)

    X = df[features].copy()
    y = df[target].copy()

    # Drop rows where target is NaN
    valid_mask = y.notna()
    X = X[valid_mask]
    y = y[valid_mask].astype(int)

    # Chronological split
    n = len(X)
    train_end = int(n * Config.TRAIN_RATIO)
    val_end = int(n * (Config.TRAIN_RATIO + Config.VALIDATION_RATIO))

    X_train = X.iloc[:train_end]
    y_train = y.iloc[:train_end]
    X_val = X.iloc[train_end:val_end]
    y_val = y.iloc[train_end:val_end]
    X_test = X.iloc[val_end:]
    y_test = y.iloc[val_end:]

    logger.info(
        f"Classification split — Train: {len(X_train)}, "
        f"Val: {len(X_val)}, Test: {len(X_test)}"
    )

    return X_train, X_val, X_test, y_train, y_val, y_test, features


def prepare_regression_data(df: pd.DataFrame):
    """
    Prepare data for speed/travel-time regression.

    Uses chronological splitting.

    Returns:
        (X_train, X_val, X_test, y_train, y_val, y_test, feature_names)
    """
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp").reset_index(drop=True)

    features = [f for f in Config.REGRESSION_FEATURES if f in df.columns]
    target = Config.REGRESSION_TARGET

    X = df[features].copy()
    y = df[target].copy()

    valid_mask = y.notna()
    X = X[valid_mask]
    y = y[valid_mask]

    n = len(X)
    train_end = int(n * Config.TRAIN_RATIO)
    val_end = int(n * (Config.TRAIN_RATIO + Config.VALIDATION_RATIO))

    X_train = X.iloc[:train_end]
    y_train = y.iloc[:train_end]
    X_val = X.iloc[train_end:val_end]
    y_val = y.iloc[train_end:val_end]
    X_test = X.iloc[val_end:]
    y_test = y.iloc[val_end:]

    logger.info(
        f"Regression split — Train: {len(X_train)}, "
        f"Val: {len(X_val)}, Test: {len(X_test)}"
    )

    return X_train, X_val, X_test, y_train, y_val, y_test, features


def create_scaler_pipeline(feature_names: list) -> Pipeline:
    """
    Create a StandardScaler pipeline for models that benefit from scaling
    (Logistic Regression, Linear Regression).

    Returns:
        Fitted-ready sklearn Pipeline.
    """
    return Pipeline([
        ("scaler", StandardScaler()),
    ])
