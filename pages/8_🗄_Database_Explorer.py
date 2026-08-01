"""
Database Explorer Page
======================
Safe, read-only interface to view raw data in the SQLite database.
"""

import streamlit as st
import pandas as pd

from database.db_connection import get_connection, get_table_counts

st.set_page_config(page_title="Database Explorer", page_icon="🗄️", layout="wide")

from utils.theme import load_css
from utils.ui_components import render_header, render_system_status
load_css()

render_system_status()
render_header("🗄️ Database Explorer", "Read-only view of the underlying SQLite database tables")

# Get counts to show in tabs
counts = get_table_counts()

tabs = st.tabs([
    f"Locations ({counts.get('locations', 0)})",
    f"Traffic Data ({counts.get('traffic_data', 0)})",
    f"Predictions ({counts.get('predictions', 0)})",
    f"Routes ({counts.get('routes', 0)})",
    f"Route History ({counts.get('route_history', 0)})"
])

def load_table_data(table_name: str, limit: int = 1000):
    try:
        with get_connection() as conn:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            df = pd.read_sql_query(query, conn)
            return df
    except Exception as e:
        st.error(f"Error loading {table_name}: {e}")
        return pd.DataFrame()

# ── 1. Locations ──────────────────────────────────────────────────────
with tabs[0]:
    df_loc = load_table_data("locations")
    if not df_loc.empty:
        st.dataframe(df_loc, use_container_width=True, hide_index=True)
    else:
        st.info("No locations found.")

# ── 2. Traffic Data ───────────────────────────────────────────────────
with tabs[1]:
    col1, col2 = st.columns([1, 3])
    with col1:
        limit_traf = st.selectbox("Row Limit (Traffic)", [100, 1000, 5000, 10000])
    df_traf = load_table_data("traffic_data", limit_traf)
    if not df_traf.empty:
        st.dataframe(df_traf, use_container_width=True, hide_index=True)
    else:
        st.info("No traffic data found.")

# ── 3. Predictions ────────────────────────────────────────────────────
with tabs[2]:
    df_pred = load_table_data("predictions")
    if not df_pred.empty:
        st.dataframe(df_pred, use_container_width=True, hide_index=True)
    else:
        st.info("No predictions found.")

# ── 4. Routes ─────────────────────────────────────────────────────────
with tabs[3]:
    df_routes = load_table_data("routes")
    if not df_routes.empty:
        st.dataframe(df_routes, use_container_width=True, hide_index=True)
    else:
        st.info("No routes found.")

# ── 5. Route History ──────────────────────────────────────────────────
with tabs[4]:
    df_hist = load_table_data("route_history")
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.info("No route history found.")
