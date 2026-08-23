"""
run_batch.py - Full Pipeline Orchestrator
==========================================
Wires together all pipeline stages:
  1. Load failed subscription data from CSV
  2. For each record, get diagnosis + decision from the AI agent
  3. Validate each decision against stopping rules
  4. Simulate outcome for each intervention
  5. Log everything to audit_trail.csv
  6. Print summary metrics

Usage:
  python -m src.run_batch
"""

import csv
import sys
import time
from datetime import datetime
from pathlib import Path

from src.agent import diagnose_batch
from src.playbook import get_allowed_actions, validate_action, is_fraud_case
from src.stopping_rules import check_action_allowed
from src.simulate import simulate_outcome, SIMULATION_SEED

import random


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "failed_subscriptions.csv"
AUDIT_FILE = PROJECT_ROOT / "logs" / "audit_trail.csv"

AUDIT_COLUMNS = [
    "subscription_id",
    "customer_id",
    "customer_segment",
    "failure_reason",
    "diagnosis",
    "chosen_action",
    "reasoning",
    "allowed_by_rules",
    "rule_override_reason",
    "final_action",
    "simulated_outcome",
    "amount_inr",
    "recovered_amount_inr",
    "discount_cost_inr",
    "timestamp",
]


def load_data(filepath: Path) -> list[dict]:
    """Load the failed subscriptions CSV into a list of dicts."""
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    # Convert numeric fields
    for r in records:
        r["amount_inr"] = float(r["amount_inr"])
        r["customer_tenure_months"] = int(r["customer_tenure_months"])
        r["days_since_failure"] = int(r["days_since_failure"])
        r["past_successful_payments"] = int(r["past_successful_payments"])
        r["retry_attempts_so_far"] = int(r["retry_attempts_so_far"])

    return records


def run_pipeline():
    """Execute the full revenue recovery pipeline."""
    print("=" * 70)
    print("  AI Revenue Recovery Agent — Batch Pipeline")
    print("=" * 70)
    start_time = time.time()

    # ---- Step 1: Load data ----
    print(f"\n[1/5] Loading data from {DATA_FILE}...")
    if not DATA_FILE.exists():
        print(f"ERROR: Data file not found at {DATA_FILE}")
        print("Run 'python data/generate_data.py' first.")
        sys.exit(1)

    records = load_data(DATA_FILE)
    total_at_risk = sum(r["amount_inr"] for r in records)
    print(f"  Loaded {len(records)} records | Total at risk: Rs {total_at_risk:,.0f}")

    # ---- Step 2: AI Agent diagnosis + decision ----
    print(f"\n[2/5] Running AI agent diagnosis on {len(records)} records...")
    print("  (This calls Claude API — please wait)\n")
    decisions = diagnose_batch(records)
    print(f"\n  Agent completed {len(decisions)} diagnoses.")

    # ---- Step 3: Apply stopping rules + simulate outcomes ----
    print(f"\n[3/5] Applying stopping rules...")
    print(f"[4/5] Simulating outcomes...\n")

    rng = random.Random(SIMULATION_SEED)
    audit_rows = []
    timestamp = datetime.now().isoformat()

    for record, decision in zip(records, decisions):
        chosen_action = decision["chosen_action"]

        # Check stopping rules
        rule_check = check_action_allowed(record, chosen_action)
        allowed = rule_check["allowed"]
        final_action = chosen_action if allowed else rule_check["override_action"]

        # If action was overridden, note it
        rule_override_reason = "" if allowed else rule_check["reason"]

        # Simulate outcome for the FINAL action (after any override)
        outcome = simulate_outcome(record, final_action, rng)

        audit_row = {
            "subscription_id": record["subscription_id"],
            "customer_id": record["customer_id"],
            "customer_segment": record["customer_segment"],
            "failure_reason": record["failure_reason"],
            "diagnosis": decision["diagnosis"],
            "chosen_action": chosen_action,
            "reasoning": decision["reasoning"],
            "allowed_by_rules": "yes" if allowed else "no",
            "rule_override_reason": rule_override_reason,
            "final_action": final_action,
            "simulated_outcome": outcome["simulated_outcome"],
            "amount_inr": record["amount_inr"],
            "recovered_amount_inr": outcome["recovered_amount_inr"],
            "discount_cost_inr": outcome["discount_cost_inr"],
            "timestamp": timestamp,
        }
        audit_rows.append(audit_row)

    # ---- Step 4: Write audit trail ----
    print(f"[5/5] Writing audit trail to {AUDIT_FILE}...")
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(audit_rows)
    print(f"  Audit trail saved: {len(audit_rows)} rows.")

    # ---- Step 5: Print summary ----
    elapsed = time.time() - start_time
    print_summary(audit_rows, total_at_risk, elapsed)


