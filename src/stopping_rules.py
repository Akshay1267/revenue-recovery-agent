"""
stopping_rules.py - Enforcement of Recovery Attempt Constraints
================================================================
Ensures compliance with:
  1. Max retry attempts per subscription (from playbook)
  2. Cooldown period between successive attempts
  3. Auto-escalation after max retries exhausted
  4. HARD BLOCK: never retry fraud-flagged cases
  5. Never contact a customer more than once per day

Usage:
    from src.stopping_rules import check_action_allowed
    result = check_action_allowed(record, attempt_history)
    if result["allowed"]:
        # proceed with action
    else:
        # use result["override_action"] instead, or skip
"""

from datetime import datetime, timedelta
from src.playbook import (
    get_max_retries,
    get_cooldown_days,
    is_fraud_case,
    validate_action,
)


def check_action_allowed(
    record: dict,
    chosen_action: str,
    attempt_history: list[dict] | None = None,
    current_time: datetime | None = None,
) -> dict:
    """
    Check whether a proposed action is allowed given the record state
    and its attempt history.

    Parameters
    ----------
    record : dict
        A single row from failed_subscriptions.csv (as a dict).
    chosen_action : str
        The action proposed by the agent.
    attempt_history : list[dict], optional
        List of past attempts for this subscription, each with keys:
          - "timestamp" (datetime)
          - "action" (str)
        If None, uses retry_attempts_so_far from the record.
    current_time : datetime, optional
        The current timestamp. Defaults to now.

    Returns
    -------
    dict with keys:
        allowed         : bool   — True if action can proceed
        override_action : str    — replacement action if blocked (or None)
        reason          : str    — human-readable explanation
    """
    if current_time is None:
        current_time = datetime.now()

    failure_reason = record["failure_reason"]
    retry_attempts = record.get("retry_attempts_so_far", 0)

    # If we have detailed history, count from that instead
    if attempt_history:
        retry_attempts = len(attempt_history)

    # ----- RULE 1: Hard fraud block -----
    # Fraud-flagged cases must NEVER be retried or contacted.
    # This is a code-level guard, independent of any LLM output.
    if is_fraud_case(failure_reason):
        if chosen_action != "escalate_to_human":
            return {
                "allowed": False,
                "override_action": "escalate_to_human",
                "reason": (
                    "FRAUD GUARD: fraud-flagged cases must only be escalated "
                    "to human review. Auto-retry and customer contact are blocked."
                ),
            }
        # escalate_to_human is fine for fraud
        return {
            "allowed": True,
            "override_action": None,
            "reason": "Fraud case — escalation to human is the correct action.",
        }

    # ----- RULE 2: Validate action against playbook -----
    if not validate_action(failure_reason, chosen_action):
        return {
            "allowed": False,
            "override_action": "no_action_do_not_disturb",
            "reason": (
                f"Action '{chosen_action}' is not in the allowed list for "
                f"failure reason '{failure_reason}'. Blocked by playbook."
            ),
        }

    # ----- RULE 3: Max retry attempts -----
    max_retries = get_max_retries(failure_reason)
    is_retry_action = chosen_action in ("smart_retry", "offer_discount_retry")

    if is_retry_action and retry_attempts >= max_retries:
        return {
            "allowed": False,
            "override_action": "escalate_to_human",
            "reason": (
                f"Max retries exhausted ({retry_attempts}/{max_retries}). "
                f"Auto-escalating to human review."
            ),
        }

    # ----- RULE 4: Cooldown period -----
    cooldown_days = get_cooldown_days(failure_reason)
    if is_retry_action and cooldown_days > 0 and attempt_history:
        last_attempt_time = max(a["timestamp"] for a in attempt_history)
        time_since_last = current_time - last_attempt_time
        if time_since_last < timedelta(days=cooldown_days):
            remaining = timedelta(days=cooldown_days) - time_since_last
            return {
                "allowed": False,
                "override_action": "no_action_do_not_disturb",
                "reason": (
                    f"Cooldown period not met. Must wait {cooldown_days} day(s) "
                    f"between retries. {remaining.total_seconds() / 3600:.0f}h remaining."
                ),
            }

    # ----- RULE 5: Max one customer contact per day -----
    contact_actions = {
        "send_update_payment_link",
        "offer_discount_retry",
    }
    if chosen_action in contact_actions and attempt_history:
        today = current_time.date()
        contacts_today = sum(
            1 for a in attempt_history
            if a["action"] in contact_actions
            and a["timestamp"].date() == today
        )
        if contacts_today >= 1:
            return {
                "allowed": False,
                "override_action": "no_action_do_not_disturb",
                "reason": (
                    "Customer already contacted once today. "
                    "Rate limit: max 1 contact per customer per day."
                ),
            }

    # ----- All rules passed -----
    return {
        "allowed": True,
        "override_action": None,
        "reason": "Action is allowed by all stopping rules.",
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from datetime import datetime

    # Test fraud hard block
    fraud_record = {"failure_reason": "fraud_flagged", "retry_attempts_so_far": 0}
    result = check_action_allowed(fraud_record, "smart_retry")
    assert result["allowed"] is False
    assert result["override_action"] == "escalate_to_human"
    print(f"[PASS] Fraud block: {result['reason']}")

    result = check_action_allowed(fraud_record, "escalate_to_human")
    assert result["allowed"] is True
    print(f"[PASS] Fraud escalation allowed: {result['reason']}")

    # Test max retries
    insuf_record = {"failure_reason": "insufficient_funds", "retry_attempts_so_far": 3}
    result = check_action_allowed(insuf_record, "smart_retry")
    assert result["allowed"] is False
    assert result["override_action"] == "escalate_to_human"
    print(f"[PASS] Max retries: {result['reason']}")

    # Test allowed action
    insuf_fresh = {"failure_reason": "insufficient_funds", "retry_attempts_so_far": 0}
    result = check_action_allowed(insuf_fresh, "smart_retry")
    assert result["allowed"] is True
    print(f"[PASS] Fresh retry allowed: {result['reason']}")

    # Test playbook violation
    result = check_action_allowed(
        {"failure_reason": "card_expired", "retry_attempts_so_far": 0},
        "smart_retry"
    )
    assert result["allowed"] is False
    print(f"[PASS] Playbook violation: {result['reason']}")

    print("\nAll stopping rules tests passed.")
