"""
agent.py - AI Diagnosis & Decision Layer (Claude API)
=====================================================
For each failed subscription record, calls the Claude API to:
  1. Diagnose the likely root cause in plain language
  2. Pick ONE intervention from the playbook-allowed list
  3. Explain reasoning in 1-2 sentences
  4. Return structured JSON

The agent is CONSTRAINED: it can only choose from actions allowed by
the playbook for that failure_reason. If the LLM returns an invalid
action, the code falls back to the safest allowed option.

Requires: ANTHROPIC_API_KEY environment variable.
"""

import json
import os
import sys
import time
from typing import Optional

from dotenv import load_dotenv
load_dotenv()  # Load .env file (ANTHROPIC_API_KEY)

import anthropic

from src.playbook import get_allowed_actions, get_playbook_entry, validate_action, is_fraud_case


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL = "claude-sonnet-4-20250514"  # Fast, cheap, capable
MAX_TOKENS = 512
TEMPERATURE = 0.2  # Low temperature for consistent, deterministic decisions

# Rate limiting: pause between API calls to stay within limits
API_DELAY_SECONDS = 0.3


def _get_client() -> anthropic.Anthropic:
    """Initialize the Anthropic client, reading API key from env."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("Set it with: $env:ANTHROPIC_API_KEY = 'your-key-here'")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# System prompt template
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are an AI payment recovery specialist working for a subscription billing platform.

Your job: analyze a failed subscription payment, diagnose the root cause, and decide the best recovery intervention.

CRITICAL RULES:
1. You MUST choose ONLY from the allowed actions listed below. Do NOT invent new actions.
2. You MUST respond with valid JSON only — no markdown, no explanation outside the JSON.
3. Be concise in your diagnosis and reasoning (1-2 sentences each).
4. For fraud-flagged cases, you MUST always choose "escalate_to_human".
5. Consider the customer's tenure, past payment history, and segment when making decisions.

Respond with exactly this JSON structure:
{
    "subscription_id": "<the subscription_id from the input>",
    "diagnosis": "<plain language root cause analysis>",
    "chosen_action": "<exactly one action from the allowed list>",
    "reasoning": "<1-2 sentence explanation of why this action>"
}"""


def _build_user_prompt(record: dict, allowed_actions: list[str], playbook_notes: str) -> str:
    """Build the user prompt with record details and allowed actions."""
    return f"""Analyze this failed subscription payment and decide on a recovery action.

SUBSCRIPTION DETAILS:
- Subscription ID: {record['subscription_id']}
- Customer ID: {record['customer_id']}
- Customer Tenure: {record['customer_tenure_months']} months
- Subscription Amount: Rs {record['amount_inr']}
- Failure Reason: {record['failure_reason']}
- Days Since Failure: {record['days_since_failure']}
- Past Successful Payments: {record['past_successful_payments']}
- Retry Attempts So Far: {record['retry_attempts_so_far']}
- Customer Segment: {record['customer_segment']}

ALLOWED ACTIONS (choose exactly ONE):
{json.dumps(allowed_actions, indent=2)}

PLAYBOOK CONTEXT: {playbook_notes}

Respond with JSON only."""


def diagnose_single(client: anthropic.Anthropic, record: dict) -> dict:
    """
    Call Claude to diagnose and decide on a single failed payment record.

    Returns a dict with keys:
        subscription_id, diagnosis, chosen_action, reasoning
    """
    failure_reason = record["failure_reason"]
    playbook_entry = get_playbook_entry(failure_reason)
    allowed_actions = playbook_entry["allowed_actions"]

    # ---- HARD GUARD: fraud cases bypass LLM entirely ----
    if is_fraud_case(failure_reason):
        return {
            "subscription_id": record["subscription_id"],
            "diagnosis": "Payment flagged for potential fraud by the payment gateway.",
            "chosen_action": "escalate_to_human",
            "reasoning": (
                "Fraud-flagged transactions must never be retried or contacted. "
                "Escalating to human fraud review team per compliance policy."
            ),
        }

    # ---- Call Claude API ----
    user_prompt = _build_user_prompt(record, allowed_actions, playbook_entry["notes"])

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text.strip()

        # Parse JSON response
        # Handle potential markdown code blocks
        if raw_text.startswith("```"):
            # Strip markdown code fences
            lines = raw_text.split("\n")
            raw_text = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            )

        result = json.loads(raw_text)

        # ---- VALIDATION: ensure chosen_action is in allowed list ----
        if not validate_action(failure_reason, result.get("chosen_action", "")):
            # LLM picked an invalid action — fall back to first allowed
            original_action = result.get("chosen_action", "unknown")
            result["chosen_action"] = allowed_actions[0]
            result["reasoning"] = (
                f"[OVERRIDE] LLM suggested '{original_action}' which is not allowed "
                f"for {failure_reason}. Falling back to '{allowed_actions[0]}'. "
                f"Original reasoning: {result.get('reasoning', 'N/A')}"
            )

        # Ensure subscription_id matches
        result["subscription_id"] = record["subscription_id"]

        return result

    except json.JSONDecodeError as e:
        # Fallback: LLM returned non-JSON
        return {
            "subscription_id": record["subscription_id"],
            "diagnosis": f"[PARSE ERROR] Could not parse LLM response: {str(e)[:100]}",
            "chosen_action": allowed_actions[0],
            "reasoning": f"Fallback to '{allowed_actions[0]}' due to JSON parse failure.",
        }
    except Exception as e:
        # Network/API error fallback
        return {
            "subscription_id": record["subscription_id"],
            "diagnosis": f"[API ERROR] {str(e)[:150]}",
            "chosen_action": allowed_actions[0],
            "reasoning": f"Fallback to '{allowed_actions[0]}' due to API error.",
        }


def diagnose_batch(
    records: list[dict],
    progress_callback: Optional[callable] = None,
) -> list[dict]:
    """
    Process a batch of records through the Claude agent.

    Parameters
    ----------
    records : list[dict]
        List of failed subscription records.
    progress_callback : callable, optional
        Called with (current_index, total, record, result) after each record.

    Returns
    -------
    list[dict] : List of diagnosis/decision dicts.
    """
    client = _get_client()
    results = []
    total = len(records)

    for i, record in enumerate(records):
        result = diagnose_single(client, record)
        results.append(result)

        if progress_callback:
            progress_callback(i + 1, total, record, result)
        else:
            # Default progress indicator
            action = result["chosen_action"]
            sid = record["subscription_id"]
            print(f"  [{i+1:>3d}/{total}] {sid} | {record['failure_reason']:<25s} -> {action}")

        # Rate limiting (skip delay for fraud cases which don't call API)
        if not is_fraud_case(record["failure_reason"]):
            time.sleep(API_DELAY_SECONDS)

    return results


# ---------------------------------------------------------------------------
# Self-test (requires API key)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import csv
    from pathlib import Path

    csv_path = Path(__file__).resolve().parent.parent / "data" / "failed_subscriptions.csv"
    if not csv_path.exists():
        print(f"Dataset not found at {csv_path}. Run generate_data.py first.")
        sys.exit(1)

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    # Test with just 3 records
    test_records = records[:3]
    print(f"Testing agent with {len(test_records)} records...\n")

    results = diagnose_batch(test_records)
    for r in results:
        print(json.dumps(r, indent=2))
        print()
