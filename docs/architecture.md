# Architecture — AI Revenue Recovery Agent

## Overview

The AI Revenue Recovery Agent is an end-to-end pipeline that processes failed
subscription payments, diagnoses root causes using AI, selects compliant recovery
interventions, and simulates outcomes with a full audit trail.

## Pipeline Flow

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Synthetic Data  │────▶│   Playbook   │────▶│   AI Agent      │
│  Generator       │     │  (Rules)     │     │  (Claude API)   │
│                  │     │              │     │                 │
│ 60 failed        │     │ Maps failure │     │ Diagnoses root  │
│ subscription     │     │ reasons to   │     │ cause, picks    │
│ records          │     │ allowed      │     │ intervention    │
│                  │     │ actions      │     │ from allowed    │
└─────────────────┘     └──────────────┘     │ list only       │
                                              └────────┬────────┘
                                                       │
                                                       ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Dashboard      │◀────│  Audit Trail │◀────│ Stopping Rules  │
│  (Streamlit)     │     │  (CSV Log)   │     │                 │
│                  │     │              │     │ Max retries,    │
│ Metrics, charts, │     │ Every record │     │ cooldowns,      │
│ filterable table │     │ logged with  │     │ fraud blocks,   │
│                  │     │ full context │     │ rate limits     │
└─────────────────┘     └──────────────┘     └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   Simulator     │
                                              │                 │
                                              │ Probabilistic   │
                                              │ outcome per     │
                                              │ intervention    │
                                              └─────────────────┘
```

## Component Details

### 1. Data Generator (`data/generate_data.py`)
- Generates 60 synthetic failed subscription records
- Realistic distribution: insufficient_funds (35%), card_expired (25%),
  bank_technical_decline (20%), card_blocked_by_bank (15%), fraud_flagged (5%)
- Derives customer segments (high_value, standard, at_risk) from tenure and history

### 2. Playbook (`src/playbook.py`)
- Pure deterministic Python — NO LLM involved
- Maps each failure_reason to allowed intervention actions
- Defines max retries and cooldown periods per failure type
- Provides validation functions used as hard guards

### 3. AI Agent (`src/agent.py`)
- Calls Claude (claude-sonnet-4-20250514) for each record
- System prompt constrains the LLM to only pick from playbook-allowed actions
- JSON-structured output with diagnosis, chosen_action, and reasoning
- Hard guard: fraud-flagged cases bypass the LLM entirely and auto-escalate
- Fallback logic for JSON parse errors and API failures

### 4. Stopping Rules (`src/stopping_rules.py`)
- Code-level enforcement (not prompt-level):
  - Max retry attempts per failure type
  - Cooldown periods between retries
  - Auto-escalation when retries exhausted
  - **HARD BLOCK**: fraud cases can only be escalated
  - Max 1 customer contact per day
- Returns override actions when original action is blocked

### 5. Outcome Simulator (`src/simulate.py`)
- Probabilistic simulation with seeded RNG for reproducibility
- Realistic success rates per (action, failure_reason) pair
- Tracks discount costs for false-positive analysis
- Escalations logged as "pending_human_review" (not auto-resolved)

### 6. Orchestrator (`src/run_batch.py`)
- Wires all components into a single pipeline
- Produces `logs/audit_trail.csv` with full record of every decision
- Prints summary metrics at completion

### 7. Dashboard (`dashboard/app.py`)
- Streamlit app with top-line metrics, charts, and filterable audit trail
- Recovery rate by intervention, failure reason distribution, outcome breakdown
- Sidebar filters for failure reason, outcome, and intervention type

## Key Design Decisions

1. **LLM Constrained by Code**: The playbook and stopping rules are enforced in
   Python code, not just in prompts. Even if the LLM hallucinated an invalid action,
   it would be overridden.

2. **Fraud Safety**: Fraud-flagged cases never reach the LLM at all — they are
   intercepted in code and always escalated.

3. **Reproducibility**: Both data generation and outcome simulation use fixed
   random seeds for consistent results across runs.

4. **Audit Trail**: Every record includes the original input, AI diagnosis, chosen
   action, rule validation result, final action (after any override), and simulated
   outcome — creating a complete audit trail for compliance review.
