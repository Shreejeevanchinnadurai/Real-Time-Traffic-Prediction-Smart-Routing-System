"""
Model Evaluation Module
=======================
Provides functions to load and display model evaluation metrics,
confusion matrices, feature importance, and comparison tables.

Usage:
    from models.evaluate_model import load_model_metrics, get_comparison_table
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


def load_classification_metrics() -> Optional[List[Dict]]:
    """Load saved classification model evaluation metrics."""
    path = Config.MODELS_DIR / Config.CLASSIFICATION_METRICS_FILE
    try:
        return joblib.load(path)
    except FileNotFoundError:
        logger.warning(f"Classification metrics not found: {path}")
        return None


def load_regression_metrics() -> Optional[List[Dict]]:
    """Load saved regression model evaluation metrics."""
    path = Config.MODELS_DIR / Config.REGRESSION_METRICS_FILE
    try:
        return joblib.load(path)
    except FileNotFoundError:
        logger.warning(f"Regression metrics not found: {path}")
        return None


def load_model_comparison() -> Optional[Dict]:
    """Load the full model comparison summary."""
    path = Config.MODELS_DIR / Config.MODEL_COMPARISON_FILE
    try:
        return joblib.load(path)
    except FileNotFoundError:
        logger.warning(f"Model comparison not found: {path}")
        return None


def get_classification_comparison_df() -> Optional[pd.DataFrame]:
    """
    Get a formatted DataFrame comparing all classification models.

    Returns:
        DataFrame with columns: Model, Accuracy, Precision, Recall, F1, Training Time.
    """
    metrics = load_classification_metrics()
    if not metrics:
        return None

    rows = []
    for m in metrics:
        rows.append({
            "Model": m["model_name"],
            "Accuracy": m["accuracy"],
            "Precision": m["precision"],
            "Recall": m["recall"],
            "F1-Score": m["f1_score"],
            "Training Time (s)": m["training_time"],
            "Train Size": m.get("train_size", "N/A"),
            "Test Size": m.get("test_size", "N/A"),
        })

    df = pd.DataFrame(rows).sort_values("F1-Score", ascending=False)
    return df


def get_regression_comparison_df() -> Optional[pd.DataFrame]:
    """
    Get a formatted DataFrame comparing all regression models.

    Returns:
        DataFrame with columns: Model, MAE, MSE, RMSE, R², Training Time.
    """
    metrics = load_regression_metrics()
    if not metrics:
        return None

    rows = []
    for m in metrics:
        rows.append({
            "Model": m["model_name"],
            "MAE": m["mae"],
            "MSE": m["mse"],
            "RMSE": m["rmse"],
            "R²": m["r2"],
            "Training Time (s)": m["training_time"],
            "Train Size": m.get("train_size", "N/A"),
            "Test Size": m.get("test_size", "N/A"),
        })

    df = pd.DataFrame(rows).sort_values("RMSE")
    return df


def get_best_classification_metrics() -> Optional[Dict]:
    """Get metrics for the best classification model."""
    comparison = load_model_comparison()
    if not comparison:
        return None

    best_name = comparison["classification"]["best_model"]
    for r in comparison["classification"]["results"]:
        if r["model_name"] == best_name:
            return r
    return None


def get_best_regression_metrics() -> Optional[Dict]:
    """Get metrics for the best regression model."""
    comparison = load_model_comparison()
    if not comparison:
        return None

    best_name = comparison["regression"]["best_model"]
    for r in comparison["regression"]["results"]:
        if r["model_name"] == best_name:
            return r
    return None


def get_feature_importance_df(task: str = "classification") -> Optional[pd.DataFrame]:
    """
    Get feature importance from the best model as a sorted DataFrame.

    Args:
        task: "classification" or "regression".

    Returns:
        DataFrame with Feature and Importance columns, sorted descending.
    """
    if task == "classification":
        metrics = get_best_classification_metrics()
    else:
        metrics = get_best_regression_metrics()

    if not metrics or not metrics.get("feature_importance"):
        return None

    imp = metrics["feature_importance"]
    df = pd.DataFrame([
        {"Feature": k, "Importance": v}
        for k, v in imp.items()
    ]).sort_values("Importance", ascending=False)

    return df
