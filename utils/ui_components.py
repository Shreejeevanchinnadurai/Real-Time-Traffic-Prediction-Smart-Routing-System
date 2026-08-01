"""
TrafficAI Ultra-Premium UI Components
======================================
Advanced HTML/CSS rendering functions delivering a Tesla + JARVIS + Apple
Vision Pro aesthetic. Features glassmorphic KPIs, animated alerts,
AI processing states, JARVIS-style cards, and holographic UI elements.
"""

import streamlit as st
import streamlit.components.v1 as components
import time


# ═══════════════════════════════════════════════════════════════════════
#  PREMIUM PAGE HEADER
# ═══════════════════════════════════════════════════════════════════════
def render_header(title: str, subtitle: str):
    """Render a futuristic page header with gradient underline and entrance animation."""
    st.markdown(f"""<div style="animation: fadeSlideUp 0.6s ease-out; margin-bottom: 30px;">
<h1 style="font-family: 'Space Grotesk', sans-serif; color: #FFFFFF; font-weight: 700; font-size: 2.2rem; margin-bottom: 4px; letter-spacing: -0.02em;">{title}</h1>
<div style="font-family: 'Inter', sans-serif; color: #00D9FF; font-weight: 500; font-size: 1.05rem; letter-spacing: 0.02em; opacity: 0.9;">{subtitle}</div>
<div style="margin-top: 12px; height: 3px; width: 80px; background: linear-gradient(90deg, #00D9FF, #6C63FF, transparent); border-radius: 4px;"></div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  SYSTEM STATUS HUD BAR
# ═══════════════════════════════════════════════════════════════════════
def render_system_status():
    """Render a floating glass HUD bar with animated pulse status dots."""
    from config.config import Config
    g_key_status = "CONNECTED" if Config.GOOGLE_MAPS_API_KEY else "OFFLINE"
    g_color = "#00FF8C" if Config.GOOGLE_MAPS_API_KEY else "#FFC247"

    st.markdown(f"""<div style="display: flex; justify-content: flex-end; align-items: center; gap: 18px; padding: 10px 18px; background: rgba(10, 15, 30, 0.6); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(0, 217, 255, 0.1); border-radius: 12px; margin-bottom: 20px; animation: fadeSlideUp 0.4s ease-out; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
<span style="display: flex; align-items: center; gap: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 600; color: #00FF8C;">
<div style="width: 8px; height: 8px; border-radius: 50%; background: #00FF8C; box-shadow: 0 0 8px #00FF8C; animation: breathe 2s ease-in-out infinite;"></div>
LIVE
</span>
<span style="display: flex; align-items: center; gap: 6px; font-family: 'Inter', sans-serif; font-size: 0.78rem; color: #94A3B8;">
<div style="width: 6px; height: 6px; border-radius: 50%; background: {g_color}; box-shadow: 0 0 6px {g_color}; animation: breathe 2.5s ease-in-out infinite 0.3s;"></div>
Google Maps: <strong style="color: {g_color};">{g_key_status}</strong>
</span>
<span style="display: flex; align-items: center; gap: 6px; font-family: 'Inter', sans-serif; font-size: 0.78rem; color: #94A3B8;">
<div style="width: 6px; height: 6px; border-radius: 50%; background: #00D9FF; box-shadow: 0 0 6px #00D9FF; animation: breathe 2.5s ease-in-out infinite 0.6s;"></div>
SQL: <strong style="color: #00D9FF;">ONLINE</strong>
</span>
<span style="display: flex; align-items: center; gap: 6px; font-family: 'Inter', sans-serif; font-size: 0.78rem; color: #94A3B8;">
<div style="width: 6px; height: 6px; border-radius: 50%; background: #6C63FF; box-shadow: 0 0 6px #6C63FF; animation: breathe 2.5s ease-in-out infinite 0.9s;"></div>
ML Engine: <strong style="color: #6C63FF;">READY</strong>
</span>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  GLASSMORPHIC KPI CARD
# ═══════════════════════════════════════════════════════════════════════
def render_kpi_card(title: str, value: str, icon: str, trend: str = "", border_color: str = "rgba(0, 217, 255, 0.12)"):
    """Render a premium glassmorphic floating KPI card."""
    st.markdown(f"""<div style="background: rgba(10, 15, 30, 0.65); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid {border_color}; border-radius: 14px; padding: 20px; color: white; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.04); transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); margin-bottom: 16px; display: flex; flex-direction: column; min-height: 130px; animation: fadeSlideUp 0.5s ease-out backwards; position: relative; overflow: hidden;">
<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, transparent, rgba(0,217,255,0.03), transparent); background-size: 200% 100%; animation: shimmer 3s ease-in-out infinite; border-radius: 14px; pointer-events: none;"></div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; position: relative; z-index: 1;">
<span style="font-family: 'Inter', sans-serif; font-size: 0.78rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">{title}</span>
<span style="font-size: 1.4rem; opacity: 0.8; filter: drop-shadow(0 0 4px rgba(0,217,255,0.3));">{icon}</span>
</div>
<div style="font-family: 'JetBrains Mono', monospace; font-size: 2.2rem; font-weight: 700; color: #FFFFFF; line-height: 1.2; position: relative; z-index: 1;">{value}</div>
<div style="font-family: 'Inter', sans-serif; font-size: 0.8rem; color: #00D9FF; margin-top: auto; padding-top: 8px; font-weight: 500; position: relative; z-index: 1;">{trend}</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  PREMIUM ALERT BANNER
# ═══════════════════════════════════════════════════════════════════════
def render_alert(message: str, level: str = "NORMAL"):
    """Render a premium glassmorphic alert with animated indicator."""
    colors = {
        "CRITICAL": ("#FF4D67", "🔴"),
        "WARNING":  ("#FFC247", "🟠"),
        "CAUTION":  ("#FFE066", "🟡"),
        "NORMAL":   ("#00FF8C", "🟢")
    }
    color, icon = colors.get(level.upper(), colors["NORMAL"])

    st.markdown(f"""<div style="display: flex; align-items: center; gap: 14px; padding: 14px 18px; background: rgba(10, 15, 30, 0.7); backdrop-filter: blur(14px); border-left: 4px solid {color}; border-radius: 10px; margin-bottom: 10px; animation: fadeSlideIn 0.4s ease-out; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25); transition: all 0.3s ease;">
<div style="font-size: 1.1rem; animation: breathe 2s ease-in-out infinite;">{icon}</div>
<div>
<div style="font-family: 'JetBrains Mono', monospace; color: {color}; font-size: 0.72rem; font-weight: 700; letter-spacing: 1.2px; margin-bottom: 2px;">{level.upper()}</div>
<div style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-size: 0.9rem;">{message}</div>
</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  AI PROCESSING STATE — Neural Animation
# ═══════════════════════════════════════════════════════════════════════
def render_ai_processing_state(container):
    """Simulates AI processing pipeline with futuristic step indicators."""
    steps = [
        ("🔍", "Scanning traffic network telemetry..."),
        ("🧠", "Running ML congestion prediction models..."),
        ("⚡", "Calculating road weights & edge costs..."),
        ("📊", "Comparing route alternatives..."),
        ("✦",  "Selecting AI-optimal route..."),
    ]
    for icon, step in steps:
        container.markdown(f"""<div style="display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: rgba(10, 15, 30, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(0, 217, 255, 0.15); border-radius: 10px; margin-bottom: 0; animation: fadeSlideIn 0.3s ease-out;">
<span style="font-size: 1.2rem; animation: breathe 1.5s ease-in-out infinite;">{icon}</span>
<span style="font-family: 'Inter', sans-serif; color: #00D9FF; font-weight: 600; font-size: 0.9rem;">{step}</span>
<div style="margin-left: auto; width: 16px; height: 16px; border: 2px solid #00D9FF; border-top-color: transparent; border-radius: 50%; animation: rotateRing 0.8s linear infinite;"></div>
</div>""", unsafe_allow_html=True)
        time.sleep(0.5)
    container.empty()


# ═══════════════════════════════════════════════════════════════════════
#  ROUTE COMPARISON CARD — Glass with Glow
# ═══════════════════════════════════════════════════════════════════════
def render_route_comparison_card(route, is_recommended=False):
    """Renders a glassmorphic route comparison card."""
    border = "rgba(0, 217, 255, 0.7)" if is_recommended else "rgba(255, 255, 255, 0.08)"
    shadow = "0 0 30px rgba(0, 217, 255, 0.2), 0 8px 32px rgba(0,0,0,0.4)" if is_recommended else "0 4px 16px rgba(0,0,0,0.3)"
    bg = "rgba(10, 15, 30, 0.85)" if is_recommended else "rgba(10, 15, 30, 0.6)"
    badge = """<div style="background: linear-gradient(135deg, #00D9FF, #00FFCC); color: #050816; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 800; padding: 5px 12px; border-radius: 20px; display: inline-block; margin-bottom: 10px; letter-spacing: 0.8px; animation: pulseGlow 2s ease-in-out infinite;">⭐ TOP AI RECOMMENDATION</div>""" if is_recommended else ""

    title = route.get("profile_title", f"Route Option {route.get('rank', 1)}")
    dist = route.get("total_distance_km", 0.0)
    dur = route.get("total_duration_min", 0.0)
    fuel = route.get("fuel_liters", round(dist * 0.07, 2))
    co2 = route.get("co2_kg", round(fuel * 2.31, 2))
    conf = route.get("confidence_score", 92.5)
    ai_rec = route.get("ai_recommendation", "Optimized by ML graph routing engine.")

    st.markdown(f"""<div style="background: {bg}; backdrop-filter: blur(20px); border: 1px solid {border}; box-shadow: {shadow}; border-radius: 14px; padding: 20px; margin-bottom: 16px; animation: fadeSlideUp 0.5s ease-out; transition: all 0.3s ease;">
{badge}
<h4 style="margin: 0 0 12px 0; color: #FFFFFF; font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700;">{title}</h4>
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 14px; text-align: center; background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px;">
<div>
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">EST. TIME</div>
<div style="font-family: 'JetBrains Mono', monospace; color: #00D9FF; font-size: 1.25rem; font-weight: 700;">{dur:.0f} min</div>
</div>
<div>
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">DISTANCE</div>
<div style="font-family: 'JetBrains Mono', monospace; color: #FFFFFF; font-size: 1.25rem; font-weight: 700;">{dist:.1f} km</div>
</div>
<div>
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">CONFIDENCE</div>
<div style="font-family: 'JetBrains Mono', monospace; color: #00FF8C; font-size: 1.25rem; font-weight: 700;">{conf:.1f}%</div>
</div>
</div>
<div style="display: flex; justify-content: space-between; font-family: 'Inter', sans-serif; font-size: 0.82rem; color: #94A3B8; margin-bottom: 8px;">
<span>⛽ Fuel: <strong style="color: #E2E8F0; font-family: 'JetBrains Mono', monospace;">{fuel:.2f} L</strong></span>
<span>🌱 CO₂: <strong style="color: #E2E8F0; font-family: 'JetBrains Mono', monospace;">{co2:.2f} kg</strong></span>
</div>
<div style="margin-top: 12px; font-family: 'Inter', sans-serif; font-size: 0.82rem; color: #94A3B8; background: rgba(0, 217, 255, 0.05); border-left: 3px solid #00D9FF; padding: 10px 14px; border-radius: 6px;">{ai_rec}</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  TRAFFICGPT JARVIS-STYLE RESPONSE CARD
# ═══════════════════════════════════════════════════════════════════════
def render_trafficgpt_card(data: dict):
    """Renders the JARVIS-style TrafficGPT Agent Report Card."""
    conv = data.get("conversational_text", "")
    status = data.get("live_status", "NORMAL 🟢")
    eta = data.get("estimated_time")
    route = data.get("recommended_route")
    delay = data.get("delay", "0 min")
    trend = data.get("prediction_trend", "Stable traffic flow.")
    advice = data.get("recommendation", "Conditions normal.")
    reason = data.get("reasoning", "Evaluated ML models & SQLite live traffic state.")
    tools = data.get("tool_calls_made", [])

    if conv:
        st.markdown(conv)

    if eta or route:
        tools_html = "".join([
            f"""<span style="background: rgba(0, 217, 255, 0.1); border: 1px solid rgba(0, 217, 255, 0.3); color: #00D9FF; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; padding: 3px 10px; border-radius: 12px; margin-right: 5px; display: inline-block; margin-top: 4px;">🛠️ {t}</span>""" for t in tools
        ])

        st.markdown(f"""<div style="background: rgba(10, 15, 30, 0.9); backdrop-filter: blur(20px); border: 1px solid rgba(0, 217, 255, 0.35); box-shadow: 0 0 30px rgba(0, 217, 255, 0.12), 0 8px 32px rgba(0,0,0,0.4); border-radius: 14px; padding: 22px; margin: 15px 0; animation: fadeSlideUp 0.5s ease-out; position: relative; overflow: hidden;">
<div style="position: absolute; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(0,217,255,0.4), transparent); animation: scanLine 3s linear infinite; pointer-events: none;"></div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 10px;">
<span style="font-family: 'Space Grotesk', sans-serif; color: #00D9FF; font-weight: 700; font-size: 0.85rem; letter-spacing: 1px;">🤖 TRAFFICGPT AGENT REPORT</span>
<span style="background: rgba(255,255,255,0.05); padding: 4px 12px; border-radius: 14px; color: white; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600;">{status}</span>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
<div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px;">
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">🕒 ESTIMATED TIME</div>
<div style="font-family: 'JetBrains Mono', monospace; color: white; font-size: 1.05rem; font-weight: 700;">{eta or 'N/A'}</div>
</div>
<div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px;">
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">🚗 RECOMMENDED ROUTE</div>
<div style="font-family: 'JetBrains Mono', monospace; color: #00D9FF; font-size: 0.95rem; font-weight: 700;">{route or 'N/A'}</div>
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
<div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px;">
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">⚠ EXPECTED DELAY</div>
<div style="font-family: 'JetBrains Mono', monospace; color: #FFC247; font-size: 0.95rem; font-weight: 700;">{delay}</div>
</div>
<div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px;">
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">📈 AI PREDICTION</div>
<div style="font-family: 'Inter', sans-serif; color: #CBD5E1; font-size: 0.82rem;">{trend}</div>
</div>
</div>
<div style="background: rgba(0, 255, 140, 0.06); border-left: 3px solid #00FF8C; padding: 12px 14px; border-radius: 6px; margin-bottom: 12px; font-family: 'Inter', sans-serif; font-size: 0.88rem; color: #E2E8F0;">
{advice}
</div>
<div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; font-family: 'Inter', sans-serif; font-size: 0.82rem; color: #94A3B8; margin-bottom: 10px;">
<strong style="color: #6C63FF;">🧠 AI Reasoning:</strong> {reason}
</div>
<div style="margin-top: 8px;">{tools_html}</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  ANIMATED LOADING SCREEN
# ═══════════════════════════════════════════════════════════════════════
def render_loading_screen():
    """Render a premium animated loading screen with rotating rings and AI brain."""
    loading_html = """<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px; text-align: center; background: rgba(10, 15, 30, 0.8); backdrop-filter: blur(20px); border: 1px solid rgba(0, 217, 255, 0.12); border-radius: 20px; animation: fadeSlideUp 0.5s ease-out;">
<div style="position: relative; width: 80px; height: 80px; margin-bottom: 24px;">
<div style="position: absolute; inset: 0; border: 3px solid transparent; border-top-color: #00D9FF; border-radius: 50%; animation: rotateRing 1.2s linear infinite;"></div>
<div style="position: absolute; inset: 8px; border: 3px solid transparent; border-top-color: #6C63FF; border-radius: 50%; animation: rotateRing 0.9s linear infinite reverse;"></div>
<div style="position: absolute; inset: 16px; border: 3px solid transparent; border-top-color: #00FFCC; border-radius: 50%; animation: rotateRing 1.5s linear infinite;"></div>
<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 10px; height: 10px; background: #00D9FF; border-radius: 50%; animation: breathe 1.5s ease-in-out infinite; box-shadow: 0 0 15px #00D9FF;"></div>
</div>
<div style="font-family: 'Space Grotesk', sans-serif; color: #00D9FF; font-weight: 600; font-size: 1.1rem; letter-spacing: 1px; animation: textGlow 2s ease-in-out infinite;">TRAFFICAI</div>
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.8rem; margin-top: 8px;">Loading traffic intelligence network...</div>
</div>"""
    st.markdown(loading_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  FLOATING AI ORB INDICATOR
# ═══════════════════════════════════════════════════════════════════════
def render_floating_ai_orb():
    """Render a floating circular AI orb with holographic pulse effect."""
    st.markdown("""<div style="display: flex; justify-content: center; margin: 20px 0;">
<div style="position: relative; width: 90px; height: 90px;">
<div style="position: absolute; inset: 0; border: 2px solid rgba(0, 217, 255, 0.3); border-radius: 50%; animation: rotateRing 4s linear infinite;"></div>
<div style="position: absolute; inset: 10px; border: 2px solid rgba(108, 99, 255, 0.3); border-top-color: #6C63FF; border-radius: 50%; animation: rotateRing 3s linear infinite reverse;"></div>
<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 40px; height: 40px; background: radial-gradient(circle, #00D9FF, #0088CC, #005599); border-radius: 50%; box-shadow: 0 0 25px rgba(0, 217, 255, 0.5), 0 0 50px rgba(0, 217, 255, 0.2); animation: breathe 2.5s ease-in-out infinite;"></div>
<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 700; color: #FFFFFF; letter-spacing: 1px; z-index: 2;">AI</div>
</div>
</div>""", unsafe_allow_html=True)
