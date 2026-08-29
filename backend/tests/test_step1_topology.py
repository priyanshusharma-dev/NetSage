"""
Step 1 Verification Test Suite
==============================

Tests Topology Automation, Fault Injection, and Simulated CLI Responses.
Demonstrates viva defensibility:
- Verification of baseline healthy state across 8 enterprise nodes
- Verification of exact failure signatures across all 5 OSI-layer fault types
- Verification of zero-state topology restoration
"""

import sys
import os

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.topology.controller import topology_controller
from backend.app.topology.topology_def import FAULT_TAXONOMY

def test_step1():
    print("=" * 70)
    print(" [Step 1 Verification] NetSage Topology & Fault Injection Engine ")
    print("=" * 70)

    # 1. Check Baseline Status
    topology_controller.reset()
    status = topology_controller.get_status()
    print(f"\n[1] Initializing Baseline Topology (Mode: {status['mode']})")
    print(f"    - Nodes loaded: {len(status['nodes'])} (Routers, Switches, Hosts, Server)")
    print(f"    - WAN/LAN Links: {len(status['links'])}")
    print(f"    - Active Faults: {len(status['active_faults'])}")
    assert len(status['nodes']) == 8, "Expected 8 nodes in canonical topology"
    assert len(status['links']) == 7, "Expected 7 links in topology"

    # 2. Test Healthy Baseline Commands
    print("\n[2] Executing Baseline CLI Commands:")
    out_hq = topology_controller.execute_command("HQ-R1", "show ip interface brief")
    print("--- [HQ-R1] show ip interface brief ---")
    print(out_hq)
    assert "administratively down" not in out_hq

    out_ping = topology_controller.execute_command("HQ-R1", "ping 10.1.13.2")
    print("\n--- [HQ-R1] ping Core-R3 (10.1.13.2) ---")
    print(out_ping)
    assert "Success rate is 100 percent" in out_ping

    out_dns = topology_controller.execute_command("Host-A", "nslookup internal.corp.local")
    print("\n--- [Host-A] nslookup internal.corp.local ---")
    print(out_dns)
    assert "192.168.10.53" in out_dns

    # 3. Test Fault 1: Interface Down
    print("\n[3] Injecting Fault 1: 'interface_down' on HQ-R1 GigabitEthernet0/1...")
    res = topology_controller.inject_fault("interface_down", {"target_node": "HQ-R1", "target_interface": "GigabitEthernet0/1"})
    print(f"    Injection Result: {res['fault']['description']}")
    out_if = topology_controller.execute_command("HQ-R1", "show ip interface brief")
    print(out_if)
    assert "GigabitEthernet0/1" in out_if and "administratively down" in out_if
    out_down_ping = topology_controller.execute_command("HQ-R1", "ping 192.168.10.10")
    print(out_down_ping)
    assert "0 percent" in out_down_ping
    topology_controller.reset()

    # 4. Test Fault 2: Subnet Misconfiguration
    print("\n[4] Injecting Fault 2: 'subnet_misconfig' on Host-B...")
    res = topology_controller.inject_fault("subnet_misconfig", {"target_node": "Host-B"})
    print(f"    Injection Result: {res['fault']['description']}")
    out_sub_ping = topology_controller.execute_command("Host-B", "ping 192.168.10.10")
    print(out_sub_ping)
    assert "100% packet loss" in out_sub_ping
    topology_controller.reset()

    # 5. Test Fault 3: ACL Blocking
    print("\n[5] Injecting Fault 3: 'acl_blocking' on HQ-R1...")
    res = topology_controller.inject_fault("acl_blocking", {"target_node": "HQ-R1"})
    print(f"    Injection Result: {res['fault']['description']}")
    out_acl = topology_controller.execute_command("HQ-R1", "show ip access-lists")
    print(out_acl)
    assert "Extended IP access list RESTRICT_CAMPUS_TRAFFIC" in out_acl
    out_acl_ping = topology_controller.execute_command("Host-B", "ping 192.168.10.10")
    print(out_acl_ping)
    assert "Destination Administratively Prohibited" in out_acl_ping
    topology_controller.reset()

    # 6. Test Fault 4: Routing Loop
    print("\n[6] Injecting Fault 4: 'routing_loop' on Core-R3...")
    res = topology_controller.inject_fault("routing_loop", {"target_node": "Core-R3"})
    print(f"    Injection Result: {res['fault']['description']}")
    out_trace = topology_controller.execute_command("HQ-R1", "traceroute 192.168.20.20")
    print(out_trace)
    assert "Routing Loop Detected" in out_trace or "!H" in out_trace
    topology_controller.reset()

    # 7. Test Fault 5: DNS Resolution Failure
    print("\n[7] Injecting Fault 5: 'dns_failure' on Host-A...")
    res = topology_controller.inject_fault("dns_failure", {"target_node": "Host-A"})
    print(f"    Injection Result: {res['fault']['description']}")
    out_bad_dns = topology_controller.execute_command("Host-A", "nslookup internal.corp.local")
    print(out_bad_dns)
    assert "connection timed out" in out_bad_dns
    topology_controller.reset()

    # 8. Clean Reset Verification
    final_status = topology_controller.get_status()
    assert len(final_status["active_faults"]) == 0
    print("\n" + "=" * 70)
    print(" [PASSED] Step 1 Verification Complete! All 5 Fault Types Verified. ")
    print("=" * 70)

if __name__ == "__main__":
    test_step1()
