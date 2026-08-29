"""
Network Topology Definition & Baseline Schema
==============================================

Viva Defensibility Rationale:
-----------------------------
1. Standard 3-Tier Enterprise Design:
   We utilize a canonical 3-tier enterprise topology (Edge-Core-Edge WAN with LAN access layers).
   This topology is standard in networking curricula (CCNA/CCNP, RFC standards) because it cleanly
   isolates broadcast domains, WAN transit points, routing boundaries, and host access subnets.
2. Defensible Fault Injection Boundaries:
   By having explicit WAN links (10.1.13.0/30, 10.1.23.0/30) and LAN access segments (192.168.10.0/24,
   192.168.20.0/24), we can deterministically model:
   - Layer 1/2 physical and data-link outages (Interface Down)
   - Layer 3 addressing/gateway mismatches (Subnet Misconfiguration)
   - Layer 3/4 filtering policies (ACL Drops)
   - Dynamic/Static convergence anomalies (Routing Loops & Blackholes)
   - Layer 7 name resolution failures (DNS resolution timeouts)
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field

class InterfaceDef(BaseModel):
    name: str
    ip_address: str
    subnet_mask: str
    connected_to: str
    status: str = "up"
    protocol: str = "up"
    speed_duplex: str = "1000Mb/s Full"

class NodeDef(BaseModel):
    id: str
    name: str
    type: str  # "router", "switch", "host", "server"
    model: str = "Cisco IOSv 15.9"
    interfaces: Dict[str, InterfaceDef]
    default_gateway: str = ""
    dns_server: str = ""
    routes: List[Dict[str, str]] = Field(default_factory=list)
    acls: List[Dict[str, Any]] = Field(default_factory=list)
    x: int
    y: int

class LinkDef(BaseModel):
    source_node: str
    source_port: str
    target_node: str
    target_port: str
    subnet: str
    status: str = "active"

# Canonical Campus Network Topology Baseline
TOPOLOGY_NODES: Dict[str, NodeDef] = {
    "HQ-R1": NodeDef(
        id="HQ-R1",
        name="HQ Edge Router (HQ-R1)",
        type="router",
        x=200,
        y=200,
        interfaces={
            "GigabitEthernet0/0": InterfaceDef(
                name="GigabitEthernet0/0",
                ip_address="10.1.13.1",
                subnet_mask="255.255.255.252",
                connected_to="Core-R3"
            ),
            "GigabitEthernet0/1": InterfaceDef(
                name="GigabitEthernet0/1",
                ip_address="192.168.10.1",
                subnet_mask="255.255.255.0",
                connected_to="SW1"
            )
        },
        routes=[
            {"prefix": "192.168.10.0/24", "nexthop": "Connected", "interface": "GigabitEthernet0/1", "metric": "0"},
            {"prefix": "10.1.13.0/30", "nexthop": "Connected", "interface": "GigabitEthernet0/0", "metric": "0"},
            {"prefix": "192.168.20.0/24", "nexthop": "10.1.13.2", "interface": "GigabitEthernet0/0", "metric": "110/20"},
            {"prefix": "0.0.0.0/0", "nexthop": "10.1.13.2", "interface": "GigabitEthernet0/0", "metric": "1"}
        ],
        acls=[]
    ),
    "Core-R3": NodeDef(
        id="Core-R3",
        name="Core Transit Router (Core-R3)",
        type="router",
        x=450,
        y=100,
        interfaces={
            "GigabitEthernet0/0": InterfaceDef(
                name="GigabitEthernet0/0",
                ip_address="10.1.13.2",
                subnet_mask="255.255.255.252",
                connected_to="HQ-R1"
            ),
            "GigabitEthernet0/1": InterfaceDef(
                name="GigabitEthernet0/1",
                ip_address="10.1.23.2",
                subnet_mask="255.255.255.252",
                connected_to="Branch-R2"
            )
        },
        routes=[
            {"prefix": "10.1.13.0/30", "nexthop": "Connected", "interface": "GigabitEthernet0/0", "metric": "0"},
            {"prefix": "10.1.23.0/30", "nexthop": "Connected", "interface": "GigabitEthernet0/1", "metric": "0"},
            {"prefix": "192.168.10.0/24", "nexthop": "10.1.13.1", "interface": "GigabitEthernet0/0", "metric": "110/10"},
            {"prefix": "192.168.20.0/24", "nexthop": "10.1.23.1", "interface": "GigabitEthernet0/1", "metric": "110/10"}
        ]
    ),
    "Branch-R2": NodeDef(
        id="Branch-R2",
        name="Branch Edge Router (Branch-R2)",
        type="router",
        x=700,
        y=200,
        interfaces={
            "GigabitEthernet0/0": InterfaceDef(
                name="GigabitEthernet0/0",
                ip_address="10.1.23.1",
                subnet_mask="255.255.255.252",
                connected_to="Core-R3"
            ),
            "GigabitEthernet0/1": InterfaceDef(
                name="GigabitEthernet0/1",
                ip_address="192.168.20.1",
                subnet_mask="255.255.255.0",
                connected_to="SW2"
            )
        },
        routes=[
            {"prefix": "192.168.20.0/24", "nexthop": "Connected", "interface": "GigabitEthernet0/1", "metric": "0"},
            {"prefix": "10.1.23.0/30", "nexthop": "Connected", "interface": "GigabitEthernet0/0", "metric": "0"},
            {"prefix": "192.168.10.0/24", "nexthop": "10.1.23.2", "interface": "GigabitEthernet0/0", "metric": "110/20"},
            {"prefix": "0.0.0.0/0", "nexthop": "10.1.23.2", "interface": "GigabitEthernet0/0", "metric": "1"}
        ]
    ),
    "SW1": NodeDef(
        id="SW1",
        name="HQ LAN Access Switch (SW1)",
        type="switch",
        model="Cisco IOSvL2",
        x=200,
        y=350,
        interfaces={
            "GigabitEthernet0/0": InterfaceDef(name="GigabitEthernet0/0", ip_address="unassigned", subnet_mask="", connected_to="HQ-R1"),
            "GigabitEthernet0/1": InterfaceDef(name="GigabitEthernet0/1", ip_address="unassigned", subnet_mask="", connected_to="Host-A"),
            "GigabitEthernet0/2": InterfaceDef(name="GigabitEthernet0/2", ip_address="unassigned", subnet_mask="", connected_to="DNS-Server")
        }
    ),
    "SW2": NodeDef(
        id="SW2",
        name="Branch LAN Access Switch (SW2)",
        type="switch",
        model="Cisco IOSvL2",
        x=700,
        y=350,
        interfaces={
            "GigabitEthernet0/0": InterfaceDef(name="GigabitEthernet0/0", ip_address="unassigned", subnet_mask="", connected_to="Branch-R2"),
            "GigabitEthernet0/1": InterfaceDef(name="GigabitEthernet0/1", ip_address="unassigned", subnet_mask="", connected_to="Host-B")
        }
    ),
    "Host-A": NodeDef(
        id="Host-A",
        name="HQ Workstation (Host-A)",
        type="host",
        model="Ubuntu/Debian Workstation",
        x=100,
        y=480,
        interfaces={
            "eth0": InterfaceDef(name="eth0", ip_address="192.168.10.10", subnet_mask="255.255.255.0", connected_to="SW1")
        },
        default_gateway="192.168.10.1",
        dns_server="192.168.10.53"
    ),
    "DNS-Server": NodeDef(
        id="DNS-Server",
        name="Internal DNS/Web Server",
        type="server",
        model="Linux Bind9/HTTP",
        x=300,
        y=480,
        interfaces={
            "eth0": InterfaceDef(name="eth0", ip_address="192.168.10.53", subnet_mask="255.255.255.0", connected_to="SW1")
        },
        default_gateway="192.168.10.1"
    ),
    "Host-B": NodeDef(
        id="Host-B",
        name="Branch Workstation (Host-B)",
        type="host",
        model="Ubuntu/Debian Workstation",
        x=700,
        y=480,
        interfaces={
            "eth0": InterfaceDef(name="eth0", ip_address="192.168.20.20", subnet_mask="255.255.255.0", connected_to="SW2")
        },
        default_gateway="192.168.20.1",
        dns_server="192.168.10.53"
    )
}

TOPOLOGY_LINKS: List[LinkDef] = [
    LinkDef(source_node="HQ-R1", source_port="GigabitEthernet0/0", target_node="Core-R3", target_port="GigabitEthernet0/0", subnet="10.1.13.0/30"),
    LinkDef(source_node="Branch-R2", source_port="GigabitEthernet0/0", target_node="Core-R3", target_port="GigabitEthernet0/1", subnet="10.1.23.0/30"),
    LinkDef(source_node="HQ-R1", source_port="GigabitEthernet0/1", target_node="SW1", target_port="GigabitEthernet0/0", subnet="192.168.10.0/24"),
    LinkDef(source_node="SW1", source_port="GigabitEthernet0/1", target_node="Host-A", target_port="eth0", subnet="192.168.10.0/24"),
    LinkDef(source_node="SW1", source_port="GigabitEthernet0/2", target_node="DNS-Server", target_port="eth0", subnet="192.168.10.0/24"),
    LinkDef(source_node="Branch-R2", source_port="GigabitEthernet0/1", target_node="SW2", target_port="GigabitEthernet0/0", subnet="192.168.20.0/24"),
    LinkDef(source_node="SW2", source_port="GigabitEthernet0/1", target_node="Host-B", target_port="eth0", subnet="192.168.20.0/24")
]

# Supported Fault Taxonomy & Injection Signatures
FAULT_TAXONOMY = {
    "interface_down": {
        "title": "Layer 1/2 Interface Administratively Down",
        "description": "Simulates an operator shutting down a critical uplink interface or a physical cable unplug.",
        "default_target": "HQ-R1",
        "default_interface": "GigabitEthernet0/1",
        "affected_subnets": ["192.168.10.0/24"]
    },
    "subnet_misconfig": {
        "title": "Layer 3 Subnet / Gateway Address Misconfiguration",
        "description": "Simulates incorrect IP subnetting or mismatched default gateway on a client/router boundary.",
        "default_target": "Host-B",
        "default_bad_ip": "192.168.20.20",
        "default_bad_mask": "255.255.255.128",
        "default_bad_gw": "192.168.20.254"
    },
    "acl_blocking": {
        "title": "Layer 3/4 Extended Access List Traffic Drop",
        "description": "Simulates an overzealous security ACL applied outbound/inbound dropping ICMP echo and TCP traffic.",
        "default_target": "HQ-R1",
        "default_interface": "GigabitEthernet0/0",
        "acl_name": "RESTRICT_CAMPUS_TRAFFIC",
        "rule": "deny ip 192.168.20.0 0.0.0.255 192.168.10.0 0.0.0.255"
    },
    "routing_loop": {
        "title": "Layer 3 Static Routing Loop & Blackhole",
        "description": "Simulates mutual next-hop route misdirection causing TTL expiration loops between Core-R3 and Branch-R2.",
        "default_target": "Core-R3",
        "bad_route": {"prefix": "192.168.20.0/24", "nexthop": "10.1.13.1", "interface": "GigabitEthernet0/0"}
    },
    "dns_failure": {
        "title": "Layer 7 DNS Name Resolution Failure",
        "description": "Simulates invalid or unreachable DNS resolver IP address resulting in DNS query timeouts.",
        "default_target": "Host-A",
        "bad_dns_server": "192.0.2.53"  # RFC 5737 TEST-NET address (unreachable)
    }
}
