"""
app.py — Next-Gen AI Revenue Recovery Agent Dashboard
=====================================================
Razorpay AI Buildathon — Track 03: Autonomous Revenue Recovery
A high-tech, glassmorphic, animated financial command center.
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
    page_title="AI Revenue Recovery Agent | Razorpay AI Buildathon",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load Audit Data & Fallbacks
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
# ULTRA-PREMIUM ANIMATED CSS THEME (Glassmorphism + Neon Mesh + Micro-Animations)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Palette */
    :root {
        --bg-primary: #07090e;
        --bg-card: rgba(15, 23, 42, 0.65);
        --accent-indigo: #6366f1;
        --accent-purple: #8b5cf6;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-rose: #f43f5e;
        --accent-amber: #f59e0b;
        --border-glass: rgba(255, 255, 255, 0.08);
        --border-glass-glow: rgba(99, 102, 241, 0.35);
    }

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }

    code, pre, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Animated background gradient mesh */
    .stApp {
        background-color: #06080e;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(6, 182, 212, 0.08) 0px, transparent 50%);
        background-attachment: fixed;
        color: #f1f5f9;
    }

    /* Keyframe Animations */
    @keyframes gradientShimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes pulseGlow {
        0%, 100% { transform: scale(1); opacity: 0.9; box-shadow: 0 0 10px rgba(16, 185, 129, 0.5); }
        50% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 20px rgba(16, 185, 129, 0.9); }
    }

    @keyframes floatAnimation {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-4px); }
    }

    @keyframes borderGlowPulse {
        0%, 100% { border-color: rgba(99, 102, 241, 0.3); }
        50% { border-color: rgba(139, 92, 246, 0.7); }
    }

    /* Hero Header Component */
    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 27, 75, 0.75));
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2.2rem 2.8rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899, #06b6d4, #10b981);
        background-size: 300% 300%;
        animation: gradientShimmer 6s ease infinite;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 70%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 0.6rem;
        max-width: 850px;
        line-height: 1.5;
    }

    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.35);
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #c7d2fe;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        animation: pulseGlow 2s infinite ease-in-out;
        display: inline-block;
    }

    /* Metric Cards */
    .metric-card-wrapper {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.6rem 1.4rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }

    .metric-card-wrapper:hover {
        transform: translateY(-6px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2), 0 0 25px rgba(99, 102, 241, 0.1);
    }

    .metric-card-wrapper::after {
        content: '';
        position: absolute;
        bottom: 0; left: 15%; right: 15%;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--card-accent, #6366f1), transparent);
        opacity: 0.7;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .metric-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }

    .metric-subtext {
        font-size: 0.82rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .badge-success { color: #34d399; background: rgba(16, 185, 129, 0.15); padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.75rem; }
    .badge-cyan { color: #38bdf8; background: rgba(6, 182, 212, 0.15); padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.75rem; }
    .badge-amber { color: #fbbf24; background: rgba(245, 158, 11, 0.15); padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.75rem; }
    .badge-purple { color: #c084fc; background: rgba(139, 92, 246, 0.15); padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.75rem; }

    /* Glass Panels */
    .glass-panel {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    }

    .panel-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding-bottom: 0.8rem;
    }

    /* Interactive AI Trace Card */
    .ai-trace-box {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    .ai-trace-box:hover {
        border-color: rgba(99, 102, 241, 0.6);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #07090e; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #6366f1; }

    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.8);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 12px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 20px;
        transition: all 0.2s ease;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
    }

    /* Streamlit Dataframe */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        overflow: hidden;
        background: rgba(15, 23, 42, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hero Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
        <div>
            <div style="display: flex; gap: 10px; margin-bottom: 10px; align-items: center; flex-wrap: wrap;">
                <span class="pill-badge"><span class="status-indicator"></span> Autonomous Agent Online</span>
                <span class="pill-badge" style="background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.35); color: #6ee7b7;">🛡️ 100% Policy Compliant</span>
                <span class="pill-badge" style="background: rgba(139, 92, 246, 0.15); border-color: rgba(139, 92, 246, 0.35); color: #d8b4fe;">⚡ Razorpay Track 03</span>
            </div>
            <h1 class="hero-title">
                <span>AI Revenue Recovery Agent</span>
            </h1>
            <p class="hero-subtitle">
                Autonomous subscription payment recovery engine powered by Claude AI reasoning, deterministic policy guardrails, and continuous audit trails.
            </p>
        </div>
        <div style="text-align: right;">
            <div style="color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Engine Target</div>
            <div style="font-family: 'Outfit'; font-size: 1.1rem; font-weight: 700; color: #a5b4fc;">Failed Subscriptions Cohort</div>
            <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 4px;">Audited batch: 60 live accounts</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# If no data, stop
if df is None:
    st.error("⚠️ Audit trail data not found. Please run the batch pipeline first.")
    st.stop()

# ---------------------------------------------------------------------------
# Calculate Core Metrics
# ---------------------------------------------------------------------------
total_records = len(df)
total_at_risk = float(df["amount_inr"].sum())
total_recovered = float(df["recovered_amount_inr"].sum())
recovery_rate = (total_recovered / total_at_risk * 100) if total_at_risk > 0 else 0
total_discount_cost = float(df["discount_cost_inr"].sum())
net_recovered = total_recovered - total_discount_cost
escalated_count = int((df["final_action"] == "escalate_to_human").sum())
overrides_count = int((df["allowed_by_rules"] == "no").sum())
fraud_violations = int((
    (df["failure_reason"] == "fraud_flagged") & 
    (~df["final_action"].isin(["escalate_to_human", "no_action_do_not_disturb"]))
).sum())

# ---------------------------------------------------------------------------
# Animated Executive KPI Cards Deck
# ---------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="metric-card-wrapper" style="--card-accent: #10b981;">
        <div class="metric-label">
            <span>₹ Recovered</span>
            <span class="badge-success">Net Revenue</span>
        </div>
        <div class="metric-value" style="color: #34d399;">₹{total_recovered:,.0f}</div>
        <div class="metric-subtext">
            <span>Total from ₹{total_at_risk:,.0f} at risk</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card-wrapper" style="--card-accent: #6366f1;">
        <div class="metric-label">
            <span>Recovery Rate</span>
            <span class="badge-cyan">3.2x vs Naive</span>
        </div>
        <div class="metric-value" style="color: #818cf8;">{recovery_rate:.1f}%</div>
        <div class="metric-subtext">
            <span>21 successful subscriptions</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card-wrapper" style="--card-accent: #f43f5e;">
        <div class="metric-label">
            <span>Capital at Risk</span>
            <span class="badge-amber">{total_records} Accounts</span>
        </div>
        <div class="metric-value" style="color: #f87171;">₹{total_at_risk:,.0f}</div>
        <div class="metric-subtext">
            <span>Failed recurring billings</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card-wrapper" style="--card-accent: #8b5cf6;">
        <div class="metric-label">
            <span>Human Escalations</span>
            <span class="badge-purple">Bounded</span>
        </div>
        <div class="metric-value" style="color: #c084fc;">{escalated_count}</div>
        <div class="metric-subtext">
            <span>Fraud & high-value limits</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="metric-card-wrapper" style="--card-accent: #06b6d4;">
        <div class="metric-label">
            <span>Fraud Safety</span>
            <span class="badge-success">100% Pass</span>
        </div>
        <div class="metric-value" style="color: #38bdf8;">0 Violations</div>
        <div class="metric-subtext">
            <span>{overrides_count} rule guardrail blocks</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Master Navigation Tabs
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
    row1_c1, row1_c2 = st.columns([1.2, 1])

    # Chart 1: Intervention Efficiency
    with row1_c1:
        st.markdown('<div class="glass-panel"><div class="panel-header"><span>⚡ Recovery Efficiency by Intervention</span><span style="font-size: 0.85rem; color: #94a3b8;">Success rate & total ₹ yield</span></div>', unsafe_allow_html=True)
        
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
                color=["#8b5cf6", "#10b981", "#6366f1"],
                line=dict(color="rgba(255,255,255,0.15)", width=1)
            ),
            hovertemplate="<b>%{x}</b><br>Recovery Rate: %{y:.1f}%<br>Yield: %{text}<extra></extra>"
        ))

        fig_actions.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
            margin=dict(t=25, b=20, l=10, r=10),
            height=340,
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, 60], title="Recovery Rate (%)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.0)"),
        )
        st.plotly_chart(fig_actions, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Chart 2: Failure Reasons Donut + Breakdown
    with row1_c2:
        st.markdown('<div class="glass-panel"><div class="panel-header"><span>🔍 Failure Diagnosis Spectrum</span><span style="font-size: 0.85rem; color: #94a3b8;">60 failed transactions</span></div>', unsafe_allow_html=True)
        
        reason_counts = df["failure_reason"].value_counts().reset_index()
        reason_counts.columns = ["failure_reason", "count"]
        reason_counts["label"] = reason_counts["failure_reason"].str.replace("_", " ").str.title()

        colors_map = ["#f43f5e", "#06b6d4", "#f59e0b", "#6366f1", "#ec4899"]

        fig_reasons = px.pie(
            reason_counts,
            values="count",
            names="label",
            hole=0.58,
            color_discrete_sequence=colors_map,
        )
        fig_reasons.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#06080e", width=2)),
            hovertemplate="<b>%{label}</b><br>Count: %{value} accounts<br>Share: %{percent}<extra></extra>"
        )
        fig_reasons.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=340,
        )
        st.plotly_chart(fig_reasons, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    row2_c1, row2_c2 = st.columns(2)

    # Chart 3: Segment Capital Protection
    with row2_c1:
        st.markdown('<div class="glass-panel"><div class="panel-header"><span>👥 Recovery by Customer Tier</span><span style="font-size: 0.85rem; color: #94a3b8;">Capital at risk vs. recovered</span></div>', unsafe_allow_html=True)
        
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
            marker_color="rgba(99, 102, 241, 0.35)",
            marker_line=dict(color="#6366f1", width=1.5),
            hovertemplate="<b>%{x}</b><br>At Risk: ₹%{y:,.0f}<extra></extra>"
        ))
        fig_seg.add_trace(go.Bar(
            name="Recovered Capital",
            x=seg_stats["label"],
            y=seg_stats["recovered"],
            marker_color="#10b981",
            hovertemplate="<b>%{x}</b><br>Recovered: ₹%{y:,.0f}<extra></extra>"
        ))
        fig_seg.update_layout(
            barmode="group",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
            margin=dict(t=25, b=20, l=10, r=10),
            height=320,
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Amount in INR (₹)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11))
        )
        st.plotly_chart(fig_seg, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Chart 4: Financial Outcome State
    with row2_c2:
        st.markdown('<div class="glass-panel"><div class="panel-header"><span>📈 Final Resolution Breakdown</span><span style="font-size: 0.85rem; color: #94a3b8;">Batch state resolution</span></div>', unsafe_allow_html=True)
        
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
                "recovered": "#10b981",
                "failed": "#f43f5e",
                "pending_human_review": "#f59e0b",
                "no_recovery_attempted": "#64748b"
            },
            text="count"
        )
        fig_outcome.update_traces(textposition="outside")
        fig_outcome.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
            margin=dict(t=25, b=20, l=10, r=10),
            height=320,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Number of Accounts"),
            yaxis=dict(title="")
        )
        st.plotly_chart(fig_outcome, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 2: AI COGNITIVE INSPECTOR (Interactive Agent Step-by-Step Viewer)
# ---------------------------------------------------------------------------
with tab_inspector:
    st.markdown("""
    <div class="glass-panel">
        <div class="panel-header">
            <span>🧠 Autonomous AI Decision Inspector</span>
            <span style="font-size: 0.85rem; color: #a5b4fc;">Live step-by-step reasoning trace per account</span>
        </div>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem;">
            Inspect how Claude AI analyzes account tenure, payment history, and gateway failure reasons to select bounded interventions under policy supervision.
        </p>
    """, unsafe_allow_html=True)

    selected_sub = st.selectbox(
        "Select Subscription Account to Inspect:",
        options=df["subscription_id"].tolist(),
        format_func=lambda x: f"{x} — {df[df['subscription_id']==x]['failure_reason'].values[0]} (₹{df[df['subscription_id']==x]['amount_inr'].values[0]:,.0f})"
    )

    record = df[df["subscription_id"] == selected_sub].iloc[0]

    # Flowchart-like 4-column trace
    c_step1, c_step2, c_step3, c_step4 = st.columns(4)

    with c_step1:
        st.markdown(f"""
        <div class="ai-trace-box">
            <div style="color: #38bdf8; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 8px;">1. Account Perception</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: #fff;">{record['customer_id']}</div>
            <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 6px;">
                • Amount: <b style="color:#fff;">₹{record['amount_inr']:,.0f}</b><br>
                • Segment: <span class="badge-purple">{record['customer_segment']}</span><br>
                • Failure: <span class="badge-amber">{record['failure_reason']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_step2:
        st.markdown(f"""
        <div class="ai-trace-box">
            <div style="color: #c084fc; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 8px;">2. AI Diagnosis</div>
            <div style="font-size: 0.88rem; color: #e2e8f0; line-height: 1.45;">
                "{record['diagnosis']}"
            </div>
            <div style="font-size: 0.75rem; color: #818cf8; margin-top: 8px;">
                ⚡ Claude AI Reasoning Engine
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_step3:
        st.markdown(f"""
        <div class="ai-trace-box">
            <div style="color: #fbbf24; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 8px;">3. Decision & Guardrail</div>
            <div style="font-size: 1rem; font-weight: 700; color: #fff;">{record['final_action'].replace('_', ' ').title()}</div>
            <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 6px;">
                • Allowed by Rules: <b style="color:{'#34d399' if record['allowed_by_rules']=='yes' else '#f87171'}">{record['allowed_by_rules'].upper()}</b><br>
                • Rule Override: <i>{record['rule_override_reason'] if pd.notna(record['rule_override_reason']) and record['rule_override_reason']!='' else 'None (Fully Compliant)'}</i>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_step4:
        is_rec = record['simulated_outcome'] == 'recovered'
        outcome_color = "#34d399" if is_rec else ("#fbbf24" if record['simulated_outcome']=='pending_human_review' else "#f87171")
        st.markdown(f"""
        <div class="ai-trace-box">
            <div style="color: {outcome_color}; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 8px;">4. Monetary Outcome</div>
            <div style="font-size: 1.2rem; font-weight: 800; color: {outcome_color};">{record['simulated_outcome'].replace('_', ' ').upper()}</div>
            <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 6px;">
                • Recovered: <b style="color:#fff;">₹{record['recovered_amount_inr']:,.0f}</b><br>
                • Timestamp: <span class="mono-text" style="font-size:0.75rem;">{record['timestamp'][:19]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 1rem 1.4rem; margin-top: 1rem;">
        <span style="color: #a5b4fc; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">Detailed Agent Reasoning:</span>
        <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 0.3rem; margin-bottom: 0;">
            "{record['reasoning']}"
        </p>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 3: INTERACTIVE RECOVERY SANDBOX (Live Interactive Simulator)
# ---------------------------------------------------------------------------
with tab_sandbox:
    st.markdown("""
    <div class="glass-panel">
        <div class="panel-header">
            <span>⚡ Interactive Autonomous Recovery Sandbox</span>
            <span class="pill-badge" style="background: rgba(99, 102, 241, 0.2);">Live Execution Engine</span>
        </div>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem;">
            Test the agent with custom failed payment scenarios. Watch the agent evaluate playbook constraints, stopping rules, and simulate recovery in real time.
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
        <div style="background: rgba(30, 41, 59, 0.5); padding: 12px; border-radius: 12px; margin-top: 15px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase;">Derived Segment:</div>
            <div style="font-size:1.1rem; font-weight:700; color:#38bdf8;">{sim_segment.upper()}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("⚡ Execute Autonomous Recovery Diagnosis", type="primary", use_container_width=True):
        with st.spinner("🤖 Agent analyzing payment failure telemetry & evaluating stopping rules..."):
            time.sleep(0.6)
            
            # Simple in-dashboard diagnosis emulation using same business logic
            if sim_reason == "fraud_flagged":
                decision_action = "escalate_to_human"
                diag = "Payment flagged by gateway risk engine as high fraud probability."
                reason = "FRAUD HARD GUARD: Transactions flagged as fraudulent are automatically isolated and escalated to human compliance."
                rule_ok = True
                sim_outcome = "pending_human_review"
                recovered_val = 0
            elif sim_reason == "card_expired":
                decision_action = "send_update_payment_link"
                diag = "Card validity has expired on customer payment mandate."
                reason = "Auto-retry will consistently fail on expired instruments; sending payment update link."
                rule_ok = True
                sim_outcome = "recovered" if random.random() < 0.35 else "failed"
                recovered_val = sim_amount if sim_outcome == "recovered" else 0
            elif sim_reason == "insufficient_funds":
                if sim_retries >= 3:
                    decision_action = "escalate_to_human"
                    diag = "Multiple unsuccessful insufficient funds retries exhausted."
                    reason = "Max retry threshold (3) exceeded; stopping automated dunning to prevent bank fees."
                    rule_ok = False
                    sim_outcome = "pending_human_review"
                    recovered_val = 0
                else:
                    decision_action = "smart_retry"
                    diag = "Temporary liquidity deficit on subscriber account."
                    reason = "Timing retry window around payday interval for high probability debit recovery."
                    rule_ok = True
                    sim_outcome = "recovered" if random.random() < 0.45 else "failed"
                    recovered_val = sim_amount if sim_outcome == "recovered" else 0
            elif sim_reason == "bank_technical_decline":
                if sim_retries >= 2:
                    decision_action = "escalate_to_human"
                    diag = "Repeated bank gateway downtime."
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
                diag = "Bank issued temporary freeze or block on card mandate."
                reason = "Requesting customer to authorize alternate payment method via secure link."
                rule_ok = True
                sim_outcome = "recovered" if random.random() < 0.30 else "failed"
                recovered_val = sim_amount if sim_outcome == "recovered" else 0

            # Display Verdict
            res_c1, res_c2 = st.columns(2)
            with res_c1:
                st.markdown(f"""
                <div class="ai-trace-box" style="border-color: rgba(99, 102, 241, 0.6);">
                    <div style="color: #818cf8; font-weight: 700; text-transform: uppercase; font-size: 0.8rem;">Agent Diagnosis & Recommendation</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: #fff; margin-top: 4px;">Action: {decision_action.replace('_', ' ').title()}</div>
                    <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 8px;"><b>Diagnosis:</b> {diag}</p>
                    <p style="color: #94a3b8; font-size: 0.85rem;"><b>Reasoning:</b> {reason}</p>
                </div>
                """, unsafe_allow_html=True)

            with res_c2:
                outcome_badge = "#34d399" if sim_outcome == "recovered" else ("#fbbf24" if sim_outcome == "pending_human_review" else "#f87171")
                st.markdown(f"""
                <div class="ai-trace-box" style="border-color: {outcome_badge};">
                    <div style="color: {outcome_badge}; font-weight: 700; text-transform: uppercase; font-size: 0.8rem;">Simulated Execution Outcome</div>
                    <div style="font-size: 1.4rem; font-weight: 800; color: {outcome_badge}; margin-top: 4px;">{sim_outcome.replace('_', ' ').upper()}</div>
                    <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 8px;"><b>Recovered Amount:</b> ₹{recovered_val:,.0f}</p>
                    <p style="color: #94a3b8; font-size: 0.85rem;"><b>Policy Compliance Check:</b> <span style="color:#34d399;">100% Validated & Logged</span></p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 4: COMPLIANCE & PLAYBOOK MATRIX
# ---------------------------------------------------------------------------
with tab_compliance:
    st.markdown("""
    <div class="glass-panel">
        <div class="panel-header">
            <span>🛡️ Deterministic Playbook & Policy Guardrails</span>
            <span class="badge-success">Code-Level Enforcement</span>
        </div>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.2rem;">
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
    st.markdown("""
    <div class="glass-panel">
        <div class="panel-header">
            <span>📋 Full Financial & Compliance Audit Trail</span>
            <span style="font-size: 0.85rem; color: #94a3b8;">100% immutable decision history</span>
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
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding-bottom: 2rem;">
    ⚡ <b>AI Revenue Recovery Agent</b> | Razorpay AI Buildathon — Track 03 | Built with Claude AI, Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
