"""
Model Training Module
=====================
Trains and compares multiple ML models for both classification (congestion level)
and regression (average speed). Saves the best model + metrics using Joblib.

Classification models: Logistic Regression, Decision Tree, Random Forest,
                       Gradient Boosting, XGBoost (if available)
Regression models:     Linear Regression, Decision Tree, Random Forest,
                       Gradient Boosting, XGBoost (if available)

Usage:
    python -m models.train_model
"""

import sys
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor,
)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, mean_absolute_error, mean_squared_error, r2_score,
)

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from preprocessing.preprocessing_pipeline import (
    build_full_dataset,
    prepare_classification_data,
    prepare_regression_data,
)
from utils.logger import get_logger

logger = get_logger(__name__)
warnings.filterwarnings("ignore")

# Try importing XGBoost (optional dependency)
try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGBOOST = True
    logger.info("XGBoost available — will include in model comparison")
except ImportError:
    HAS_XGBOOST = False
    logger.info("XGBoost not available — skipping XGBoost models")


# ═══════════════════════════════════════════════════════════════════════
# MODEL DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════

def _get_classification_models() -> dict:
    """Return dictionary of classification models to compare."""
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=42
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=10, random_state=42,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=12, random_state=42, n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42,
        ),
    }
    if HAS_XGBOOST:
        models["XGBoost"] = XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, use_label_encoder=False,
            eval_metric="mlogloss", verbosity=0,
        )
    return models


def _get_regression_models() -> dict:
    """Return dictionary of regression models to compare."""
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(
            max_depth=10, random_state=42,
        ),
        "Random Forest": RandomForestRegressor(
            n_estimators=100, max_depth=12, random_state=42, n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42,
        ),
    }
    if HAS_XGBOOST:
        models["XGBoost"] = XGBRegressor(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, verbosity=0,
        )
    return models


# ═══════════════════════════════════════════════════════════════════════
# TRAINING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def train_classification_models(df: pd.DataFrame) -> dict:
    """
    Train and evaluate all classification models.

    Returns:
        Dictionary with model results, best model, and metrics.
    """
    logger.info("=" * 60)
    logger.info("TRAINING CLASSIFICATION MODELS")
    logger.info("=" * 60)

    X_train, X_val, X_test, y_train, y_val, y_test, feature_names = \
        prepare_classification_data(df)

    # Scale features for models that benefit from it
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train), columns=feature_names, index=X_train.index
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test), columns=feature_names, index=X_test.index
    )

    models = _get_classification_models()
    results = []
    best_f1 = -1
    best_model = None
    best_model_name = None

    labels = Config.CONGESTION_LABELS

    for name, model in models.items():
        logger.info(f"\n  Training: {name}")
        start_time = time.time()

        # Use scaled data for linear models
        if name in ("Logistic Regression",):
            X_tr, X_te = X_train_scaled, X_test_scaled
        else:
            X_tr, X_te = X_train, X_test

        try:
            model.fit(X_tr, y_train)
            train_time = time.time() - start_time

            y_pred = model.predict(X_te)

            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
            rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
            cm = confusion_matrix(y_test, y_pred)

            # Feature importance (if available)
            feat_imp = None
            if hasattr(model, "feature_importances_"):
                feat_imp = dict(zip(feature_names, model.feature_importances_))
            elif hasattr(model, "coef_"):
                # Use absolute mean of coefficients across classes
                feat_imp = dict(zip(
                    feature_names,
                    np.abs(model.coef_).mean(axis=0) if model.coef_.ndim > 1
                    else np.abs(model.coef_)
                ))

            result = {
                "model_name": name,
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "confusion_matrix": cm,
                "training_time": round(train_time, 2),
                "feature_importance": feat_imp,
                "train_size": len(X_train),
                "test_size": len(X_test),
            }
            results.append(result)

            logger.info(
                f"    Accuracy={acc:.4f}  F1={f1:.4f}  "
                f"Time={train_time:.2f}s"
            )

            if f1 > best_f1:
                best_f1 = f1
                best_model = model
                best_model_name = name

        except Exception as e:
            logger.error(f"    FAILED: {e}")
            continue

    logger.info(f"\n  BEST CLASSIFIER: {best_model_name} (F1={best_f1:.4f})")

    return {
        "results": results,
        "best_model": best_model,
        "best_model_name": best_model_name,
        "scaler": scaler,
        "feature_names": feature_names,
        "labels": labels,
    }


