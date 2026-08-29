"""
NetSage FastAPI Server Application
==================================

Viva Defensibility Rationale:
-----------------------------
1. OpenAPI Compliant Autonomous Operations:
   Exposes standard RESTful contracts for all control plane (fault injection, topology status)
   and AI cognitive plane (diagnostic inference, vector search, safety thresholds) interactions.
2. Complete CORS & Middleware Integration:
   Seamlessly communicates with the Next.js frontend running locally on `http://localhost:3000`.
"""

import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.config import settings
from backend.app.topology.controller import topology_controller
from backend.app.topology.topology_def import FAULT_TAXONOMY
from backend.app.collector.netmiko_collector import collector
from backend.app.kb.vector_store import vector_store
from backend.app.rag.rag_engine import rag_pipeline
from backend.app.rag.fallback_gatekeeper import gatekeeper
from backend.app.rag.audit_logger import audit_logger

app = FastAPI(
    title="NetSage Autonomous Network Troubleshooting API",
    description="LLM-assisted autonomous network diagnosis, RAG vector retrieval, and fault injection API.",
    version="1.0.0"
)

# Enable CORS for local Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Hook: Ensure Vector Store is initialized
@app.on_event("startup")
def startup_event():
    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base", "source_docs"))
    if os.path.exists(source_dir):
        vector_store.ingest_directory(source_dir)

# --------------------------------------------------------------------------
# Request / Response Schemas
# --------------------------------------------------------------------------
class FaultInjectRequest(BaseModel):
    fault_type: str = Field(..., description="One of: interface_down, subnet_misconfig, acl_blocking, routing_loop, dns_failure")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional custom target node or interface parameters")

class ThresholdsRequest(BaseModel):
    max_retrieval_distance: Optional[float] = None
    min_confidence_threshold: Optional[int] = None

class LabelRequest(BaseModel):
    label: str = Field(..., description="'correct', 'incorrect', or 'unlabeled'")

class CLIExecRequest(BaseModel):
    node_id: str
    command: str

# --------------------------------------------------------------------------
# Topology & Fault Endpoints
# --------------------------------------------------------------------------
@app.get("/api/v1/topology/status")
def get_topology_status():
    """Returns the current state of all topology nodes, links, and active faults."""
    return topology_controller.get_status()

@app.get("/api/v1/fault/taxonomy")
def get_fault_taxonomy():
    """Returns supported fault types and their academic OSI layer definitions."""
    return FAULT_TAXONOMY

@app.post("/api/v1/fault/inject")
def inject_fault(req: FaultInjectRequest):
    """Injects a designated fault into the simulated/GNS3 network topology."""
    try:
        res = topology_controller.inject_fault(req.fault_type, req.params)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/fault/reset")
def reset_topology():
    """Resets topology and clears all active faults."""
    return topology_controller.reset()

@app.post("/api/v1/cli/execute")
def execute_cli_command(req: CLIExecRequest):
    """Executes a diagnostic CLI command on a specified node."""
    output = topology_controller.execute_command(req.node_id, req.command)
    return {"node_id": req.node_id, "command": req.command, "output": output}

# --------------------------------------------------------------------------
# Telemetry & Diagnosis Endpoints
# --------------------------------------------------------------------------
@app.get("/api/v1/telemetry")
def collect_live_telemetry():
    """Gathers raw and parsed telemetry across all network nodes without running diagnosis."""
    report = collector.collect_all_telemetry()
    return report

@app.post("/api/v1/diagnose")
def run_autonomous_diagnosis():
    """Triggers the full RAG diagnostic pipeline: Symptom Collection -> Vector Retrieval -> LLM -> Safety Gatekeeper -> SQLite Audit Log."""
    status = topology_controller.get_status()
    active_fault_type = status["active_faults"][0]["type"] if status["active_faults"] else None
    result = rag_pipeline.run_diagnosis(active_fault_type=active_fault_type)
    return result

# --------------------------------------------------------------------------
# Safety Gatekeeper & Configuration
# --------------------------------------------------------------------------
@app.get("/api/v1/config/thresholds")
def get_safety_thresholds():
    """Returns current retrieval similarity distance and LLM confidence thresholds."""
    return {
        "max_retrieval_distance": gatekeeper.max_distance,
        "min_confidence_threshold": gatekeeper.min_confidence,
        "active_mode": topology_controller.mode,
        "groq_model": settings.GROQ_MODEL,
        "ollama_model": settings.OLLAMA_MODEL
    }

@app.post("/api/v1/config/thresholds")
def update_safety_thresholds(req: ThresholdsRequest):
    """Updates safety thresholds dynamically."""
    gatekeeper.update_thresholds(
        max_distance=req.max_retrieval_distance,
        min_confidence=req.min_confidence_threshold
    )
    return {
        "status": "success",
        "max_retrieval_distance": gatekeeper.max_distance,
        "min_confidence_threshold": gatekeeper.min_confidence
    }

# --------------------------------------------------------------------------
# Knowledge Base Endpoints
# --------------------------------------------------------------------------
@app.get("/api/v1/knowledge-base")
def get_knowledge_base_chunks():
    """Lists indexed knowledge chunks for transparency and examiner inspection."""
    return {
        "chunks": [
            {"id": c.chunk_id, "content": c.content, "metadata": c.metadata}
            for c in vector_store._in_memory_docs
        ],
        "total_chunks": len(vector_store._in_memory_docs)
    }

@app.post("/api/v1/knowledge-base/reindex")
def reindex_knowledge_base():
    """Reindexes source documents."""
    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base", "source_docs"))
    res = vector_store.ingest_directory(source_dir)
    return res

# --------------------------------------------------------------------------
# Audit History & Statistics Endpoints
# --------------------------------------------------------------------------
@app.get("/api/v1/history")
def get_diagnosis_history(limit: int = 50):
    """Returns historical diagnosis runs."""
    return audit_logger.get_history(limit=limit)

@app.post("/api/v1/history/{run_id}/label")
def label_diagnosis_run(run_id: int, req: LabelRequest):
    """Labels run correctness ('correct' or 'incorrect') for accuracy tracking."""
    success = audit_logger.update_label(run_id, req.label)
    if not success:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return {"status": "success", "run_id": run_id, "label": req.label}

@app.get("/api/v1/stats")
def get_system_statistics():
    """Calculates accuracy telemetry and run statistics."""
    return audit_logger.get_statistics()

@app.get("/api/v1/architecture-diagram")
def get_architecture_diagram():
    """Returns Mermaid architecture diagram string for viva documentation."""
    diagram = """
    flowchart TD
        A[Fault Injector / GNS3 Controller] -->|Layer 1-7 Fault Injection| B[Network Simulation Topology]
        B -->|Live Network State| C[Netmiko Data Collector]
        C -->|CLI Commands: show ip route, ping, nslookup| D[Structured Symptom Parser]
        D -->|Symptom Context & Anomaly Tags| E[ChromaDB Vector Retrieval]
        E -->|Top-k Chunks + Cosine Distance| F[RAG Prompt Assembly]
        F -->|JSON Output Schema Prompt| G[Dual LLM Router: Groq Llama 3 / Ollama]
        G -->|Self-Confidence & Root Cause JSON| H[Fallback Gatekeeper]
        H -->|Sim Dist > Max OR Conf < Min| I[Escalate to Manual Diagnosis]
        H -->|Sufficient Evidence & Conf| J[Autonomous Root Cause & CLI Fix]
        I --> K[SQLite Audit Logger & FastAPI Backend]
        J --> K
        K --> L[Next.js Interactive Dashboard]
    """
    return {"mermaid": diagram.strip()}
