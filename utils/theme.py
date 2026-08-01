"""
TrafficAI Ultra-Premium Futuristic Theme Engine
=================================================
Injects an advanced CSS design system into Streamlit, delivering a
Tesla Dashboard + Apple Vision Pro + Iron Man JARVIS HUD aesthetic.

Features:
  • Glassmorphism cards with animated gradient borders
  • Premium typography (Space Grotesk, Inter, JetBrains Mono)
  • Neon glow accents (Electric Blue, AI Cyan, Cyber Purple)
  • Animated entrance effects for all components
  • Magnetic hover buttons with ripple & glow
  • Custom ultra-thin neon scrollbar
  • Frosted glass navbar & sidebar
  • Floating card hover-tilt with depth shadows
"""

import streamlit as st


def load_css():
    """Inject the complete ultra-premium futuristic CSS design system."""
    st.markdown(
        """
        <style>
        /* ═══════════════════════════════════════════════════════════════
           §1  FONTS — Premium Typography Stack
           ═══════════════════════════════════════════════════════════════ */
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;600;700&display=swap');

        /* ═══════════════════════════════════════════════════════════════
           §2  KEYFRAME ANIMATIONS
           ═══════════════════════════════════════════════════════════════ */
        @keyframes fadeSlideUp {
            0%   { opacity: 0; transform: translateY(25px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeSlideIn {
            0%   { opacity: 0; transform: translateX(-20px); }
            100% { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 5px rgba(0, 217, 255, 0.3); }
            50%      { box-shadow: 0 0 20px rgba(0, 217, 255, 0.6), 0 0 40px rgba(0, 217, 255, 0.2); }
        }
        @keyframes breathe {
            0%, 100% { opacity: 0.7; transform: scale(1); }
            50%      { opacity: 1;   transform: scale(1.15); }
        }
        @keyframes borderGradient {
            0%   { border-color: rgba(0, 217, 255, 0.4); }
            33%  { border-color: rgba(108, 99, 255, 0.5); }
            66%  { border-color: rgba(0, 255, 140, 0.4); }
            100% { border-color: rgba(0, 217, 255, 0.4); }
        }
        @keyframes shimmer {
            0%   { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50%      { transform: translateY(-6px); }
        }
        @keyframes scanLine {
            0%   { top: 0%; }
            100% { top: 100%; }
        }
        @keyframes rotateRing {
            0%   { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes textGlow {
            0%, 100% { text-shadow: 0 0 10px rgba(0, 217, 255, 0.5); }
            50%      { text-shadow: 0 0 25px rgba(0, 217, 255, 0.8), 0 0 50px rgba(0, 217, 255, 0.3); }
        }
        @keyframes dotPulse {
            0%, 100% { box-shadow: 0 0 4px currentColor; transform: scale(1); }
            50%      { box-shadow: 0 0 12px currentColor, 0 0 24px currentColor; transform: scale(1.3); }
        }
        @keyframes gradientShift {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes ripple {
            0%   { transform: scale(0); opacity: 0.6; }
            100% { transform: scale(4); opacity: 0; }
        }
        @keyframes meshMove {
            0%   { background-position: 0% 0%; }
            50%  { background-position: 100% 100%; }
            100% { background-position: 0% 0%; }
        }

        /* ═══════════════════════════════════════════════════════════════
           §3  BASE APPLICATION — Dark Futuristic Canvas
           ═══════════════════════════════════════════════════════════════ */
        .stApp {
            background: #050816 !important;
            font-family: 'Inter', 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: #E2E8F0 !important;
        }

        /* Animated mesh gradient background overlay */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background:
                radial-gradient(ellipse at 20% 50%, rgba(0, 217, 255, 0.03) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(108, 99, 255, 0.03) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 80%, rgba(0, 255, 140, 0.02) 0%, transparent 50%);
            background-size: 200% 200%;
            animation: meshMove 20s ease infinite;
            pointer-events: none;
            z-index: 0;
        }

        /* ═══════════════════════════════════════════════════════════════
           §4  TOP HEADER BAR — Frosted Glass
           ═══════════════════════════════════════════════════════════════ */
        .stApp > header {
            background: rgba(5, 8, 22, 0.75) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            border-bottom: 1px solid rgba(0, 217, 255, 0.1) !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §5  SIDEBAR — Glass Command Panel
           ═══════════════════════════════════════════════════════════════ */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0A0F1E 0%, #070B19 50%, #050816 100%) !important;
            border-right: 1px solid rgba(0, 217, 255, 0.12) !important;
            box-shadow: 4px 0 30px rgba(0, 0, 0, 0.5) !important;
        }

        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: #00D9FF !important;
        }

        /* Sidebar nav links — animated indicator */
        [data-testid="stSidebar"] a {
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            border-radius: 8px !important;
            position: relative;
        }
        [data-testid="stSidebar"] a:hover {
            background: rgba(0, 217, 255, 0.08) !important;
            padding-left: 8px !important;
        }
        [data-testid="stSidebar"] a[aria-selected="true"] {
            background: rgba(0, 217, 255, 0.12) !important;
            border-left: 3px solid #00D9FF !important;
        }

        /* Sidebar horizontal rules */
        [data-testid="stSidebar"] hr {
            border-color: rgba(0, 217, 255, 0.1) !important;
            margin: 12px 0 !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §6  TYPOGRAPHY — Premium Hierarchy
           ═══════════════════════════════════════════════════════════════ */
        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: #FFFFFF !important;
            letter-spacing: -0.02em !important;
        }
        h1 { font-weight: 700 !important; }
        h2 { font-weight: 600 !important; color: #F1F5F9 !important; }
        h3 { font-weight: 600 !important; color: #E2E8F0 !important; }

        h4, h5, h6, p, span, div, label {
            font-family: 'Inter', sans-serif !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §7  GLASSMORPHIC CONTAINERS
           ═══════════════════════════════════════════════════════════════ */
        [data-testid="stExpander"],
        [data-testid="stForm"] {
            background: rgba(10, 15, 30, 0.7) !important;
            backdrop-filter: blur(20px) saturate(150%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
            border: 1px solid rgba(0, 217, 255, 0.12) !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            animation: fadeSlideUp 0.5s ease-out !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(10, 15, 30, 0.5) !important;
            border-radius: 12px !important;
            padding: 4px !important;
            gap: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px !important;
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            transition: all 0.3s ease !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #00D9FF !important;
            background: rgba(0, 217, 255, 0.08) !important;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(0, 217, 255, 0.15) !important;
            color: #00D9FF !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #00D9FF !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §8  BUTTONS — Premium Magnetic Hover
           ═══════════════════════════════════════════════════════════════ */
        div.stButton > button {
            background: linear-gradient(135deg, rgba(10, 18, 42, 0.9), rgba(5, 8, 22, 0.95)) !important;
            border: 1px solid rgba(0, 217, 255, 0.25) !important;
            color: #E2E8F0 !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            border-radius: 10px !important;
            padding: 10px 24px !important;
            transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            position: relative;
            overflow: hidden;
        }

        div.stButton > button:hover {
            transform: translateY(-3px) scale(1.02) !important;
            border-color: rgba(0, 217, 255, 0.7) !important;
            box-shadow: 0 8px 25px rgba(0, 217, 255, 0.2),
                        0 0 40px rgba(0, 217, 255, 0.1) !important;
            color: #FFFFFF !important;
        }

        div.stButton > button:active {
            transform: translateY(1px) scale(0.98) !important;
            box-shadow: 0 2px 8px rgba(0, 217, 255, 0.15) !important;
        }

        /* Primary CTA Button */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #00D9FF 0%, #0088CC 50%, #00D9FF 100%) !important;
            background-size: 200% auto !important;
            color: #050816 !important;
            border: none !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 20px rgba(0, 217, 255, 0.4) !important;
            animation: gradientShift 3s ease infinite !important;
        }
        div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 8px 35px rgba(0, 217, 255, 0.6),
                        0 0 60px rgba(0, 217, 255, 0.2) !important;
            transform: translateY(-3px) scale(1.03) !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §9  METRIC CARDS — Floating Glass KPIs
           ═══════════════════════════════════════════════════════════════ */
        [data-testid="stMetric"] {
            background: rgba(10, 15, 30, 0.65) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(0, 217, 255, 0.1) !important;
            border-radius: 14px !important;
            padding: 18px !important;
            transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
            animation: fadeSlideUp 0.6s ease-out backwards !important;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-6px) !important;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5),
                        0 0 30px rgba(0, 217, 255, 0.1) !important;
            border-color: rgba(0, 217, 255, 0.3) !important;
        }

        [data-testid="stMetricLabel"] {
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.8px !important;
        }
        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricDelta"] {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §10  DATA TABLES — Glass Data Grid
           ═══════════════════════════════════════════════════════════════ */
        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            background: rgba(10, 15, 30, 0.5) !important;
            backdrop-filter: blur(14px) !important;
            border: 1px solid rgba(0, 217, 255, 0.08) !important;
            border-radius: 14px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
            animation: fadeSlideUp 0.5s ease-out !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §11  FORM INPUTS — Glow Focus Ring
           ═══════════════════════════════════════════════════════════════ */
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stNumberInput > div > div,
        .stTextInput > div > div,
        .stDateInput > div > div,
        .stTimeInput > div > div,
        .stTextArea > div > div {
            background: rgba(10, 15, 30, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
            color: #E2E8F0 !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }

        .stSelectbox > div > div:focus-within,
        .stMultiSelect > div > div:focus-within,
        .stNumberInput > div > div:focus-within,
        .stTextInput > div > div:focus-within,
        .stTextArea > div > div:focus-within {
            border-color: rgba(0, 217, 255, 0.6) !important;
            box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.15),
                        0 0 20px rgba(0, 217, 255, 0.1) !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §12  ALERTS & NOTIFICATIONS — Glass Panels
           ═══════════════════════════════════════════════════════════════ */
        .stAlert, [data-testid="stAlert"] {
            background: rgba(10, 15, 30, 0.7) !important;
            backdrop-filter: blur(14px) !important;
            border-radius: 12px !important;
            border-left-width: 4px !important;
            animation: fadeSlideIn 0.4s ease-out !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §13  CHAT INTERFACE — JARVIS Glass Messages
           ═══════════════════════════════════════════════════════════════ */
        [data-testid="stChatMessage"] {
            background: rgba(10, 15, 30, 0.6) !important;
            backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 14px !important;
            animation: fadeSlideUp 0.4s ease-out !important;
        }

        [data-testid="stChatInput"] > div {
            background: rgba(10, 15, 30, 0.8) !important;
            border: 1px solid rgba(0, 217, 255, 0.2) !important;
            border-radius: 14px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stChatInput"] > div:focus-within {
            border-color: rgba(0, 217, 255, 0.6) !important;
            box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.1) !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §14  SLIDERS — Neon Track
           ═══════════════════════════════════════════════════════════════ */
        .stSlider [data-baseweb="slider"] [role="slider"] {
            background: #00D9FF !important;
            border: 2px solid #FFFFFF !important;
            box-shadow: 0 0 10px rgba(0, 217, 255, 0.5) !important;
        }
        .stSlider [data-baseweb="slider"] > div > div {
            background: linear-gradient(90deg, #00D9FF, #0088CC) !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §15  CHECKBOXES & TOGGLES
           ═══════════════════════════════════════════════════════════════ */
        .stCheckbox label span[data-testid="stCheckbox"] {
            transition: all 0.2s ease !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §16  SCROLLBAR — Ultra-Thin Neon
           ═══════════════════════════════════════════════════════════════ */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(5, 8, 22, 0.5);
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #00D9FF, #6C63FF);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #37F6FF, #8B7CFF);
        }

        /* ═══════════════════════════════════════════════════════════════
           §17  SELECTION & HIGHLIGHT — Cyan Accent
           ═══════════════════════════════════════════════════════════════ */
        ::selection {
            background: rgba(0, 217, 255, 0.3);
            color: #FFFFFF;
        }

        /* ═══════════════════════════════════════════════════════════════
           §18  HORIZONTAL RULES — Glowing Divider
           ═══════════════════════════════════════════════════════════════ */
        hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(90deg, transparent, rgba(0, 217, 255, 0.3), rgba(108, 99, 255, 0.2), transparent) !important;
            margin: 24px 0 !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §19  SPINNER — Neon Override
           ═══════════════════════════════════════════════════════════════ */
        .stSpinner > div > div {
            border-top-color: #00D9FF !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §20  RADIO BUTTONS — Glass Pill Style
           ═══════════════════════════════════════════════════════════════ */
        .stRadio > div {
            gap: 8px !important;
        }
        .stRadio > div > label {
            background: rgba(10, 15, 30, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 10px !important;
            padding: 8px 14px !important;
            transition: all 0.3s ease !important;
        }
        .stRadio > div > label:hover {
            border-color: rgba(0, 217, 255, 0.3) !important;
            background: rgba(0, 217, 255, 0.06) !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §21  PLOTLY CHART CONTAINER
           ═══════════════════════════════════════════════════════════════ */
        .stPlotlyChart {
            animation: fadeSlideUp 0.5s ease-out !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §22  COLUMNS — Staggered Animation
           ═══════════════════════════════════════════════════════════════ */
        [data-testid="stHorizontalBlock"] > div:nth-child(1) { animation: fadeSlideUp 0.4s ease-out 0.05s backwards; }
        [data-testid="stHorizontalBlock"] > div:nth-child(2) { animation: fadeSlideUp 0.4s ease-out 0.10s backwards; }
        [data-testid="stHorizontalBlock"] > div:nth-child(3) { animation: fadeSlideUp 0.4s ease-out 0.15s backwards; }
        [data-testid="stHorizontalBlock"] > div:nth-child(4) { animation: fadeSlideUp 0.4s ease-out 0.20s backwards; }
        [data-testid="stHorizontalBlock"] > div:nth-child(5) { animation: fadeSlideUp 0.4s ease-out 0.25s backwards; }

        /* ═══════════════════════════════════════════════════════════════
           §23  GLOBAL LINK STYLING
           ═══════════════════════════════════════════════════════════════ */
        a {
            color: #00D9FF !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
        }
        a:hover {
            color: #37F6FF !important;
            text-shadow: 0 0 8px rgba(0, 217, 255, 0.4) !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §24  MULTISELECT TAGS
           ═══════════════════════════════════════════════════════════════ */
        [data-baseweb="tag"] {
            background: rgba(0, 217, 255, 0.15) !important;
            border: 1px solid rgba(0, 217, 255, 0.3) !important;
            border-radius: 8px !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §25  FILE UPLOADER
           ═══════════════════════════════════════════════════════════════ */
        [data-testid="stFileUploader"] {
            background: rgba(10, 15, 30, 0.5) !important;
            border: 1px dashed rgba(0, 217, 255, 0.25) !important;
            border-radius: 14px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: rgba(0, 217, 255, 0.5) !important;
            background: rgba(0, 217, 255, 0.03) !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           §26  UTILITY CLASSES (for inline HTML)
           ═══════════════════════════════════════════════════════════════ */
        .tai-glass {
            background: rgba(10, 15, 30, 0.65);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 217, 255, 0.12);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
        }
        .tai-glow-border {
            animation: borderGradient 4s ease infinite;
        }
        .tai-float {
            animation: float 4s ease-in-out infinite;
        }
        .tai-fade-in {
            animation: fadeSlideUp 0.6s ease-out;
        }
        .tai-pulse {
            animation: pulseGlow 2.5s ease-in-out infinite;
        }
        .tai-gradient-text {
            background: linear-gradient(135deg, #00D9FF, #6C63FF, #00FFCC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .tai-shimmer {
            background: linear-gradient(90deg, transparent, rgba(0,217,255,0.08), transparent);
            background-size: 200% 100%;
            animation: shimmer 2s ease-in-out infinite;
        }
        .tai-number {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
