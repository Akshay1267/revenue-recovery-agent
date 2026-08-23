"""
playbook.py - Deterministic Recovery Intervention Rulebook
==========================================================
Maps each failure_reason to:
  - Allowed intervention options
  - Max retry attempts permitted
  - Cooldown period (days) between retries

This file is pure deterministic logic — NO LLM calls.
The agent (agent.py) must only choose from the options this playbook allows.

Interventions available in the system:
  - "smart_retry"                : Auto-retry the payment via gateway
  - "send_update_payment_link"   : Email/SMS the customer a link to update card
  - "offer_discount_retry"       : Offer a small discount and retry
  - "escalate_to_human"          : Flag for manual human review
  - "no_action_do_not_disturb"   : Do nothing, respect the customer
"""

# ---------------------------------------------------------------------------
# Playbook rules: one entry per failure_reason
# ---------------------------------------------------------------------------
# Each entry defines:
#   allowed_actions : list[str]   — actions the agent may choose from
#   max_retries     : int         — total retry attempts allowed (across all time)
#   cooldown_days   : int         — minimum days between successive retries
#   notes           : str         — human-readable rationale

PLAYBOOK = {
    "card_expired": {
        "allowed_actions": ["send_update_payment_link"],
        "max_retries": 0,  # retrying a dead card is pointless
        "cooldown_days": 0,
        "notes": (
            "Card is expired — auto-retry will always fail. "
            "Only action is to ask the customer to update their payment method."
        ),
    },
    "insufficient_funds": {
        "allowed_actions": [
            "smart_retry",
            "offer_discount_retry",
            "send_update_payment_link",
        ],
        "max_retries": 3,
        "cooldown_days": 2,  # wait 2 days hoping funds arrive
        "notes": (
            "Customer may get paid / top up within a few days. "
            "Smart retry timed to likely payday is the primary strategy. "
            "Discount retry is a fallback for at-risk customers."
        ),
    },
    "bank_technical_decline": {
        "allowed_actions": ["smart_retry"],
        "max_retries": 2,
        "cooldown_days": 0,  # transient issue, can retry same day
        "notes": (
            "Likely a transient gateway/bank error. "
            "Quick retry usually succeeds. Keep attempts low to avoid spam."
        ),
    },
    "fraud_flagged": {
        # HARD RULE: fraud-flagged payments must NEVER be auto-retried.
        # Only action is to escalate to a human fraud analyst.
        "allowed_actions": ["escalate_to_human"],
        "max_retries": 0,
        "cooldown_days": 0,
        "notes": (
            "FRAUD ALERT — never retry, never contact the customer directly. "
            "Immediately escalate to the fraud/compliance team for review."
        ),
    },
    "card_blocked_by_bank": {
        "allowed_actions": ["send_update_payment_link", "escalate_to_human"],
        "max_retries": 0,  # blocked card won't unblock via retry
        "cooldown_days": 0,
        "notes": (
            "Card has been blocked by the issuing bank. "
            "Ask customer to update payment method. "
            "Escalate high-value customers to retain them."
        ),
    },
}

# All valid actions in the system (for validation)
ALL_VALID_ACTIONS = {
    "smart_retry",
    "send_update_payment_link",
    "offer_discount_retry",
    "escalate_to_human",
    "no_action_do_not_disturb",
}


def get_allowed_actions(failure_reason: str) -> list[str]:
    """Return the list of allowed intervention actions for a given failure reason."""
    entry = PLAYBOOK.get(failure_reason)
    if entry is None:
        # Unknown failure reason — safest action is do nothing + escalate
        return ["no_action_do_not_disturb", "escalate_to_human"]
    return entry["allowed_actions"]


def get_max_retries(failure_reason: str) -> int:
    """Return the maximum number of retry attempts allowed for a failure reason."""
    entry = PLAYBOOK.get(failure_reason)
    if entry is None:
        return 0
    return entry["max_retries"]


def get_cooldown_days(failure_reason: str) -> int:
    """Return the minimum cooldown period (days) between retries."""
    entry = PLAYBOOK.get(failure_reason)
    if entry is None:
        return 0
    return entry["cooldown_days"]


def get_playbook_entry(failure_reason: str) -> dict:
    """Return the full playbook entry for a failure reason, or a safe default."""
    return PLAYBOOK.get(failure_reason, {
        "allowed_actions": ["no_action_do_not_disturb", "escalate_to_human"],
        "max_retries": 0,
        "cooldown_days": 0,
        "notes": "Unknown failure reason — defaulting to safe no-action.",
    })


def validate_action(failure_reason: str, chosen_action: str) -> bool:
    """
    Validate that a chosen action is allowed by the playbook.
    Returns True if valid, False otherwise.

    This is the HARD GUARD — used to override/reject LLM decisions
    that violate the playbook.
    """
    allowed = get_allowed_actions(failure_reason)
    return chosen_action in allowed


def is_fraud_case(failure_reason: str) -> bool:
    """Hard check: is this a fraud-flagged case? Used for safety guards."""
    return failure_reason == "fraud_flagged"


# ---------------------------------------------------------------------------
# Self-test when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Playbook Summary ===\n")
    for reason, entry in PLAYBOOK.items():
        print(f"  {reason}")
        print(f"    Allowed actions : {entry['allowed_actions']}")
        print(f"    Max retries     : {entry['max_retries']}")
        print(f"    Cooldown (days) : {entry['cooldown_days']}")
        print(f"    Notes           : {entry['notes']}")
        print()

    # Validation tests
    assert validate_action("fraud_flagged", "escalate_to_human") is True
    assert validate_action("fraud_flagged", "smart_retry") is False
    assert validate_action("card_expired", "send_update_payment_link") is True
    assert validate_action("card_expired", "smart_retry") is False
    assert is_fraud_case("fraud_flagged") is True
    assert is_fraud_case("insufficient_funds") is False
    print("All validation tests passed.")
