"""
generate_data.py - Synthetic Failed Subscription Dataset Generator
==================================================================
Generates 60 realistic failed-subscription payment records for the
AI Revenue Recovery Agent pipeline.

Distribution targets:
  - card_expired:            ~25%  (15 records)
  - insufficient_funds:      ~35%  (21 records)
  - bank_technical_decline:  ~20%  (12 records)
  - fraud_flagged:           ~5%   (3 records)
  - card_blocked_by_bank:    ~15%  (9 records)

Run:  python data/generate_data.py
"""

import csv
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED = 42
NUM_RECORDS = 60
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "failed_subscriptions.csv"

# Failure reason distribution (must sum to NUM_RECORDS)
FAILURE_DISTRIBUTION = {
    "insufficient_funds": 21,
    "card_expired": 15,
    "bank_technical_decline": 12,
    "card_blocked_by_bank": 9,
    "fraud_flagged": 3,
}

# Subscription amount buckets (INR) - weighted to look realistic
AMOUNT_BUCKETS = [
    (199, 0.15),
    (299, 0.20),
    (499, 0.20),
    (999, 0.18),
    (1499, 0.10),
    (1999, 0.08),
    (2999, 0.05),
    (4999, 0.04),
]

COLUMNS = [
    "subscription_id",
    "customer_id",
    "customer_tenure_months",
    "amount_inr",
    "failure_reason",
    "days_since_failure",
    "past_successful_payments",
    "retry_attempts_so_far",
    "customer_segment",
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def weighted_choice(items_with_weights):
    """Pick a value from a list of (value, weight) tuples."""
    values, weights = zip(*items_with_weights)
    return random.choices(values, weights=weights, k=1)[0]


def derive_segment(tenure, past_payments):
    """
    Derive customer segment from tenure and payment history.
      - high_value:  long tenure (>18 mo) AND decent payment record (>12)
      - at_risk:     short tenure (<6 mo) OR very few past payments (<3)
      - standard:    everyone else
    """
    if tenure > 18 and past_payments > 12:
        return "high_value"
    elif tenure < 6 or past_payments < 3:
        return "at_risk"
    else:
        return "standard"


def generate_record(idx, failure_reason):
    """Generate one synthetic failed-subscription record."""
    subscription_id = f"sub_{idx:04d}"
    customer_id = f"cust_{random.randint(1000, 9999)}"

    # Tenure: 1-48 months, skewed toward mid-range
    tenure = max(1, min(48, int(random.gauss(18, 10))))

    # Amount: weighted bucket selection
    amount = weighted_choice(AMOUNT_BUCKETS)

    # Days since failure: 0-14, most failures are recent
    days_since = max(0, min(14, int(random.expovariate(0.25))))

    # Past successful payments: loosely correlated with tenure
    max_payments = min(36, tenure * 2)
    past_payments = random.randint(0, max(0, max_payments))

    # Retry attempts so far: 0-3 (most have not been retried yet)
    retry_attempts = random.choices(
        [0, 1, 2, 3], weights=[0.50, 0.25, 0.15, 0.10], k=1
    )[0]

    # Fraud-flagged records should look suspicious: low tenure, few payments
    if failure_reason == "fraud_flagged":
        tenure = random.randint(1, 4)
        past_payments = random.randint(0, 2)
        retry_attempts = 0  # should never have been retried

    segment = derive_segment(tenure, past_payments)

    return {
        "subscription_id": subscription_id,
        "customer_id": customer_id,
        "customer_tenure_months": tenure,
        "amount_inr": amount,
        "failure_reason": failure_reason,
        "days_since_failure": days_since,
        "past_successful_payments": past_payments,
        "retry_attempts_so_far": retry_attempts,
        "customer_segment": segment,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    random.seed(SEED)

    # Build the full list of failure reasons according to distribution
    failure_reasons = []
    for reason, count in FAILURE_DISTRIBUTION.items():
        failure_reasons.extend([reason] * count)
    random.shuffle(failure_reasons)

    assert len(failure_reasons) == NUM_RECORDS, (
        f"Distribution sums to {len(failure_reasons)}, expected {NUM_RECORDS}"
    )

    # Generate records
    records = []
    for idx, reason in enumerate(failure_reasons, start=1):
        records.append(generate_record(idx, reason))

    # Write CSV
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)

    # -----------------------------------------------------------------------
    # Print summary
    # -----------------------------------------------------------------------
    print(f"Generated {NUM_RECORDS} records -> {OUTPUT_FILE}")
    print()

    # Failure reason distribution
    reason_counts = {}
    amount_total = 0
    segment_counts = {}
    for r in records:
        reason_counts[r["failure_reason"]] = reason_counts.get(r["failure_reason"], 0) + 1
        amount_total += r["amount_inr"]
        segment_counts[r["customer_segment"]] = segment_counts.get(r["customer_segment"], 0) + 1

    print("--- Failure Reason Distribution ---")
    for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
        pct = count / NUM_RECORDS * 100
        print(f"  {reason:<28s} {count:>3d}  ({pct:5.1f}%)")

    print(f"\n--- Total INR at Risk ---")
    print(f"  Rs {amount_total:,.0f}")

    print(f"\n--- Customer Segment Distribution ---")
    for seg, count in sorted(segment_counts.items(), key=lambda x: -x[1]):
        pct = count / NUM_RECORDS * 100
        print(f"  {seg:<15s} {count:>3d}  ({pct:5.1f}%)")

    print(f"\n--- Retry Attempts So Far ---")
    retry_counts = {}
    for r in records:
        retry_counts[r["retry_attempts_so_far"]] = retry_counts.get(r["retry_attempts_so_far"], 0) + 1
    for attempts in sorted(retry_counts):
        print(f"  {attempts} retries:  {retry_counts[attempts]:>3d} records")

    print("\nDone. Inspect data/failed_subscriptions.csv before proceeding to Step 2.")


if __name__ == "__main__":
    main()
