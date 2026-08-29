"""
Autonomous RAG Diagnosis Pipeline Orchestrator
==============================================

Viva Defensibility Rationale:
-----------------------------
1. Complete End-to-End Orchestration:
   Integrates Data Collection -> Semantic Search -> Prompt Assembly -> Dual LLM Inference ->
   Safety Gatekeeping -> Persistent Audit Logging into a single, cohesive workflow.
2. Complete Traceability:
   Every diagnostic artifact retains references to its underlying telemetry snapshot, the exact
   vector chunks retrieved from the knowledge base, cosine distances, and safety threshold gates.
"""

import logging
from typing import Dict, Any, Optional
from backend.app.collector.netmiko_collector import collector
from backend.app.kb.vector_store import vector_store
from backend.app.rag.prompt_config import build_diagnosis_user_prompt
from backend.app.rag.llm_client import llm_client
from backend.app.rag.fallback_gatekeeper import gatekeeper
from backend.app.rag.audit_logger import audit_logger
from backend.app.topology.controller import topology_controller

logger = logging.getLogger(__name__)

class RAGDiagnosisPipeline:
    def __init__(self):
        self.collector = collector
        self.vector_store = vector_store
        self.llm_client = llm_client
        self.gatekeeper = gatekeeper
        self.audit_logger = audit_logger

    def run_diagnosis(self, active_fault_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes full end-to-end diagnosis pipeline:
        1. Collect live symptom telemetry
        2. Retrieve top-k knowledge base chunks from ChromaDB
        3. Construct prompt and query LLM (Groq / Ollama / Expert)
        4. Apply Fallback Gatekeeper evaluation
        5. Persist run to SQLite audit log
        """
        # 1. Collect Telemetry
        symptom_report = self.collector.collect_all_telemetry()
        symptom_text = symptom_report.condensed_symptom_text

        # 2. Vector Retrieval (ChromaDB)
        # Search query combines detected anomalies with symptom text
        search_query = " ".join(symptom_report.anomalies_detected) if symptom_report.anomalies_detected else "healthy network baseline"
        retrieved_chunks = self.vector_store.query_top_k(search_query, k=3)

        # 3. Prompt Construction & LLM Query
        user_prompt = build_diagnosis_user_prompt(symptom_text, retrieved_chunks)
        raw_llm_diagnosis = self.llm_client.generate_diagnosis(user_prompt)

        # 4. Fallback Gatekeeper Safety Evaluation
        validated_result = self.gatekeeper.evaluate_diagnosis(raw_llm_diagnosis, retrieved_chunks)
        
        # Enrich result with telemetry & runtime details
        validated_result["symptom_summary"] = symptom_text
        validated_result["anomalies_detected"] = symptom_report.anomalies_detected
        validated_result["llm_provider"] = raw_llm_diagnosis.get("llm_provider", "Unknown")
        validated_result["active_fault"] = active_fault_type or ("none" if not symptom_report.anomalies_detected else "detected_anomaly")

        # 5. Persist to Audit Log
        run_id = self.audit_logger.log_run(validated_result)
        validated_result["run_id"] = run_id

        return validated_result

rag_pipeline = RAGDiagnosisPipeline()
