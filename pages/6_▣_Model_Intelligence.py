"""
Model Performance Page
======================
Displays ML evaluation metrics, confusion matrices, feature importance,
and model comparison tables for both classification and regression tasks.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.config import Config
from utils.ui_components import render_header, render_system_status, render_kpi_card
from models.evaluate_model import (
    get_classification_comparison_df,
    get_regression_comparison_df,
    get_best_classification_metrics,
    get_best_regression_metrics,
    get_feature_importance_df
)

st.set_page_config(page_title="Model Intelligence | TrafficAI", page_icon="▣", layout="wide")

from utils.theme import load_css
load_css()

render_system_status()
render_header("▣ AI Model Intelligence", "Machine Learning Performance & Metrics")

@st.cache_data
def load_model_metrics():
    pass

tab1, tab2 = st.tabs(["🚦 Congestion Classification", "⏱️ Speed Regression"])

# ═══════════════════════════════════════════════════════════════════════
# TAB 1: CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════
with tab1:
    clf_comp = get_classification_comparison_df()
    best_clf = get_best_classification_metrics()
    
    if clf_comp is None or best_clf is None:
        st.warning("Classification metrics not found. Run 'python -m models.train_model' to train models.")
    else:
        st.subheader("Model Comparison")
        st.dataframe(
            clf_comp.style.highlight_max(subset=["Accuracy", "F1-Score"], color="lightgreen"),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader(f"🏆 Best Model: {best_clf['model_name']}")
            
            # KPI Metrics
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                render_kpi_card("Accuracy", f"{best_clf['accuracy']:.4f}", "🎯", "linear-gradient(135deg, #11998e, #38ef7d)")
            with kpi2:
                render_kpi_card("F1-Score", f"{best_clf['f1_score']:.4f}", "📈", "linear-gradient(135deg, #3a7bd5, #3a6073)")
            with kpi3:
                render_kpi_card("Precision", f"{best_clf['precision']:.4f}", "🔍", "linear-gradient(135deg, #8E2DE2, #4A00E0)")
            with kpi4:
                render_kpi_card("Recall", f"{best_clf['recall']:.4f}", "🔄", "linear-gradient(135deg, #FF416C, #FF4B2B)")
            
            st.caption(f"Trained on {best_clf['train_size']:,} records. Tested on {best_clf['test_size']:,} records.")
            
        with col_m2:
            st.subheader("Confusion Matrix")
            cm = best_clf.get("confusion_matrix")
            labels = Config.CONGESTION_LABELS
            if cm is not None:
                # Truncate labels if shape doesn't match (rare edge case in some splits)
                max_idx = min(len(cm), len(labels))
                
                fig_cm = px.imshow(
                    cm[:max_idx, :max_idx],
                    labels=dict(x="Predicted", y="Actual", color="Count"),
                    x=labels[:max_idx],
                    y=labels[:max_idx],
                    text_auto=True,
                    color_continuous_scale="Blues",
                    aspect="auto"
                )
                st.plotly_chart(fig_cm, use_container_width=True)

        st.subheader("Feature Importance")
        feat_imp_clf = get_feature_importance_df("classification")
        if feat_imp_clf is not None:
            fig_feat = px.bar(
                feat_imp_clf.head(10),
                x="Importance",
                y="Feature",
                orientation="h",
                title="Top 10 Most Important Features (Classification)"
            )
            fig_feat.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_feat, use_container_width=True)
        else:
            st.info("Feature importance not available for this model type.")


# ═══════════════════════════════════════════════════════════════════════
# TAB 2: REGRESSION
# ═══════════════════════════════════════════════════════════════════════
with tab2:
    reg_comp = get_regression_comparison_df()
    best_reg = get_best_regression_metrics()
    
    if reg_comp is None or best_reg is None:
        st.warning("Regression metrics not found. Run 'python -m models.train_model' to train models.")
    else:
        st.subheader("Model Comparison")
        st.dataframe(
            reg_comp.style.highlight_min(subset=["RMSE", "MAE"], color="lightgreen")
                          .highlight_max(subset=["R²"], color="lightgreen"),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        st.subheader(f"🏆 Best Model: {best_reg['model_name']}")
        
        # KPI Metrics
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            render_kpi_card("RMSE", f"{best_reg['rmse']:.4f}", "📉", "linear-gradient(135deg, #11998e, #38ef7d)")
        with kpi2:
            render_kpi_card("MAE", f"{best_reg['mae']:.4f}", "📏", "linear-gradient(135deg, #3a7bd5, #3a6073)")
        with kpi3:
            render_kpi_card("MSE", f"{best_reg['mse']:.4f}", "📐", "linear-gradient(135deg, #8E2DE2, #4A00E0)")
        with kpi4:
            render_kpi_card("R² Score", f"{best_reg['r2']:.4f}", "🎯", "linear-gradient(135deg, #FF416C, #FF4B2B)")
        
        st.caption(f"Trained on {best_reg['train_size']:,} records. Tested on {best_reg['test_size']:,} records.")
        
        st.subheader("Feature Importance")
        feat_imp_reg = get_feature_importance_df("regression")
        if feat_imp_reg is not None:
            fig_feat2 = px.bar(
                feat_imp_reg.head(10),
                x="Importance",
                y="Feature",
                orientation="h",
                title="Top 10 Most Important Features (Regression)"
            )
            fig_feat2.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_feat2, use_container_width=True)
        else:
            st.info("Feature importance not available for this model type.")
