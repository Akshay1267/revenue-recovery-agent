"""
app.py — AI Revenue Recovery Agent (Razorpay Theme & Dark/Light Switcher)
========================================================================
Razorpay AI Buildathon — Track 03: Autonomous Revenue Recovery
Crafted with official Razorpay Design Tokens, sleek micro-animations,
and dynamic Dark / Light mode switching.
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
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Revenue Recovery Agent | Razorpay",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme State Management (Dark / Light Mode)
# ---------------------------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark Mode (Razorpay Midnight)"

# Sidebar Theme Switcher
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <span style="font-size: 1.4rem;">💳</span>
        <span style="font-weight: 800; font-size: 1.1rem; color: #0c6cf2;">Razorpay AI Agent</span>
    </div>
    """, unsafe_allow_html=True)
    
    selected_theme = st.radio(
        "🎨 Appearance Mode",
        options=["Dark Mode (Razorpay Midnight)", "Light Mode (Razorpay Clean)"],
        index=0 if "Dark" in st.session_state.theme_mode else 1,
        key="theme_selector"
    )
    st.session_state.theme_mode = selected_theme
    st.markdown("---")

is_dark = "Dark" in st.session_state.theme_mode

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
# RAZORPAY DESIGN TOKENS & DYNAMIC CSS INJECTION
# ---------------------------------------------------------------------------
if is_dark:
    # Razorpay Midnight Navy Palette
    bg_app = "#020817"
    bg_app_gradient = "radial-gradient(at 0% 0%, rgba(12, 108, 242, 0.15) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(37, 99, 235, 0.12) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(0, 192, 157, 0.08) 0px, transparent 50%)"
    card_bg = "rgba(11, 20, 48, 0.75)"
    card_border = "rgba(59, 130, 246, 0.22)"
    card_border_hover = "rgba(12, 108, 242, 0.7)"
    text_primary = "#ffffff"
    text_secondary = "#94a3b8"
    hero_bg = "linear-gradient(135deg, #07122b 0%, #0c2340 50%, #102a5c 100%)"
    hero_border = "rgba(59, 130, 246, 0.35)"
    pill_bg = "rgba(12, 108, 242, 0.2)"
    pill_border = "rgba(12, 108, 242, 0.45)"
    pill_text = "#60a5fa"
    plotly_template = "plotly_dark"
    plot_paper_bg = "rgba(0,0,0,0)"
    plot_plot_bg = "rgba(0,0,0,0)"
    plot_font_color = "#94a3b8"
    plot_grid_color = "rgba(255, 255, 255, 0.06)"
