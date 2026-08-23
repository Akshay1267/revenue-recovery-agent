# 💰 AI Revenue Recovery Agent

> **Razorpay AI Buildathon — Track 03: Revenue Recovery**  
> Autonomous, compliance-bounded payment recovery system powered by Claude AI, deterministic guardrails, and real-time audit logging.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-brightgreen?style=for-the-badge&logo=render)](https://revenue-recovery-agent.onrender.com)
[![Kaggle Dataset](https://img.shields.io/badge/Kaggle-Dataset-blue?style=for-the-badge&logo=kaggle)](https://www.kaggle.com/datasets/akshayjain1267/subscription-payment-failures-and-ai-audit-trail)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/Akshay1267/revenue-recovery-agent)

---

## 🌐 Quick Links
- 🚀 **Live Dashboard:** [https://revenue-recovery-agent.onrender.com](https://revenue-recovery-agent.onrender.com)
- 📊 **Kaggle Dataset:** [Subscription Payment Failures & AI Recovery Audit Trail](https://www.kaggle.com/datasets/akshayjain1267/subscription-payment-failures-and-ai-audit-trail)
- 📖 **Architecture Docs:** [docs/architecture.md](docs/architecture.md)
- 📈 **Metrics Report:** [docs/report.md](docs/report.md)

---

## 🏗️ Agentic Architecture

Unlike naive dunning scripts that blindly retry failed transactions, this agent operates on a continuous cognitive loop:

`
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Failed Payment │────▶│   Playbook   │────▶│   AI Agent      │
│  State & Context│     │  (Policy)    │     │  (Claude AI)    │
│                 │     │              │     │                 │
│ 60 failed       │     │ Strict action│     │ Diagnoses root  │
│ subscriptions   │     │ bounds per   │     │ cause, picks    │
│ with history    │     │ failure code │     │ optimal action  │
└─────────────────┘     └──────────────┘     └────────┬────────┘
                                                      │
                                                      ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Live Dashboard  │◀────│  Audit Trail │◀────│ Stopping Rules  │
│ (Streamlit Web) │     │ (Full Memory)│     │  (Supervisor)   │
│                 │     │              │     │                 │
│ KPIs, charts,   │     │ 100% auditable│    │ Fraud guards,   │
│ multi-filters   │     │ compliance   │     │ max retries,    │
└─────────────────┘     └──────────────┘     │ anti-spam caps  │
                                             └────────┬────────┘
                                                      │
                                                      ▼
                                             ┌─────────────────┐
                                             │    Simulator    │
                                             │                 │
                                             │ Realistic       │
                                             │ probabilistic   │
                                             │ outcomes & ROI  │
                                             └─────────────────┘
`

---

## 📊 Measured Benchmark Results

| Metric | Result |
|---|---|
| **Total Records Processed** | 60 |
| **Total ₹ at Risk** | **₹68,240** |
| **Total ₹ Recovered** | **₹22,179** |
| **Recovery Rate** | **32.5%** |
| **Fraud Cases Auto-Retried** | **0 ✅ (100% Compliant)** |
| **Stopping Rule Overrides** | 6 invalid retry attempts blocked |
| **Escalated to Human Review** | 9 records |

### Recovery Performance by Action
- **smart_retry**: 44.4% success rate (₹8,588 recovered)
- **send_update_payment_link**: 37.5% success rate (₹13,591 recovered)
- **scalate_to_human**: Pending human review

---

## 🚀 Quick Start & Local Run

### 1. Installation
`ash
git clone https://github.com/Akshay1267/revenue-recovery-agent.git
cd revenue-recovery-agent
pip install -r requirements.txt
`

### 2. Configuration
Create a .env file in the project root:
`nv
ANTHROPIC_API_KEY=your-api-key-here
`

### 3. Run Pipeline & Dashboard
`ash
# Step 1: Generate synthetic dataset (or use data/failed_subscriptions.csv)
python data/generate_data.py

# Step 2: Run end-to-end AI batch pipeline
python -m src.run_batch

# Step 3: Launch Streamlit dashboard
streamlit run dashboard/app.py
`

---

## 📁 Project Structure

`
revenue-recovery-agent/
├── data/
│   ├── generate_data.py          # Synthetic dataset generator
│   └── failed_subscriptions.csv  # 60 failed records benchmark
├── src/
│   ├── playbook.py               # Deterministic rulebook (action boundaries)
│   ├── agent.py                  # Claude AI diagnosis & decision engine
│   ├── simulate.py               # Probabilistic recovery outcome simulator
│   ├── stopping_rules.py         # Compliance & safety guardrails
│   └── run_batch.py              # Full orchestrator
├── logs/
│   └── audit_trail.csv           # Complete compliance audit trail
├── dashboard/
│   └── app.py                    # Streamlit visual dashboard
├── docs/
│   ├── architecture.md           # Deep-dive architecture design
│   └── report.md                 # Evaluation & metrics report
├── requirements.txt
├── .env.example
└── README.md
`

---

## 🔒 Safety & Enterprise Compliance

1. **Deterministic Guardrails:** The LLM cannot hallucinate actions outside the predefined Playbook.
2. **Hard Fraud Interception:** Fraud-flagged transactions never touch retries or customer communication channels.
3. **Anti-Spam Rate Limits:** Max 1 customer notification per 24 hours.
4. **Full Financial Auditability:** Every decision records the raw input, LLM reasoning, safety validation, and outcome.

---

## 📄 License & Attribution
Built for the **Razorpay AI Buildathon — Track 03 (Revenue Recovery)**.