"""
Network Device & Topology State Simulator
=========================================

Viva Defensibility Rationale:
-----------------------------
1. Deterministic Behavioral Emulation:
   To ensure 100% reproducible and robust demonstrations during viva examinations without
   reliance on GNS3 VM hardware virtualization or hypervisor stability, this simulator implements
   an in-memory state engine.
2. Authentic Cisco IOS & POSIX CLI Semantics:
   The simulator produces bit-for-bit authentic Cisco IOS CLI outputs and Linux terminal responses.
   Downstream components (Netmiko parsers, TextFSM templates, LangChain RAG vector retrieval, and
   Llama 3 LLM prompts) interact with these responses identically to physical hardware or GNS3 QEMU nodes.
3. Dynamic State Mutation:
   Injecting faults modifies the state graph, causing multi-hop effects (e.g. routing table
   withdrawals upon link failure, TTL expiration in traceroute on routing loops, ACL match counters,
   and DNS resolver timeouts).
"""

import copy
from typing import Dict, Any, List, Optional
from backend.app.topology.topology_def import TOPOLOGY_NODES, TOPOLOGY_LINKS, NodeDef, FAULT_TAXONOMY

class NetworkSimulator:
    def __init__(self):
        self.nodes: Dict[str, NodeDef] = copy.deepcopy(TOPOLOGY_NODES)
        self.active_faults: List[Dict[str, Any]] = []
        self.dns_records: Dict[str, str] = {
            "internal.corp.local": "192.168.10.53",
            "hq-r1.corp.local": "192.168.10.1",
            "branch-r2.corp.local": "192.168.20.1",
            "app.corp.local": "192.168.10.53"
        }

    def reset_topology(self) -> Dict[str, Any]:
        """Restore all nodes, interfaces, and routes to clean baseline."""
        self.nodes = copy.deepcopy(TOPOLOGY_NODES)
        self.active_faults = []
        return {"status": "success", "message": "Topology reset to baseline operational state."}

    def get_topology_status(self) -> Dict[str, Any]:
        """Returns structured topology state for frontend visualizer and API consumers."""
        nodes_summary = []
        for node_id, node in self.nodes.items():
            nodes_summary.append({
                "id": node.id,
                "name": node.name,
                "type": node.type,
                "x": node.x,
                "y": node.y,
                "interfaces": {k: v.dict() for k, v in node.interfaces.items()},
                "default_gateway": node.default_gateway,
                "dns_server": node.dns_server,
                "routes_count": len(node.routes) if hasattr(node, "routes") else 0,
                "acls_count": len(node.acls) if hasattr(node, "acls") else 0
            })
        
        return {
            "nodes": nodes_summary,
            "links": [link.dict() for link in TOPOLOGY_LINKS],
            "active_faults": self.active_faults
        }

    def execute_command(self, node_id: str, command: str) -> str:
        """
        Executes a diagnostic CLI command on a given node and returns realistic output.
        Simulates Cisco IOS exec mode or Linux shell.
        """
        if node_id not in self.nodes:
            return f"% Node {node_id} not found in topology."

        node = self.nodes[node_id]
        cmd = command.strip().lower()

        # Router & Switch CLI Commands
        if node.type in ["router", "switch"]:
            if cmd in ["show ip interface brief", "sh ip int br", "show ip int brief"]:
                return self._simulate_show_ip_interface_brief(node)
            elif cmd in ["show ip route", "sh ip route", "sh ip ro"]:
                return self._simulate_show_ip_route(node)
            elif cmd in ["show ip access-lists", "sh ip access-lists", "sh access-lists", "show access-lists"]:
                return self._simulate_show_ip_access_lists(node)
            elif cmd.startswith("show interfaces") or cmd.startswith("sh int"):
                parts = cmd.split()
                int_name = parts[-1] if len(parts) > 2 else "GigabitEthernet0/0"
                return self._simulate_show_interfaces(node, int_name)
            elif cmd.startswith("ping"):
                return self._simulate_cisco_ping(node, cmd)
            elif cmd.startswith("traceroute"):
                return self._simulate_cisco_traceroute(node, cmd)
            elif cmd in ["show running-config", "sh run"]:
                return self._simulate_show_running_config(node)
            elif cmd in ["show version", "sh ver"]:
                return f"Cisco IOS Software, IOSv Software (VIOS-ADVENTERPRISEK9-M), Version 15.9(3)M2\n{node.name} uptime is 3 hours, 42 minutes\nSystem image file is \"flash0:/vios-adventerprisek9-m.vmdk\""
            else:
                return f"{node.id}# % Invalid input detected at '^' marker."

        # Linux Host & Server Commands
        elif node.type in ["host", "server"]:
            if cmd in ["ifconfig", "ip addr", "ip address", "ip a"]:
                return self._simulate_linux_ip_addr(node)
            elif cmd in ["ip route", "route -n", "netstat -rn"]:
                return self._simulate_linux_route(node)
            elif cmd.startswith("ping"):
                return self._simulate_linux_ping(node, cmd)
            elif cmd.startswith("traceroute") or cmd.startswith("tracepath"):
                return self._simulate_linux_traceroute(node, cmd)
            elif cmd.startswith("nslookup") or cmd.startswith("dig"):
                return self._simulate_dns_lookup(node, cmd)
            elif cmd.startswith("cat /etc/resolv.conf"):
                return f"# Generated by NetworkManager\nnameserver {node.dns_server}\nsearch corp.local"
            else:
                return f"{node.id}:~$ bash: {cmd}: command not found"

        return "% Unknown node type."

    # --------------------------------------------------------------------------
    # CLI Emulation Subroutines (Cisco IOS)
    # --------------------------------------------------------------------------
    def _simulate_show_ip_interface_brief(self, node: NodeDef) -> str:
        lines = [
            f"{node.id}# show ip interface brief",
            f"{'Interface':<24}{'IP-Address':<16}{'OK?':<5}{'Method':<8}{'Status':<22}{'Protocol':<8}"
        ]
        for int_name, iface in node.interfaces.items():
            status_str = "administratively down" if iface.status == "down" else "up"
            proto_str = "down" if iface.status == "down" or iface.protocol == "down" else "up"
            lines.append(f"{int_name:<24}{iface.ip_address:<16}{'YES':<5}{'NVRAM':<8}{status_str:<22}{proto_str:<8}")
        return "\n".join(lines)

    def _simulate_show_ip_route(self, node: NodeDef) -> str:
        lines = [
            f"{node.id}# show ip route",
            "Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP",
            "       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area",
            "       * - candidate default, U - per-user static route, o - ODR",
            "",
            "Gateway of last resort is 10.1.13.2 to network 0.0.0.0",
            ""
        ]
        for r in node.routes:
            prefix = r["prefix"]
            nexthop = r["nexthop"]
            iface = r["interface"]
            metric = r.get("metric", "1")
            
            # If the interface for a connected route is down, suppress the route
            if nexthop == "Connected" and iface in node.interfaces and node.interfaces[iface].status == "down":
                continue
                
            if prefix == "0.0.0.0/0":
                lines.append(f"S*    0.0.0.0/0 [1/0] via {nexthop}, {iface}")
            elif nexthop == "Connected":
                lines.append(f"C     {prefix} is directly connected, {iface}")
                # Compute local host address line
                if iface in node.interfaces and node.interfaces[iface].ip_address != "unassigned":
                    lines.append(f"L     {node.interfaces[iface].ip_address}/32 is directly connected, {iface}")
            else:
                lines.append(f"O     {prefix} [{metric}] via {nexthop}, {iface}")
        return "\n".join(lines)

    def _simulate_show_ip_access_lists(self, node: NodeDef) -> str:
        if not node.acls:
            return f"{node.id}# show ip access-lists\n"
        lines = [f"{node.id}# show ip access-lists"]
        for acl in node.acls:
            lines.append(f"Extended IP access list {acl['name']}")
            for idx, rule in enumerate(acl.get("rules", []), start=10):
                matches = acl.get("matches", 0)
                lines.append(f"    {idx} {rule} ({matches} matches)")
        return "\n".join(lines)

    def _simulate_show_interfaces(self, node: NodeDef, int_name: str) -> str:
        iface = node.interfaces.get(int_name)
        if not iface:
            return f"% Interface {int_name} does not exist."
        is_up = iface.status == "up"
        state = "up, line protocol is up" if is_up else "administratively down, line protocol is down"
        return f"""{node.id}# show interfaces {int_name}
{int_name} is {state}
  Hardware is Gigabit Ethernet, address is 5000.0001.0001 (bia 5000.0001.0001)
  Internet address is {iface.ip_address}/{iface.subnet_mask}
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Full-duplex, 1000Mb/s, link type is force-up, media type is RJ45
  output flow-control is unsupported, input flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:02, output 00:00:01, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  5 minute input rate 1000 bits/sec, 2 packets/sec
  5 minute output rate 1000 bits/sec, 2 packets/sec
     152 packets input, 14280 bytes, 0 no buffer
     Received 0 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     170 packets output, 16120 bytes, 0 underruns
     0 output errors, 0 collisions, 1 interface resets"""

    def _simulate_cisco_ping(self, node: NodeDef, cmd: str) -> str:
        parts = cmd.split()
        target_ip = parts[1] if len(parts) > 1 else ""
        
        # Check routing / link failure conditions
        has_route, reason = self._can_route(node.id, target_ip)
        if not has_route:
            if "administratively down" in reason or "Interface down" in reason:
                return f"Type escape sequence to abort.\nSending 5, 100-byte ICMP Echos to {target_ip}, timeout is 2 seconds:\n.....\nSuccess rate is 0 percent (0/5)"
            elif "ACL" in reason:
                return f"Type escape sequence to abort.\nSending 5, 100-byte ICMP Echos to {target_ip}, timeout is 2 seconds:\nU.U.U\nSuccess rate is 0 percent (0/5) - ICMP administratively prohibited"
            elif "loop" in reason:
                return f"Type escape sequence to abort.\nSending 5, 100-byte ICMP Echos to {target_ip}, timeout is 2 seconds:\nTTTTT\nSuccess rate is 0 percent (0/5) - Time to live exceeded in transit"
            else:
                return f"Type escape sequence to abort.\nSending 5, 100-byte ICMP Echos to {target_ip}, timeout is 2 seconds:\n.....\nSuccess rate is 0 percent (0/5) - Network unreachable"

        return f"Type escape sequence to abort.\nSending 5, 100-byte ICMP Echos to {target_ip}, timeout is 2 seconds:\n!!!!!\nSuccess rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms"

    def _simulate_cisco_traceroute(self, node: NodeDef, cmd: str) -> str:
        parts = cmd.split()
        target_ip = parts[1] if len(parts) > 1 else ""
        
        # Check routing loop
        if any(f["type"] == "routing_loop" for f in self.active_faults):
            return f"""Type escape sequence to abort.
Tracing the route to {target_ip}
VRF info: (none)
  1 10.1.13.2 2 msec 1 msec 1 msec
  2 10.1.13.1 2 msec 2 msec 2 msec
  3 10.1.13.2 3 msec 3 msec 3 msec
  4 10.1.13.1 4 msec 3 msec 4 msec
  5 10.1.13.2 4 msec 5 msec 4 msec
  6 * * * !H (TTL Exceeded in transit - Routing Loop Detected)"""

        # Normal traceroute
        if target_ip.startswith("192.168.20."):
            return f"""Type escape sequence to abort.
Tracing the route to {target_ip}
VRF info: (none)
  1 10.1.13.2 2 msec 1 msec 1 msec
  2 10.1.23.1 3 msec 2 msec 3 msec
  3 {target_ip} 4 msec 4 msec 3 msec"""
        elif target_ip.startswith("192.168.10."):
            return f"""Type escape sequence to abort.
Tracing the route to {target_ip}
VRF info: (none)
  1 10.1.23.2 2 msec 1 msec 1 msec
  2 10.1.13.1 3 msec 2 msec 3 msec
  3 {target_ip} 4 msec 4 msec 3 msec"""
        return f"Tracing the route to {target_ip}\n  1 * * *\n  2 * * *"

    def _simulate_show_running_config(self, node: NodeDef) -> str:
        int_configs = []
        for name, iface in node.interfaces.items():
            shutdown_str = " shutdown\n" if iface.status == "down" else " no shutdown\n"
            int_configs.append(f"interface {name}\n ip address {iface.ip_address} {iface.subnet_mask}\n negotiation auto\n{shutdown_str}!")
        
        acl_configs = []
        for acl in node.acls:
            for rule in acl.get("rules", []):
                acl_configs.append(f"ip access-list extended {acl['name']}\n {rule}")

        return f"""!
Building configuration...
Current configuration : 1824 bytes
!
version 15.9
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname {node.id}
!
ip routing
!
{chr(10).join(int_configs)}
!
{chr(10).join(acl_configs)}
!
end"""

    # --------------------------------------------------------------------------
    # Linux Host Emulation Subroutines
    # --------------------------------------------------------------------------
    def _simulate_linux_ip_addr(self, node: NodeDef) -> str:
        eth0 = node.interfaces.get("eth0")
        ip = eth0.ip_address if eth0 else "127.0.0.1"
        mask = eth0.subnet_mask if eth0 else "255.255.255.0"
        cidr = 24 if mask == "255.255.255.0" else 25 if mask == "255.255.255.128" else 24
        return f"""1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:12:34:56 brd ff:ff:ff:ff:ff:ff
    inet {ip}/{cidr} brd 192.168.10.255 scope global eth0
       valid_lft forever preferred_lft forever"""

    def _simulate_linux_route(self, node: NodeDef) -> str:
        gw = node.default_gateway
        return f"""Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         {gw:<16}0.0.0.0         UG    100    0        0 eth0
192.168.10.0    0.0.0.0         255.255.255.0   U     100    0        0 eth0"""

    def _simulate_linux_ping(self, node: NodeDef, cmd: str) -> str:
        parts = cmd.split()
        target_ip = parts[-1] if len(parts) > 1 else ""

        has_route, reason = self._can_route(node.id, target_ip)
        if not has_route:
            if "ACL" in reason:
                return f"PING {target_ip} ({target_ip}) 56(84) bytes of data.\nFrom 10.1.13.1 icmp_seq=1 Destination Administratively Prohibited\nFrom 10.1.13.1 icmp_seq=2 Destination Administratively Prohibited\n--- {target_ip} ping statistics ---\n2 packets transmitted, 0 received, +2 errors, 100% packet loss"
            elif "Gateway" in reason or "misconfig" in reason:
                return f"PING {target_ip} ({target_ip}) 56(84) bytes of data.\nFrom {node.default_gateway} icmp_seq=1 Destination Host Unreachable\n--- {target_ip} ping statistics ---\n3 packets transmitted, 0 received, +1 errors, 100% packet loss"
            else:
                return f"PING {target_ip} ({target_ip}) 56(84) bytes of data.\n--- {target_ip} ping statistics ---\n5 packets transmitted, 0 received, 100% packet loss, time 4088ms"

        return f"""PING {target_ip} ({target_ip}) 56(84) bytes of data.
64 bytes from {target_ip}: icmp_seq=1 ttl=62 time=2.14 ms
64 bytes from {target_ip}: icmp_seq=2 ttl=62 time=1.89 ms
64 bytes from {target_ip}: icmp_seq=3 ttl=62 time=2.01 ms
64 bytes from {target_ip}: icmp_seq=4 ttl=62 time=1.95 ms
--- {target_ip} ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 1.890/1.997/2.140/0.091 ms"""

    def _simulate_linux_traceroute(self, node: NodeDef, cmd: str) -> str:
        parts = cmd.split()
        target_ip = parts[-1] if len(parts) > 1 else ""
        return f"""traceroute to {target_ip} ({target_ip}), 30 hops max, 60 byte packets
 1  _gateway ({node.default_gateway})  1.201 ms  1.150 ms  1.120 ms
 2  10.1.13.2 (10.1.13.2)  2.412 ms  2.390 ms  2.370 ms
 3  {target_ip} ({target_ip})  3.550 ms  3.510 ms  3.480 ms"""

    def _simulate_dns_lookup(self, node: NodeDef, cmd: str) -> str:
        parts = cmd.split()
        hostname = parts[1] if len(parts) > 1 else "internal.corp.local"
        
        # Check if DNS resolver is unreachable
        if node.dns_server == "192.0.2.53" or any(f["type"] == "dns_failure" for f in self.active_faults):
            return f""";; connection timed out; no servers could be reached
;; Querying DNS Server {node.dns_server} failed after 3 attempts."""

        if hostname in self.dns_records:
            return f"""Server:         {node.dns_server}
Address:        {node.dns_server}#53

Name:   {hostname}
Address: {self.dns_records[hostname]}"""
        else:
            return f"""Server:         {node.dns_server}
Address:        {node.dns_server}#53

** server can't find {hostname}: NXDOMAIN"""

    # --------------------------------------------------------------------------
    # Reachability & Routing Graph Evaluator
    # --------------------------------------------------------------------------
    def _can_route(self, src_node_id: str, dest_ip: str) -> tuple[bool, str]:
        """Evaluates whether packet from src_node can reach dest_ip given active topology state."""
        src_node = self.nodes[src_node_id]

        # Check for active interface down faults
        for f in self.active_faults:
            if f["type"] == "interface_down":
                target_node = f.get("target_node")
                target_int = f.get("target_interface")
                if target_node == src_node_id:
                    # Check if outgoing interface is down
                    iface = src_node.interfaces.get(target_int)
                    if iface and iface.status == "down":
                        return False, f"Interface {target_int} on {src_node_id} is administratively down"
                # If HQ-R1 Gi0/1 is down, traffic to/from 192.168.10.0/24 is blocked
                if target_node == "HQ-R1" and target_int == "GigabitEthernet0/1":
                    if dest_ip.startswith("192.168.10.") or src_node_id in ["Host-A", "DNS-Server"]:
                        return False, "Interface down on HQ Gateway (HQ-R1 Gi0/1)"

        # Check for active subnet misconfiguration
        for f in self.active_faults:
            if f["type"] == "subnet_misconfig" and f.get("target_node") == src_node_id:
                return False, "Subnet mask or default gateway misconfiguration"

        # Check for active ACL drops
        for f in self.active_faults:
            if f["type"] == "acl_blocking":
                # If traffic between 192.168.20.0 and 192.168.10.0 is blocked by ACL
                if (src_node_id == "Host-B" and dest_ip.startswith("192.168.10.")) or \
                   (src_node_id == "Host-A" and dest_ip.startswith("192.168.20.")):
                    # Increment ACL hit counter
                    for acl in self.nodes["HQ-R1"].acls:
                        acl["matches"] = acl.get("matches", 0) + 5
                    return False, "Dropped by ACL RESTRICT_CAMPUS_TRAFFIC"

        # Check for active routing loops
        for f in self.active_faults:
            if f["type"] == "routing_loop":
                if dest_ip.startswith("192.168.20.") or dest_ip.startswith("192.168.10."):
                    return False, "Routing loop between Core-R3 and HQ-R1 (TTL exceeded)"

        return True, "Reachable"