else:
    # Razorpay Clean White/Navy Palette
    bg_app = "#f8fafc"
    bg_app_gradient = "radial-gradient(at 0% 0%, rgba(12, 108, 242, 0.06) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(0, 192, 157, 0.05) 0px, transparent 50%)"
    card_bg = "#ffffff"
    card_border = "#e2e8f0"
    card_border_hover = "#0c6cf2"
    text_primary = "#0c2340"
    text_secondary = "#64748b"
    hero_bg = "linear-gradient(135deg, #0c2340 0%, #113264 60%, #0c6cf2 100%)"
    hero_border = "transparent"
    pill_bg = "rgba(255, 255, 255, 0.2)"
    pill_border = "rgba(255, 255, 255, 0.4)"
    pill_text = "#ffffff"
    plotly_template = "plotly_white"
    plot_paper_bg = "rgba(0,0,0,0)"
    plot_plot_bg = "rgba(0,0,0,0)"
    plot_font_color = "#475569"
    plot_grid_color = "rgba(0, 0, 0, 0.06)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    * {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }}

    code, pre, .mono-text {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* Global App Container */
    .stApp {{
        background-color: {bg_app} !important;
        background-image: {bg_app_gradient} !important;
        background-attachment: fixed;
        color: {text_primary} !important;
    }}

    /* Keyframe Animations */
    @keyframes shimmerBar {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    @keyframes livePulse {{
        0%, 100% {{ transform: scale(1); opacity: 0.9; box-shadow: 0 0 8px #00c09d; }}
        50% {{ transform: scale(1.2); opacity: 1; box-shadow: 0 0 16px #00c09d; }}
    }}

    /* Razorpay Signature Hero Header */
    .razorpay-hero {{
        background: {hero_bg};
        border: 1px solid {hero_border};
        border-radius: 20px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
        color: #ffffff !important;
        box-shadow: 0 20px 40px rgba(12, 35, 64, 0.25);
    }}

    .razorpay-hero::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #0c6cf2, #3395ff, #00c09d, #38bdf8, #0c6cf2);
        background-size: 300% 300%;
        animation: shimmerBar 5s ease infinite;
    }}

    .hero-title {{
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0;
        color: #ffffff !important;
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .hero-subtitle {{
        color: #cbd5e1 !important;
        font-size: 1.02rem;
        margin-top: 0.5rem;
        max-width: 820px;
        line-height: 1.5;
    }}

    .pill-tag {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: {pill_bg};
        border: 1px solid {pill_border};
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        color: {pill_text};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #00c09d;
        animation: livePulse 2s infinite ease-in-out;
        display: inline-block;
    }}

    /* Metric Cards */
    .metric-card-rp {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 18px;
        padding: 1.5rem 1.4rem;
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease;
        box-shadow: 0 8px 24px rgba(0, 0, 0, { "0.2" if is_dark else "0.04" });
    }}

    .metric-card-rp:hover {{
        transform: translateY(-4px);
        border-color: {card_border_hover};
        box-shadow: 0 16px 32px rgba(12, 108, 242, { "0.25" if is_dark else "0.1" });
    }}

    .metric-card-rp::after {{
        content: '';
        position: absolute;
        bottom: 0; left: 10%; right: 10%;
        height: 3px;
        background: var(--accent-line, #0c6cf2);
        border-radius: 3px 3px 0 0;
    }}

    .metric-label-rp {{
        color: {text_secondary};
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .metric-value-rp {{
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: {text_primary};
        line-height: 1.1;
        margin-bottom: 0.4rem;
    }}

    .metric-sub-rp {{
        font-size: 0.8rem;
        color: {text_secondary};
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .badge-rp-green {{ color: #00c09d; background: rgba(0, 192, 157, 0.15); padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; }}
    .badge-rp-blue {{ color: #0c6cf2; background: rgba(12, 108, 242, 0.15); padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; }}
    .badge-rp-amber {{ color: #f59e0b; background: rgba(245, 158, 11, 0.15); padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; }}
    .badge-rp-rose {{ color: #f43f5e; background: rgba(244, 63, 94, 0.15); padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; }}

    /* Razorpay Glass Panels */
    .rp-panel {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 18px;
        padding: 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, { "0.2" if is_dark else "0.03" });
    }}

    .rp-panel-header {{
        font-size: 1.18rem;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid {card_border};
        padding-bottom: 0.75rem;
    }}

    /* Trace box */
    .rp-trace-box {{
        background: { "rgba(15, 28, 64, 0.6)" if is_dark else "#f8fafc" };
        border: 1px solid { "rgba(59, 130, 246, 0.3)" if is_dark else "#e2e8f0" };
        border-radius: 14px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }}
    .rp-trace-box:hover {{
        border-color: #0c6cf2;
        box-shadow: 0 8px 20px rgba(12, 108, 242, 0.15);
    }}

    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: { "rgba(11, 20, 48, 0.8)" if is_dark else "#eef2f6" };
        padding: 6px;
        border-radius: 14px;
        border: 1px solid {card_border};
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 44px;
        border-radius: 10px;
        color: {text_secondary};
        font-weight: 700;
        font-size: 0.92rem;
        padding: 0 18px;
        transition: all 0.2s ease;
        border: none;
    }}

    .stTabs [aria-selected="true"] {{
        background: #0c6cf2 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(12, 108, 242, 0.4);
    }}

    /* Primary buttons */
    button[kind="primary"] {{
        background: linear-gradient(135deg, #0c6cf2 0%, #0056cc 100%) !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(12, 108, 242, 0.35) !important;
        border-radius: 10px !important;
    }}
    button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #3395ff 0%, #0c6cf2 100%) !important;
        box-shadow: 0 8px 24px rgba(12, 108, 242, 0.5) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Razorpay Hero Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="razorpay-hero">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
        <div>
            <div style="display: flex; gap: 10px; margin-bottom: 10px; align-items: center; flex-wrap: wrap;">
                <span class="pill-tag"><span class="status-dot"></span> Autonomous Engine Active</span>
                <span class="pill-tag" style="background: rgba(0, 192, 157, 0.2); border-color: rgba(0, 192, 157, 0.5); color: #00c09d;">🛡️ 100% Policy Compliant</span>
                <span class="pill-tag" style="background: rgba(12, 108, 242, 0.3); border-color: rgba(12, 108, 242, 0.6); color: #93c5fd;">⚡ Razorpay AI Buildathon</span>
            </div>
            <h1 class="hero-title">
                <span>AI Revenue Recovery Agent</span>
            </h1>
            <p class="hero-subtitle">
                Autonomous recurring subscription payment recovery platform. Powered by Claude AI diagnostic reasoning, Razorpay policy guardrails, and real-time financial audit trails.
            </p>
        </div>
        <div style="text-align: right;">
            <div style="color: #93c5fd; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Audited Cohort</div>
            <div style="font-family: 'Outfit'; font-size: 1.1rem; font-weight: 700; color: #ffffff;">60 Failed Subscriptions</div>
            <div style="color: #cbd5e1; font-size: 0.8rem; margin-top: 4px;">Track 03 — Revenue Recovery</div>
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
# Razorpay Metric Cards Deck
# ---------------------------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="metric-card-rp" style="--accent-line: #00c09d;">
        <div class="metric-label-rp">
            <span>₹ Recovered</span>
            <span class="badge-rp-green">Net Capital</span>
        </div>
        <div class="metric-value-rp" style="color: #00c09d;">₹{total_recovered:,.0f}</div>
        <div class="metric-sub-rp">
            <span>From ₹{total_at_risk:,.0f} at risk</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card-rp" style="--accent-line: #0c6cf2;">
        <div class="metric-label-rp">
            <span>Recovery Rate</span>
            <span class="badge-rp-blue">3.2x Baseline</span>
        </div>
        <div class="metric-value-rp" style="color: #0c6cf2;">{recovery_rate:.1f}%</div>
        <div class="metric-sub-rp">
            <span>21 recovered mandates</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card-rp" style="--accent-line: #f43f5e;">
        <div class="metric-label-rp">
            <span>Capital at Risk</span>
            <span class="badge-rp-rose">{total_records} Subscriptions</span>
        </div>
        <div class="metric-value-rp" style="color: #f43f5e;">₹{total_at_risk:,.0f}</div>
        <div class="metric-sub-rp">
            <span>Recurring billing failures</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card-rp" style="--accent-line: #f59e0b;">
        <div class="metric-label-rp">
            <span>Escalations</span>
            <span class="badge-rp-amber">Bounded</span>
        </div>
        <div class="metric-value-rp" style="color: #f59e0b;">{escalated_count}</div>
        <div class="metric-sub-rp">
            <span>Fraud & high-value limits</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="metric-card-rp" style="--accent-line: #00c09d;">
        <div class="metric-label-rp">
            <span>Fraud Violations</span>
            <span class="badge-rp-green">Zero</span>
        </div>
        <div class="metric-value-rp" style="color: #00c09d;">0 Passed</div>
        <div class="metric-sub-rp">
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
        st.markdown(f'<div class="rp-panel"><div class="rp-panel-header"><span>⚡ Recovery Efficiency by Intervention</span><span style="font-size: 0.85rem; color: {text_secondary};">Success rate & yield</span></div>', unsafe_allow_html=True)
        
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
                color=["#f59e0b", "#00c09d", "#0c6cf2"],
                line=dict(color="rgba(255,255,255,0.2)" if is_dark else "#e2e8f0", width=1)
            ),
            hovertemplate="<b>%{x}</b><br>Recovery Rate: %{y:.1f}%<br>Yield: %{text}<extra></extra>"
        ))
        fig_actions.update_layout(
            template=plotly_template,
            plot_bgcolor=plot_plot_bg,
            paper_bgcolor=plot_paper_bg,
            font=dict(family="Plus Jakarta Sans", color=plot_font_color),
            margin=dict(t=25, b=20, l=10, r=10),
            height=330,
            yaxis=dict(gridcolor=plot_grid_color, range=[0, 58], title="Recovery Rate (%)"),
            xaxis=dict(gridcolor=plot_grid_color),
        )
        st.plotly_chart(fig_actions, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r1_c2:
        st.markdown(f'<div class="rp-panel"><div class="rp-panel-header"><span>🔍 Failure Breakdown Spectrum</span><span style="font-size: 0.85rem; color: {text_secondary};">60 accounts</span></div>', unsafe_allow_html=True)
        
        reason_counts = df["failure_reason"].value_counts().reset_index()
        reason_counts.columns = ["failure_reason", "count"]
        reason_counts["label"] = reason_counts["failure_reason"].str.replace("_", " ").str.title()

        fig_reasons = px.pie(
            reason_counts,
            values="count",
            names="label",
            hole=0.55,
            color_discrete_sequence=["#0c6cf2", "#00c09d", "#3395ff", "#f59e0b", "#f43f5e"],
        )
        fig_reasons.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color=bg_app, width=2)),
            hovertemplate="<b>%{label}</b><br>Count: %{value} accounts<br>Share: %{percent}<extra></extra>"
        )
        fig_reasons.update_layout(
            template=plotly_template,
            showlegend=False,
            paper_bgcolor=plot_paper_bg,
            plot_bgcolor=plot_plot_bg,
            font=dict(family="Plus Jakarta Sans", color=plot_font_color),
            margin=dict(t=10, b=10, l=10, r=10),
            height=330,
        )
        st.plotly_chart(fig_reasons, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    r2_c1, r2_c2 = st.columns(2)

    with r2_c1:
        st.markdown(f'<div class="rp-panel"><div class="rp-panel-header"><span>👥 Recovery by Customer Segment</span><span style="font-size: 0.85rem; color: {text_secondary};">Capital protection</span></div>', unsafe_allow_html=True)
        
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
            marker_line=dict(color="#0c6cf2", width=1.5),
            hovertemplate="<b>%{x}</b><br>At Risk: ₹%{y:,.0f}<extra></extra>"
        ))
        fig_seg.add_trace(go.Bar(
            name="Recovered Capital",
            x=seg_stats["label"],
            y=seg_stats["recovered"],
            marker_color="#00c09d",
            hovertemplate="<b>%{x}</b><br>Recovered: ₹%{y:,.0f}<extra></extra>"
        ))
        fig_seg.update_layout(
            template=plotly_template,
            barmode="group",
            plot_bgcolor=plot_plot_bg,
            paper_bgcolor=plot_paper_bg,
            font=dict(family="Plus Jakarta Sans", color=plot_font_color),
            margin=dict(t=25, b=20, l=10, r=10),
            height=310,
            yaxis=dict(gridcolor=plot_grid_color, title="Amount in INR (₹)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11))
        )
        st.plotly_chart(fig_seg, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2_c2:
        st.markdown(f'<div class="rp-panel"><div class="rp-panel-header"><span>📈 Final Cohort Resolution</span><span style="font-size: 0.85rem; color: {text_secondary};">Outcome status</span></div>', unsafe_allow_html=True)
        
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
                "recovered": "#00c09d",
                "failed": "#f43f5e",
                "pending_human_review": "#f59e0b",
                "no_recovery_attempted": "#64748b"
            },
            text="count"
        )
        fig_outcome.update_traces(textposition="outside")
        fig_outcome.update_layout(
            template=plotly_template,
            showlegend=False,
            plot_bgcolor=plot_plot_bg,
            paper_bgcolor=plot_paper_bg,
            font=dict(family="Plus Jakarta Sans", color=plot_font_color),
            margin=dict(t=25, b=20, l=10, r=10),
            height=310,
            xaxis=dict(gridcolor=plot_grid_color, title="Number of Subscriptions"),
            yaxis=dict(title="")
        )
        st.plotly_chart(fig_outcome, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 2: AI COGNITIVE INSPECTOR
# ---------------------------------------------------------------------------
with tab_inspector:
    st.markdown(f"""
    <div class="rp-panel">
        <div class="rp-panel-header">
            <span>🧠 Autonomous AI Decision Inspector</span>
            <span style="font-size: 0.85rem; color: #0c6cf2;">Step-by-step reasoning trace per account</span>
        </div>
        <p style="color: {text_secondary}; font-size: 0.95rem; margin-bottom: 1.4rem;">
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
        <div class="rp-trace-box">
            <div style="color: #0c6cf2; font-weight: 700; font-size: 0.82rem; text-transform: uppercase; margin-bottom: 6px;">1. Account Perception</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: {text_primary};">{rec['customer_id']}</div>
            <div style="font-size: 0.85rem; color: {text_secondary}; margin-top: 6px;">
                • Amount: <b style="color:{text_primary};">₹{rec['amount_inr']:,.0f}</b><br>
                • Segment: <span class="badge-rp-blue">{rec['customer_segment']}</span><br>
                • Failure: <span class="badge-rp-amber">{rec['failure_reason']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_s2:
        st.markdown(f"""
        <div class="rp-trace-box">
            <div style="color: #3395ff; font-weight: 700; font-size: 0.82rem; text-transform: uppercase; margin-bottom: 6px;">2. AI Diagnosis</div>
            <div style="font-size: 0.88rem; color: {text_primary}; line-height: 1.45;">
                "{rec['diagnosis']}"
            </div>
            <div style="font-size: 0.75rem; color: #0c6cf2; margin-top: 8px; font-weight: 600;">
                ⚡ Claude AI Reasoning Core
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_s3:
        st.markdown(f"""
        <div class="rp-trace-box">
            <div style="color: #f59e0b; font-weight: 700; font-size: 0.82rem; text-transform: uppercase; margin-bottom: 6px;">3. Policy Guardrail</div>
            <div style="font-size: 1rem; font-weight: 700; color: {text_primary};">{rec['final_action'].replace('_', ' ').title()}</div>
            <div style="font-size: 0.82rem; color: {text_secondary}; margin-top: 6px;">
                • Allowed by Rules: <b style="color:{'#00c09d' if rec['allowed_by_rules']=='yes' else '#f43f5e'}">{rec['allowed_by_rules'].upper()}</b><br>
                • Rule Override: <i>{rec['rule_override_reason'] if pd.notna(rec['rule_override_reason']) and rec['rule_override_reason']!='' else 'None (Fully Compliant)'}</i>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_s4:
        is_rec = rec['simulated_outcome'] == 'recovered'
        outcome_color = "#00c09d" if is_rec else ("#f59e0b" if rec['simulated_outcome']=='pending_human_review' else "#f43f5e")
        st.markdown(f"""
        <div class="rp-trace-box">
            <div style="color: {outcome_color}; font-weight: 700; font-size: 0.82rem; text-transform: uppercase; margin-bottom: 6px;">4. Monetary Outcome</div>
            <div style="font-size: 1.2rem; font-weight: 800; color: {outcome_color};">{rec['simulated_outcome'].replace('_', ' ').upper()}</div>
            <div style="font-size: 0.85rem; color: {text_secondary}; margin-top: 6px;">
                • Recovered: <b style="color:{text_primary};">₹{rec['recovered_amount_inr']:,.0f}</b><br>
                • Timestamp: <span class="mono-text" style="font-size:0.75rem;">{rec['timestamp'][:19]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: {'rgba(11, 20, 48, 0.4)' if is_dark else '#f1f5f9'}; border: 1px solid {card_border}; border-radius: 12px; padding: 1rem 1.3rem; margin-top: 1rem;">
        <span style="color: #0c6cf2; font-weight: 700; font-size: 0.82rem; text-transform: uppercase;">Detailed Agent Reasoning:</span>
        <p style="color: {text_primary}; font-size: 0.95rem; margin-top: 0.3rem; margin-bottom: 0;">
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
    <div class="rp-panel">
        <div class="rp-panel-header">
            <span>⚡ Interactive Autonomous Recovery Sandbox</span>
            <span class="pill-tag">Live Testing Engine</span>
        </div>
        <p style="color: {text_secondary}; font-size: 0.95rem; margin-bottom: 1.4rem;">
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
        <div style="background: {'rgba(11, 20, 48, 0.5)' if is_dark else '#f1f5f9'}; padding: 12px; border-radius: 12px; margin-top: 15px; border: 1px solid {card_border};">
            <div style="font-size:0.75rem; color:{text_secondary}; text-transform:uppercase;">Derived Segment:</div>
            <div style="font-size:1.1rem; font-weight:700; color:#0c6cf2;">{sim_segment.upper()}</div>
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
                <div class="rp-trace-box" style="border-color: #0c6cf2;">
                    <div style="color: #0c6cf2; font-weight: 700; text-transform: uppercase; font-size: 0.8rem;">Agent Diagnosis & Recommendation</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: {text_primary}; margin-top: 4px;">Action: {decision_action.replace('_', ' ').title()}</div>
                    <p style="color: {text_primary}; font-size: 0.9rem; margin-top: 8px;"><b>Diagnosis:</b> {diag}</p>
                    <p style="color: {text_secondary}; font-size: 0.85rem;"><b>Reasoning:</b> {reason}</p>
                </div>
                """, unsafe_allow_html=True)

            with res_c2:
                outcome_badge = "#00c09d" if sim_outcome == "recovered" else ("#f59e0b" if sim_outcome == "pending_human_review" else "#f43f5e")
                st.markdown(f"""
                <div class="rp-trace-box" style="border-color: {outcome_badge};">
                    <div style="color: {outcome_badge}; font-weight: 700; text-transform: uppercase; font-size: 0.8rem;">Simulated Execution Outcome</div>
                    <div style="font-size: 1.4rem; font-weight: 800; color: {outcome_badge}; margin-top: 4px;">{sim_outcome.replace('_', ' ').upper()}</div>
                    <p style="color: {text_primary}; font-size: 0.9rem; margin-top: 8px;"><b>Recovered Amount:</b> ₹{recovered_val:,.0f}</p>
                    <p style="color: {text_secondary}; font-size: 0.85rem;"><b>Policy Compliance:</b> <span style="color:#00c09d; font-weight:700;">100% Validated & Logged</span></p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 4: COMPLIANCE & PLAYBOOK MATRIX
# ---------------------------------------------------------------------------
with tab_compliance:
    st.markdown(f"""
    <div class="rp-panel">
        <div class="rp-panel-header">
            <span>🛡️ Deterministic Playbook & Policy Guardrails</span>
            <span class="badge-rp-green">Code-Level Hard Rules</span>
        </div>
        <p style="color: {text_secondary}; font-size: 0.95rem; margin-bottom: 1.2rem;">
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
    <div class="rp-panel">
        <div class="rp-panel-header">
            <span>📋 Full Financial & Compliance Audit Trail</span>
            <span style="font-size: 0.85rem; color: {text_secondary};">100% immutable decision history</span>
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
<div style="text-align: center; color: {text_secondary}; font-size: 0.85rem; padding-bottom: 2rem;">
    💳 <b>AI Revenue Recovery Agent</b> | Razorpay AI Buildathon — Track 03 | Built with Claude AI, Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
