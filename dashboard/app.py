"""
app.py - Streamlit Dashboard for Revenue Recovery Agent
========================================================
Displays summary metrics, audit trail, and charts from the
pipeline's audit_trail.csv output.

Run:
  streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Revenue Recovery Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
AUDIT_FILE = Path(__file__).resolve().parent.parent / "logs" / "audit_trail.csv"

@st.cache_data
def load_audit_data():
    if not AUDIT_FILE.exists():
        return None
    df = pd.read_csv(AUDIT_FILE)
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df["recovered_amount_inr"] = pd.to_numeric(df["recovered_amount_inr"], errors="coerce")
    df["discount_cost_inr"] = pd.to_numeric(df["discount_cost_inr"], errors="coerce")
    return df

df = load_audit_data()

if df is None:
    st.error("⚠️ No audit trail found. Run `python -m src.run_batch` first.")
    st.stop()

# ---------------------------------------------------------------------------
# Custom CSS for premium look
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .main { font-family: 'Inter', sans-serif; }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-4px); }
    .metric-card h2 { margin: 0; font-size: 2.2rem; font-weight: 800; }
    .metric-card p { margin: 0.3rem 0 0; font-size: 0.9rem; opacity: 0.85; }

    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        box-shadow: 0 10px 40px rgba(17, 153, 142, 0.3);
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 10px 40px rgba(245, 87, 108, 0.3);
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 10px 40px rgba(79, 172, 254, 0.3);
    }
    .metric-card-amber {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        box-shadow: 0 10px 40px rgba(247, 151, 30, 0.3);
    }

    .header-container {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
    }
    .header-container h1 {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .header-container p { color: #a0a0b0; margin: 0.5rem 0 0; }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2d3748;
        margin: 1.5rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="header-container">
    <h1>💰 AI Revenue Recovery Agent</h1>
    <p>Razorpay AI Buildathon — Track 03 | Automated failed payment recovery with AI-powered diagnosis</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Top-line metrics
# ---------------------------------------------------------------------------
total_records = len(df)
total_at_risk = df["amount_inr"].sum()
total_recovered = df["recovered_amount_inr"].sum()
recovery_rate = (total_recovered / total_at_risk * 100) if total_at_risk > 0 else 0
escalated = len(df[df["final_action"] == "escalate_to_human"])
overrides = len(df[df["allowed_by_rules"] == "no"])

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h2>{total_records}</h2>
        <p>Records Processed</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card-green metric-card">
        <h2>₹{total_recovered:,.0f}</h2>
        <p>Amount Recovered</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card-blue metric-card">
        <h2>{recovery_rate:.1f}%</h2>
        <p>Recovery Rate</p>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card-orange metric-card">
        <h2>₹{total_at_risk:,.0f}</h2>
        <p>Total At Risk</p>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card-amber metric-card">
        <h2>{escalated}</h2>
        <p>Escalated to Human</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Charts row
# ---------------------------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown('<div class="section-header">📊 Recovery Rate by Intervention</div>', unsafe_allow_html=True)

    action_stats = df.groupby("final_action").agg(
        total=("simulated_outcome", "count"),
        recovered=("simulated_outcome", lambda x: (x == "recovered").sum()),
        amount_recovered=("recovered_amount_inr", "sum"),
    ).reset_index()
    action_stats["recovery_rate"] = (action_stats["recovered"] / action_stats["total"] * 100).round(1)

    colors = {
        "smart_retry": "#667eea",
        "send_update_payment_link": "#38ef7d",
        "offer_discount_retry": "#f093fb",
        "escalate_to_human": "#f7971e",
        "no_action_do_not_disturb": "#a0a0b0",
    }

    fig1 = px.bar(
        action_stats,
        x="final_action",
        y="recovery_rate",
        color="final_action",
        color_discrete_map=colors,
        text="recovery_rate",
        labels={"final_action": "Intervention", "recovery_rate": "Recovery Rate (%)"},
    )
    fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig1.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        yaxis=dict(range=[0, max(action_stats["recovery_rate"].max() * 1.3, 10)]),
        margin=dict(t=20, b=20),
        height=380,
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    st.markdown('<div class="section-header">🔍 Failure Reason Distribution</div>', unsafe_allow_html=True)

    reason_counts = df["failure_reason"].value_counts().reset_index()
    reason_counts.columns = ["failure_reason", "count"]

    reason_colors = {
        "insufficient_funds": "#f5576c",
        "card_expired": "#4facfe",
        "bank_technical_decline": "#f7971e",
        "card_blocked_by_bank": "#667eea",
        "fraud_flagged": "#ff4757",
    }

    fig2 = px.bar(
        reason_counts,
        x="failure_reason",
        y="count",
        color="failure_reason",
        color_discrete_map=reason_colors,
        text="count",
        labels={"failure_reason": "Failure Reason", "count": "Count"},
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        margin=dict(t=20, b=20),
        height=380,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------------------
# Second row of charts
# ---------------------------------------------------------------------------
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown('<div class="section-header">📈 Outcome Distribution</div>', unsafe_allow_html=True)

    outcome_counts = df["simulated_outcome"].value_counts().reset_index()
    outcome_counts.columns = ["outcome", "count"]

    outcome_colors = {"recovered": "#38ef7d", "failed": "#f5576c", "pending_human_review": "#f7971e", "no_recovery_attempted": "#a0a0b0"}

    fig3 = px.pie(
        outcome_counts,
        values="count",
        names="outcome",
        color="outcome",
        color_discrete_map=outcome_colors,
        hole=0.45,
    )
    fig3.update_layout(
        font=dict(family="Inter"),
        margin=dict(t=20, b=20),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig3, use_container_width=True)

with chart_col4:
    st.markdown('<div class="section-header">💰 Recovery by Customer Segment</div>', unsafe_allow_html=True)

    seg_stats = df.groupby("customer_segment").agg(
        at_risk=("amount_inr", "sum"),
        recovered=("recovered_amount_inr", "sum"),
    ).reset_index()
    seg_stats["recovery_pct"] = (seg_stats["recovered"] / seg_stats["at_risk"] * 100).round(1)

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(name="At Risk", x=seg_stats["customer_segment"], y=seg_stats["at_risk"], marker_color="#667eea", opacity=0.6))
    fig4.add_trace(go.Bar(name="Recovered", x=seg_stats["customer_segment"], y=seg_stats["recovered"], marker_color="#38ef7d"))
    fig4.update_layout(
        barmode="overlay",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        margin=dict(t=20, b=20),
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------------------------------
# Audit trail table
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">📋 Full Audit Trail</div>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.markdown("## 🔎 Filters")
selected_reasons = st.sidebar.multiselect(
    "Failure Reason",
    options=sorted(df["failure_reason"].unique()),
    default=sorted(df["failure_reason"].unique()),
)
selected_outcomes = st.sidebar.multiselect(
    "Outcome",
    options=sorted(df["simulated_outcome"].unique()),
    default=sorted(df["simulated_outcome"].unique()),
)
selected_actions = st.sidebar.multiselect(
    "Intervention",
    options=sorted(df["final_action"].unique()),
    default=sorted(df["final_action"].unique()),
)

filtered_df = df[
    (df["failure_reason"].isin(selected_reasons))
    & (df["simulated_outcome"].isin(selected_outcomes))
    & (df["final_action"].isin(selected_actions))
]

st.markdown(f"Showing **{len(filtered_df)}** of {total_records} records")

display_cols = [
    "subscription_id", "customer_id", "customer_segment",
    "failure_reason", "diagnosis", "chosen_action", "reasoning",
    "allowed_by_rules", "final_action", "simulated_outcome",
    "amount_inr", "recovered_amount_inr",
]

st.dataframe(
    filtered_df[display_cols],
    use_container_width=True,
    height=500,
    column_config={
        "amount_inr": st.column_config.NumberColumn("Amount (₹)", format="₹%.0f"),
        "recovered_amount_inr": st.column_config.NumberColumn("Recovered (₹)", format="₹%.0f"),
        "diagnosis": st.column_config.TextColumn("Diagnosis", width="large"),
        "reasoning": st.column_config.TextColumn("Reasoning", width="large"),
    },
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    '<div style="text-align:center; color:#888; font-size:0.85rem;">'
    "AI Revenue Recovery Agent | Razorpay AI Buildathon — Track 03 | "
    "Built with Claude AI + Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
