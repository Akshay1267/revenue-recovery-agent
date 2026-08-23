# 💰 AI Revenue Recovery Agent

> Razorpay AI Buildathon — Track 03: Revenue Recovery

An AI-powered agent that processes failed subscription payments, diagnoses root
causes using Claude AI, selects compliant recovery interventions, simulates
outcomes, and reports results with a full audit trail.

## 🏗️ Architecture

```
Data → Playbook → AI Agent (Claude) → Stopping Rules → Simulator → Audit Trail → Dashboard
```

See [docs/architecture.md](docs/architecture.md) for the full architecture diagram.

## 📊 Results

| Metric | Value |
|--------|-------|
| Records processed | 60 |
| ₹ at risk | ₹68,240 |
| ₹ recovered | ₹22,179 |
| Recovery rate | 32.5% |
| Fraud safety | ✅ 0 violations |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- An Anthropic API key

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd revenue-recovery-agent

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your-api-key-here
```

### Run the Pipeline

```bash
# Step 1: Generate synthetic data (optional — already included)
python data/generate_data.py

# Step 2: Run the full recovery pipeline
python -m src.run_batch

# Step 3: Launch the dashboard
streamlit run dashboard/app.py
```

## 📁 Project Structure

```
revenue-recovery-agent/
├── data/
│   ├── generate_data.py          # Synthetic dataset generator
│   └── failed_subscriptions.csv  # Generated dataset (60 records)
├── src/
│   ├── playbook.py               # Deterministic rules engine
│   ├── agent.py                  # Claude AI diagnosis & decision
│   ├── simulate.py               # Probabilistic outcome simulator
│   ├── stopping_rules.py         # Compliance enforcement
│   └── run_batch.py              # Full pipeline orchestrator
├── logs/
│   └── audit_trail.csv           # Complete audit trail
├── dashboard/
│   └── app.py                    # Streamlit dashboard
├── docs/
│   ├── architecture.md           # Architecture documentation
│   └── report.md                 # Results report
├── requirements.txt
├── .env.example
└── README.md
```

## 🔒 Safety & Compliance

- **Fraud cases** are NEVER auto-retried — enforced in code, not just prompts
- **LLM constrained** to playbook-allowed actions with code-level validation
- **Stopping rules** enforce max retries, cooldowns, and daily contact limits
- **Full audit trail** logs every decision with reasoning for compliance review

## 🛠️ Tech Stack

- **Python 3.11+** — Core runtime
- **Claude AI** (claude-sonnet-4-20250514) — Diagnosis & decision engine
- **pandas** — Data handling
- **Streamlit + Plotly** — Interactive dashboard
- **Anthropic SDK** — Claude API integration

## 📄 License

Built for the Razorpay AI Buildathon.
