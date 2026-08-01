"""
TrafficAI Application Entry Point — Ultra Premium Futuristic Landing
=====================================================================
Animated splash hero, glassmorphic branding, particle-mesh gradient
background, and futuristic CTA — the gateway to intelligent mobility.
"""

import streamlit as st
import os

from utils.constants import APP_TITLE, PAGE_ICON
from database.db_connection import initialize_database
from database.seed_database import seed_database
from config.config import Config

# Configure the Streamlit page
st.set_page_config(
    page_title="TrafficAI Command Centre",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global Futuristic Theme
from utils.theme import load_css
load_css()

# ── Initialization ───────────────────────────────────────────────────

@st.cache_resource
def init_system():
    """Run database initialization, seeding, and model training on startup if missing."""
    try:
        initialize_database()

        # Check if database is empty and seed if necessary
        db_path = str(Config.DB_PATH)
        if not (os.path.exists(db_path) and os.path.getsize(db_path) > 100 * 1024):
            seed_database()

        # Ensure trained models exist (critical for Streamlit Cloud deployment)
        clf_model_path = Config.MODELS_DIR / Config.CLASSIFICATION_MODEL_FILE
        if not clf_model_path.exists():
            from models.train_model import train_all_models
            train_all_models()
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")

init_system()

# ── Sidebar Branding ─────────────────────────────────────────────────
st.sidebar.markdown(
    """<div style="text-align: center; margin-bottom: 24px; animation: fadeSlideUp 0.6s ease-out;">
<div style="display: inline-block; position: relative; width: 60px; height: 60px; margin-bottom: 12px;">
<div style="position: absolute; inset: 0; border: 2px solid rgba(0, 217, 255, 0.3); border-top-color: #00D9FF; border-radius: 50%; animation: rotateRing 3s linear infinite;"></div>
<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.4rem;">🌐</div>
</div>
<h1 style="font-family: 'Space Grotesk', sans-serif; background: linear-gradient(135deg, #00D9FF, #6C63FF, #00FFCC); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 1.6rem; margin-bottom: 2px; font-weight: 700; letter-spacing: -0.01em;">TrafficAI</h1>
<p style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 500;">Intelligent Mobility Platform</p>
</div>""",
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# ── Landing Page — Hero Section ──────────────────────────────────────
from utils.ui_components import render_system_status

render_system_status()

# Animated Hero (Stripped leading indentation and comments to prevent Markdown codeblock rendering)
hero_html = """<div style="position: relative; background: rgba(10, 15, 30, 0.5); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(0, 217, 255, 0.1); border-radius: 20px; padding: 60px 40px; text-align: center; margin-top: 10px; overflow: hidden; box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4); animation: fadeSlideUp 0.7s ease-out;">
<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(2px 2px at 20% 30%, rgba(0,217,255,0.3), transparent), radial-gradient(2px 2px at 40% 70%, rgba(108,99,255,0.2), transparent), radial-gradient(2px 2px at 60% 20%, rgba(0,255,204,0.2), transparent), radial-gradient(2px 2px at 80% 60%, rgba(0,217,255,0.25), transparent), radial-gradient(3px 3px at 10% 80%, rgba(108,99,255,0.15), transparent), radial-gradient(2px 2px at 90% 40%, rgba(0,255,140,0.2), transparent), radial-gradient(2px 2px at 50% 50%, rgba(0,217,255,0.15), transparent), radial-gradient(1px 1px at 30% 55%, rgba(255,255,255,0.1), transparent), radial-gradient(1px 1px at 70% 35%, rgba(255,255,255,0.08), transparent); background-size: 200% 200%; animation: meshMove 15s ease infinite; pointer-events: none; border-radius: 20px;"></div>
<div style="position: absolute; top: -100px; right: -100px; width: 250px; height: 250px; border: 1px solid rgba(0, 217, 255, 0.08); border-top-color: rgba(0, 217, 255, 0.2); border-radius: 50%; animation: rotateRing 12s linear infinite; pointer-events: none;"></div>
<div style="position: absolute; bottom: -80px; left: -80px; width: 200px; height: 200px; border: 1px solid rgba(108, 99, 255, 0.08); border-bottom-color: rgba(108, 99, 255, 0.2); border-radius: 50%; animation: rotateRing 10s linear infinite reverse; pointer-events: none;"></div>
<div style="position: relative; z-index: 1;">
<h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 3.2rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 8px; background: linear-gradient(135deg, #FFFFFF 0%, #00D9FF 50%, #6C63FF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; animation: textGlow 3s ease-in-out infinite;">TRAFFICAI</h1>
<p style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 1.15rem; font-weight: 400; margin-bottom: 30px; letter-spacing: 0.02em;">
<span style="color: #00D9FF; font-weight: 600;">Predict</span> &nbsp;·&nbsp;
<span style="color: #6C63FF; font-weight: 600;">Analyse</span> &nbsp;·&nbsp;
<span style="color: #00FFCC; font-weight: 600;">Navigate Smarter</span>
</p>
<p style="font-family: 'Inter', sans-serif; color: #64748B; font-size: 0.95rem; max-width: 600px; margin: 0 auto 35px auto; line-height: 1.6;">
Real-time urban mobility intelligence powered by machine learning.
Predict congestion, optimise routes, and move smarter across the city network.
</p>
<div style="display: flex; justify-content: center; gap: 14px; flex-wrap: wrap;">
<span style="background: rgba(0, 217, 255, 0.1); border: 1px solid rgba(0, 217, 255, 0.3); color: #00D9FF; font-family: 'JetBrains Mono', monospace; padding: 8px 20px; border-radius: 24px; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px; animation: pulseGlow 3s ease-in-out infinite;">◉ LIVE SYSTEM</span>
<span style="background: rgba(108, 99, 255, 0.1); border: 1px solid rgba(108, 99, 255, 0.3); color: #6C63FF; font-family: 'JetBrains Mono', monospace; padding: 8px 20px; border-radius: 24px; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px;">✦ ML POWERED</span>
<span style="background: rgba(0, 255, 140, 0.1); border: 1px solid rgba(0, 255, 140, 0.3); color: #00FF8C; font-family: 'JetBrains Mono', monospace; padding: 8px 20px; border-radius: 24px; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px;">➤ SMART ROUTING</span>
</div>
</div>
</div>"""

st.markdown(hero_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick action cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""<div style="background: rgba(10, 15, 30, 0.6); backdrop-filter: blur(16px); border: 1px solid rgba(0, 217, 255, 0.1); border-radius: 14px; padding: 24px; text-align: center; transition: all 0.4s ease; animation: fadeSlideUp 0.5s ease-out 0.1s backwards; min-height: 160px;">
<div style="font-size: 2rem; margin-bottom: 10px;">🗺️</div>
<div style="font-family: 'Space Grotesk', sans-serif; color: #FFFFFF; font-weight: 600; font-size: 1rem; margin-bottom: 6px;">Live Traffic Map</div>
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.8rem;">Real-time monitoring with AI forecast overlay</div>
</div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""<div style="background: rgba(10, 15, 30, 0.6); backdrop-filter: blur(16px); border: 1px solid rgba(108, 99, 255, 0.1); border-radius: 14px; padding: 24px; text-align: center; transition: all 0.4s ease; animation: fadeSlideUp 0.5s ease-out 0.2s backwards; min-height: 160px;">
<div style="font-size: 2rem; margin-bottom: 10px;">✦</div>
<div style="font-family: 'Space Grotesk', sans-serif; color: #FFFFFF; font-weight: 600; font-size: 1rem; margin-bottom: 6px;">AI Prediction Engine</div>
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.8rem;">ML-powered congestion & speed forecasting</div>
</div>""", unsafe_allow_html=True)

with col3:
    st.markdown("""<div style="background: rgba(10, 15, 30, 0.6); backdrop-filter: blur(16px); border: 1px solid rgba(0, 255, 140, 0.1); border-radius: 14px; padding: 24px; text-align: center; transition: all 0.4s ease; animation: fadeSlideUp 0.5s ease-out 0.3s backwards; min-height: 160px;">
<div style="font-size: 2rem; margin-bottom: 10px;">➤</div>
<div style="font-family: 'Space Grotesk', sans-serif; color: #FFFFFF; font-weight: 600; font-size: 1rem; margin-bottom: 6px;">Smart Routing</div>
<div style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.8rem;">AI-optimised navigation with real-time traffic</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""<div style="text-align: center; padding: 14px; background: rgba(0, 217, 255, 0.05); border: 1px solid rgba(0, 217, 255, 0.15); border-radius: 12px; animation: fadeSlideUp 0.6s ease-out 0.4s backwards;">
<span style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 0.88rem;">
👈 Use the <strong style="color: #00D9FF;">sidebar</strong> to access the operational dashboard, AI predictions, and smart routing tools.
</span>
</div>""", unsafe_allow_html=True)
