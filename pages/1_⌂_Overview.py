"""
TrafficAI Overview (Dashboard)
==============================
Main operational dashboard with premium glassmorphic KPIs, animated
alerts, traffic hotspots, and futuristic command center aesthetic.
"""

import streamlit as st
import pandas as pd

from services.prediction_service import get_traffic_stats
from database.queries import execute_query
from utils.ui_components import render_header, render_system_status, render_kpi_card, render_alert

st.set_page_config(page_title="Overview | TrafficAI", page_icon="⌂", layout="wide")

# Apply global theme
from utils.theme import load_css
load_css()

render_system_status()
render_header("AI Traffic Command Centre", "Operational Overview · Real-Time Network Intelligence")

# ── 1. Alerts Section ────────────────────────────────────────────────
st.markdown("""<div style="font-family: 'Space Grotesk', sans-serif; color: #FFFFFF; font-size: 1.15rem; font-weight: 600; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; animation: fadeSlideUp 0.4s ease-out;">
<span style="color: #00D9FF;">⚡</span> Traffic Intelligence Alerts
</div>""", unsafe_allow_html=True)

# Fetch recent alerts
stats = get_traffic_stats()
if stats.get('accident_count', 0) > 0:
    render_alert(f"Multiple accidents ({stats['accident_count']}) detected across the network.", "CRITICAL")
if stats.get('severe_count', 0) > 0:
    render_alert(f"Severe congestion predicted at {stats['severe_count']} monitoring nodes.", "WARNING")
if stats.get('avg_speed', 0) < 30:
    render_alert(f"Average network speed decreased to {stats['avg_speed']:.1f} km/h.", "CAUTION")
if stats.get('avg_speed', 0) >= 30:
    render_alert("Traffic flow is relatively stable across major corridors.", "NORMAL")

st.markdown("<br>", unsafe_allow_html=True)

# ── 2. KPI Cards ─────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Average Speed", f"{stats.get('avg_speed', 0):.1f} km/h", "⏱️", "Live network average")
with col2:
    render_kpi_card("Active Vehicles", f"{stats.get('total_records', 0):,}", "🚗", "Total tracked data points")
with col3:
    render_kpi_card("Congested Roads", f"{stats.get('severe_count', 0):,}", "🔥", "Nodes in severe state", border_color="rgba(255, 77, 103, 0.3)")
with col4:
    overall_status = "High Traffic" if stats.get('avg_speed', 50) < 30 else "Moderate"
    render_kpi_card("AI Prediction", overall_status, "✦", "Next 30 min forecast", border_color="rgba(0, 217, 255, 0.3)")

st.markdown("---")

# ── 3. Traffic Hotspots ──────────────────────────────────────────────
st.markdown("""<div style="font-family: 'Space Grotesk', sans-serif; color: #FFFFFF; font-size: 1.15rem; font-weight: 600; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; animation: fadeSlideUp 0.4s ease-out;">
<span style="color: #FF4D67;">🔥</span> Traffic Hotspots
</div>
<p style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.85rem; margin-bottom: 16px;">
Top locations currently experiencing the lowest average speeds.
</p>""", unsafe_allow_html=True)

# Query database for worst locations
query = """
    SELECT l.location_name, AVG(td.average_speed) as avg_speed, SUM(td.accident_reported) as accidents
    FROM traffic_data td
    JOIN locations l ON td.location_id = l.location_id
    GROUP BY td.location_id
    ORDER BY avg_speed ASC
    LIMIT 3
"""
try:
    hotspots_df = execute_query(query)
    if not hotspots_df.empty:
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        for idx, row in hotspots_df.iterrows():
            with cols[idx]:
                speed = row['avg_speed']
                level = "Severe" if speed < 20 else "High" if speed < 40 else "Moderate"
                color = "#FF4D67" if level == "Severe" else "#FFC247" if level == "High" else "#FFE066"

                html = f"""<div style="background: rgba(10, 15, 30, 0.7); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.06); border-top: 3px solid {color}; padding: 22px; border-radius: 12px; transition: all 0.4s ease; animation: fadeSlideUp 0.5s ease-out {0.1 * (idx + 1)}s backwards; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);">
<h3 style="margin: 0; color: white; font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 600;">{row['location_name']}</h3>
<div style="display: flex; align-items: center; gap: 6px; margin: 8px 0;">
<div style="width: 8px; height: 8px; border-radius: 50%; background: {color}; animation: breathe 2s ease-in-out infinite;"></div>
<span style="color: {color}; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.85rem;">{level}</span>
</div>
<p style="color: #94A3B8; font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; margin: 0;">{speed:.1f} <span style="font-size: 0.8rem; font-weight: 400;">km/h</span></p>
</div>"""
                st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("No hotspot data currently available.")
except Exception as e:
    st.error(f"Could not load hotspots: {e}")
