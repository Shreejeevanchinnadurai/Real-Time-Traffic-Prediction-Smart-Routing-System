"""
Pydeck 3D Geospatial Map Component
==================================
Renders interactive 3D extruded columns, animated traffic flow arcs,
and spatial density heatmaps using Pydeck (Deck.gl).
"""

import pydeck as pdk
import pandas as pd
import streamlit as st


def get_congestion_color(level: str):
    """Map congestion string level to RGBA array."""
    lvl = str(level).lower()
    if "low" in lvl or "free" in lvl or "clear" in lvl:
        return [0, 230, 118, 200]  # Green
    elif "moderate" in lvl or "med" in lvl:
        return [255, 171, 0, 220]  # Yellow/Gold
    elif "heavy" in lvl:
        return [255, 109, 0, 240]  # Orange
    else:  # Severe / Extreme
        return [255, 23, 68, 255]  # Glowing Neon Red


def render_pydeck_3d_traffic_map(
    nodes_df: pd.DataFrame,
    show_arcs: bool = True,
    show_columns: bool = True,
    show_hexagon: bool = False,
    pitch: int = 55,
    bearing: int = -20,
    height: int = 550
):
    """
    Renders an interactive Pydeck 3D Map in Streamlit.
    """
    if nodes_df is None or nodes_df.empty:
        st.warning("No traffic node data available for 3D map rendering.")
        return

    # Ensure required numeric columns exist
    df = nodes_df.copy()
    if "latitude" not in df.columns and "lat" in df.columns:
        df["latitude"] = df["lat"]
    if "longitude" not in df.columns and "lon" in df.columns:
        df["longitude"] = df["lon"]

    # Compute color arrays and column heights
    df["color"] = df["congestion_level"].apply(get_congestion_color)
    df["elevation"] = df["vehicle_count"].apply(lambda x: float(x) * 2.5 + 50.0)

    # Initial view state centered around data
    center_lat = float(df["latitude"].mean()) if not df.empty else 13.0600
    center_lon = float(df["longitude"].mean()) if not df.empty else 80.2300

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11.8,
        pitch=pitch,
        bearing=bearing
    )

    layers = []

    # 1. 3D Column Extrusion Layer
    if show_columns:
        column_layer = pdk.Layer(
            "ColumnLayer",
            data=df,
            get_position=["longitude", "latitude"],
            get_elevation="elevation",
            elevation_scale=1.5,
            radius=160,
            get_fill_color="color",
            pickable=True,
            auto_highlight=True,
            extruded=True,
        )
        layers.append(column_layer)

    # 2. 3D Animated Traffic Arcs Layer
    if show_arcs and len(df) >= 2:
        arc_records = []
        df_list = df.to_dict('records')
        for i in range(len(df_list)):
            for j in range(i + 1, min(i + 4, len(df_list))):
                src = df_list[i]
                dst = df_list[j]
                arc_records.append({
                    "src_name": src.get("location_name", "Origin"),
                    "dst_name": dst.get("location_name", "Destination"),
                    "src_lon": float(src["longitude"]),
                    "src_lat": float(src["latitude"]),
                    "dst_lon": float(dst["longitude"]),
                    "dst_lat": float(dst["latitude"]),
                    "color": src.get("color", [0, 229, 255, 200]),
                })
        
        if arc_records:
            arc_df = pd.DataFrame(arc_records)
            arc_layer = pdk.Layer(
                "ArcLayer",
                data=arc_df,
                get_source_position=["src_lon", "src_lat"],
                get_target_position=["dst_lon", "dst_lat"],
                get_source_color="color",
                get_target_color="[0, 229, 255, 255]",
                get_width=4.5,
                pickable=True,
                auto_highlight=True
            )
            layers.append(arc_layer)

    # 3. 3D Hexagon Aggregation Layer
    if show_hexagon:
        hex_layer = pdk.Layer(
            "HexagonLayer",
            data=df,
            get_position=["longitude", "latitude"],
            radius=350,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        )
        layers.append(hex_layer)

    # Tooltip configuration
    tooltip = {
        "html": "<b>Location:</b> {location_name}<br/>"
                "<b>Speed:</b> {average_speed} km/h<br/>"
                "<b>Vehicles:</b> {vehicle_count}<br/>"
                "<b>Congestion:</b> {congestion_level}",
        "style": {
            "backgroundColor": "#0F172A",
            "color": "#00E5FF",
            "border": "1px solid #00E5FF",
            "borderRadius": "8px",
            "fontFamily": "Inter, sans-serif",
            "fontSize": "13px",
            "padding": "10px"
        }
    }

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip=tooltip
    )

    st.pydeck_chart(deck, use_container_width=True, height=height)
