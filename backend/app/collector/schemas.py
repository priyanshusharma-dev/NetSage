"""
Network Telemetry & Structured Symptom Schemas
=============================================

Viva Defensibility Rationale:
-----------------------------
1. Strongly Typed Domain Modeling:
   Raw CLI strings are notoriously inconsistent across NOS versions (Cisco IOS, Arista EOS, Linux).
   Converting semi-structured CLI text into strictly validated Pydantic data contracts ensures the
   downstream RAG embedding and LLM prompt builder receive normalized, clean telemetry.
2. Comprehensive Symptom Aggregation:
   Captures Layer 1 physical link states, Layer 3 routing table convergence, Layer 4 access-list
   match hits, and Layer 7 resolution status in a single unified `SymptomReport`.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class InterfaceStatus(BaseModel):
    interface: str
    ip_address: str
    status: str  # "up", "administratively down", "down"
    protocol: str  # "up", "down"

class RouteEntry(BaseModel):
    prefix: str
    nexthop: str
    interface: str
    protocol: str = "connected"  # "connected", "static", "ospf"
    metric: str = "0"

class ACLRule(BaseModel):
    name: str
    rule: str
    matches: int = 0

class PingSummary(BaseModel):
    source_node: str
    target_ip: str
    transmitted: int
    received: int
    loss_percent: float
    is_reachable: bool
    raw_output: str

class TracerouteHop(BaseModel):
    hop_number: int
    ip_address: str
    rtt_ms: Optional[float] = None
    status: str = "normal"  # "normal", "timeout", "loop_detected"

class DNSQuerySummary(BaseModel):
    hostname: str
    server_queried: str
    resolved_ip: Optional[str] = None
    is_success: bool
    raw_output: str

class NodeTelemetry(BaseModel):
    node_id: str
    node_type: str
    interfaces: List[InterfaceStatus] = Field(default_factory=list)
    routes: List[RouteEntry] = Field(default_factory=list)
    acls: List[ACLRule] = Field(default_factory=list)
    raw_commands: Dict[str, str] = Field(default_factory=dict)

class SymptomReport(BaseModel):
    timestamp: str
    nodes_telemetry: Dict[str, NodeTelemetry] = Field(default_factory=dict)
    ping_tests: List[PingSummary] = Field(default_factory=list)
    dns_tests: List[DNSQuerySummary] = Field(default_factory=list)
    anomalies_detected: List[str] = Field(default_factory=list)
    condensed_symptom_text: str = ""
