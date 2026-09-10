"""
=============================================================================
VisionDNA
Visual Intelligence & Predictive Safety Platform
Clean Enterprise Light & Dark Slate Interface (High-Contrast Sidebar)
=============================================================================
"""

import sys
import os
import time
import datetime
import tempfile
import cv2
import numpy as np
import pandas as pd
import streamlit as st

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.camera import VideoStream
from src.detector import UnifiedPersonPoseDetector
from src.tracker import PersonTracker
from src.activity import ActivityClassifier
from src.digital_twin import DigitalTwinEngine
from src.prediction import ActivityPredictor
from src.risk_engine import RiskEngine

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VisionDNA | Visual Intelligence Platform",
    page_icon="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f52c.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Global Top-Level High-Contrast CSS Theme Injection
# -----------------------------------------------------------------------------
# Initialize session state for theme if not present
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Clean Light"

is_light = (st.session_state.app_theme == "Clean Light")

if is_light:
    css_theme = """
    /* Main App Background & Text */
    .stApp {
        background-color: #F8FAFC !important;
        background-image: linear-gradient(180deg, #FFFFFF 0%, #F1F5F9 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: #0F172A !important;
    }

    /* Sidebar Container */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* All Sidebar Text & Labels - High Contrast Deep Slate */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] div {
        color: #0F172A !important;
    }

    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {
        color: #475569 !important;
    }

    /* Sidebar Expanders */
    section[data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        border-bottom: 1px solid #E2E8F0 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 12px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stExpander"] summary span {
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    /* Sidebar Radio Buttons */
    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: #0F172A !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        margin-bottom: 4px !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #0284C7 !important;
        background-color: #F0F9FF !important;
    }

    /* Sidebar Checkboxes & Toggles */
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
        color: #0F172A !important;
        font-weight: 500 !important;
    }

    /* Sidebar Dropdowns / Select Boxes */
    section[data-testid="stSidebar"] [data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #0F172A !important;
    }

    /* Sidebar Number Inputs & Sliders */
    section[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSlider"] label {
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    /* Top Application Header */
    .app-header {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 14px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 2px 8px rgba(0,0,0,0.02) !important;
    }

    .brand-title {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        letter-spacing: -0.02em !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }

    .brand-subtitle {
        font-size: 0.80rem !important;
        color: #475569 !important;
        margin: 2px 0 0 0 !important;
        font-weight: 400 !important;
    }

    /* Metric Cards */
    .metric-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 2px 8px rgba(0,0,0,0.02) !important;
    }

    .metric-caption {
        font-size: 0.72rem !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-weight: 600 !important;
        margin-bottom: 4px !important;
    }

    .metric-number {
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }

    .metric-hint {
        font-size: 0.72rem !important;
        color: #0284C7 !important;
        margin-top: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Viewports */
    .viewport-card-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding: 8px 12px !important;
        background: #F1F5F9 !important;
        border: 1px solid #E2E8F0 !important;
        border-bottom: none !important;
        border-top-left-radius: 10px !important;
        border-top-right-radius: 10px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }

    .viewport-tag {
        font-size: 0.70rem !important;
        color: #0284C7 !important;
        font-family: 'JetBrains Mono', monospace !important;
        background: #E0F2FE !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }

    /* Alerts */
    .alert-normal {
        background: #ECFDF5 !important;
        border: 1px solid #A7F3D0 !important;
        border-left: 4px solid #10B981 !important;
        color: #065F46 !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        margin-bottom: 12px !important;
    }

    .alert-warning {
        background: #FFFBEB !important;
        border: 1px solid #FDE68A !important;
        border-left: 4px solid #F59E0B !important;
        color: #92400E !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        margin-bottom: 12px !important;
    }

    .alert-critical {
        background: #FEF2F2 !important;
        border: 1px solid #FECACA !important;
        border-left: 4px solid #EF4444 !important;
        color: #991B1B !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        margin-bottom: 12px !important;
    }

    .forecast-box {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 14px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        background-color: #F1F5F9 !important;
        padding: 4px !important;
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 34px !important;
        border-radius: 6px !important;
        color: #475569 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0 14px !important;
    }

    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }

    .stDataFrame {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid #E2E8F0 !important;
        background: #FFFFFF !important;
    }
    """
    cv_theme = {
        "is_light": True,
        "cv_bg": (248, 250, 252),
        "cv_grid": (226, 232, 240),
        "hdr_bg": (255, 255, 255),
        "text_primary": (15, 23, 42),
        "text_muted": (100, 116, 139),
    }
