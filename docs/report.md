# Revenue Recovery Report

## Pipeline Results Summary

| Metric | Value |
|--------|-------|
| Total records processed | 60 |
| Total ₹ at risk | ₹68,240 |
| Total ₹ recovered | ₹22,179 |
| Recovery rate | 32.5% |
| Records escalated to human | 9 |
| Stopping rule overrides | 6 |
| Fraud cases auto-retried | 0 ✅ |
| Pipeline execution time | ~17s |

## Recovery by Intervention

| Intervention | Records | Recovered | Rate | ₹ Recovered |
|---|---|---|---|---|
| smart_retry | 27 | 12 | 44.4% | ₹8,588 |
| send_update_payment_link | 24 | 9 | 37.5% | ₹13,591 |
| escalate_to_human | 9 | 0 | 0.0% | ₹0 |

## Outcome Distribution

| Outcome | Count | % |
|---|---|---|
| Failed | 30 | 50.0% |
| Recovered | 21 | 35.0% |
| Pending human review | 9 | 15.0% |

## Compliance Verification

- ✅ **Fraud safety**: All 3 fraud-flagged cases were escalated to human review.
  None were auto-retried or contacted.
- ✅ **Stopping rules**: 6 actions were overridden by stopping rules (max retries
  exceeded), auto-escalating to human review.
- ✅ **Playbook compliance**: All agent decisions were constrained to playbook-
  allowed actions, with code-level validation.

## What Would Change with Real Razorpay Production Data

1. **Higher recovery rates expected**: Real-world smart retries timed to payday
   cycles (e.g., 1st and 15th of the month) would likely yield higher recovery
   rates than our 40% simulation baseline, especially for insufficient_funds
   cases which make up the largest cohort.

2. **Dynamic probability calibration**: With real transaction history, the
   simulator's fixed probabilities would be replaced by ML models trained on
   actual recovery outcomes, enabling per-customer success predictions and
   optimal retry timing.

3. **RBI compliance integration**: Production deployment would need integration
   with RBI's recurring payment mandate framework (e-mandate), adding consent
   verification before any retry attempt and respecting customer opt-out
   preferences stored in Razorpay's mandate system.