def train_regression_models(df: pd.DataFrame) -> dict:
    """
    Train and evaluate all regression models.

    Returns:
        Dictionary with model results, best model, and metrics.
    """
    logger.info("=" * 60)
    logger.info("TRAINING REGRESSION MODELS")
    logger.info("=" * 60)

    X_train, X_val, X_test, y_train, y_val, y_test, feature_names = \
        prepare_regression_data(df)

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train), columns=feature_names, index=X_train.index
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test), columns=feature_names, index=X_test.index
    )

    models = _get_regression_models()
    results = []
    best_rmse = float("inf")
    best_model = None
    best_model_name = None

    for name, model in models.items():
        logger.info(f"\n  Training: {name}")
        start_time = time.time()

        if name in ("Linear Regression",):
            X_tr, X_te = X_train_scaled, X_test_scaled
        else:
            X_tr, X_te = X_train, X_test

        try:
            model.fit(X_tr, y_train)
            train_time = time.time() - start_time

            y_pred = model.predict(X_te)

            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)

            feat_imp = None
            if hasattr(model, "feature_importances_"):
                feat_imp = dict(zip(feature_names, model.feature_importances_))
            elif hasattr(model, "coef_"):
                feat_imp = dict(zip(feature_names, np.abs(model.coef_)))

            result = {
                "model_name": name,
                "mae": round(mae, 4),
                "mse": round(mse, 4),
                "rmse": round(rmse, 4),
                "r2": round(r2, 4),
                "training_time": round(train_time, 2),
                "feature_importance": feat_imp,
                "train_size": len(X_train),
                "test_size": len(X_test),
            }
            results.append(result)

            logger.info(
                f"    RMSE={rmse:.4f}  R²={r2:.4f}  "
                f"MAE={mae:.4f}  Time={train_time:.2f}s"
            )

            if rmse < best_rmse:
                best_rmse = rmse
                best_model = model
                best_model_name = name

        except Exception as e:
            logger.error(f"    FAILED: {e}")
            continue

    logger.info(f"\n  BEST REGRESSOR: {best_model_name} (RMSE={best_rmse:.4f})")

    return {
        "results": results,
        "best_model": best_model,
        "best_model_name": best_model_name,
        "scaler": scaler,
        "feature_names": feature_names,
    }


# ═══════════════════════════════════════════════════════════════════════
# SAVE MODELS
# ═══════════════════════════════════════════════════════════════════════

def save_models(clf_results: dict, reg_results: dict) -> None:
    """Save best models, scalers, and metrics to disk."""
    Config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Save classification model + scaler + metrics
    joblib.dump(
        clf_results["best_model"],
        Config.MODELS_DIR / Config.CLASSIFICATION_MODEL_FILE,
    )
    joblib.dump(
        {
            "scaler": clf_results["scaler"],
            "feature_names": clf_results["feature_names"],
            "labels": clf_results["labels"],
        },
        Config.MODELS_DIR / Config.CLASSIFICATION_PIPELINE_FILE,
    )
    joblib.dump(
        clf_results["results"],
        Config.MODELS_DIR / Config.CLASSIFICATION_METRICS_FILE,
    )

    # Save regression model + scaler + metrics
    joblib.dump(
        reg_results["best_model"],
        Config.MODELS_DIR / Config.REGRESSION_MODEL_FILE,
    )
    joblib.dump(
        {
            "scaler": reg_results["scaler"],
            "feature_names": reg_results["feature_names"],
        },
        Config.MODELS_DIR / Config.REGRESSION_PIPELINE_FILE,
    )
    joblib.dump(
        reg_results["results"],
        Config.MODELS_DIR / Config.REGRESSION_METRICS_FILE,
    )

    # Save model comparison summary
    comparison = {
        "classification": {
            "best_model": clf_results["best_model_name"],
            "results": clf_results["results"],
        },
        "regression": {
            "best_model": reg_results["best_model_name"],
            "results": reg_results["results"],
        },
    }
    joblib.dump(comparison, Config.MODELS_DIR / Config.MODEL_COMPARISON_FILE)

    logger.info(f"All models saved to: {Config.MODELS_DIR}")


# ═══════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

def train_all_models() -> tuple:
    """
    Full training pipeline: load data → clean → feature engineer →
    train classification + regression → save best models.

    Returns:
        (classification_results, regression_results)
    """
    Config.ensure_directories()

    # Build dataset
    df = build_full_dataset()

    # Train classification models
    clf_results = train_classification_models(df)

    # Train regression models
    reg_results = train_regression_models(df)

    # Save everything
    save_models(clf_results, reg_results)

    return clf_results, reg_results


if __name__ == "__main__":
    train_all_models()