else:
    css_theme = """
    .stApp {
        background-color: #070B14 !important;
        background-image: radial-gradient(circle at 50% 0%, #0B132B 0%, #070B14 75%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: #F8FAFC !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0B1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] div {
        color: #F8FAFC !important;
    }
    .app-header {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 14px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }
    .brand-title {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        letter-spacing: -0.02em !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    .brand-subtitle {
        font-size: 0.80rem !important;
        color: #94A3B8 !important;
        margin: 2px 0 0 0 !important;
        font-weight: 400 !important;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
    }
    .metric-caption {
        font-size: 0.72rem !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-weight: 600 !important;
        margin-bottom: 4px !important;
    }
    .metric-number {
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }
    .metric-hint {
        font-size: 0.72rem !important;
        color: #38BDF8 !important;
        margin-top: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .viewport-card-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding: 8px 12px !important;
        background: rgba(255, 255, 255, 0.02) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-top-left-radius: 10px !important;
        border-top-right-radius: 10px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
    }
    .viewport-tag {
        font-size: 0.70rem !important;
        color: #38BDF8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(56, 189, 248, 0.10) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    .alert-normal {
        background: rgba(16, 185, 129, 0.08) !important;
        border: 1px solid rgba(16, 185, 129, 0.25) !important;
        border-left: 4px solid #10B981 !important;
        color: #6EE7B7 !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        margin-bottom: 12px !important;
    }
    .alert-warning {
        background: rgba(245, 158, 11, 0.08) !important;
        border: 1px solid rgba(245, 158, 11, 0.25) !important;
        border-left: 4px solid #F59E0B !important;
        color: #FCD34D !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        margin-bottom: 12px !important;
    }
    .alert-critical {
        background: rgba(239, 68, 68, 0.08) !important;
        border: 1px solid rgba(239, 68, 68, 0.25) !important;
        border-left: 4px solid #EF4444 !important;
        color: #FCA5A5 !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        margin-bottom: 12px !important;
    }
    .forecast-box {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 14px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        background-color: rgba(15, 23, 42, 0.5) !important;
        padding: 4px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 34px !important;
        border-radius: 6px !important;
        color: #94A3B8 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0 14px !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }
    .stDataFrame {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    """
    cv_theme = {
        "is_light": False,
        "cv_bg": (15, 23, 42),
        "cv_grid": (30, 41, 59),
        "hdr_bg": (15, 23, 42),
        "text_primary": (248, 250, 252),
        "text_muted": (148, 163, 184),
    }

st.markdown(f"<style>{css_theme}</style>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Sidebar Navigation & Controls Setup
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
<div style="background: linear-gradient(135deg, #0284C7, #38BDF8); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3);">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
<circle cx="12" cy="13" r="3"/>
</svg>
</div>
<div>
<h3 style="margin: 0; font-size: 1.05rem; font-weight: 700; letter-spacing: -0.01em;">VisionDNA</h3>
<p style="margin: 0; color: #64748B; font-size: 0.70rem; font-weight: 500;">Visual Intelligence Platform</p>
</div>
</div>
<div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.10); border: 1px solid rgba(16, 185, 129, 0.30); color: #059669; padding: 2px 8px; border-radius: 12px; font-size: 0.70rem; font-weight: 600; margin-bottom: 12px;">
<span style="font-size: 0.55rem;">●</span> System Operational
</div>""",
        unsafe_allow_html=True,
    )

    theme_selection = st.selectbox(
        "Interface Theme",
        ["Clean Light", "Refined Dark"],
        index=0 if st.session_state.app_theme == "Clean Light" else 1,
    )
    if theme_selection != st.session_state.app_theme:
        st.session_state.app_theme = theme_selection
        st.rerun()

    st.markdown("<hr style='border-color: rgba(0,0,0,0.08); margin: 8px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 4px 0 6px 0;'>Select Workspace</p>", unsafe_allow_html=True)
    workspace = st.radio(
        "Workspace Selection",
        [
            "Live Camera",
            "Video Intelligence",
            "Scenario Simulator",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # Configuration Accordion
    with st.expander("Configuration", expanded=True):
        if workspace == "Live Camera":
            st.markdown("<p style='font-size: 0.74rem; color: #0F172A; font-weight: 600; margin: 0 0 4px 0;'>Camera Device</p>", unsafe_allow_html=True)
            camera_idx = st.number_input("Device Index", min_value=0, max_value=5, value=0, step=1, label_visibility="collapsed")
            use_dshow = st.checkbox("Windows DirectShow Backend", value=True, help="Low-latency capture driver for Windows.")
            target_res_str = st.selectbox("Capture Resolution", ["640x480 (VGA)", "1280x720 (HD)", "320x240 (Fast)"], index=0)
            target_w = 640 if "640" in target_res_str else (1280 if "1280" in target_res_str else 320)
            target_h = 480 if "480" in target_res_str else (720 if "720" in target_res_str else 240)
        elif workspace == "Video Intelligence":
            st.markdown("<p style='font-size: 0.74rem; color: #0F172A; font-weight: 600; margin: 0 0 4px 0;'>Video File</p>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Choose Video File",
                type=["mp4", "avi", "mov", "mkv", "webm"],
                label_visibility="collapsed",
                help="Select video file for frame-by-frame analysis.",
            )
            frame_stride = st.slider("Frame Stride", min_value=1, max_value=4, value=1, help="Process every Nth frame for higher playback speed.")
        else:
            st.markdown("<p style='font-size: 0.74rem; color: #0F172A; font-weight: 600; margin: 0 0 4px 0;'>Test Scenario</p>", unsafe_allow_html=True)
            demo_scenario = st.selectbox(
                "Scenario",
                ["Standard Room Walk", "Zone Approach Simulation", "Critical Fall Anomaly", "Proximity Alert"],
                index=0,
                label_visibility="collapsed",
            )

        st.markdown("<hr style='border-color: rgba(0,0,0,0.08); margin: 8px 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.74rem; color: #0F172A; font-weight: 600; margin: 0 0 4px 0;'>Perception Tuning</p>", unsafe_allow_html=True)
        conf_thresh = st.slider("Detection Confidence", min_value=0.20, max_value=0.90, value=0.35, step=0.05)
        speed_profile = st.selectbox("Inference Resolution", ["Balanced (480px)", "Ultra-Fast (320px)", "High-Precision (640px)"], index=0)
        img_size = 480 if "480" in speed_profile else (320 if "320" in speed_profile else 640)

        st.markdown("<hr style='border-color: rgba(0,0,0,0.08); margin: 8px 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.74rem; color: #0F172A; font-weight: 600; margin: 0 0 4px 0;'>Visual Overlays</p>", unsafe_allow_html=True)
        enable_detection = st.checkbox("Person Detection", value=True)
        enable_tracking = st.checkbox("Object Tracking", value=True)
        enable_skeleton = st.checkbox("Skeleton Overlay", value=True)
        enable_danger_zone = st.checkbox("Restricted Danger Zone", value=True)
        enable_trajectories = st.checkbox("Motion Trails", value=True)

    with st.expander("Analysis Settings", expanded=False):
        st.markdown(
            """<div style="font-size: 0.75rem; line-height: 1.6;">
