"""
Fault Injection Module
======================

Viva Defensibility Rationale:
-----------------------------
1. Structured Chaos Engineering for Enterprise Networks:
   Fault injection simulates real-world failure modes across Layers 1 through 7 of the OSI model:
   - Layer 1/2: Physical/Link Administrative Shutdown (`interface_down`)
   - Layer 3: Addressing, Masking & Default Gateway mismatches (`subnet_misconfig`)
   - Layer 3/4: Packet Filtering & Security Access Control List Drops (`acl_blocking`)
   - Layer 3: Routing Control Plane Divergence / Blackholing (`routing_loop`)
   - Layer 7: Application Layer Name Resolution Failure (`dns_failure`)
2. Deterministic & Idempotent Operations:
   Each injection operation modifies the network state predictably, returns a structured
   confirmation payload, and records the injection timestamp for subsequent diagnostic auditing.
"""

import time
from typing import Dict, Any, Optional
from backend.app.topology.simulator import NetworkSimulator
from backend.app.topology.topology_def import FAULT_TAXONOMY

class FaultInjector:
    def __init__(self, simulator: NetworkSimulator):
        self.simulator = simulator

    def inject_fault(self, fault_type: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Injects a specific fault into the network topology.
        Supports: 'interface_down', 'subnet_misconfig', 'acl_blocking', 'routing_loop', 'dns_failure'.
        """
        if fault_type not in FAULT_TAXONOMY:
            raise ValueError(f"Unsupported fault type '{fault_type}'. Available: {list(FAULT_TAXONOMY.keys())}")

        params = custom_params or {}
        taxonomy_info = FAULT_TAXONOMY[fault_type]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # 1. Interface Down (Layer 1/2)
        if fault_type == "interface_down":
            target_node = params.get("target_node", taxonomy_info["default_target"])
            target_int = params.get("target_interface", taxonomy_info["default_interface"])
            
            if target_node in self.simulator.nodes:
                node = self.simulator.nodes[target_node]
                if target_int in node.interfaces:
                    node.interfaces[target_int].status = "down"
                    node.interfaces[target_int].protocol = "down"
            
            fault_record = {
                "type": fault_type,
                "title": taxonomy_info["title"],
                "target_node": target_node,
                "target_interface": target_int,
                "timestamp": timestamp,
                "description": f"Interface {target_int} on {target_node} forced administratively down."
            }

        # 2. Subnet Misconfiguration (Layer 3)
        elif fault_type == "subnet_misconfig":
            target_node = params.get("target_node", taxonomy_info["default_target"])
            bad_gw = params.get("bad_gw", taxonomy_info["default_bad_gw"])
            bad_mask = params.get("bad_mask", taxonomy_info["default_bad_mask"])
            
            if target_node in self.simulator.nodes:
                node = self.simulator.nodes[target_node]
                node.default_gateway = bad_gw
                if "eth0" in node.interfaces:
                    node.interfaces["eth0"].subnet_mask = bad_mask
            
            fault_record = {
                "type": fault_type,
                "title": taxonomy_info["title"],
                "target_node": target_node,
                "bad_gateway": bad_gw,
                "bad_subnet_mask": bad_mask,
                "timestamp": timestamp,
                "description": f"Default gateway on {target_node} set to non-existent IP {bad_gw} and mask {bad_mask}."
            }

        # 3. ACL Traffic Drop (Layer 3/4)
        elif fault_type == "acl_blocking":
            target_node = params.get("target_node", taxonomy_info["default_target"])
            acl_name = taxonomy_info["acl_name"]
            rule = taxonomy_info["rule"]
            
            if target_node in self.simulator.nodes:
                node = self.simulator.nodes[target_node]
                node.acls = [{
                    "name": acl_name,
                    "applied_to": "GigabitEthernet0/0",
                    "direction": "in",
                    "rules": [rule, "permit ip any any"],
                    "matches": 0
                }]
                
            fault_record = {
                "type": fault_type,
                "title": taxonomy_info["title"],
                "target_node": target_node,
                "acl_name": acl_name,
                "rule": rule,
                "timestamp": timestamp,
                "description": f"Extended ACL '{acl_name}' applied to {target_node} dropping inter-branch traffic."
            }

        # 4. Routing Loop (Layer 3)
        elif fault_type == "routing_loop":
            target_node = params.get("target_node", taxonomy_info["default_target"])
            bad_route = taxonomy_info["bad_route"]
            
            if target_node in self.simulator.nodes:
                node = self.simulator.nodes[target_node]
                # Replace normal 192.168.20.0/24 route with loop route back to HQ-R1
                node.routes = [r for r in node.routes if r["prefix"] != bad_route["prefix"]]
                node.routes.append(bad_route)

            fault_record = {
                "type": fault_type,
                "title": taxonomy_info["title"],
                "target_node": target_node,
                "bad_route": bad_route,
                "timestamp": timestamp,
                "description": f"Conflicting static route on {target_node} pointing {bad_route['prefix']} back to {bad_route['nexthop']}."
            }

        # 5. DNS Failure (Layer 7)
        elif fault_type == "dns_failure":
            target_node = params.get("target_node", taxonomy_info["default_target"])
            bad_dns = params.get("bad_dns_server", taxonomy_info["bad_dns_server"])
            
            if target_node in self.simulator.nodes:
                node = self.simulator.nodes[target_node]
                node.dns_server = bad_dns

            fault_record = {
                "type": fault_type,
                "title": taxonomy_info["title"],
                "target_node": target_node,
                "bad_dns_server": bad_dns,
                "timestamp": timestamp,
                "description": f"Primary DNS server on {target_node} pointed to unreachable IP {bad_dns}."
            }

        # Record in simulator state
        # Remove any existing fault of this same type
        self.simulator.active_faults = [f for f in self.simulator.active_faults if f["type"] != fault_type]
        self.simulator.active_faults.append(fault_record)

        return {
            "status": "success",
            "fault": fault_record,
            "active_faults_count": len(self.simulator.active_faults)
        }

    def clear_all_faults(self) -> Dict[str, Any]:
        """Clears all active faults and resets topology to baseline."""
        return self.simulator.reset_topology()
