"""
TrafficAI Digital Twin & Scenario Simulator
============================================
Simulates "What-If" urban scenarios (Accidents, Severe Weather, Road Closures, Volume Spikes)
and detects traffic anomalies using rolling statistics and ML inference.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from database.queries import get_all_locations, get_latest_traffic
from models.predict import predict_full
from utils.ui_components import render_header, render_system_status, render_kpi_card

st.set_page_config(page_title="Digital Twin Simulator | TrafficAI", page_icon="🔮", layout="wide")

from utils.theme import load_css
load_css()

render_system_status()
render_header("🔮 Smart City Digital Twin & Scenario Simulator", "What-If Traffic Stress Testing & Eco Impact Modeling")

st.markdown("### 🎛️ Scenario Simulation Controls")

col_sim1, col_sim2, col_sim3 = st.columns(3)

with col_sim1:
    st.subheader("1. Traffic Volume & Demand")
    volume_multiplier = st.slider("Vehicle Volume Change (%)", -50, 100, 20, help="Simulate sudden traffic spikes or holiday drops")
    special_event = st.checkbox("🎉 Major Public Event (IPL Match / Concert)")

with col_sim2:
    st.subheader("2. Weather & Environment")
    sim_weather = st.selectbox("Weather Scenario", ["Clear", "Light Rain", "Heavy Rain / Storm", "Low Visibility / Fog"])
    sim_temp = st.slider("Temperature (°C)", 15.0, 45.0, 32.0)

with col_sim3:
    st.subheader("3. Incidents & Closures")
    sim_accident = st.checkbox("⚠ Accident Incident Reported")
    road_closure = st.checkbox("🚧 Major Corridor Road Closure")

# Run Simulation Engine
if st.button("🚀 RUN DIGITAL TWIN SIMULATION", type="primary", use_container_width=True):
    st.markdown("---")
    st.subheader("📊 Digital Twin Scenario Analysis")
    
    locations = get_all_locations()
    sim_results = []
    
    for loc in locations:
        base_cap = loc["road_capacity"]
        base_vol = int(base_cap * 0.6 * (1 + volume_multiplier / 100.0))
        
        weather_sev = 1 if sim_weather in ["Light Rain", "Heavy Rain / Storm"] else 0
        rain_val = 25.0 if sim_weather == "Heavy Rain / Storm" else 5.0 if sim_weather == "Light Rain" else 0.0
        
        feat = {
            "hour": 18, # Peak evening rush
            "day_of_week": 4,
            "month": 7,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "is_morning_peak": 0,
            "is_evening_peak": 1,
            "vehicle_count": base_vol,
            "road_capacity": base_cap,
            "traffic_density": base_vol / max(base_cap, 1),
            "speed_ratio": 0.6 if sim_accident else 0.8,
            "capacity_utilization": base_vol / max(base_cap, 1),
            "weather_severity": weather_sev,
            "visibility": 5.0 if sim_weather == "Heavy Rain / Storm" else 10.0,
            "accident_reported": 1 if sim_accident else 0,
            "temperature": sim_temp,
            "rainfall": rain_val,
            "accident_risk": 0.8 if sim_accident else 0.2,
            "is_holiday": 0,
            "is_special_event": 1 if special_event else 0
        }
        
        pred = predict_full(feat)
        sim_speed = pred["predicted_speed"]
        if road_closure and loc["location_id"] in [1, 2]: # Block first couple nodes
            sim_speed = 5.0
            pred["predicted_congestion"] = "Severe"
            
        sim_results.append({
            "Location": loc["location_name"],
            "Road": loc["road_name"],
            "Base Speed": loc["speed_limit"],
            "Simulated Speed": round(sim_speed, 1),
            "Congestion": pred["predicted_congestion"],
            "Delay Overhead": f"+{int((1 - sim_speed / loc['speed_limit']) * 30)} min" if sim_speed < loc['speed_limit'] else "0 min"
        })
        
    df_sim = pd.DataFrame(sim_results)
    
    # Summary Metrics
    avg_sim_speed = df_sim["Simulated Speed"].mean()
    severe_nodes = len(df_sim[df_sim["Congestion"] == "Severe"])
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card("Simulated Avg Speed", f"{avg_sim_speed:.1f} km/h", "⏱️", "Network Average")
    with m2:
        render_kpi_card("Severe Nodes", f"{severe_nodes}", "🔥", "Critical Congestion Points", border_color="rgba(255, 23, 68, 0.5)")
    with m3:
        # Eco Metrics
        est_fuel = (100.0 / max(avg_sim_speed, 5.0)) * 2.5 # Liters per 100km approx
        render_kpi_card("Est. Fuel Idle Burn", f"{est_fuel:.1f} L/100km", "⛽", "Network Fuel Efficiency")
    with m4:
        est_co2 = est_fuel * 2.31 # kg CO2 per liter
        render_kpi_card("Est. Carbon Footprint", f"{est_co2:.1f} kg CO₂", "🌱", "CO₂ Impact Estimate")

    # 3D Animated WebGL City Digital Twin Visualization
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🌐 Interactive 3D WebGL Digital Twin Simulation")
    st.caption("Live 60 FPS WebGL city simulation rendering simulated vehicles, speed factors, and weather conditions in real-time.")
    
    from components.three_js_city import render_three_js_city
    sim_veh_density = int(30 * (1 + volume_multiplier / 100.0))
    sim_speed_fact = max(0.2, float(avg_sim_speed / 40.0))
    
    render_three_js_city(
        vehicle_density=sim_veh_density,
        speed_factor=sim_speed_fact,
        weather=sim_weather,
        night_mode=True,
        show_traffic_lights=True,
        height=500
    )

    # Comparison Chart
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Simulated Speed by Corridor (km/h)")
        fig_sim = px.bar(
            df_sim, x="Simulated Speed", y="Location", orientation="h",
            color="Congestion",
            color_discrete_map={"Low": "#00E676", "Moderate": "#FFEA00", "High": "#FF9100", "Severe": "#FF1744"}
        )
        st.plotly_chart(fig_sim, use_container_width=True)
        
    with col_chart2:
        st.subheader("⚠ Traffic Anomaly Detector")
        anomalies = df_sim[df_sim["Simulated Speed"] < 20.0]
        if not anomalies.empty:
            for _, a_row in anomalies.iterrows():
                st.error(f"🚨 **ANOMALY DETECTED at {a_row['Location']} ({a_row['Road']})**:\n- Simulated Speed: **{a_row['Simulated Speed']} km/h** (Speed Limit: {a_row['Base Speed']} km/h)\n- Deviation: **-{int((1 - a_row['Simulated Speed']/a_row['Base Speed'])*100)}%** from baseline\n- Diagnostic: High vehicle density combined with scenario constraints.")
        else:
            st.success("✅ No critical traffic anomalies detected under this scenario.")

    # Table
    st.subheader("📋 Full Scenario Simulation Results Table")
    st.dataframe(df_sim, use_container_width=True, hide_index=True)