<b>Zone Alpha:</b> <code>[380, 40]</code> to <code>[620, 320]</code><br>
<b>Threat Severity:</b> Critical Breach<br>
<b>Markov Forecast:</b> T+1.0s
</div>""",
            unsafe_allow_html=True,
        )

    if workspace == "Live Camera":
        st.markdown("<hr style='border-color: rgba(0,0,0,0.08); margin: 10px 0;'>", unsafe_allow_html=True)
        run_live_camera = st.toggle("Live Stream Active", value=True)


# -----------------------------------------------------------------------------
# Cached Model Loader
# -----------------------------------------------------------------------------
@st.cache_resource
def load_pose_detector():
    """Initializes and caches YOLOv8-Pose engine in memory."""
    detector = UnifiedPersonPoseDetector(
        model_path="models/person_detection/yolov8n-pose.pt",
        confidence_threshold=0.35,
    )
    return detector


# =============================================================================
# WORKSPACE 1: LIVE CAMERA
# =============================================================================
if workspace == "Live Camera":
    # Main Header
    st.markdown(
        """<div class="app-header">
<div style="display: flex; align-items: center; gap: 12px;">
<div style="background: linear-gradient(135deg, #0284C7, #38BDF8); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
<circle cx="12" cy="13" r="3"/>
</svg>
</div>
<div>
<h1 class="brand-title" style="margin: 0;">VisionDNA</h1>
<p class="brand-subtitle">Visual Intelligence & Predictive Safety Platform</p>
</div>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); color: #059669; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 20px; font-family: 'JetBrains Mono', monospace;">
● Live Camera
</div>
<div style="background: rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.08); color: #475569; font-size: 0.75rem; font-weight: 500; padding: 4px 10px; border-radius: 20px; font-family: 'JetBrains Mono', monospace;">
Camera 0 Connected
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # Top Metric Row
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        metric_tracked_ph = st.empty()
        metric_tracked_ph.markdown(
            """<div class="metric-card">
<div class="metric-caption">Active Entities</div>
<div class="metric-number">00</div>
<div class="metric-hint">Tracking in Frame</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col_m2:
        metric_risk_ph = st.empty()
        metric_risk_ph.markdown(
            """<div class="metric-card">
<div class="metric-caption">Zone Status</div>
<div class="metric-number" style="color: #059669;">Safe</div>
<div class="metric-hint">Perimeter Nominal</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col_m3:
        metric_activity_ph = st.empty()
        metric_activity_ph.markdown(
            """<div class="metric-card">
<div class="metric-caption">Motion State</div>
<div class="metric-number" style="font-size: 1.12rem;">Stationary</div>
<div class="metric-hint">Real-Time Kinematics</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col_m4:
        metric_fps_ph = st.empty()
        metric_fps_ph.markdown(
            """<div class="metric-card">
<div class="metric-caption">Processing Speed</div>
<div class="metric-number" style="color: #0284C7;">0.0 FPS</div>
<div class="metric-hint">0.0 ms Latency</div>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    alert_placeholder = st.empty()

    # Dual Viewports
    col_cam, col_twin = st.columns([1, 1])
    with col_cam:
        st.markdown(
            """<div class="viewport-card-header">
<span>Live Perception</span>
<span class="viewport-tag">Camera Feed</span>
</div>""",
            unsafe_allow_html=True,
        )
        cam_placeholder = st.empty()

    with col_twin:
        st.markdown(
            """<div class="viewport-card-header">
<span>Digital Twin</span>
<span class="viewport-tag">Spatial Replica</span>
</div>""",
            unsafe_allow_html=True,
        )
        twin_placeholder = st.empty()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Analysis Tabs
    tab_status, tab_traj, tab_log = st.tabs([
        "Entity Status",
        "Trajectory & Next-State Forecast",
        "Incident & Safety Log",
    ])

    with tab_status:
        table_placeholder = st.empty()
    with tab_traj:
        pred_placeholder = st.empty()
    with tab_log:
        incidents_placeholder = st.empty()

    if not run_live_camera:
        alert_placeholder.markdown(
            """<div class="alert-normal">
<b>Camera Standby:</b> Live video stream is paused. Toggle 'Live Stream Active' in the sidebar to resume.
</div>""",
            unsafe_allow_html=True,
        )
        st.stop()

    detector = load_pose_detector()
    detector.confidence_threshold = conf_thresh
    tracker = PersonTracker(history_len=25, jitter_deadzone_px=2.0)
    activity_classifier = ActivityClassifier(smoothing_window=5)
    digital_twin = DigitalTwinEngine()
    predictor = ActivityPredictor()
    risk_engine = RiskEngine()

    stream = VideoStream(source=int(camera_idx), width=target_w, height=target_h, use_directshow=use_dshow)

    if not stream.is_opened:
        alert_placeholder.markdown(
            f"""<div class="alert-critical">
<b>Camera Unavailable:</b> Unable to open hardware camera at device index <code>{camera_idx}</code>. Please allow camera permissions or switch to <b>Video Intelligence</b> workspace.
</div>""",
            unsafe_allow_html=True,
        )
        st.stop()

    prev_time = time.time()
    fps = 0.0
    incident_logs = []

    try:
        while run_live_camera:
            ret, frame = stream.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            h, w, _ = frame.shape

            detections = []
            if enable_detection:
                detections = detector.detect_and_estimate(frame, inference_size=img_size)

            tracks = []
            if enable_tracking and enable_detection:
                tracks = tracker.update(detections)

            annotated_frame = frame.copy()
            if enable_danger_zone:
                annotated_frame = risk_engine.draw_zones(annotated_frame)

            if enable_skeleton:
                for p in tracks:
                    if p.pose and p.pose.is_valid:
                        annotated_frame = detector.draw_skeleton(annotated_frame, p.pose)

            if enable_trajectories:
                annotated_frame = tracker.draw_tracks(annotated_frame, tracks)

            status_rows = []
            highest_risk_level = "LOW"
            highest_risk_score = 0.0
            primary_alert = None
            dominant_motion_state = "No Detected Subject"
            prediction_summary = None
            active_pose_res = None

            for person in tracks:
                pose_res = person.pose
                if pose_res and pose_res.is_valid:
                    active_pose_res = pose_res

                act_res = activity_classifier.classify(pose_res, person, frame_height=h)
                motion_state_val = getattr(act_res, "motion_state", act_res.activity)
                dominant_motion_state = motion_state_val

                pred_res = predictor.predict(
                    person.track_id,
                    act_res.activity,
                    person.velocity,
                    person.center,
                    danger_zones=risk_engine.danger_zones if enable_danger_zone else None,
                )
                prediction_summary = pred_res

                risk_res = risk_engine.assess(person, tracks, act_res, pred_res)

                if risk_res.risk_score > highest_risk_score:
                    highest_risk_score = risk_res.risk_score
                    highest_risk_level = risk_res.risk_level
                    if len(risk_res.all_reasons) > 0:
                        primary_alert = f"Subject #{person.track_id:02d}: {risk_res.all_reasons[0]}"

                current_timecode = datetime.datetime.now().strftime("%H:%M:%S")
                if risk_res.in_danger_zone:
                    log_msg = f"Person #{person.track_id:02d} entered Restricted Zone Alpha"
                    if not any(e["Event"] == log_msg for e in incident_logs[-6:]):
                        incident_logs.append({
                            "Timestamp": current_timecode,
                            "Severity": "Critical",
                            "Entity": f"P{person.track_id:02d}",
                            "Event": log_msg,
                            "Confidence": f"{int(person.confidence*100)}%",
                        })
                elif risk_res.approaching_danger_zone:
                    log_msg = f"Person #{person.track_id:02d} approaching Restricted Zone Alpha"
                    if not any(e["Event"] == log_msg for e in incident_logs[-6:]):
                        incident_logs.append({
                            "Timestamp": current_timecode,
                            "Severity": "Warning",
                            "Entity": f"P{person.track_id:02d}",
                            "Event": log_msg,
                            "Confidence": f"{int(person.confidence*100)}%",
                        })

                digital_twin.update_twin(
                    person=person,
                    activity_res=act_res,
                    pose_res=pose_res,
                    risk_score=risk_res.risk_score,
                    risk_level=risk_res.risk_level,
                    risk_reasons=risk_res.all_reasons,
                    predicted_activity=pred_res.predicted_next_activity,
                    prediction_conf=pred_res.probability,
                )

                zone_label = "Restricted" if risk_res.in_danger_zone else "Safe"
                status_label = "Alert" if risk_res.in_danger_zone else "Normal"

                status_rows.append({
                    "ID": f"P{person.track_id:02d}",
                    "Object": "Person",
                    "Confidence": f"{int(person.confidence*100)}%",
                    "Zone": zone_label,
                    "Direction": person.direction,
                    "Speed": f"{person.velocity:.1f} m/s",
                    "Motion State": motion_state_val,
                    "Status": status_label,
                })

            digital_twin.cleanup_twins([p.track_id for p in tracks])

            curr_time = time.time()
            dt = curr_time - prev_time
            if dt > 0:
                fps = 0.85 * fps + 0.15 * (1.0 / dt) if fps > 0 else (1.0 / dt)
            prev_time = curr_time

            # Update Metric Cards
            metric_tracked_ph.markdown(
                f"""<div class="metric-card">
<div class="metric-caption">Active Entities</div>
<div class="metric-number">{len(tracks):02d}</div>
<div class="metric-hint">Tracking in Frame</div>
</div>""",
                unsafe_allow_html=True,
            )

            risk_color = "#DC2626" if highest_risk_level == "HIGH" else ("#D97706" if highest_risk_level == "MEDIUM" else "#059669")
            zone_text = "Alert (Breach)" if highest_risk_level == "HIGH" else ("Warning" if highest_risk_level == "MEDIUM" else "Safe")
            metric_risk_ph.markdown(
                f"""<div class="metric-card">
<div class="metric-caption">Zone Status</div>
<div class="metric-number" style="color: {risk_color};">{zone_text}</div>
<div class="metric-hint">Risk Score: {highest_risk_score:.0f} / 100</div>
</div>""",
                unsafe_allow_html=True,
            )

            metric_activity_ph.markdown(
                f"""<div class="metric-card">
<div class="metric-caption">Motion State</div>
<div class="metric-number" style="font-size: 1.12rem;">{dominant_motion_state[:20]}</div>
<div class="metric-hint">Real-Time Kinematics</div>
</div>""",
                unsafe_allow_html=True,
            )

            metric_fps_ph.markdown(
                f"""<div class="metric-card">
<div class="metric-caption">Processing Speed</div>
<div class="metric-number" style="color: #0284C7;">{fps:.1f} FPS</div>
<div class="metric-hint">{1000.0/max(1.0, fps):.1f} ms Latency</div>
</div>""",
                unsafe_allow_html=True,
            )

            # Update Alert Banners
            if highest_risk_level == "HIGH":
                alert_placeholder.markdown(
                    f"""<div class="alert-critical">
<b>Restricted Zone Alert:</b> {primary_alert or 'Critical safety breach detected in monitored area.'}
</div>""",
                    unsafe_allow_html=True,
                )
            elif highest_risk_level == "MEDIUM":
                alert_placeholder.markdown(
                    f"""<div class="alert-warning">
<b>Safety Warning:</b> {primary_alert or 'Subject approaching restricted zone boundary.'}
</div>""",
                    unsafe_allow_html=True,
                )
            else:
                alert_placeholder.markdown(
                    """<div class="alert-normal">
<b>Room Status: Secure</b> — All detected individuals are within safe boundaries.
</div>""",
                    unsafe_allow_html=True,
                )

            # Render Viewports
            annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            cam_placeholder.image(annotated_rgb, use_container_width=True)

            twin_canvas = digital_twin.render_canvas(
                width=640,
                height=480,
                pose_res=active_pose_res,
                theme_colors=cv_theme,
                danger_zones=risk_engine.danger_zones if enable_danger_zone else None,
            )
            twin_rgb = cv2.cvtColor(twin_canvas, cv2.COLOR_BGR2RGB)
            twin_placeholder.image(twin_rgb, use_container_width=True)

            # Status Table
            if len(status_rows) > 0:
                df = pd.DataFrame(status_rows)
                table_placeholder.dataframe(df, use_container_width=True, hide_index=True)
            else:
                table_placeholder.info("No individuals currently visible in camera field of view.")

            # Prediction Panel
            if prediction_summary and prediction_summary.is_sufficient_data:
                pred_prob_pct = int(prediction_summary.probability * 100)
                pred_zone = "Restricted Zone" if prediction_summary.trajectory_trend == "Approaching Restricted Zone" else "Safe"
                pred_zone_color = "#DC2626" if pred_zone == "Restricted Zone" else "#0284C7"
                
                pred_html = f"""<div class="forecast-box">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<span style="color: #64748B; font-size: 0.80rem; font-weight: 600;">Next-State Forecast</span>
<span style="background: rgba(2, 132, 199, 0.10); color: #0284C7; font-size: 0.72rem; padding: 2px 8px; border-radius: 4px;">Markov Model</span>
</div>
<h3 style="margin: 0 0 10px 0; color: {'#0F172A' if is_light else '#F8FAFC'}; font-size: 1.05rem;">Subject #{prediction_summary.current_activity}</h3>
<div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 8px;">
<div>Current State: <b style="color: #059669;">{prediction_summary.current_activity}</b></div>
<div>Predicted Zone: <b style="color: {pred_zone_color};">{pred_zone}</b></div>
<div>Probability: <b style="color: #0284C7;">{pred_prob_pct}%</b></div>
</div>
<div style="background: rgba(0,0,0,0.06); border-radius: 4px; height: 6px; width: 100%; overflow: hidden; margin-bottom: 8px;">
<div style="background: #0284C7; width: {pred_prob_pct}%; height: 100%;"></div>
</div>
<div style="font-size: 0.78rem; color: #64748B;">
Trajectory Trend: <span style="color: {'#0F172A' if is_light else '#F8FAFC'}; font-weight: 600;">{prediction_summary.trajectory_trend}</span> | Coordinate: <code>X:{prediction_summary.predicted_future_position[0]}, Y:{prediction_summary.predicted_future_position[1]}</code>
</div>
</div>"""
                pred_placeholder.markdown(pred_html, unsafe_allow_html=True)
            else:
                pred_placeholder.info("Tracking person positions to compute predictive trajectory vectors.")

            # Incident Log
            if len(incident_logs) > 0:
                inc_df = pd.DataFrame(incident_logs[::-1])
                incidents_placeholder.dataframe(inc_df, use_container_width=True, hide_index=True)
            else:
                incidents_placeholder.success("Session active — no safety incidents detected.")

    finally:
        stream.release()


# =============================================================================
# WORKSPACE 2: VIDEO INTELLIGENCE
# =============================================================================
elif workspace == "Video Intelligence":
    # Main Header
    st.markdown(
        """<div class="app-header">
<div style="display: flex; align-items: center; gap: 12px;">
<div style="background: linear-gradient(135deg, #0284C7, #38BDF8); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
<circle cx="12" cy="13" r="3"/>
</svg>
</div>
<div>
<h1 class="brand-title" style="margin: 0;">VisionDNA</h1>
<p class="brand-subtitle">Visual Intelligence & Predictive Safety Platform</p>
</div>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); color: #059669; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 20px; font-family: 'JetBrains Mono', monospace;">
● Video Intelligence
</div>
<div style="background: rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.08); color: #475569; font-size: 0.75rem; font-weight: 500; padding: 4px 10px; border-radius: 20px; font-family: 'JetBrains Mono', monospace;">
File Analyzer
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    uploaded_video_path = None
    if 'uploaded_file' in locals() and uploaded_file is not None:
        temp_dir = os.path.join(tempfile.gettempdir(), "visiondna_videos")
        os.makedirs(temp_dir, exist_ok=True)
        saved_path = os.path.join(temp_dir, uploaded_file.name)
        with open(saved_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        uploaded_video_path = saved_path

    # Top Metric Row
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        metric_tracked_ph = st.empty()
        metric_tracked_ph.markdown(
            """<div class="metric-card">
<div class="metric-caption">Active Entities</div>
<div class="metric-number">00</div>
<div class="metric-hint">Detected in Video</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col_m2:
        metric_risk_ph = st.empty()
        metric_risk_ph.markdown(
            """<div class="metric-card">
<div class="metric-caption">Zone Status</div>
<div class="metric-number" style="color: #059669;">Safe</div>
<div class="metric-hint">Perimeter Nominal</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col_m3:
        metric_activity_ph = st.empty()
        metric_activity_ph.markdown(
            """<div class="metric-card">
<div class="metric-caption">Motion State</div>
<div class="metric-number" style="font-size: 1.12rem;">Stationary</div>
<div class="metric-hint">Video Kinematics</div>
</div>""",
            unsafe_allow_html=True,
        )

    with col_m4:
        metric_fps_ph = st.empty()
        metric_fps_ph.markdown(
            """<div class="metric-card">
<div class="metric-caption">Processing Speed</div>
<div class="metric-number" style="color: #0284C7;">0.0 FPS</div>
<div class="metric-hint">0.0 ms Latency</div>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    alert_placeholder = st.empty()

    if uploaded_video_path is None or not os.path.exists(uploaded_video_path):
        alert_placeholder.markdown(
            """<div class="alert-warning">
<b>Select Video File:</b> Please click <b>'Choose Video File'</b> in the left sidebar to analyze a recorded video (e.g. <code>students.mp4</code>).
</div>""",
            unsafe_allow_html=True,
        )
        st.stop()

    # Dual Viewports
    col_cam, col_twin = st.columns([1, 1])
    with col_cam:
        st.markdown(
            f"""<div class="viewport-card-header">
<span>Live Perception ({uploaded_file.name})</span>
<span class="viewport-tag">Frame-by-Frame</span>
</div>""",
            unsafe_allow_html=True,
        )
        cam_placeholder = st.empty()

    with col_twin:
        st.markdown(
            """<div class="viewport-card-header">
<span>Digital Twin</span>
<span class="viewport-tag">Spatial Replica</span>
</div>""",
            unsafe_allow_html=True,
        )
        twin_placeholder = st.empty()

    # Video Control Bar
    col_c1, col_c2, col_c3 = st.columns([1, 1, 3])
    with col_c1:
        play_btn = st.button("Play Video", use_container_width=True)
    with col_c2:
        restart_btn = st.button("Restart (Frame 0)", use_container_width=True)
    with col_c3:
        seek_slider_ph = st.empty()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Analysis Tabs
    tab_status, tab_traj, tab_log = st.tabs([
        "Entity Status",
        "Trajectory & Next-State Forecast",
        "Incident & Safety Log",
    ])

    with tab_status:
        table_placeholder = st.empty()
    with tab_traj:
        pred_placeholder = st.empty()
    with tab_log:
        incidents_placeholder = st.empty()

    detector = load_pose_detector()
    detector.confidence_threshold = conf_thresh
    tracker = PersonTracker(history_len=25, jitter_deadzone_px=2.0)
    activity_classifier = ActivityClassifier(smoothing_window=5)
    digital_twin = DigitalTwinEngine()
    predictor = ActivityPredictor()
    risk_engine = RiskEngine()

    stream = VideoStream(source=uploaded_video_path, width=640, height=480)

    if restart_btn:
        stream.seek_frame(0)

    prev_time = time.time()
    fps = 0.0
    incident_logs = []
    processed_count = 0

    try:
        while True:
            ret, frame = stream.read()
            if not ret or frame is None:
                stream.seek_frame(0)
                time.sleep(0.02)
                continue

            processed_count += 1
            if 'frame_stride' in locals() and frame_stride > 1 and (processed_count % frame_stride != 0):
                continue

            h, w, _ = frame.shape

            detections = []
            if enable_detection:
                detections = detector.detect_and_estimate(frame, inference_size=img_size)

            tracks = []
            if enable_tracking and enable_detection:
                tracks = tracker.update(detections)

            annotated_frame = frame.copy()
            if enable_danger_zone:
                annotated_frame = risk_engine.draw_zones(annotated_frame)

            if enable_skeleton:
                for p in tracks:
                    if p.pose and p.pose.is_valid:
                        annotated_frame = detector.draw_skeleton(annotated_frame, p.pose)

            if enable_trajectories:
                annotated_frame = tracker.draw_tracks(annotated_frame, tracks)

            status_rows = []
            highest_risk_level = "LOW"
            highest_risk_score = 0.0
            primary_alert = None
            dominant_motion_state = "No Detected Subject"
            prediction_summary = None
            active_pose_res = None

            for person in tracks:
                pose_res = person.pose
                if pose_res and pose_res.is_valid:
                    active_pose_res = pose_res

                act_res = activity_classifier.classify(pose_res, person, frame_height=h)
                motion_state_val = getattr(act_res, "motion_state", act_res.activity)
                dominant_motion_state = motion_state_val

                pred_res = predictor.predict(
                    person.track_id,
                    act_res.activity,
                    person.velocity,
                    person.center,
                    danger_zones=risk_engine.danger_zones if enable_danger_zone else None,
                )
                prediction_summary = pred_res

                risk_res = risk_engine.assess(person, tracks, act_res, pred_res)

                if risk_res.risk_score > highest_risk_score:
                    highest_risk_score = risk_res.risk_score
                    highest_risk_level = risk_res.risk_level
                    if len(risk_res.all_reasons) > 0:
                        primary_alert = f"Subject #{person.track_id:02d}: {risk_res.all_reasons[0]}"

                current_timecode = stream.get_current_time_str()
                if risk_res.in_danger_zone:
                    log_msg = f"Person #{person.track_id:02d} entered Restricted Zone Alpha"
                    if not any(e["Event"] == log_msg for e in incident_logs[-6:]):
                        incident_logs.append({
                            "Timestamp": current_timecode,
                            "Severity": "Critical",
                            "Entity": f"P{person.track_id:02d}",
                            "Event": log_msg,
                            "Confidence": f"{int(person.confidence*100)}%",
                        })
                elif risk_res.approaching_danger_zone:
                    log_msg = f"Person #{person.track_id:02d} approaching Restricted Zone Alpha"
                    if not any(e["Event"] == log_msg for e in incident_logs[-6:]):
                        incident_logs.append({
                            "Timestamp": current_timecode,
                            "Severity": "Warning",
                            "Entity": f"P{person.track_id:02d}",
                            "Event": log_msg,
                            "Confidence": f"{int(person.confidence*100)}%",
                        })

                digital_twin.update_twin(
                    person=person,
                    activity_res=act_res,
                    pose_res=pose_res,
                    risk_score=risk_res.risk_score,
                    risk_level=risk_res.risk_level,
                    risk_reasons=risk_res.all_reasons,
                    predicted_activity=pred_res.predicted_next_activity,
                    prediction_conf=pred_res.probability,
                )

                zone_label = "Restricted" if risk_res.in_danger_zone else "Safe"
                status_label = "Alert" if risk_res.in_danger_zone else "Normal"

                status_rows.append({
                    "ID": f"P{person.track_id:02d}",
                    "Object": "Person",
                    "Confidence": f"{int(person.confidence*100)}%",
                    "Zone": zone_label,
                    "Direction": person.direction,
                    "Speed": f"{person.velocity:.1f} m/s",
                    "Motion State": motion_state_val,
                    "Status": status_label,
                })

            digital_twin.cleanup_twins([p.track_id for p in tracks])

            curr_time = time.time()
            dt = curr_time - prev_time
            if dt > 0:
                fps = 0.85 * fps + 0.15 * (1.0 / dt) if fps > 0 else (1.0 / dt)
            prev_time = curr_time

            # Update Metrics
            metric_tracked_ph.markdown(
                f"""<div class="metric-card">
<div class="metric-caption">Active Entities</div>
<div class="metric-number">{len(tracks):02d}</div>
<div class="metric-hint">Detected in Video</div>
</div>""",
                unsafe_allow_html=True,
            )

            risk_color = "#DC2626" if highest_risk_level == "HIGH" else ("#D97706" if highest_risk_level == "MEDIUM" else "#059669")
            zone_text = "Alert (Breach)" if highest_risk_level == "HIGH" else ("Warning" if highest_risk_level == "MEDIUM" else "Safe")
            metric_risk_ph.markdown(
                f"""<div class="metric-card">
<div class="metric-caption">Zone Status</div>
<div class="metric-number" style="color: {risk_color};">{zone_text}</div>
<div class="metric-hint">Risk Score: {highest_risk_score:.0f} / 100</div>
</div>""",
                unsafe_allow_html=True,
            )

            metric_activity_ph.markdown(
                f"""<div class="metric-card">
<div class="metric-caption">Motion State</div>
<div class="metric-number" style="font-size: 1.12rem;">{dominant_motion_state[:20]}</div>
<div class="metric-hint">Video Kinematics</div>
</div>""",
                unsafe_allow_html=True,
            )

            metric_fps_ph.markdown(
                f"""<div class="metric-card">
<div class="metric-caption">Processing Speed</div>
<div class="metric-number" style="color: #0284C7;">{fps:.1f} FPS</div>
<div class="metric-hint">{1000.0/max(1.0, fps):.1f} ms Latency</div>
</div>""",
                unsafe_allow_html=True,
            )

            # Update Alert Banners
            if highest_risk_level == "HIGH":
                alert_placeholder.markdown(
                    f"""<div class="alert-critical">
<b>Restricted Zone Alert:</b> {primary_alert or 'Critical safety breach detected in monitored area.'}
</div>""",
                    unsafe_allow_html=True,
                )
            elif highest_risk_level == "MEDIUM":
                alert_placeholder.markdown(
                    f"""<div class="alert-warning">
<b>Safety Warning:</b> {primary_alert or 'Subject approaching restricted zone boundary.'}
</div>""",
                    unsafe_allow_html=True,
                )
            else:
                alert_placeholder.markdown(
                    f"""<div class="alert-normal">
<b>Room Status: Secure</b> — All detected individuals are within safe boundaries. Time: {stream.get_current_time_str()}
</div>""",
                    unsafe_allow_html=True,
                )

            # Render Viewports
            annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            cam_placeholder.image(annotated_rgb, use_container_width=True)

            twin_canvas = digital_twin.render_canvas(
                width=640,
                height=480,
                pose_res=active_pose_res,
                theme_colors=cv_theme,
                danger_zones=risk_engine.danger_zones if enable_danger_zone else None,
            )
            twin_rgb = cv2.cvtColor(twin_canvas, cv2.COLOR_BGR2RGB)
            twin_placeholder.image(twin_rgb, use_container_width=True)

            seek_slider_ph.markdown(
                f"""<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.80rem; color: #64748B; text-align: right; padding-top: 8px;">
Timeline: <b style="color: {'#0F172A' if is_light else '#F8FAFC'};">{stream.get_current_time_str()}</b> ({stream.get_current_frame_idx()}/{stream.total_frames} frames)
</div>""",
                unsafe_allow_html=True,
            )

            # Status Table
            if len(status_rows) > 0:
                df = pd.DataFrame(status_rows)
                table_placeholder.dataframe(df, use_container_width=True, hide_index=True)
            else:
                table_placeholder.info("No entities currently detected in the active video frame.")

            # Prediction Panel
            if prediction_summary and prediction_summary.is_sufficient_data:
                pred_prob_pct = int(prediction_summary.probability * 100)
                pred_zone = "Restricted Zone" if prediction_summary.trajectory_trend == "Approaching Restricted Zone" else "Safe"
                pred_zone_color = "#DC2626" if pred_zone == "Restricted Zone" else "#0284C7"
                
                pred_html = f"""<div class="forecast-box">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<span style="color: #64748B; font-size: 0.80rem; font-weight: 600;">Next-State Forecast</span>
<span style="background: rgba(2, 132, 199, 0.10); color: #0284C7; font-size: 0.72rem; padding: 2px 8px; border-radius: 4px;">Markov Model</span>
</div>
<h3 style="margin: 0 0 10px 0; color: {'#0F172A' if is_light else '#F8FAFC'}; font-size: 1.05rem;">Subject #{prediction_summary.current_activity}</h3>
<div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 8px;">
<div>Current State: <b style="color: #059669;">{prediction_summary.current_activity}</b></div>
<div>Predicted Zone: <b style="color: {pred_zone_color};">{pred_zone}</b></div>
<div>Probability: <b style="color: #0284C7;">{pred_prob_pct}%</b></div>
</div>
<div style="background: rgba(0,0,0,0.06); border-radius: 4px; height: 6px; width: 100%; overflow: hidden; margin-bottom: 8px;">
<div style="background: #0284C7; width: {pred_prob_pct}%; height: 100%;"></div>
</div>
<div style="font-size: 0.78rem; color: #64748B;">
Trajectory Trend: <span style="color: {'#0F172A' if is_light else '#F8FAFC'}; font-weight: 600;">{prediction_summary.trajectory_trend}</span> | Coordinate: <code>X:{prediction_summary.predicted_future_position[0]}, Y:{prediction_summary.predicted_future_position[1]}</code>
</div>
</div>"""
                pred_placeholder.markdown(pred_html, unsafe_allow_html=True)
            else:
                pred_placeholder.info("Tracking person positions to compute predictive trajectory vectors.")

            # Incident Log
            if len(incident_logs) > 0:
                inc_df = pd.DataFrame(incident_logs[::-1])
                incidents_placeholder.dataframe(inc_df, use_container_width=True, hide_index=True)
            else:
                incidents_placeholder.success(f"Session active — no safety incidents detected as of {stream.get_current_time_str()}.")

    finally:
        stream.release()


# =============================================================================
# WORKSPACE 3: SCENARIO SIMULATOR (CONTROLLED TEST ENVIRONMENT)
# =============================================================================
else:
    st.markdown(
        """<div class="app-header">
<div style="display: flex; align-items: center; gap: 12px;">
<div style="background: linear-gradient(135deg, #0284C7, #38BDF8); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
<circle cx="12" cy="13" r="3"/>
</svg>
</div>
<div>
<h1 class="brand-title" style="margin: 0;">VisionDNA</h1>
<p class="brand-subtitle">Visual Intelligence & Predictive Safety Platform</p>
</div>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<div style="background: rgba(148, 163, 184, 0.12); border: 1px solid rgba(148, 163, 184, 0.30); color: #475569; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 20px; font-family: 'JetBrains Mono', monospace;">
● Scenario Simulator
</div>
<div style="background: rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.08); color: #64748B; font-size: 0.75rem; font-weight: 500; padding: 4px 10px; border-radius: 20px; font-family: 'JetBrains Mono', monospace;">
Controlled Testing Environment
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    stream = VideoStream(source=-1, width=640, height=480)
    col_cam, col_twin = st.columns([1, 1])
    with col_cam:
        st.markdown(
            """<div class="viewport-card-header">
<span>Synthetic Perception Stream</span>
<span class="viewport-tag">Test Bench</span>
</div>""",
            unsafe_allow_html=True,
        )
        cam_placeholder = st.empty()

    with col_twin:
        st.markdown(
            """<div class="viewport-card-header">
<span>Digital Twin</span>
<span class="viewport-tag">Simulated Replica</span>
</div>""",
            unsafe_allow_html=True,
        )
        twin_placeholder = st.empty()

    digital_twin = DigitalTwinEngine()
    ret, frame = stream.read()
    if ret and frame is not None:
        cam_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
        twin_canvas = digital_twin.render_canvas(width=640, height=480, theme_colors=cv_theme)
        twin_placeholder.image(cv2.cvtColor(twin_canvas, cv2.COLOR_BGR2RGB), use_container_width=True)

    st.markdown(
        f"""<div class="alert-normal" style="background: #F0F9FF; border-color: #BAE6FD; color: #0369A1;">
<b>Active Synthetic Scenario:</b> {demo_scenario}. This controlled test sandbox validates incident alarms and digital twin synchronization.
</div>""",
        unsafe_allow_html=True,
    )