def print_summary(audit_rows: list[dict], total_at_risk: float, elapsed: float):
    """Print the final metrics summary."""
    total_records = len(audit_rows)
    total_recovered = sum(float(r["recovered_amount_inr"]) for r in audit_rows)
    total_discount_cost = sum(float(r["discount_cost_inr"]) for r in audit_rows)
    recovery_rate = (total_recovered / total_at_risk * 100) if total_at_risk > 0 else 0

    # Count outcomes
    outcomes = {}
    for r in audit_rows:
        o = r["simulated_outcome"]
        outcomes[o] = outcomes.get(o, 0) + 1

    # Count by action
    action_stats = {}
    for r in audit_rows:
        action = r["final_action"]
        if action not in action_stats:
            action_stats[action] = {"total": 0, "recovered": 0, "amount_recovered": 0.0}
        action_stats[action]["total"] += 1
        if r["simulated_outcome"] == "recovered":
            action_stats[action]["recovered"] += 1
            action_stats[action]["amount_recovered"] += float(r["recovered_amount_inr"])

    # Count overrides
    overrides = sum(1 for r in audit_rows if r["allowed_by_rules"] == "no")

    # Count escalations
    escalated = sum(1 for r in audit_rows if r["final_action"] == "escalate_to_human")

    # Fraud safety check
    fraud_retried = sum(
        1 for r in audit_rows
        if r["failure_reason"] == "fraud_flagged"
        and r["final_action"] not in ("escalate_to_human", "no_action_do_not_disturb")
    )

    print("\n" + "=" * 70)
    print("  REVENUE RECOVERY SUMMARY")
    print("=" * 70)

    print(f"""
  Total records processed  : {total_records}
  Total Rs at risk         : Rs {total_at_risk:>12,.0f}
  Total Rs recovered       : Rs {total_recovered:>12,.0f}
  Recovery rate            : {recovery_rate:>11.1f}%
  Net recovered (after     : Rs {total_recovered - total_discount_cost:>12,.0f}
    discount costs)
  Total discount cost      : Rs {total_discount_cost:>12,.0f}
  Records escalated to     : {escalated:>11d}
    human review
  Stopping rule overrides  : {overrides:>11d}
  Fraud cases auto-retried : {fraud_retried:>11d} {'(PASS - zero is correct)' if fraud_retried == 0 else '*** VIOLATION ***'}
  Pipeline time            : {elapsed:>10.1f}s
""")

    print("  --- Outcome Distribution ---")
    for outcome, count in sorted(outcomes.items(), key=lambda x: -x[1]):
        pct = count / total_records * 100
        print(f"    {outcome:<25s} {count:>3d}  ({pct:5.1f}%)")

    print("\n  --- Recovery Rate by Intervention ---")
    print(f"    {'Action':<30s} {'Total':>5s} {'Recov':>5s} {'Rate':>7s} {'Rs Recovered':>14s}")
    print(f"    {'-'*30} {'-'*5} {'-'*5} {'-'*7} {'-'*14}")
    for action in sorted(action_stats.keys()):
        stats = action_stats[action]
        rate = (stats["recovered"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(
            f"    {action:<30s} {stats['total']:>5d} {stats['recovered']:>5d} "
            f"{rate:>6.1f}% Rs {stats['amount_recovered']:>10,.0f}"
        )

    print("\n  --- False-Positive Cost Analysis ---")
    # Estimate: discount offers to customers who would have paid anyway
    # In real production, this would use churn prediction models.
    # Here we approximate: 30% of successful discount recoveries might
    # have paid at full price anyway (false positives).
    discount_recoveries = sum(
        1 for r in audit_rows
        if r["final_action"] == "offer_discount_retry"
        and r["simulated_outcome"] == "recovered"
    )
    estimated_false_positives = int(discount_recoveries * 0.30)
    fp_cost = estimated_false_positives * total_discount_cost / max(1, discount_recoveries) if discount_recoveries > 0 else 0

    print(f"    Discount offers made         : {sum(1 for r in audit_rows if r['final_action'] == 'offer_discount_retry')}")
    print(f"    Discount recoveries          : {discount_recoveries}")
    print(f"    Est. false positives (~30%)   : {estimated_false_positives}")
    print(f"    Est. false-positive cost      : Rs {fp_cost:,.0f}")
    print(f"    Total discount cost incurred  : Rs {total_discount_cost:,.0f}")

    print("\n" + "=" * 70)
    print("  Pipeline complete. See logs/audit_trail.csv for full details.")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline()
