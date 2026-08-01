"""
Prediction Module
=================
Loads saved ML models and generates predictions from user input.

Usage:
    from models.predict import predict_congestion, predict_speed
    result = predict_congestion(input_features)
"""

import joblib
import numpy as np
import pandas as pd
from typing import Any, Dict, Optional

from config.config import Config
from preprocessing.feature_engineering import engineer_features
from utils.logger import get_logger

logger = get_logger(__name__)

# Module-level model cache (loaded once, reused)
_classification_model = None
_classification_pipeline = None
_regression_model = None
_regression_pipeline = None


def _load_classification_model():
    """Load classification model and pipeline from disk (cached)."""
    global _classification_model, _classification_pipeline
    if _classification_model is None:
        model_path = Config.MODELS_DIR / Config.CLASSIFICATION_MODEL_FILE
        pipeline_path = Config.MODELS_DIR / Config.CLASSIFICATION_PIPELINE_FILE

        if not model_path.exists():
            raise FileNotFoundError(
                f"Classification model not found at {model_path}. "
                f"Run 'python -m models.train_model' first."
            )

        _classification_model = joblib.load(model_path)
        _classification_pipeline = joblib.load(pipeline_path)
        logger.info("Classification model loaded from disk")

    return _classification_model, _classification_pipeline


def _load_regression_model():
    """Load regression model and pipeline from disk (cached)."""
    global _regression_model, _regression_pipeline
    if _regression_model is None:
        model_path = Config.MODELS_DIR / Config.REGRESSION_MODEL_FILE
        pipeline_path = Config.MODELS_DIR / Config.REGRESSION_PIPELINE_FILE

        if not model_path.exists():
            raise FileNotFoundError(
                f"Regression model not found at {model_path}. "
                f"Run 'python -m models.train_model' first."
            )

        _regression_model = joblib.load(model_path)
        _regression_pipeline = joblib.load(pipeline_path)
        logger.info("Regression model loaded from disk")

    return _regression_model, _regression_pipeline


def predict_congestion(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict traffic congestion level from input features.

    Args:
        input_data: Dictionary with feature values matching training features.
                    Must include keys like hour, day_of_week, vehicle_count, etc.

    Returns:
        Dictionary with:
            - predicted_congestion: str ("Low", "Moderate", "High", "Severe")
            - confidence_score: float (probability of predicted class, if available)
            - model_name: str
            - all_probabilities: dict (class → probability, if available)
    """
    model, pipeline_data = _load_classification_model()
    feature_names = pipeline_data["feature_names"]
    scaler = pipeline_data["scaler"]
    labels = pipeline_data["labels"]

    # Build feature vector
    features = {}
    for f in feature_names:
        if f in input_data:
            features[f] = input_data[f]
        else:
            features[f] = 0  # Default for missing features
            logger.warning(f"Feature '{f}' missing from input, using default 0")

    X = pd.DataFrame([features])[feature_names]

    # Scale if the model is linear (check model type)
    model_name = type(model).__name__
    if model_name in ("LogisticRegression",):
        X = pd.DataFrame(scaler.transform(X), columns=feature_names)

    # Predict
    prediction = int(model.predict(X)[0])
    predicted_label = labels[prediction] if prediction < len(labels) else "Unknown"

    # Get probability/confidence
    confidence = None
    all_probs = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        confidence = float(max(proba))
        all_probs = {
            labels[i]: round(float(proba[i]), 4)
            for i in range(min(len(labels), len(proba)))
        }

    # Determine best model name from comparison
    try:
        comparison = joblib.load(Config.MODELS_DIR / Config.MODEL_COMPARISON_FILE)
        best_name = comparison["classification"]["best_model"]
    except Exception:
        best_name = model_name

    return {
        "predicted_congestion": predicted_label,
        "confidence_score": round(confidence, 4) if confidence else None,
        "model_name": best_name,
        "all_probabilities": all_probs,
    }


def predict_speed(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict average speed from input features.

    Args:
        input_data: Dictionary with feature values.

    Returns:
        Dictionary with:
            - predicted_speed: float (km/h)
            - model_name: str
    """
    model, pipeline_data = _load_regression_model()
    feature_names = pipeline_data["feature_names"]
    scaler = pipeline_data["scaler"]

    features = {}
    for f in feature_names:
        if f in input_data:
            features[f] = input_data[f]
        else:
            features[f] = 0
            logger.warning(f"Feature '{f}' missing from input, using default 0")

    X = pd.DataFrame([features])[feature_names]

    model_name = type(model).__name__
    if model_name in ("LinearRegression",):
        X = pd.DataFrame(scaler.transform(X), columns=feature_names)

    predicted = float(model.predict(X)[0])
    predicted = max(3.0, min(predicted, 120.0))  # Clamp to realistic range

    try:
        comparison = joblib.load(Config.MODELS_DIR / Config.MODEL_COMPARISON_FILE)
        best_name = comparison["regression"]["best_model"]
    except Exception:
        best_name = model_name

    return {
        "predicted_speed": round(predicted, 1),
        "model_name": best_name,
    }


def predict_full(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run both congestion classification and speed regression.

    Returns:
        Combined dictionary with all prediction results.
    """
    congestion_result = predict_congestion(input_data)
    speed_result = predict_speed(input_data)

    return {
        **congestion_result,
        **speed_result,
        "input_data": input_data,
    }
