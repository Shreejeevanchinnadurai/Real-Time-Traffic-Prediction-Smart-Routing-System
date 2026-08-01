"""
TrafficAI 3D Traffic Animation Studio
=====================================
Interactive 3D visualization studio featuring WebGL Three.js City Digital Twin,
Pydeck 3D Geospatial Extrusions & Animated Arc Flows, and Plotly 3D Spatiotemporal Surfaces.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from database.queries import get_latest_traffic, get_all_locations
from utils.ui_components import render_header, render_system_status, render_kpi_card
from components.three_js_city import render_three_js_city
from components.pydeck_3d_map import render_pydeck_3d_traffic_map

st.set_page_config(page_title="3D Traffic Studio | TrafficAI", page_icon="🌐", layout="wide")

from utils.theme import load_css
load_css()

render_system_status()
render_header("🌐 3D Traffic Animation Studio", "Real-Time WebGL Digital Twin & 3D Spatial Intelligence")

# ── Sidebar Controls ─────────────────────────────────────────────────
st.sidebar.header("🕹️ 3D Studio Controls")

engine = st.sidebar.radio(
    "Select 3D Animation Engine",
    [
        "🎮 WebGL 3D City Digital Twin (Three.js)",
        "🗺️ 3D Geospatial Extrusions & Arc Flow (Deck.gl/Pydeck)",
        "🌊 3D Spatiotemporal Congestion Surface (Plotly 3D)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Simulation Parameters")

vehicle_density = st.sidebar.slider("🚗 Vehicle Traffic Density", 10, 80, 40, help="Control active simulated 3D vehicles")
speed_mult = st.sidebar.slider("⚡ Traffic Velocity Factor", 0.2, 3.0, 1.0, 0.1)
weather_cond = st.sidebar.selectbox("🌧️ Weather Environment", ["Clear", "Light Rain", "Heavy Storm", "Low Visibility / Fog"])
night_mode = st.sidebar.checkbox("🌙 Cyberpunk Night Lighting", value=True)

# Fetch current live node data for geospatial views
raw_data = get_latest_traffic(limit=200)
df_traffic = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()

# ── MODE 1: Three.js 3D WebGL City ──────────────────────────────────
if engine.startswith("🎮 WebGL"):
    st.markdown("### 🌆 Interactive 3D City Digital Twin")
    st.caption("60 FPS WebGL simulation engine with procedural 3D buildings, moving vehicles, traffic signals, and weather particles.")

    # Top KPI summary cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Active 3D Vehicles", f"{vehicle_density} Units", "+15% vs normal", "#00E5FF")
    with k2:
        render_kpi_card("Simulation Velocity", f"{speed_mult:.1f}x Speed", "Real-time sync", "#00E676")
    with k3:
        render_kpi_card("Weather State", weather_cond, "Particle engine active", "#FFB300")
    with k4:
        render_kpi_card("Rendering Engine", "Three.js WebGL", "Hardware accelerated", "#7C4DFF")

    st.markdown("---")

    render_three_js_city(
        vehicle_density=vehicle_density,
        speed_factor=speed_mult,
        weather=weather_cond,
        night_mode=night_mode,
        show_traffic_lights=True,
        height=620
    )

    st.info("💡 **Tips for Interactive 3D Orbit Camera:** Left-Click + Drag to Rotate | Scroll to Zoom | Right-Click + Drag to Pan | Use lower-right buttons for camera presets.")

# ── MODE 2: Deck.gl / Pydeck 3D Geospatial Map ─────────────────────
elif engine.startswith("🗺️ 3D Geospatial"):
    st.markdown("### 🗺️ 3D Extruded Traffic Density & Flow Arcs")
    st.caption("Geospatial 3D extrusion where tower height represents traffic volume, colors show congestion level, and arcs trace active corridors.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 Pydeck 3D Camera & Layers")
    cam_pitch = st.sidebar.slider("Camera Tilt (Pitch)", 0, 70, 55)
    cam_bearing = st.sidebar.slider("Camera Rotation (Bearing)", -180, 180, -20)
    show_arcs = st.sidebar.checkbox("Show 3D Flow Arcs", value=True)
    show_cols = st.sidebar.checkbox("Show 3D Density Towers", value=True)
    show_hex = st.sidebar.checkbox("Show 3D Hexagon Aggregation", value=False)

    if not df_traffic.empty:
        df_latest = df_traffic.sort_values('timestamp').drop_duplicates('location_id', keep='last').copy()
        
        # Scale vehicle count by density slider
        df_latest["vehicle_count"] = (df_latest["vehicle_count"] * (vehicle_density / 40.0)).astype(int)
        
        render_pydeck_3d_traffic_map(
            nodes_df=df_latest,
            show_arcs=show_arcs,
            show_columns=show_cols,
            show_hexagon=show_hex,
            pitch=cam_pitch,
            bearing=cam_bearing,
            height=600
        )
    else:
        st.error("No traffic telemetry data available for 3D map rendering.")

# ── MODE 3: Plotly 3D Spatiotemporal Surface ────────────────────────
else:
    st.markdown("### 🌊 3D Spatiotemporal Traffic Velocity Surface")
    st.caption("3D surface plot depicting urban grid coordinates (Lat/Lon) against traffic velocity & congestion waves over time.")

    # Create synthetic or interpolated 3D grid surface
    x_coords = np.linspace(80.15, 80.28, 35)  # Longitude
    y_coords = np.linspace(13.00, 13.12, 35)  # Latitude
    X, Y = np.meshgrid(x_coords, y_coords)

    # Wave function simulating peak congestion ripple
    Z = 45.0 + 20.0 * np.sin(X * 80 + Y * 50) * np.cos(speed_mult * 2.0) - (vehicle_density / 2.0)
    Z = np.clip(Z, 5, 80)

    fig = go.Figure(data=[
        go.Surface(
            z=Z, x=X, y=Y,
            colorscale="Electric",
            colorbar=dict(title="Speed (km/h)", len=0.75),
            contours=dict(
                z=dict(show=True, usecolormap=True, highlightcolor="cyan", project_z=True)
            )
        )
    ])

    fig.update_layout(
        title="3D Traffic Velocity Landscape across Chennai Urban Grid",
        autosize=True,
        height=650,
        margin=dict(l=20, r=20, b=20, t=50),
        template="plotly_dark",
        paper_bgcolor="rgba(15,23,42,0.6)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        scene=dict(
            xaxis=dict(title="Longitude", backgroundcolor="#090D1C", gridcolor="rgba(0,229,255,0.2)"),
            yaxis=dict(title="Latitude", backgroundcolor="#090D1C", gridcolor="rgba(0,229,255,0.2)"),
            zaxis=dict(title="Speed (km/h)", backgroundcolor="#090D1C", gridcolor="rgba(0,229,255,0.2)"),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        )
    )

    st.plotly_chart(fig, use_container_width=True)
