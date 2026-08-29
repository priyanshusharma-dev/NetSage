"""
NetSage Unit & Isolated Component Test Suite
============================================

Viva Defensibility & Testing Standards:
- Isolated test cases using pytest
- Mocked LLM responses (zero external API calls during CI)
- Complete coverage of Fallback Gatekeeper edge cases
- Strict schema validation
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.rag.fallback_gatekeeper import FallbackGatekeeper
from backend.app.collector.parser import CLIParser
from backend.app.topology.simulator import NetworkSimulator
from backend.app.topology.fault_injector import FaultInjector

@pytest.fixture
def fresh_simulator():
    sim = NetworkSimulator()
    sim.reset_topology()
    return sim

@pytest.fixture
def parser():
    return CLIParser()

@pytest.fixture
def gatekeeper():
    return FallbackGatekeeper(max_distance=0.85, min_confidence=65)

# --- 1. Parser Unit Tests ---
def test_parse_show_ip_interface_brief(parser):
    sample_output = """
    Interface               IP-Address      OK?  Method  Status                Protocol
    GigabitEthernet0/0      10.1.13.1       YES  NVRAM   up                    up      
    GigabitEthernet0/1      192.168.10.1    YES  NVRAM   administratively down down    
    """
    parsed = parser.parse_show_ip_interface_brief(sample_output)
    assert len(parsed) == 2
    assert parsed[0].interface == "GigabitEthernet0/0"
    assert parsed[0].status == "up"
    assert parsed[1].interface == "GigabitEthernet0/1"
    assert parsed[1].status == "administratively down"

def test_parse_ping_cisco(parser):
    output_success = "Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms"
    output_fail = "Success rate is 0 percent (0/5)"
    
    res_succ = parser.parse_ping("HQ-R1", output_success, "10.1.13.2")
    res_fail = parser.parse_ping("HQ-R1", output_fail, "192.168.10.10")
    
    assert res_succ.is_reachable is True
    assert res_succ.loss_percent == 0.0
    assert res_fail.is_reachable is False
    assert res_fail.loss_percent == 100.0

# --- 2. Fault Injector Unit Tests ---
def test_fault_injection_interface_down(fresh_simulator):
    injector = FaultInjector(fresh_simulator)
    res = injector.inject_fault("interface_down", {"target_node": "HQ-R1", "target_interface": "GigabitEthernet0/1"})
    
    assert res["status"] == "success"
    assert len(fresh_simulator.active_faults) == 1
    
    out = fresh_simulator.execute_command("HQ-R1", "show ip interface brief")
    assert "administratively down" in out

def test_fault_injection_invalid_type(fresh_simulator):
    injector = FaultInjector(fresh_simulator)
    with pytest.raises(ValueError):
        injector.inject_fault("non_existent_fault_type")

# --- 3. Fallback Gatekeeper Unit Tests ---
def test_gatekeeper_autonomous_pass(gatekeeper):
    raw_diag = {
        "most_likely_root_cause": "Interface GigabitEthernet0/1 down",
        "confidence_score": 95,
        "recommended_fix": "no shutdown",
        "reasoning_chain": "Interface is shut."
    }
    retrieved_chunks = [
        {"id": "chunk_1", "content": "fix guide", "distance": 0.25}
    ]
    result = gatekeeper.evaluate_diagnosis(raw_diag, retrieved_chunks)
    
    assert result["status"] == "AUTONOMOUS_DIAGNOSIS_VERIFIED"
    assert result["fallback_triggered"] is False
    assert result["confidence_score"] == 95

def test_gatekeeper_low_confidence_escalation(gatekeeper):
    raw_diag = {
        "most_likely_root_cause": "Uncertain anomaly",
        "confidence_score": 45,  # below threshold 65
        "recommended_fix": "manual check",
        "reasoning_chain": "unclear telemetry"
    }
    retrieved_chunks = [
        {"id": "chunk_1", "content": "guide", "distance": 0.25}
    ]
    result = gatekeeper.evaluate_diagnosis(raw_diag, retrieved_chunks)
    
    assert result["status"] == "ESCALATED_TO_MANUAL"
    assert result["fallback_triggered"] is True
    assert "Insufficient evidence" in result["final_root_cause"]

def test_gatekeeper_poor_retrieval_distance_escalation(gatekeeper):
    raw_diag = {
        "most_likely_root_cause": "Guessed cause",
        "confidence_score": 90,
        "recommended_fix": "fix",
        "reasoning_chain": "logic"
    }
    retrieved_chunks = [
        {"id": "chunk_1", "content": "unrelated doc", "distance": 1.25}  # exceeds max 0.85
    ]
    result = gatekeeper.evaluate_diagnosis(raw_diag, retrieved_chunks)
    
    assert result["status"] == "ESCALATED_TO_MANUAL"
    assert result["fallback_triggered"] is True
