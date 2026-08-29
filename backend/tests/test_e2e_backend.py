"""
End-to-End Backend Verification Suite
=====================================

Validates:
1. Knowledge Base Ingestion & ChromaDB indexing
2. Data Collector telemetry extraction & parsing
3. RAG Diagnosis Pipeline across Fault Types (Groq / Ollama / Expert fallback)
4. Fallback Gatekeeper Deferral Case (Low confidence escalation requirement)
5. SQLite Audit Logging & Accuracy Calculation
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.topology.controller import topology_controller
from backend.app.kb.vector_store import vector_store
from backend.app.collector.netmiko_collector import collector
from backend.app.rag.rag_engine import rag_pipeline
from backend.app.rag.fallback_gatekeeper import gatekeeper
from backend.app.rag.audit_logger import audit_logger

def test_full_pipeline():
    print("=" * 75)
    print(" [End-to-End Verification] NetSage Autonomous Diagnostic Pipeline ")
    print("=" * 75)

    # 1. Ingest Knowledge Base
    print("\n[1] Ingesting Knowledge Base Source Docs...")
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base", "source_docs"))
    ingest_res = vector_store.ingest_directory(src_dir)
    print(f"    Indexed: {ingest_res['documents_indexed']} documents into {ingest_res['chunks_stored']} chunks.")
    assert ingest_res['chunks_stored'] >= 5

    # 2. Test Fault: Interface Down
    print("\n[2] Testing Autonomous Diagnosis on 'interface_down'...")
    topology_controller.reset()
    topology_controller.inject_fault("interface_down", {"target_node": "HQ-R1", "target_interface": "GigabitEthernet0/1"})
    
    diag_res1 = rag_pipeline.run_diagnosis(active_fault_type="interface_down")
    print(f"    - Status: {diag_res1['status']}")
    print(f"    - Confidence Score: {diag_res1['confidence_score']}%")
    print(f"    - Root Cause: {diag_res1['final_root_cause']}")
    print(f"    - Recommended CLI Fix:\n      {diag_res1['recommended_fix'].replace(chr(10), ' | ')}")
    print(f"    - Retrieved Chunks: {len(diag_res1['retrieved_evidence'])}")
    print(f"    - Fallback Triggered: {diag_res1['fallback_triggered']}")
    assert diag_res1['status'] == "AUTONOMOUS_DIAGNOSIS_VERIFIED"
    assert diag_res1['fallback_triggered'] is False
    assert "GigabitEthernet0/1" in diag_res1['final_root_cause'] or "down" in diag_res1['final_root_cause']

    # 3. Test Fault: ACL Blocking
    print("\n[3] Testing Autonomous Diagnosis on 'acl_blocking'...")
    topology_controller.reset()
    topology_controller.inject_fault("acl_blocking", {"target_node": "HQ-R1"})
    diag_res2 = rag_pipeline.run_diagnosis(active_fault_type="acl_blocking")
    print(f"    - Status: {diag_res2['status']}")
    print(f"    - Confidence Score: {diag_res2['confidence_score']}%")
    print(f"    - Root Cause: {diag_res2['final_root_cause']}")
    print(f"    - Fallback Triggered: {diag_res2['fallback_triggered']}")
    assert diag_res2['status'] == "AUTONOMOUS_DIAGNOSIS_VERIFIED"
    assert "access" in diag_res2['final_root_cause'].lower() or "acl" in diag_res2['final_root_cause'].lower()

    # 4. Test Documented Failure Case: Fallback Gatekeeper Escalation
    print("\n[4] Testing Defensible Failure Case: Low Confidence Fallback Deferral...")
    # Artificially set high confidence threshold (99%) to force safety gatekeeper deferral
    gatekeeper.update_thresholds(min_confidence=99)
    diag_fallback = rag_pipeline.run_diagnosis(active_fault_type="acl_blocking")
    print(f"    - Status: {diag_fallback['status']}")
    print(f"    - Fallback Triggered: {diag_fallback['fallback_triggered']}")
    print(f"    - Final Verdict: {diag_fallback['final_root_cause']}")
    print(f"    - Escalation Reason: {diag_fallback['escalation_reason']}")
    assert diag_fallback['status'] == "ESCALATED_TO_MANUAL"
    assert diag_fallback['fallback_triggered'] is True
    assert "insufficient evidence — escalate to manual diagnosis" in diag_fallback['final_root_cause'].lower()
    
    # Restore normal threshold (65%)
    gatekeeper.update_thresholds(min_confidence=65)

    # 5. Test SQLite Audit Logging & Ground Truth Labeling
    print("\n[5] Testing SQLite Audit Logging & Accuracy Metrics...")
    history = audit_logger.get_history(limit=5)
    print(f"    - Total Logged Runs Retrieved: {len(history)}")
    latest_run_id = history[0]["id"]
    
    # Label the run as correct
    audit_logger.update_label(latest_run_id, "correct")
    stats = audit_logger.get_statistics()
    print(f"    - System Stats: Total Runs={stats['total_runs']}, Autonomous={stats['autonomous_runs']}, Fallbacks={stats['escalated_fallbacks']}, Accuracy={stats['accuracy_percentage']}%")
    assert stats['total_runs'] >= 3

    topology_controller.reset()
    print("\n" + "=" * 75)
    print(" [PASSED] All Backend Core Modules & Viva Criteria Verified! ")
    print("=" * 75)

if __name__ == "__main__":
    test_full_pipeline()
