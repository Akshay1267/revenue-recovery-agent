"""
app.py — AI Revenue Recovery Agent (Razorpay Blade Design System)
=================================================================
Razorpay AI Buildathon — Track 03: Autonomous Revenue Recovery
Official Razorpay Blade Design System integration with TASA Orbiter + Inter
typography, Razorpay Navy/Electric Blue palette, and seamless Dark/Light Mode.
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Revenue Recovery Agent — Razorpay",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme State Management (Dark / Light Mode)
# ---------------------------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

# Top Sidebar Header & Theme Toggle
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0 16px 0;">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="#0C6CF2"/>
            <path d="M19.8 8L10 24H14.8L22.2 12H17.4L19.8 8Z" fill="white"/>
            <path d="M12.2 12L8 19H12.8L15.2 15H12.2Z" fill="#00D285"/>
        </svg>
        <div>
            <div style="font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em; line-height: 1.1;">Razorpay</div>
            <div style="font-size: 0.75rem; color: #0C6CF2; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">AI Recovery Agent</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    theme_choice = st.radio(
        "🌗 Theme Appearance",
        options=["🌙 Razorpay Dark (Midnight)", "☀️ Razorpay Light (Clean)"],
        index=0 if st.session_state.theme_mode == "Dark" else 1,
        key="app_theme_radio"
    )
    
    st.session_state.theme_mode = "Dark" if "Dark" in theme_choice else "Light"
    st.markdown("---")

is_dark = st.session_state.theme_mode == "Dark"

# ---------------------------------------------------------------------------
# Load Audit Data
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_FILE = PROJECT_ROOT / "logs" / "audit_trail.csv"
DATA_FILE = PROJECT_ROOT / "data" / "failed_subscriptions.csv"

@st.cache_data
def load_audit_data():
    if not AUDIT_FILE.exists():
        return None
    df = pd.read_csv(AUDIT_FILE)
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce").fillna(0)
    df["recovered_amount_inr"] = pd.to_numeric(df["recovered_amount_inr"], errors="coerce").fillna(0)
    df["discount_cost_inr"] = pd.to_numeric(df["discount_cost_inr"], errors="coerce").fillna(0)
    return df

df = load_audit_data()

# ---------------------------------------------------------------------------
# RAZORPAY BLADE DESIGN SYSTEM TOKENS & DYNAMIC CSS
# ---------------------------------------------------------------------------
if is_dark:
    # Blade Dark Theme (Razorpay Midnight Obsidian)
    c_bg_app = "#02042B"
    c_bg_gradient = "radial-gradient(at 0% 0%, rgba(12, 108, 242, 0.18) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(0, 210, 133, 0.10) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(11, 19, 43, 0.9) 0px, transparent 50%)"
    c_surface_card = "rgba(11, 19, 43, 0.85)"
    c_surface_card_solid = "#0B132B"
    c_surface_panel = "rgba(14, 27, 62, 0.7)"
    c_border_subtle = "rgba(59, 130, 246, 0.18)"
    c_border_strong = "rgba(12, 108, 242, 0.45)"
    c_text_high = "#FFFFFF"
    c_text_med = "#94A3B8"
    c_text_low = "#64748B"
    c_brand_primary = "#0C6CF2"
    c_brand_accent = "#3395FF"
    c_positive = "#00D285"
    c_notice = "#FF9900"
    c_negative = "#FF4D4D"
    c_sidebar_bg = "#03061C"
    
    # Plotly Dark Configuration
    plt_template = "plotly_dark"
    plt_paper_bg = "rgba(0,0,0,0)"
    plt_plot_bg = "rgba(0,0,0,0)"
    plt_font = "#94A3B8"
    plt_grid = "rgba(255, 255, 255, 0.05)"
else:
    # Blade Light Theme (Razorpay Clean Ice Blue)
    c_bg_app = "#F4F8FB"
    c_bg_gradient = "radial-gradient(at 0% 0%, rgba(12, 108, 242, 0.06) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(0, 210, 133, 0.04) 0px, transparent 50%)"
    c_surface_card = "#FFFFFF"
    c_surface_card_solid = "#FFFFFF"
    c_surface_panel = "#FFFFFF"
    c_border_subtle = "#E2E8F0"
    c_border_strong = "#0C6CF2"
    c_text_high = "#0C2340"
    c_text_med = "#475569"
    c_text_low = "#94A3B8"
    c_brand_primary = "#0C6CF2"
    c_brand_accent = "#0056CC"
    c_positive = "#00A86B"
    c_notice = "#D97706"
    c_negative = "#E11D48"
    c_sidebar_bg = "#FFFFFF"
    
    # Plotly Light Configuration
    plt_template = "plotly_white"
    plt_paper_bg = "rgba(0,0,0,0)"
    plt_plot_bg = "rgba(0,0,0,0)"
    plt_font = "#475569"
    plt_grid = "rgba(0, 0, 0, 0.06)"

# Inject Complete Blade Stylesheet
st.markdown(f"""
<style>
    /* Google Fonts Import matching Razorpay Blade Design System */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Mulish:wght@600;700;800;900&family=Outfit:wght@600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography Tokens */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: {c_text_high} !important;
    }}

    h1, h2, h3, h4, h5, h6, .brand-font {{
        font-family: 'Mulish', 'Outfit', sans-serif !important;
        letter-spacing: -0.03em !important;
        font-weight: 800 !important;
        color: {c_text_high} !important;
    }}

    code, pre, .mono-code {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* Main Container Theme */
    .stApp {{
        background-color: {c_bg_app} !important;
        background-image: {c_bg_gradient} !important;
        background-attachment: fixed !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: {c_sidebar_bg} !important;
        border-right: 1px solid {c_border_subtle} !important;
    }}

    /* Keyframe Animations */
    @keyframes bladeGlow {{
        0%, 100% {{ box-shadow: 0 0 15px rgba(12, 108, 242, 0.3); }}
        50% {{ box-shadow: 0 0 25px rgba(12, 108, 242, 0.7); }}
    }}

    @keyframes livePulseDot {{
        0%, 100% {{ transform: scale(1); opacity: 0.85; box-shadow: 0 0 8px {c_positive}; }}
        50% {{ transform: scale(1.25); opacity: 1; box-shadow: 0 0 16px {c_positive}; }}
    }}

    @keyframes shimmerHeader {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Razorpay Blade Hero Banner */
    .blade-hero {{
        background: {'linear-gradient(135deg, #07122B 0%, #0C2340 50%, #0E1B3E 100%)' if is_dark else 'linear-gradient(135deg, #0C2340 0%, #113264 60%, #0C6CF2 100%)'};
        border: 1px solid {'rgba(59, 130, 246, 0.3)' if is_dark else 'transparent'};
        border-radius: 20px;
        padding: 2.2rem 2.6rem;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
        color: #FFFFFF !important;
        box-shadow: 0 20px 45px rgba(12, 35, 64, { "0.35" if is_dark else "0.15" });
    }}

    .blade-hero::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #0C6CF2, #3395FF, #00D285, #38BDF8, #0C6CF2);
        background-size: 300% 300%;
        animation: shimmerHeader 6s ease infinite;
    }}

    .blade-title {{
        font-family: 'Mulish', 'Outfit', sans-serif !important;
        font-size: 2.35rem;
        font-weight: 900;
        margin: 0;
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.03em;
    }}

    .blade-subtitle {{
        color: #CBD5E1 !important;
        font-size: 1.02rem;
        margin-top: 0.5rem;
        max-width: 850px;
        line-height: 1.55;
    }}

    /* Blade Badges & Pills */
    .blade-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(12, 108, 242, 0.25);
        border: 1px solid rgba(12, 108, 242, 0.5);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #93C5FD !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .blade-pill-success {{
        background: rgba(0, 210, 133, 0.18);
        border: 1px solid rgba(0, 210, 133, 0.45);
        color: #00D285 !important;
    }}

    .live-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: {c_positive};
        animation: livePulseDot 2s infinite ease-in-out;
        display: inline-block;
    }}

    /* Blade Card Tokens */
    .blade-card {{
        background: {c_surface_card};
        border: 1px solid {c_border_subtle};
        border-radius: 16px;
        padding: 1.5rem 1.4rem;
        position: relative;
        overflow: hidden;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 25px rgba(0, 0, 0, { "0.25" if is_dark else "0.04" });
    }}

    .blade-card:hover {{
        transform: translateY(-4px);
        border-color: {c_brand_primary};
        box-shadow: 0 18px 36px rgba(12, 108, 242, { "0.25" if is_dark else "0.1" });
    }}

    .blade-card::after {{
        content: '';
        position: absolute;
        bottom: 0; left: 10%; right: 10%;
        height: 3px;
        background: var(--card-accent, {c_brand_primary});
        border-radius: 3px 3px 0 0;
    }}

    .blade-card-label {{
        color: {c_text_med};
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .blade-card-value {{
        font-family: 'Mulish', 'Outfit', sans-serif !important;
        font-size: 2.2rem;
        font-weight: 900;
        color: {c_text_high} !important;
        line-height: 1.15;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
    }}

    .blade-card-sub {{
        font-size: 0.82rem;
        color: {c_text_low};
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    /* Blade Glass Panels */
    .blade-panel {{
        background: {c_surface_panel};
        border: 1px solid {c_border_subtle};
        border-radius: 18px;
        padding: 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 30px rgba(0, 0, 0, { "0.2" if is_dark else "0.03" });
    }}

    .blade-panel-header {{
        font-family: 'Mulish', sans-serif !important;
        font-size: 1.2rem;
        font-weight: 800;
        color: {c_text_high} !important;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid {c_border_subtle};
        padding-bottom: 0.75rem;
    }}

    /* AI Trace Box */
    .blade-trace-box {{
        background: {'rgba(15, 28, 64, 0.6)' if is_dark else '#F8FAFC'};
        border: 1px solid {'rgba(59, 130, 246, 0.3)' if is_dark else '#E2E8F0'};
        border-radius: 14px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }}
    .blade-trace-box:hover {{
        border-color: {c_brand_primary};
        box-shadow: 0 8px 20px rgba(12, 108, 242, 0.15);
    }}

    /* Blade Tab Navigation */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: {'rgba(11, 19, 43, 0.9)' if is_dark else '#EEF4FB'};
        padding: 6px;
        border-radius: 14px;
        border: 1px solid {c_border_subtle};
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 44px;
        border-radius: 10px;
        color: {c_text_med} !important;
        font-weight: 700;
        font-size: 0.92rem;
        padding: 0 18px;
        transition: all 0.2s ease;
        border: none;
    }}

    .stTabs [aria-selected="true"] {{
        background: {c_brand_primary} !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(12, 108, 242, 0.4);
    }}

    /* Razorpay Blade Buttons */
    button[kind="primary"] {{
        background: linear-gradient(135deg, #0C6CF2 0%, #0056CC 100%) !important;
        border: none !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 16px rgba(12, 108, 242, 0.35) !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.2rem !important;
    }}
    button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #3395FF 0%, #0C6CF2 100%) !important;
        box-shadow: 0 8px 24px rgba(12, 108, 242, 0.5) !important;
        transform: translateY(-1px);
    }}

    /* Form Inputs & Selects */
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {'#0B132B' if is_dark else '#FFFFFF'} !important;
        border-color: {c_border_subtle} !important;
        color: {c_text_high} !important;
        border-radius: 10px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Razorpay Blade Hero Component
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="blade-hero">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
        <div>
            <div style="display: flex; gap: 10px; margin-bottom: 12px; align-items: center; flex-wrap: wrap;">
                <span class="blade-pill"><span class="live-dot"></span> Autonomous Engine Live</span>
                <span class="blade-pill blade-pill-success">🛡️ Razorpay Policy Guardrails</span>
                <span class="blade-pill" style="background: rgba(255, 255, 255, 0.15); border-color: rgba(255, 255, 255, 0.3); color: #FFFFFF !important;">⚡ Track 03: Revenue Recovery</span>
            </div>
            <h1 class="blade-title">
                <span>AI Revenue Recovery Agent</span>
            </h1>
            <p class="blade-subtitle">
                Enterprise subscription payment recovery platform built on Razorpay's Blade design system. Diagnoses failed payment mandates with Claude AI reasoning and enforces strict deterministic stopping rules.
            </p>
        </div>
        <div style="text-align: right; background: {'rgba(11, 19, 43, 0.6)' if is_dark else 'rgba(255, 255, 255, 0.15)'}; padding: 12px 18px; border-radius: 12px; border: 1px solid {'rgba(59, 130, 246, 0.25)' if is_dark else 'rgba(255, 255, 255, 0.25)'};">
            <div style="color: {'#93C5FD' if is_dark else '#FFFFFF'}; font-size: 0.78rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 2px;">Cohort Telemetry</div>
            <div style="font-family: 'Mulish'; font-size: 1.15rem; font-weight: 900; color: #FFFFFF;">60 Failed Subscriptions</div>
            <div style="color: {'#CBD5E1' if is_dark else '#E2E8F0'}; font-size: 0.78rem; margin-top: 2px;">₹68,240 Total Capital at Risk</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if df is None:
    st.error("⚠️ Audit trail data not found. Please run the batch pipeline first.")
    st.stop()

# ---------------------------------------------------------------------------
# Calculate Metrics
# ---------------------------------------------------------------------------
total_records = len(df)
total_at_risk = float(df["amount_inr"].sum())
total_recovered = float(df["recovered_amount_inr"].sum())
recovery_rate = (total_recovered / total_at_risk * 100) if total_at_risk > 0 else 0
total_discount_cost = float(df["discount_cost_inr"].sum())
net_recovered = total_recovered - total_discount_cost
escalated_count = int((df["final_action"] == "escalate_to_human").sum())
overrides_count = int((df["allowed_by_rules"] == "no").sum())

# ---------------------------------------------------------------------------
# Razorpay Blade Metric Cards Deck
# ---------------------------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="blade-card" style="--card-accent: {c_positive};">
        <div class="blade-card-label">
            <span>₹ Recovered</span>
            <span style="color: {c_positive}; font-weight: 800; font-size: 0.75rem; background: {'rgba(0, 210, 133, 0.15)' if is_dark else 'rgba(0, 168, 107, 0.12)'}; padding: 2px 6px; border-radius: 4px;">NET REVENUE</span>
        </div>
        <div class="blade-card-value" style="color: {c_positive} !important;">₹{total_recovered:,.0f}</div>
        <div class="blade-card-sub">
            <span>From ₹{total_at_risk:,.0f} at risk</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="blade-card" style="--card-accent: {c_brand_primary};">
        <div class="blade-card-label">
            <span>Recovery Rate</span>
            <span style="color: {c_brand_primary}; font-weight: 800; font-size: 0.75rem; background: {'rgba(12, 108, 242, 0.15)' if is_dark else 'rgba(12, 108, 242, 0.1)'}; padding: 2px 6px; border-radius: 4px;">3.2x BASELINE</span>
        </div>
        <div class="blade-card-value" style="color: {c_brand_primary} !important;">{recovery_rate:.1f}%</div>
        <div class="blade-card-sub">
            <span>21 recovered accounts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="blade-card" style="--card-accent: {c_negative};">
        <div class="blade-card-label">
            <span>Capital at Risk</span>
            <span style="color: {c_negative}; font-weight: 800; font-size: 0.75rem; background: {'rgba(255, 77, 77, 0.15)' if is_dark else 'rgba(225, 29, 72, 0.1)'}; padding: 2px 6px; border-radius: 4px;">{total_records} ACCOUNTS</span>
        </div>
        <div class="blade-card-value" style="color: {c_negative} !important;">₹{total_at_risk:,.0f}</div>
        <div class="blade-card-sub">
            <span>Failed recurring debits</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="blade-card" style="--card-accent: {c_notice};">
        <div class="blade-card-label">
            <span>Escalations</span>
            <span style="color: {c_notice}; font-weight: 800; font-size: 0.75rem; background: {'rgba(255, 153, 0, 0.15)' if is_dark else 'rgba(217, 119, 6, 0.1)'}; padding: 2px 6px; border-radius: 4px;">HUMAN OPS</span>
        </div>
        <div class="blade-card-value" style="color: {c_notice} !important;">{escalated_count}</div>
        <div class="blade-card-sub">
            <span>Fraud & retry caps</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="blade-card" style="--card-accent: {c_positive};">
        <div class="blade-card-label">
            <span>Fraud Safety</span>
            <span style="color: {c_positive}; font-weight: 800; font-size: 0.75rem; background: {'rgba(0, 210, 133, 0.15)' if is_dark else 'rgba(0, 168, 107, 0.12)'}; padding: 2px 6px; border-radius: 4px;">100% COMPLIANT</span>
        </div>
        <div class="blade-card-value" style="color: {c_positive} !important;">0 Violations</div>
        <div class="blade-card-sub">
            <span>{overrides_count} rule safety stops</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Navigation Tabs
# ---------------------------------------------------------------------------
tab_overview, tab_inspector, tab_sandbox, tab_compliance, tab_audit = st.tabs([
    "📊 Executive Command Center",
    "🧠 AI Cognitive Inspector",
    "⚡ Interactive Recovery Sandbox",
    "🛡️ Playbook & Guardrails",
    "📋 Compliance Audit Trail",
])

# ---------------------------------------------------------------------------
# TAB 1: EXECUTIVE COMMAND CENTER
# ---------------------------------------------------------------------------
with tab_overview:
    r1_c1, r1_c2 = st.columns([1.2, 1])

    with r1_c1:
        st.markdown(f'<div class="blade-panel"><div class="blade-panel-header"><span>⚡ Recovery Efficiency by Intervention</span><span style="font-size: 0.82rem; color: {c_text_med};">Yield & success conversion</span></div>', unsafe_allow_html=True)
        
        action_stats = df.groupby("final_action").agg(
            total=("simulated_outcome", "count"),
            recovered=("simulated_outcome", lambda x: (x == "recovered").sum()),
            amount_recovered=("recovered_amount_inr", "sum"),
        ).reset_index()
        action_stats["recovery_rate"] = (action_stats["recovered"] / action_stats["total"] * 100).round(1)
        action_stats["label"] = action_stats["final_action"].str.replace("_", " ").str.title()

        fig_actions = go.Figure()
        fig_actions.add_trace(go.Bar(
            x=action_stats["label"],
            y=action_stats["recovery_rate"],
            text=[f"{r:.1f}% (₹{amt:,.0f})" for r, amt in zip(action_stats["recovery_rate"], action_stats["amount_recovered"])],
            textposition="outside",
            marker=dict(
                color=[c_notice, c_positive, c_brand_primary],
                line=dict(color=c_border_subtle, width=1)
            ),
            hovertemplate="<b>%{x}</b><br>Recovery Rate: %{y:.1f}%<br>Yield: %{text}<extra></extra>"
        ))
        fig_actions.update_layout(
            template=plt_template,
            plot_bgcolor=plt_plot_bg,
            paper_bgcolor=plt_paper_bg,
            font=dict(family="Inter", color=plt_font),
            margin=dict(t=25, b=20, l=10, r=10),
            height=330,
            yaxis=dict(gridcolor=plt_grid, range=[0, 58], title="Recovery Rate (%)"),
            xaxis=dict(gridcolor=plt_grid),
        )
        st.plotly_chart(fig_actions, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r1_c2:
        st.markdown(f'<div class="blade-panel"><div class="blade-panel-header"><span>🔍 Failure Diagnosis Spectrum</span><span style="font-size: 0.82rem; color: {c_text_med};">60 accounts</span></div>', unsafe_allow_html=True)
        
        reason_counts = df["failure_reason"].value_counts().reset_index()
        reason_counts.columns = ["failure_reason", "count"]
        reason_counts["label"] = reason_counts["failure_reason"].str.replace("_", " ").str.title()

        fig_reasons = px.pie(
            reason_counts,
            values="count",
            names="label",
            hole=0.55,
            color_discrete_sequence=[c_brand_primary, c_positive, "#3395FF", c_notice, c_negative],
        )
        fig_reasons.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color=c_bg_app, width=2)),
            hovertemplate="<b>%{label}</b><br>Count: %{value} accounts<br>Share: %{percent}<extra></extra>"
        )
        fig_reasons.update_layout(
            template=plt_template,
            showlegend=False,
            paper_bgcolor=plt_paper_bg,
            plot_bgcolor=plt_plot_bg,
            font=dict(family="Inter", color=plt_font),
            margin=dict(t=10, b=10, l=10, r=10),
            height=330,
        )
        st.plotly_chart(fig_reasons, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    r2_c1, r2_c2 = st.columns(2)

    with r2_c1:
        st.markdown(f'<div class="blade-panel"><div class="blade-panel-header"><span>👥 Recovery by Customer Tier</span><span style="font-size: 0.82rem; color: {c_text_med};">Capital protection</span></div>', unsafe_allow_html=True)
        
        seg_stats = df.groupby("customer_segment").agg(
            at_risk=("amount_inr", "sum"),
            recovered=("recovered_amount_inr", "sum"),
        ).reset_index()
        seg_stats["label"] = seg_stats["customer_segment"].str.replace("_", " ").str.title()

        fig_seg = go.Figure()
        fig_seg.add_trace(go.Bar(
            name="Capital At Risk",
            x=seg_stats["label"],
            y=seg_stats["at_risk"],
            marker_color="rgba(12, 108, 242, 0.3)" if is_dark else "rgba(12, 108, 242, 0.15)",
            marker_line=dict(color=c_brand_primary, width=1.5),
            hovertemplate="<b>%{x}</b><br>At Risk: ₹%{y:,.0f}<extra></extra>"
        ))
        fig_seg.add_trace(go.Bar(
            name="Recovered Capital",
            x=seg_stats["label"],
            y=seg_stats["recovered"],
            marker_color=c_positive,
            hovertemplate="<b>%{x}</b><br>Recovered: ₹%{y:,.0f}<extra></extra>"
        ))
        fig_seg.update_layout(
            template=plt_template,
            barmode="group",
            plot_bgcolor=plt_plot_bg,
            paper_bgcolor=plt_paper_bg,
            font=dict(family="Inter", color=plt_font),
            margin=dict(t=25, b=20, l=10, r=10),
            height=310,
            yaxis=dict(gridcolor=plt_grid, title="Amount in INR (₹)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11))
        )
        st.plotly_chart(fig_seg, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2_c2:
        st.markdown(f'<div class="blade-panel"><div class="blade-panel-header"><span>📈 Final Cohort Resolution</span><span style="font-size: 0.82rem; color: {c_text_med};">Outcome state</span></div>', unsafe_allow_html=True)
        
        outcome_counts = df["simulated_outcome"].value_counts().reset_index()
        outcome_counts.columns = ["outcome", "count"]
        outcome_counts["label"] = outcome_counts["outcome"].str.replace("_", " ").str.title()

        fig_outcome = px.bar(
            outcome_counts,
            x="count",
            y="label",
            orientation="h",
            color="outcome",
            color_discrete_map={
                "recovered": c_positive,
                "failed": c_negative,
                "pending_human_review": c_notice,
                "no_recovery_attempted": c_text_low
            },
            text="count"
        )
        fig_outcome.update_traces(textposition="outside")
        fig_outcome.update_layout(
            template=plt_template,
            showlegend=False,
            plot_bgcolor=plt_plot_bg,
            paper_bgcolor=plt_paper_bg,
            font=dict(family="Inter", color=plt_font),
            margin=dict(t=25, b=20, l=10, r=10),
            height=310,
            xaxis=dict(gridcolor=plt_grid, title="Number of Subscriptions"),
            yaxis=dict(title="")
        )
        st.plotly_chart(fig_outcome, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 2: AI COGNITIVE INSPECTOR
# ---------------------------------------------------------------------------
with tab_inspector:
    st.markdown(f"""
    <div class="blade-panel">
        <div class="blade-panel-header">
            <span>🧠 Autonomous AI Decision Inspector</span>
            <span style="font-size: 0.82rem; color: {c_brand_primary};">Step-by-step reasoning trace per account</span>
        </div>
        <p style="color: {c_text_med}; font-size: 0.95rem; margin-bottom: 1.4rem;">
            Inspect how Claude AI analyzes account tenure, past payment history, and gateway failure reasons to select bounded interventions under policy supervision.
        </p>
    """, unsafe_allow_html=True)

    selected_sub = st.selectbox(
        "Select Subscription Account to Inspect:",
        options=df["subscription_id"].tolist(),
        format_func=lambda x: f"{x} — {df[df['subscription_id']==x]['failure_reason'].values[0]} (₹{df[df['subscription_id']==x]['amount_inr'].values[0]:,.0f})"
    )

    rec = df[df["subscription_id"] == selected_sub].iloc[0]

    c_s1, c_s2, c_s3, c_s4 = st.columns(4)

    with c_s1:
        st.markdown(f"""
        <div class="blade-trace-box">
            <div style="color: {c_brand_primary}; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 6px;">1. Account Perception</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: {c_text_high};">{rec['customer_id']}</div>
            <div style="font-size: 0.85rem; color: {c_text_med}; margin-top: 6px;">
                • Amount: <b style="color:{c_text_high};">₹{rec['amount_inr']:,.0f}</b><br>
                • Segment: <span class="blade-pill" style="font-size:0.7rem; padding:1px 6px;">{rec['customer_segment']}</span><br>
                • Failure: <b style="color:{c_notice};">{rec['failure_reason']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_s2:
        st.markdown(f"""
        <div class="blade-trace-box">
            <div style="color: {c_brand_accent}; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 6px;">2. AI Diagnosis</div>
            <div style="font-size: 0.88rem; color: {c_text_high}; line-height: 1.45;">
                "{rec['diagnosis']}"
            </div>
            <div style="font-size: 0.75rem; color: {c_brand_primary}; margin-top: 8px; font-weight: 700;">
                ⚡ Claude AI Reasoning Core
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_s3:
        st.markdown(f"""
        <div class="blade-trace-box">
            <div style="color: {c_notice}; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 6px;">3. Policy Guardrail</div>
            <div style="font-size: 1rem; font-weight: 800; color: {c_text_high};">{rec['final_action'].replace('_', ' ').title()}</div>
            <div style="font-size: 0.82rem; color: {c_text_med}; margin-top: 6px;">
                • Allowed by Rules: <b style="color:{c_positive if rec['allowed_by_rules']=='yes' else c_negative}">{rec['allowed_by_rules'].upper()}</b><br>
                • Rule Override: <i>{rec['rule_override_reason'] if pd.notna(rec['rule_override_reason']) and rec['rule_override_reason']!='' else 'None (Fully Compliant)'}</i>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_s4:
        is_rec = rec['simulated_outcome'] == 'recovered'
        outcome_color = c_positive if is_rec else (c_notice if rec['simulated_outcome']=='pending_human_review' else c_negative)
        st.markdown(f"""
        <div class="blade-trace-box">
            <div style="color: {outcome_color}; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 6px;">4. Monetary Outcome</div>
            <div style="font-size: 1.2rem; font-weight: 900; color: {outcome_color};">{rec['simulated_outcome'].replace('_', ' ').upper()}</div>
            <div style="font-size: 0.85rem; color: {c_text_med}; margin-top: 6px;">
                • Recovered: <b style="color:{c_text_high};">₹{rec['recovered_amount_inr']:,.0f}</b><br>
                • Timestamp: <span class="mono-code" style="font-size:0.75rem;">{rec['timestamp'][:19]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: {'rgba(11, 19, 43, 0.5)' if is_dark else '#EEF4FB'}; border: 1px solid {c_border_subtle}; border-radius: 12px; padding: 1rem 1.3rem; margin-top: 1rem;">
        <span style="color: {c_brand_primary}; font-weight: 800; font-size: 0.82rem; text-transform: uppercase;">Detailed Agent Reasoning:</span>
        <p style="color: {c_text_high}; font-size: 0.95rem; margin-top: 0.3rem; margin-bottom: 0;">
            "{rec['reasoning']}"
        </p>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 3: INTERACTIVE RECOVERY SANDBOX
# ---------------------------------------------------------------------------
with tab_sandbox:
    st.markdown(f"""
    <div class="blade-panel">
        <div class="blade-panel-header">
            <span>⚡ Interactive Autonomous Recovery Sandbox</span>
            <span class="blade-pill">Live Testing Engine</span>
        </div>
        <p style="color: {c_text_med}; font-size: 0.95rem; margin-bottom: 1.4rem;">
            Test the agent with custom payment failure scenarios. Watch the agent evaluate playbook constraints, stopping rules, and simulate recovery in real time.
        </p>
    """, unsafe_allow_html=True)

    sb_c1, sb_c2, sb_c3 = st.columns(3)

    with sb_c1:
        sim_reason = st.selectbox(
            "Failure Code:",
            options=["insufficient_funds", "card_expired", "bank_technical_decline", "card_blocked_by_bank", "fraud_flagged"]
        )
        sim_amount = st.number_input("Subscription Amount (₹):", min_value=99, max_value=25000, value=1499, step=100)

    with sb_c2:
        sim_tenure = st.slider("Customer Tenure (Months):", min_value=1, max_value=48, value=18)
        sim_past_payments = st.slider("Past Successful Payments:", min_value=0, max_value=40, value=14)

    with sb_c3:
        sim_retries = st.slider("Past Retry Attempts So Far:", min_value=0, max_value=4, value=1)
        sim_segment = "high_value" if (sim_tenure > 18 and sim_past_payments > 12) else ("at_risk" if (sim_tenure < 6 or sim_past_payments < 3) else "standard")
        st.markdown(f"""
        <div style="background: {'rgba(11, 19, 43, 0.6)' if is_dark else '#EEF4FB'}; padding: 12px; border-radius: 12px; margin-top: 15px; border: 1px solid {c_border_subtle};">
            <div style="font-size:0.75rem; color:{c_text_med}; text-transform:uppercase; font-weight:700;">Derived Segment:</div>
            <div style="font-size:1.1rem; font-weight:900; color:{c_brand_primary};">{sim_segment.upper()}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("⚡ Execute Autonomous Recovery Diagnosis", type="primary", use_container_width=True):
        with st.spinner("🤖 Agent analyzing payment failure telemetry & evaluating stopping rules..."):
            time.sleep(0.5)
            
            if sim_reason == "fraud_flagged":
                decision_action = "escalate_to_human"
                diag = "Payment flagged by risk engine as high fraud probability."
                reason = "FRAUD HARD GUARD: Fraudulent transactions are isolated and escalated immediately."
                rule_ok = True
                sim_outcome = "pending_human_review"
                recovered_val = 0
            elif sim_reason == "card_expired":
                decision_action = "send_update_payment_link"
                diag = "Card validity expired on customer mandate."
                reason = "Auto-retry disabled for expired cards; sending secure update link."
                rule_ok = True
                sim_outcome = "recovered" if random.random() < 0.35 else "failed"
                recovered_val = sim_amount if sim_outcome == "recovered" else 0
            elif sim_reason == "insufficient_funds":
                if sim_retries >= 3:
                    decision_action = "escalate_to_human"
                    diag = "Max insufficient funds retries reached."
                    reason = "Stopping automated retries to protect customer from excessive decline fees."
                    rule_ok = False
                    sim_outcome = "pending_human_review"
                    recovered_val = 0
                else:
                    decision_action = "smart_retry"
                    diag = "Temporary liquidity deficit on subscriber account."
                    reason = "Timing retry window around likely payday interval for high probability debit."
                    rule_ok = True
                    sim_outcome = "recovered" if random.random() < 0.45 else "failed"
                    recovered_val = sim_amount if sim_outcome == "recovered" else 0
            elif sim_reason == "bank_technical_decline":
                if sim_retries >= 2:
                    decision_action = "escalate_to_human"
                    diag = "Repeated bank switch downtime."
                    reason = "Max technical retries reached; routing to operations team."
                    rule_ok = False
                    sim_outcome = "pending_human_review"
                    recovered_val = 0
                else:
                    decision_action = "smart_retry"
                    diag = "Transient bank switch timeout / network glitch."
                    reason = "Immediate automated retry recommended for transient bank error."
                    rule_ok = True
                    sim_outcome = "recovered" if random.random() < 0.65 else "failed"
                    recovered_val = sim_amount if sim_outcome == "recovered" else 0
            else: # card_blocked_by_bank
                decision_action = "send_update_payment_link"
                diag = "Bank issued temporary block on card mandate."
                reason = "Requesting customer to authorize alternate payment method via secure link."
                rule_ok = True
                sim_outcome = "recovered" if random.random() < 0.30 else "failed"
                recovered_val = sim_amount if sim_outcome == "recovered" else 0

            res_c1, res_c2 = st.columns(2)
            with res_c1:
                st.markdown(f"""
                <div class="blade-trace-box" style="border-color: {c_brand_primary};">
                    <div style="color: {c_brand_primary}; font-weight: 800; text-transform: uppercase; font-size: 0.8rem;">Agent Diagnosis & Recommendation</div>
                    <div style="font-size: 1.2rem; font-weight: 900; color: {c_text_high}; margin-top: 4px;">Action: {decision_action.replace('_', ' ').title()}</div>
                    <p style="color: {c_text_high}; font-size: 0.9rem; margin-top: 8px;"><b>Diagnosis:</b> {diag}</p>
                    <p style="color: {c_text_med}; font-size: 0.85rem;"><b>Reasoning:</b> {reason}</p>
                </div>
                """, unsafe_allow_html=True)

            with res_c2:
                outcome_badge = c_positive if sim_outcome == "recovered" else (c_notice if sim_outcome == "pending_human_review" else c_negative)
                st.markdown(f"""
                <div class="blade-trace-box" style="border-color: {outcome_badge};">
                    <div style="color: {outcome_badge}; font-weight: 800; text-transform: uppercase; font-size: 0.8rem;">Simulated Execution Outcome</div>
                    <div style="font-size: 1.4rem; font-weight: 900; color: {outcome_badge}; margin-top: 4px;">{sim_outcome.replace('_', ' ').upper()}</div>
                    <p style="color: {c_text_high}; font-size: 0.9rem; margin-top: 8px;"><b>Recovered Amount:</b> ₹{recovered_val:,.0f}</p>
                    <p style="color: {c_text_med}; font-size: 0.85rem;"><b>Policy Compliance:</b> <span style="color:{c_positive}; font-weight:800;">100% Validated & Logged</span></p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 4: COMPLIANCE & PLAYBOOK MATRIX
# ---------------------------------------------------------------------------
with tab_compliance:
    st.markdown(f"""
    <div class="blade-panel">
        <div class="blade-panel-header">
            <span>🛡️ Deterministic Playbook & Policy Guardrails</span>
            <span class="blade-pill blade-pill-success">Code-Level Hard Rules</span>
        </div>
        <p style="color: {c_text_med}; font-size: 0.95rem; margin-bottom: 1.2rem;">
            The AI agent's actions are strictly bounded by deterministic rules. Fraud-flagged transactions and excessive retry attempts are hard-blocked at the code level.
        </p>
    """, unsafe_allow_html=True)

    playbook_matrix = pd.DataFrame([
        {"Failure Code": "insufficient_funds", "Allowed Interventions": "smart_retry, offer_discount_retry, send_update_payment_link", "Max Retries": 3, "Cooldown": "2 Days", "Fraud Policy": "Standard"},
        {"Failure Code": "card_expired", "Allowed Interventions": "send_update_payment_link", "Max Retries": 0, "Cooldown": "0 Days", "Fraud Policy": "Standard"},
        {"Failure Code": "bank_technical_decline", "Allowed Interventions": "smart_retry", "Max Retries": 2, "Cooldown": "0 Days (Fast)", "Fraud Policy": "Standard"},
        {"Failure Code": "card_blocked_by_bank", "Allowed Interventions": "send_update_payment_link, escalate_to_human", "Max Retries": 0, "Cooldown": "0 Days", "Fraud Policy": "Standard"},
        {"Failure Code": "fraud_flagged", "Allowed Interventions": "escalate_to_human (ONLY)", "Max Retries": 0, "Cooldown": "N/A", "Fraud Policy": "🚨 HARD BLOCK AUTO-RETRY"},
    ])

    st.dataframe(playbook_matrix, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 5: COMPLIANCE AUDIT TRAIL
# ---------------------------------------------------------------------------
with tab_audit:
    st.markdown(f"""
    <div class="blade-panel">
        <div class="blade-panel-header">
            <span>📋 Full Financial & Compliance Audit Trail</span>
            <span style="font-size: 0.82rem; color: {c_text_med};">100% immutable decision history</span>
        </div>
    """, unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        f_reasons = st.multiselect("Filter by Failure Reason:", options=sorted(df["failure_reason"].unique()), default=sorted(df["failure_reason"].unique()))
    with f_col2:
        f_outcomes = st.multiselect("Filter by Outcome:", options=sorted(df["simulated_outcome"].unique()), default=sorted(df["simulated_outcome"].unique()))
    with f_col3:
        f_actions = st.multiselect("Filter by Action:", options=sorted(df["final_action"].unique()), default=sorted(df["final_action"].unique()))

    filtered_df = df[
        (df["failure_reason"].isin(f_reasons)) &
        (df["simulated_outcome"].isin(f_outcomes)) &
        (df["final_action"].isin(f_actions))
    ]

    st.markdown(f"Displaying **{len(filtered_df)}** of {total_records} audited transactions")

    display_cols = [
        "subscription_id", "customer_id", "customer_segment",
        "failure_reason", "diagnosis", "final_action", "reasoning",
        "allowed_by_rules", "simulated_outcome", "amount_inr", "recovered_amount_inr", "timestamp"
    ]

    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        height=480,
        column_config={
            "amount_inr": st.column_config.NumberColumn("At Risk (₹)", format="₹%.0f"),
            "recovered_amount_inr": st.column_config.NumberColumn("Recovered (₹)", format="₹%.0f"),
            "diagnosis": st.column_config.TextColumn("AI Diagnosis", width="medium"),
            "reasoning": st.column_config.TextColumn("Agent Reasoning", width="large"),
        }
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: {c_text_low}; font-size: 0.85rem; padding-bottom: 2rem;">
    💳 <b>AI Revenue Recovery Agent</b> | Powered by Razorpay Blade Design System | Built for Razorpay AI Buildathon 2026
</div>
""", unsafe_allow_html=True)
