"""
simulate.py - Outcome Simulator for Recovery Interventions
==========================================================
Simulates realistic success/fail outcomes for each chosen intervention
using predefined probability tables.

Uses random.seed() for reproducibility across runs.

Probability rationale:
  - smart_retry on insufficient_funds: 40% — customer may have funds later
  - smart_retry on bank_technical_decline: 65% — transient error, high success
  - send_update_payment_link: 30% — requires customer action, lower conversion
  - offer_discount_retry: 55% — discount incentivizes, but not guaranteed
  - escalate_to_human: tracked as "pending_human_review" (not auto-resolved)
  - no_action_do_not_disturb: always "no_recovery_attempted"
"""

import random

# ---------------------------------------------------------------------------
# Simulation seed for reproducibility
# ---------------------------------------------------------------------------
SIMULATION_SEED = 123

# ---------------------------------------------------------------------------
# Success probability table: (action, failure_reason) -> probability
# ---------------------------------------------------------------------------
SUCCESS_PROBABILITIES = {
    # smart_retry success varies by failure type
    ("smart_retry", "insufficient_funds"): 0.40,
    ("smart_retry", "bank_technical_decline"): 0.65,
    # smart_retry on other reasons (shouldn't happen per playbook, but safe default)
    ("smart_retry", "card_expired"): 0.02,  # almost never works
    ("smart_retry", "card_blocked_by_bank"): 0.05,
    ("smart_retry", "fraud_flagged"): 0.0,  # should never be called

    # send_update_payment_link — requires customer to act
    ("send_update_payment_link", "card_expired"): 0.30,
    ("send_update_payment_link", "card_blocked_by_bank"): 0.25,
    ("send_update_payment_link", "insufficient_funds"): 0.20,

    # offer_discount_retry — incentive helps
    ("offer_discount_retry", "insufficient_funds"): 0.55,
    ("offer_discount_retry", "card_expired"): 0.15,  # discount doesn't fix expired card

    # Default fallback for unlisted combinations
    "_default": 0.10,
}

# Discount cost as fraction of amount (for false-positive cost estimation)
DISCOUNT_PERCENTAGE = 0.10  # 10% discount offered


def _get_success_probability(action: str, failure_reason: str) -> float:
    """Look up the success probability for an (action, failure_reason) pair."""
    return SUCCESS_PROBABILITIES.get(
        (action, failure_reason),
        SUCCESS_PROBABILITIES["_default"]
    )


def simulate_outcome(
    record: dict,
    chosen_action: str,
    rng: random.Random | None = None,
) -> dict:
    """
    Simulate the outcome of a recovery intervention.

    Parameters
    ----------
    record : dict
        The subscription record.
    chosen_action : str
        The intervention action to simulate.
    rng : random.Random, optional
        A seeded Random instance for reproducibility.

    Returns
    -------
    dict with keys:
        simulated_outcome   : str   — "recovered", "failed", "pending_human_review",
                                       or "no_recovery_attempted"
        recovered_amount_inr: float — amount recovered (0 if not recovered)
        discount_cost_inr   : float — cost of discount if offer_discount_retry was used
        success_probability : float — the probability used for simulation
    """
    amount = float(record["amount_inr"])

    if rng is None:
        rng = random.Random()

    # ---- Special outcomes that don't depend on probability ----
    if chosen_action == "escalate_to_human":
        return {
            "simulated_outcome": "pending_human_review",
            "recovered_amount_inr": 0.0,
            "discount_cost_inr": 0.0,
            "success_probability": 0.0,
        }

    if chosen_action == "no_action_do_not_disturb":
        return {
            "simulated_outcome": "no_recovery_attempted",
            "recovered_amount_inr": 0.0,
            "discount_cost_inr": 0.0,
            "success_probability": 0.0,
        }

    # ---- Probabilistic simulation ----
    prob = _get_success_probability(chosen_action, record["failure_reason"])
    roll = rng.random()
    success = roll < prob

    if success:
        recovered = amount
        discount_cost = 0.0

        # If discount was offered, reduce recovered amount and track cost
        if chosen_action == "offer_discount_retry":
            discount_cost = amount * DISCOUNT_PERCENTAGE
            recovered = amount - discount_cost  # net recovery after discount

        return {
            "simulated_outcome": "recovered",
            "recovered_amount_inr": recovered,
            "discount_cost_inr": discount_cost,
            "success_probability": prob,
        }
    else:
        discount_cost = 0.0
        # Even failed discount offers have a cost (discount was promised)
        if chosen_action == "offer_discount_retry":
            # Assume 20% of failed discount attempts still incur some cost
            # (e.g., coupon already issued but payment still failed)
            discount_cost = amount * DISCOUNT_PERCENTAGE * 0.20

        return {
            "simulated_outcome": "failed",
            "recovered_amount_inr": 0.0,
            "discount_cost_inr": discount_cost,
            "success_probability": prob,
        }


def simulate_batch(
    records: list[dict],
    decisions: list[dict],
    seed: int = SIMULATION_SEED,
) -> list[dict]:
    """
    Simulate outcomes for a batch of records and their agent decisions.

    Parameters
    ----------
    records : list[dict]
        The subscription records.
    decisions : list[dict]
        The agent decisions (from agent.py), matched by subscription_id.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    list[dict] : Simulation results aligned with input records.
    """
    rng = random.Random(seed)

    # Index decisions by subscription_id
    decision_map = {d["subscription_id"]: d for d in decisions}

    results = []
    for record in records:
        sid = record["subscription_id"]
        decision = decision_map.get(sid)

        if decision is None:
            results.append({
                "simulated_outcome": "no_decision",
                "recovered_amount_inr": 0.0,
                "discount_cost_inr": 0.0,
                "success_probability": 0.0,
            })
            continue

        outcome = simulate_outcome(record, decision["chosen_action"], rng)
        results.append(outcome)

    return results


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_record = {
        "subscription_id": "sub_test",
        "amount_inr": "999",
        "failure_reason": "insufficient_funds",
    }

    rng = random.Random(42)
    print("Simulating 10 smart_retry outcomes for insufficient_funds (Rs 999):")
    successes = 0
    for i in range(10):
        result = simulate_outcome(test_record, "smart_retry", rng)
        status = result["simulated_outcome"]
        recovered = result["recovered_amount_inr"]
        print(f"  Trial {i+1}: {status} (recovered Rs {recovered})")
        if status == "recovered":
            successes += 1
    print(f"\nSuccess rate: {successes}/10 = {successes*10}%")

    # Test escalation
    result = simulate_outcome(test_record, "escalate_to_human")
    assert result["simulated_outcome"] == "pending_human_review"
    print("\n[PASS] Escalation returns pending_human_review")

    # Test no action
    result = simulate_outcome(test_record, "no_action_do_not_disturb")
    assert result["simulated_outcome"] == "no_recovery_attempted"
    print("[PASS] No action returns no_recovery_attempted")

    print("\nAll simulation tests passed.")
