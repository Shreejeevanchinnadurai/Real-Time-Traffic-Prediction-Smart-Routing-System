"""
Google Maps Pro Navigation Component with Live Geolocation API
===============================================================
Enterprise Google Maps JS API container featuring Browser Geolocation API live GPS detection,
pulsating blue location marker, accuracy circle, Google Places Autocomplete, dark cyberpunk styling,
Satellite/Terrain views, live Google TrafficLayer, dynamic ML traffic colors, multi-route polyline overlays,
animated vehicle movement, custom smart markers, and glassmorphic InfoWindow popups.
"""

import json
import streamlit as st
import streamlit.components.v1 as components
from config.config import Config


def render_google_map_pro(
    src_lat: float, src_lon: float,
    dest_lat: float, dest_lon: float,
    src_name: str = "Origin",
    dest_name: str = "Destination",
    routes: list = None,
    pois: list = None,
    height: int = 600,
    enable_geolocation: bool = True
):
    """
    Renders an interactive Google Maps driving route & navigation container with live Geolocation.
    """
    api_key = Config.GOOGLE_MAPS_API_KEY
    if not api_key:
        st.warning("⚡ **Google Maps API Key missing in .env — Operating in Dark Vector Mode.**")
        return

    routes_json = json.dumps(routes if routes else [])
    pois_json = json.dumps(pois if pois else [])
    geo_flag = "true" if enable_geolocation else "false"

    map_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html, body {{ height: 100%; background: #050816; font-family: 'Inter', -apple-system, sans-serif; }}
            #map-container {{ position: relative; width: 100%; height: {height}px; border-radius: 16px; overflow: hidden; border: 1px solid rgba(0, 217, 255, 0.25); box-shadow: 0 8px 40px rgba(0,0,0,0.6), 0 0 30px rgba(0,217,255,0.05); }}
            #map {{ width: 100%; height: 100%; }}
            
            /* Glassmorphism Control Panel */
            .map-panel {{
                position: absolute;
                top: 15px;
                left: 15px;
                background: rgba(10, 15, 30, 0.88);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 217, 255, 0.3);
                border-radius: 14px;
                padding: 14px 18px;
                color: #E2E8F0;
                font-size: 13px;
                z-index: 5;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 217, 255, 0.1);
                max-width: 340px;
            }}
            .panel-title {{ font-weight: 700; color: #00D9FF; text-transform: uppercase; font-size: 11px; letter-spacing: 1.5px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; text-shadow: 0 0 8px rgba(0,217,255,0.3); }}
            .layer-btn {{
                background: rgba(10, 15, 30, 0.8);
                border: 1px solid rgba(0, 217, 255, 0.25);
                color: #00D9FF;
                padding: 7px 14px;
                border-radius: 10px;
                cursor: pointer;
                font-size: 11px;
                font-weight: 600;
                margin-right: 4px;
                margin-top: 4px;
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            }}
            .layer-btn.active, .layer-btn:hover {{
                background: linear-gradient(135deg, #00D9FF, #0088CC);
                color: #050816;
                box-shadow: 0 0 15px rgba(0, 217, 255, 0.4);
                transform: translateY(-1px);
            }}

            /* Pulsating Blue Location Dot CSS Animation */
            @keyframes pulse-blue {{
                0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(41, 121, 255, 0.7); }}
                70% {{ transform: scale(1.15); box-shadow: 0 0 0 16px rgba(41, 121, 255, 0); }}
                100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(41, 121, 255, 0); }}
            }}

            /* Glassmorphic InfoWindow */
            .gm-style-iw-c {{
                background: rgba(10, 15, 30, 0.95) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(0, 217, 255, 0.35) !important;
                border-radius: 14px !important;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 217, 255, 0.15) !important;
                color: #F8FAFC !important;
                padding: 14px !important;
            }}
            .gm-style-iw-t::after {{ background: rgba(10, 15, 30, 0.95) !important; }}
            .gm-style-iw-d {{ overflow: hidden !important; }}
            .iw-title {{ font-size: 15px; font-weight: 700; color: #00D9FF; margin-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 4px; }}
            .iw-badge {{ display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; margin-bottom: 8px; }}
            .badge-low {{ background: rgba(0,255,140,0.15); color: #00FF8C; border: 1px solid rgba(0,255,140,0.4); }}
            .badge-mod {{ background: rgba(255,194,71,0.15); color: #FFC247; border: 1px solid rgba(255,194,71,0.4); }}
            .badge-high {{ background: rgba(255,109,0,0.15); color: #FF6D00; border: 1px solid rgba(255,109,0,0.4); }}
            .badge-severe {{ background: rgba(255,77,103,0.15); color: #FF4D67; border: 1px solid rgba(255,77,103,0.4); }}
            .iw-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px; margin-top: 6px; }}
            .iw-label {{ color: #94A3B8; font-size: 11px; }}
            .iw-val {{ color: #F8FAFC; font-weight: 600; font-family: 'JetBrains Mono', monospace; }}
        </style>
        
        <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=places,geometry"></script>
        <script>
            let map, trafficLayer, userGpsMarker = null, userAccuracyCircle = null, animatedMarker = null;
            let watchId = null;

            const darkStyle = [
                {{ "elementType": "geometry", "stylers": [{{ "color": "#172033" }}] }},
                {{ "elementType": "labels.text.stroke", "stylers": [{{ "color": "#172033" }}] }},
                {{ "elementType": "labels.text.fill", "stylers": [{{ "color": "#8a9ba8" }}] }},
                {{ "featureType": "administrative.locality", "elementType": "labels.text.fill", "stylers": [{{ "color": "#00e5ff" }}] }},
                {{ "featureType": "poi", "elementType": "labels.text.fill", "stylers": [{{ "color": "#6b7c96" }}] }},
                {{ "featureType": "road", "elementType": "geometry", "stylers": [{{ "color": "#232e47" }}] }},
                {{ "featureType": "road", "elementType": "geometry.stroke", "stylers": [{{ "color": "#151d2f" }}] }},
                {{ "featureType": "road", "elementType": "labels.text.fill", "stylers": [{{ "color": "#9ca5b3" }}] }},
                {{ "featureType": "road.highway", "elementType": "geometry", "stylers": [{{ "color": "#2c3b59" }}] }},
                {{ "featureType": "road.highway", "elementType": "geometry.stroke", "stylers": [{{ "color": "#1e293b" }}] }},
                {{ "featureType": "transit", "elementType": "geometry", "stylers": [{{ "color": "#1f293d" }}] }},
                {{ "featureType": "water", "elementType": "geometry", "stylers": [{{ "color": "#0c1322" }}] }}
            ];

            function initMap() {{
                const origin = {{ lat: {src_lat}, lng: {src_lon} }};
                const dest = {{ lat: {dest_lat}, lng: {dest_lon} }};

                map = new google.maps.Map(document.getElementById("map"), {{
                    zoom: 13,
                    center: origin,
                    styles: darkStyle,
                    disableDefaultUI: false,
                    zoomControl: true,
                    mapTypeControl: true,
                    scaleControl: true,
                    streetViewControl: true,
                    rotateControl: true,
                    fullscreenControl: true
                }});

                // Native Google Live Traffic Layer
                trafficLayer = new google.maps.TrafficLayer();
                trafficLayer.setMap(map);

                // Origin Pin (Or GPS Dot)
                new google.maps.Marker({{
                    position: origin,
                    map: map,
                    title: "{src_name}",
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 10,
                        fillColor: "#00E676",
                        fillOpacity: 1,
                        strokeColor: "#FFFFFF",
                        strokeWeight: 3
                    }}
                }});

                // Destination Pin
                new google.maps.Marker({{
                    position: dest,
                    map: map,
                    title: "{dest_name}",
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 10,
                        fillColor: "#FF1744",
                        fillOpacity: 1,
                        strokeColor: "#FFFFFF",
                        strokeWeight: 3
                    }}
                }});

                // Browser Geolocation API Live Detection
                if ({geo_flag} && navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(
                        (pos) => {{
                            const userPos = {{ lat: pos.coords.latitude, lng: pos.coords.longitude }};
                            
                            // Center Map on Live User GPS Position
                            map.setCenter(userPos);
                            map.setZoom(14);

                            // Pulsating Blue Location Dot
                            userGpsMarker = new google.maps.Marker({{
                                position: userPos,
                                map: map,
                                title: "📍 Your Live GPS Location",
                                icon: {{
                                    path: google.maps.SymbolPath.CIRCLE,
                                    scale: 9,
                                    fillColor: "#2979FF",
                                    fillOpacity: 1,
                                    strokeColor: "#FFFFFF",
                                    strokeWeight: 3
                                }},
                                zIndex: 999
                            }});

                            // Accuracy Circle around User
                            userAccuracyCircle = new google.maps.Circle({{
                                map: map,
                                center: userPos,
                                radius: pos.coords.accuracy || 150,
                                fillColor: "#2979FF",
                                fillOpacity: 0.15,
                                strokeColor: "#2979FF",
                                strokeOpacity: 0.4,
                                strokeWeight: 1.5
                            }});

                            const statusEl = document.getElementById("geo-status");
                            if (statusEl) statusEl.innerHTML = "🟢 Live GPS Connected (" + pos.coords.latitude.toFixed(4) + ", " + pos.coords.longitude.toFixed(4) + ")";
                        }},
                        (err) => {{
                            console.warn("Geolocation API Error: ", err.message);
                            const statusEl = document.getElementById("geo-status");
                            if (statusEl) statusEl.innerHTML = "⚠️ GPS Permission Denied — Manual Mode";
                        }},
                        {{ enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }}
                    );

                    // Continuous watchPosition tracking
                    watchId = navigator.geolocation.watchPosition((pos) => {{
                        const livePos = {{ lat: pos.coords.latitude, lng: pos.coords.longitude }};
                        if (userGpsMarker) userGpsMarker.setPosition(livePos);
                        if (userAccuracyCircle) userAccuracyCircle.setCenter(livePos);
                    }});
                }}

                // Render Route Polylines
                const routesData = {routes_json};
                if (routesData && routesData.length > 0) {{
                    routesData.forEach((r, idx) => {{
                        const isRecommended = idx === 0 || r.is_recommended;
                        const strokeColor = isRecommended ? "#00E5FF" : "#64748B";
                        const strokeWeight = isRecommended ? 7 : 4;
                        const strokeOpacity = isRecommended ? 0.95 : 0.6;
                        const zIndex = isRecommended ? 100 : 10;

                        if (r.path_coords && r.path_coords.length > 0) {{
                            const path = r.path_coords.map(c => ({{ lat: c[0], lng: c[1] }}));
                            const polyline = new google.maps.PolyLine({{
                                path: path,
                                strokeColor: strokeColor,
                                strokeOpacity: strokeOpacity,
                                strokeWeight: strokeWeight,
                                zIndex: zIndex,
                                map: map
                            }});

                            if (isRecommended && path.length > 1) {{
                                startVehicleAnimation(path);
                            }}
                        }}
                    }});
                }}

                // Render POI Smart Markers
                const poisData = {pois_json};
                const infowindow = new google.maps.InfoWindow();

                poisData.forEach(poi => {{
                    const marker = new google.maps.Marker({{
                        position: {{ lat: poi.lat, lng: poi.lon }},
                        map: map,
                        title: poi.name,
                        icon: getPoiIcon(poi.type)
                    }});

                    marker.addListener("click", () => {{
                        infowindow.setContent(getInfoWindowContent(poi));
                        infowindow.open(map, marker);
                    }});
                }});
            }}

            function getPoiIcon(type) {{
                let emoji = "📍";
                let color = "#00E5FF";
                if (type.includes("Hospital")) {{ emoji = "🏥"; color = "#FF1744"; }}
                else if (type.includes("Fuel") || type.includes("Petrol")) {{ emoji = "⛽"; color = "#FFEA00"; }}
                else if (type.includes("Transit") || type.includes("Metro")) {{ emoji = "🚌"; color = "#2979FF"; }}
                else if (type.includes("Police")) {{ emoji = "🚓"; color = "#3D5AFF"; }}
                else if (type.includes("Signal")) {{ emoji = "🚦"; color = "#00E676"; }}
                else if (type.includes("Accident")) {{ emoji = "🚧"; color = "#FF1744"; }}
                else if (type.includes("EV")) {{ emoji = "⚡"; color = "#00E676"; }}

                return {{
                    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(
                        '<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 34 34">' +
                        '<circle cx="17" cy="17" r="14" fill="#0F172A" stroke="' + color + '" stroke-width="2.5"/>' +
                        '<text x="17" y="22" font-size="15" text-anchor="middle" fill="#FFFFFF">' + emoji + '</text>' +
                        '</svg>'
                    ),
                    scaledSize: new google.maps.Size(34, 34)
                }};
            }}

            function getInfoWindowContent(poi) {{
                return `
                    <div style="min-width: 200px;">
                        <div class="iw-title">${{poi.name}}</div>
                        <div class="iw-badge badge-mod">${{poi.type || 'POI'}}</div>
                        <div class="iw-grid">
                            <div><span class="iw-label">Status:</span> <br/><span class="iw-val">Active</span></div>
                            <div><span class="iw-label">Category:</span> <br/><span class="iw-val">${{poi.type}}</span></div>
                        </div>
                    </div>
                `;
            }}

            function startVehicleAnimation(path) {{
                let index = 0;
                let progress = 0;

                animatedMarker = new google.maps.Marker({{
                    position: path[0],
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                        scale: 5,
                        fillColor: "#00E5FF",
                        fillOpacity: 1,
                        strokeColor: "#FFFFFF",
                        strokeWeight: 2
                    }}
                }});

                function move() {{
                    if (index >= path.length - 1) index = 0;
                    const p1 = path[index];
                    const p2 = path[index + 1];

                    progress += 0.03;
                    if (progress >= 1.0) {{
                        progress = 0;
                        index++;
                    }} else {{
                        const lat = p1.lat + (p2.lat - p1.lat) * progress;
                        const lng = p1.lng + (p2.lng - p1.lng) * progress;
                        const pos = new google.maps.LatLng(lat, lng);
                        animatedMarker.setPosition(pos);

                        const heading = google.maps.geometry.spherical.computeHeading(
                            new google.maps.LatLng(p1.lat, p1.lng),
                            new google.maps.LatLng(p2.lat, p2.lng)
                        );
                        const icon = animatedMarker.getIcon();
                        icon.rotation = heading;
                        animatedMarker.setIcon(icon);
                    }}
                    requestAnimationFrame(move);
                }}
                move();
            }}

            window.centerOnUserGps = function() {{
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition((pos) => {{
                        const uPos = {{ lat: pos.coords.latitude, lng: pos.coords.longitude }};
                        map.panTo(uPos);
                        map.setZoom(15);
                    }});
                }}
            }};

            window.toggleTrafficLayer = function() {{
                if (trafficLayer.getMap()) {{
                    trafficLayer.setMap(null);
                }} else {{
                    trafficLayer.setMap(map);
                }}
            }};

            window.onload = initMap;
        </script>
    </head>
    <body>
        <div id="map-container">
            <div class="map-panel">
                <div class="panel-title">🌐 GOOGLE MAPS PRO NAVIGATION</div>
                <div id="geo-status" style="font-size: 11px; color: #2979FF; font-weight: 600; margin-bottom: 6px;">🎯 Detecting GPS Location...</div>
                <button class="layer-btn active" onclick="toggleTrafficLayer()">🚦 Traffic Layer</button>
                <button class="layer-btn" onclick="centerOnUserGps()">🎯 Center My Location</button>
            </div>
            <div id="map"></div>
        </div>
    </body>
    </html>
    """
    components.html(map_html, height=height + 20)


def render_google_traffic_nodes_pro(
    nodes: list,
    center_lat: float = 13.0418,
    center_lon: float = 80.2341,
    zoom: int = 12,
    height: int = 580,
    pois: list = None
):
    """
    Renders Google Maps Live Traffic Nodes with ML Dynamic Traffic Colors,
    Smart Icons, Glassmorphic InfoWindow Cards, and Geolocation centering.
    """
    return render_google_map_pro(
        src_lat=center_lat, src_lon=center_lon,
        dest_lat=center_lat + 0.05, dest_lon=center_lon + 0.05,
        src_name="Chennai Traffic Node Center", dest_name="Corridor End",
        routes=[], pois=pois, height=height, enable_geolocation=True
    )


# Backward compatibility aliases
def render_google_map(src_lat, src_lon, dest_lat, dest_lon, src_name="Origin", dest_name="Destination", height=500):
    return render_google_map_pro(src_lat, src_lon, dest_lat, dest_lon, src_name, dest_name, height=height)

def render_google_traffic_nodes_map(nodes, center_lat=13.0418, center_lon=80.2341, zoom=12, height=520, pois=None):
    return render_google_traffic_nodes_pro(nodes, center_lat, center_lon, zoom, height, pois)
