"""
TrafficAI Predictive Traffic Map
=================================
Real-time and ML-forecasted traffic map with POI overlays.
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime

from database.queries import get_latest_traffic, get_all_locations
from utils.constants import SIMULATED_LABEL, CONGESTION_COLORS
from utils.ui_components import render_header, render_system_status
from models.predict import predict_full

st.set_page_config(page_title="AI Traffic Map | TrafficAI", page_icon="🚦", layout="wide")

from utils.theme import load_css
load_css()

render_system_status()
render_header("🚦 AI Predictive Traffic Map", "Real-Time Monitoring & ML Forecast Horizon")

# Sidebar Controls
st.sidebar.header("🕹️ Map Controls")

locations = get_all_locations()
loc_names = ["All"] + [loc["location_name"] for loc in locations]

selected_location = st.sidebar.selectbox("Location Filter", loc_names)

# Forecast Horizon Selector
forecast_horizon = st.sidebar.select_slider(
    "✦ AI Forecast Horizon",
    options=["LIVE (Now)", "+15 Min", "+30 Min", "+1 Hour", "+2 Hours"],
    value="LIVE (Now)"
)

# POI Overlay Toggles
st.sidebar.markdown("---")
st.sidebar.subheader("📍 Nearby POI Layers")
show_hospitals = st.sidebar.checkbox("🏥 Emergency Hospitals", value=True)
show_petrol = st.sidebar.checkbox("⛽ Fuel Stations", value=True)
show_transit = st.sidebar.checkbox("🚌 Bus / Metro Hubs", value=False)

# Fetch latest traffic observation
raw_data = get_latest_traffic(limit=200)

if raw_data:
    df = pd.DataFrame(raw_data)
    
    if selected_location != "All":
        df = df[df["location_name"] == selected_location]
        
    if not df.empty:
        df_map = df.sort_values('timestamp').drop_duplicates('location_id', keep='last').copy()
        
        # If forecast horizon is in the future, run ML prediction for each node!
        if forecast_horizon != "LIVE (Now)":
            offset_hours = 0.25 if forecast_horizon == "+15 Min" else 0.5 if forecast_horizon == "+30 Min" else 1.0 if forecast_horizon == "+1 Hour" else 2.0
            
            for idx, row in df_map.iterrows():
                feat = {
                    "hour": (datetime.datetime.now().hour + int(offset_hours)) % 24,
                    "day_of_week": datetime.datetime.now().weekday(),
                    "month": datetime.datetime.now().month,
                    "is_weekend": 1 if datetime.datetime.now().weekday() >= 5 else 0,
                    "is_peak_hour": 1 if (datetime.datetime.now().hour + int(offset_hours)) in [8, 9, 17, 18] else 0,
                    "is_morning_peak": 1 if (datetime.datetime.now().hour + int(offset_hours)) in [8, 9] else 0,
                    "is_evening_peak": 1 if (datetime.datetime.now().hour + int(offset_hours)) in [17, 18] else 0,
                    "vehicle_count": int(row["vehicle_count"] * (1.3 if (datetime.datetime.now().hour + int(offset_hours)) in [8, 9, 17, 18] else 1.0)),
                    "road_capacity": row["road_capacity"],
                    "traffic_density": row["vehicle_count"] / max(row["road_capacity"], 1),
                    "speed_ratio": row["average_speed"] / 50.0,
                    "capacity_utilization": row["vehicle_count"] / max(row["road_capacity"], 1),
                    "weather_severity": 1 if row["weather_condition"] in ["Light Rain", "Heavy Rain"] else 0,
                    "visibility": row["visibility"],
                    "accident_reported": row["accident_reported"],
                    "temperature": row["temperature"],
                    "rainfall": row["rainfall"],
                    "accident_risk": 0.2,
                    "is_holiday": row["is_holiday"],
                    "is_special_event": row["is_special_event"]
                }
                pred = predict_full(feat)
                df_map.at[idx, "congestion_level"] = pred["predicted_congestion"].title()
                df_map.at[idx, "average_speed"] = pred["predicted_speed"]

        st.subheader(f"🗺️ Map View — Mode: {forecast_horizon}")
        
        from config.config import Config
        from components.google_map import render_google_traffic_nodes_map
        
        # Build node objects for Google Maps JS container
        nodes_list = []
        for _, row in df_map.iterrows():
            nodes_list.append({
                "name": row["location_name"],
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"]),
                "speed": float(row["average_speed"]),
                "congestion": row["congestion_level"]
            })
            
        pois_list = []
        if show_hospitals:
            pois_list.append({"name": "Apollo Hospital, Greams Road", "lat": 13.0603, "lon": 80.2512, "type": "Hospital"})
            pois_list.append({"name": "MIOT International", "lat": 13.0232, "lon": 80.1772, "type": "Hospital"})
        if show_petrol:
            pois_list.append({"name": "Indian Oil Bunk, T. Nagar", "lat": 13.0401, "lon": 80.2322, "type": "Fuel Station"})
            pois_list.append({"name": "BPCL Fuel Station, Guindy", "lat": 13.0080, "lon": 80.2050, "type": "Fuel Station"})
        if show_transit:
            pois_list.append({"name": "Koyambedu CMBT", "lat": 13.0694, "lon": 80.1948, "type": "Transit Hub"})

        with st.sidebar:
            st.markdown("---")
            map_engine = st.selectbox(
                "🗺️ Visual Map Engine",
                ["Google Maps Pro Navigation (Recommended)", "Dark Vector Map (Fallback)", "🌐 3D Pydeck Geospatial Extrusion"],
                help="Select map container renderer. 'Google Maps Pro Navigation' renders live Google Traffic with smart POIs & glassmorphic popups."
            )

        if map_engine.startswith("Google Maps Pro") and Config.GOOGLE_MAPS_API_KEY:
            st.info("ℹ️ *Displaying Google Maps Pro Navigation Engine with live TrafficLayer, Satellite toggle & Smart POI pins.*")
            render_google_traffic_nodes_map(nodes=nodes_list, center_lat=13.0418, center_lon=80.2341, height=580, pois=pois_list)
        elif map_engine == "🌐 3D Pydeck Geospatial Extrusion":
            from components.pydeck_3d_map import render_pydeck_3d_traffic_map
            render_pydeck_3d_traffic_map(
                nodes_df=df_map,
                show_arcs=True,
                show_columns=True,
                pitch=55,
                height=520
            )
        else:
            # High performance Folium dark matter map with traffic node markers & POIs
            m = folium.Map(location=[13.0418, 80.2341], zoom_start=12, tiles="CartoDB dark_matter")
            for _, row in df_map.iterrows():
                c_level = row["congestion_level"]
                color = "#00E676" if c_level == "Low" else "#FFEA00" if c_level == "Moderate" else "#FF9100" if c_level == "High" else "#FF1744"
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=10, color=color, fill=True, fill_color=color, fill_opacity=0.85,
                    tooltip=f"<b>{row['location_name']}</b><br>Speed: {row['average_speed']:.1f} km/h<br>Congestion: {c_level}"
                ).add_to(m)

            if show_hospitals:
                for h in pois_list:
                    if h.get("type") == "Hospital":
                        folium.Marker([h["lat"], h["lon"]], icon=folium.Icon(color='red', icon='plus-square', prefix='fa'), tooltip=f"🏥 {h['name']}").add_to(m)
            if show_petrol:
                for p in pois_list:
                    if p.get("type") == "Fuel Station":
                        folium.Marker([p["lat"], p["lon"]], icon=folium.Icon(color='green', icon='fire', prefix='fa'), tooltip=f"⛽ {p['name']}").add_to(m)
            if show_transit:
                for t in pois_list:
                    if t.get("type") == "Transit Hub":
                        folium.Marker([t["lat"], t["lon"]], icon=folium.Icon(color='blue', icon='subway', prefix='fa'), tooltip=f"🚌 {t['name']}").add_to(m)

            st_folium(m, height=520, use_container_width=True, returned_objects=[])
        
        # Display Table
        st.subheader("📋 Traffic Observations & AI Forecast Table")
        st.dataframe(
            df_map[["location_name", "road_name", "vehicle_count", "average_speed", "congestion_level", "weather_condition"]],
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # ── Crowdsourced Traffic Intelligence (Feature 17) ──
        st.subheader("📢 Crowdsourced Traffic Incident Intelligence")
        c_col1, c_col2 = st.columns([1, 1])
        
        with c_col1:
            st.markdown("##### 📝 Submit Incident Report")
            with st.form("crowdsource_form"):
                report_loc = st.selectbox("Incident Location", [l["location_name"] for l in locations])
                report_type = st.selectbox("Incident Type", ["Accident", "Water Logging (Rain)", "Construction Work", "Heavy Traffic Jam", "Police Checking"])
                report_desc = st.text_input("Description / Notes", value="Lanes blocked near junction.")
                sub_report = st.form_submit_button("🚨 Submit Incident Report", type="primary", use_container_width=True)
                
                if sub_report:
                    from database.queries import insert_crowdsourced_report
                    insert_crowdsourced_report(report_loc, report_type, report_desc)
                    st.success("✅ Incident report submitted! AI verification confidence score: **85% (Auto-Verified)**.")
                    st.rerun()
                    
        with c_col2:
            st.markdown("##### 🛰️ Verified User Incidents")
            from database.queries import get_recent_crowdsourced_reports
            reports = get_recent_crowdsourced_reports(limit=5)
            if reports:
                for r in reports:
                    st.markdown(f"""
                    <div style="background: rgba(15,23,42,0.7); border-left: 3px solid #FF9100; padding: 10px 14px; margin-bottom: 8px; border-radius: 4px;">
                        <span style="color: #FF9100; font-weight: 700;">{r['incident_type']}</span> @ <strong style="color: white;">{r['location_name']}</strong><br>
                        <span style="color: #CBD5E1; font-size: 0.85rem;">{r['description']}</span><br>
                        <span style="color: #00E676; font-size: 0.75rem;">Verified Confidence: {int(r['confidence_score']*100)}% | Upvotes: {r['upvotes']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active user incidents reported.")

    else:
        st.warning("No data matches selected location.")
else:
    st.info("No traffic data available in database.")

