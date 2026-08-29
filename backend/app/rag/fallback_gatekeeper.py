"""
Fallback Gatekeeper & Safety Verification Engine
================================================

Viva Defensibility Rationale:
-----------------------------
1. Defense Against Hallucination in Mission-Critical Systems:
   In automated networking operations, a hallucinated CLI command (such as applying the wrong
   shutdown command or deleting correct BGP peers) could cause widespread outages.
   The Fallback Gatekeeper guarantees that autonomous remediation is ONLY permitted when both:
   (a) RAG Vector Retrieval similarity satisfies statistical thresholds (sufficient domain context)
   (b) LLM Self-Assessed Confidence meets or exceeds the configurable confidence threshold.
2. Defensible Deferral Pattern:
   When telemetry is noisy, incomplete, or unprecedented, the system purposefully declines to guess
   and cleanly yields control to human network engineers with an explanation of why confidence was low.
"""

from typing import Dict, Any, List
from backend.app.config import settings

class FallbackGatekeeper:
    def __init__(self, max_distance: float = None, min_confidence: int = None):
        self.max_distance = max_distance if max_distance is not None else settings.MAX_RETRIEVAL_DISTANCE
        self.min_confidence = min_confidence if min_confidence is not None else settings.MIN_CONFIDENCE_THRESHOLD

    def update_thresholds(self, max_distance: float = None, min_confidence: int = None):
        """Allows dynamic runtime configuration of safety thresholds."""
        if max_distance is not None:
            self.max_distance = max_distance
        if min_confidence is not None:
            self.min_confidence = min_confidence

    def evaluate_diagnosis(self, raw_diagnosis: Dict[str, Any], retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Applies dual-threshold safety evaluation.
        Returns validated diagnosis payload with fallback and escalation metadata.
        """
        confidence = raw_diagnosis.get("confidence_score", 0)
        
        # Calculate best (lowest) distance among retrieved chunks
        best_distance = 1.0
        if retrieved_chunks:
            best_distance = min(c.get("distance", 1.0) for c in retrieved_chunks)

        is_confidence_low = confidence < self.min_confidence
        is_retrieval_poor = bool(retrieved_chunks and best_distance > self.max_distance)

        # Evaluate Fallback Condition
        if is_confidence_low or is_retrieval_poor or not retrieved_chunks:
            reasons = []
            if is_confidence_low:
                reasons.append(f"LLM self-assessed confidence ({confidence}%) is below minimum threshold ({self.min_confidence}%).")
            if is_retrieval_poor:
                reasons.append(f"RAG vector cosine distance ({best_distance:.3f}) exceeds maximum threshold ({self.max_distance}).")
            if not retrieved_chunks:
                reasons.append("No relevant knowledge base documentation was matched.")

            reason_str = " ".join(reasons)
            
            return {
                "status": "ESCALATED_TO_MANUAL",
                "fallback_triggered": True,
                "escalation_reason": reason_str,
                "final_root_cause": "Insufficient evidence — escalate to manual diagnosis",
                "autonomous_action_allowed": False,
                "confidence_score": confidence,
                "confidence_threshold": self.min_confidence,
                "best_retrieval_distance": round(best_distance, 4),
                "distance_threshold": self.max_distance,
                "recommended_fix": "MANUAL ACTION REQUIRED: Escalate incident to Level 2 Network Operations Center. Do not execute unverified commands.",
                "original_llm_diagnosis": raw_diagnosis,
                "retrieved_evidence": retrieved_chunks
            }

        # Passed all safety checks
        return {
            "status": "AUTONOMOUS_DIAGNOSIS_VERIFIED",
            "fallback_triggered": False,
            "escalation_reason": None,
            "final_root_cause": raw_diagnosis.get("most_likely_root_cause", "Diagnosis completed."),
            "autonomous_action_allowed": True,
            "confidence_score": confidence,
            "confidence_threshold": self.min_confidence,
            "best_retrieval_distance": round(best_distance, 4),
            "distance_threshold": self.max_distance,
            "affected_layer": raw_diagnosis.get("affected_layer", "Layer 3"),
            "recommended_fix": raw_diagnosis.get("recommended_fix", ""),
            "reasoning_chain": raw_diagnosis.get("reasoning_chain", ""),
            "original_llm_diagnosis": raw_diagnosis,
            "retrieved_evidence": retrieved_chunks
        }

gatekeeper = FallbackGatekeeper()
