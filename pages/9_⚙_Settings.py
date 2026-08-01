"""
TrafficAI Settings & About
==========================
Configuration, project details, and system architecture.
"""

import streamlit as st
from utils.ui_components import render_header, render_system_status

st.set_page_config(page_title="Settings | TrafficAI", page_icon="⚙", layout="wide")

from utils.theme import load_css
load_css()

render_system_status()
render_header("⚙ Settings & About", "TrafficAI Platform Configuration")

st.markdown("""
### TrafficAI: Intelligent Urban Mobility Platform

This application is an end-to-end Machine Learning pipeline that simulates a real-time smart city traffic monitoring center.

#### System Architecture
1. **Data Layer (SQLite):** Stores synthetic traffic records, locations, and prediction history.
2. **ML Engine:** Scikit-learn and XGBoost models trained for classification (Congestion Level) and regression (Speed).
3. **Routing Service:** Integrates globally with OSRM and Nominatim to provide real-world, live routing overlaid with ML heuristics.
4. **Command Centre:** A futuristic, dark-mode Streamlit interface using custom CSS glassmorphism.

#### Developer
*Developed as an advanced Data Science & ML engineering project.*
""")

if st.button("Reset Global Database (Dev Only)", type="primary"):
    st.warning("Database reset is disabled in the production UI.")
