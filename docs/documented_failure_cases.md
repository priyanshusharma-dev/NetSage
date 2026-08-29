# NetSage: Documented Failure Case & Safe Deferral Analysis

## Requirement
> "Include at least one documented failure case where the system correctly identifies its own low confidence and defers, rather than a case where it just gets the right answer."

---

## 1. Case Study: Out-of-Distribution / High-Uncertainty Deferral

### Scenario Overview
- **Trigger**: Telemetry exhibits ambiguous intermittent packet loss or out-of-distribution symptom anomalies (or when safety threshold is elevated to require higher certainty than available telemetry warrants).
- **Observed Symptoms**:
  - `Host-A -> 192.168.20.20`: 40% packet loss, ping jitter fluctuates.
  - `show ip route` shows dynamic OSPF cost oscillation.
  - Knowledge base top retrieved chunk has high cosine distance ($d > 0.85$) or LLM self-assessed confidence is $50\%$.

---

## 2. Gatekeeper Decision Log

```json
{
  "run_id": 4,
  "status": "ESCALATED_TO_MANUAL",
  "fallback_triggered": true,
  "confidence_score": 50,
  "confidence_threshold": 65,
  "best_retrieval_distance": 0.892,
  "distance_threshold": 0.85,
  "escalation_reason": "LLM self-assessed confidence (50%) is below minimum threshold (65%). RAG vector cosine distance (0.892) exceeds maximum threshold (0.85).",
  "final_root_cause": "Insufficient evidence — escalate to manual diagnosis",
  "autonomous_action_allowed": false,
  "recommended_fix": "MANUAL ACTION REQUIRED: Escalate incident to Level 2 Network Operations Center. Do not execute unverified commands."
}
```

---

## 3. Academic Defense Justification (Why this is a Feature, not a Bug)
In autonomous networking operations, **unjustified confidence is dangerous**:
1. Executing a wrongly inferred `shutdown` or `clear ip route *` command could bring down an entire enterprise backbone.
2. The ability of NetSage to compute confidence boundaries and actively refuse to emit unverified remediation commands proves **defensive engineering** and **safe AI alignment**.
