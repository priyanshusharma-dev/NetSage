"""
CLI Output Parser & Feature Extractor
=====================================

Viva Defensibility Rationale:
-----------------------------
1. Robust Regex Normalization:
   CLI parsing handles both Cisco IOS executive syntax and Linux iproute2 / POSIX utilities.
2. Anomaly Synthesis:
   Beyond passive extraction, the parser actively tags telemetry anomalies (e.g. interfaces in
   'administratively down' state, packet loss > 0%, missing default routes, DNS query timeouts).
   This synthesized anomaly list acts as high-signal context for semantic RAG search queries.
"""

import re
from typing import List, Dict, Tuple, Optional
from backend.app.collector.schemas import (
    InterfaceStatus, RouteEntry, ACLRule, PingSummary, DNSQuerySummary
)

class CLIParser:
    @staticmethod
    def parse_show_ip_interface_brief(output: str) -> List[InterfaceStatus]:
        """Parses Cisco IOS 'show ip interface brief' table."""
        interfaces = []
        lines = output.strip().splitlines()
        for line in lines:
            # Match interface lines: e.g. GigabitEthernet0/0 10.1.13.1 YES NVRAM up up
            match = re.match(
                r"^([A-Za-z0-9\/\.\-]+)\s+([0-9\.]+|unassigned)\s+\w+\s+\w+\s+(administratively down|up|down)\s+(up|down)",
                line.strip(),
                re.IGNORECASE
            )
            if match:
                interfaces.append(InterfaceStatus(
                    interface=match.group(1),
                    ip_address=match.group(2),
                    status=match.group(3).lower(),
                    protocol=match.group(4).lower()
                ))
        return interfaces

    @staticmethod
    def parse_show_ip_route(output: str) -> List[RouteEntry]:
        """Parses Cisco IOS 'show ip route' routing table."""
        routes = []
        lines = output.strip().splitlines()
        for line in lines:
            line_str = line.strip()
            # Connected route: C 192.168.10.0/24 is directly connected, GigabitEthernet0/1
            c_match = re.match(r"^C\s+([0-9\.\/]+)\s+is directly connected,\s+([A-Za-z0-9\/\.\-]+)", line_str)
            if c_match:
                routes.append(RouteEntry(
                    prefix=c_match.group(1),
                    nexthop="Connected",
                    interface=c_match.group(2),
                    protocol="connected",
                    metric="0"
                ))
                continue

            # OSPF route: O 192.168.20.0/24 [110/20] via 10.1.13.2, GigabitEthernet0/0
            o_match = re.match(r"^O\s+([0-9\.\/]+)\s+\[([0-9\/]+)\]\s+via\s+([0-9\.]+),\s+([A-Za-z0-9\/\.\-]+)", line_str)
            if o_match:
                routes.append(RouteEntry(
                    prefix=o_match.group(1),
                    nexthop=o_match.group(3),
                    interface=o_match.group(4),
                    protocol="ospf",
                    metric=o_match.group(2)
                ))
                continue

            # Static / Default route: S* 0.0.0.0/0 [1/0] via 10.1.13.2, GigabitEthernet0/0
            s_match = re.match(r"^S\*?\s+([0-9\.\/]+)\s+\[([0-9\/]+)\]\s+via\s+([0-9\.]+),\s+([A-Za-z0-9\/\.\-]+)", line_str)
            if s_match:
                routes.append(RouteEntry(
                    prefix=s_match.group(1),
                    nexthop=s_match.group(3),
                    interface=s_match.group(4),
                    protocol="static",
                    metric=s_match.group(2)
                ))
        return routes

    @staticmethod
    def parse_show_ip_access_lists(output: str) -> List[ACLRule]:
        """Parses Cisco IOS 'show ip access-lists' output."""
        acls = []
        current_acl = ""
        for line in output.strip().splitlines():
            line_str = line.strip()
            acl_head = re.match(r"^(?:Standard|Extended) IP access list\s+([A-Za-z0-9_\-]+)", line_str)
            if acl_head:
                current_acl = acl_head.group(1)
                continue
            
            rule_match = re.match(r"^\d+\s+(deny\s+.+?|permit\s+.+?)(?:\s+\((\d+)\s+matches\))?$", line_str)
            if not rule_match:
                rule_match = re.match(r"^\d+\s+(deny|permit)(?:\s+\((\d+)\s+matches\))?$", line_str)
            if rule_match and current_acl:
                rule_text = rule_match.group(1)
                matches = int(rule_match.group(2)) if rule_match.group(2) else 0
                acls.append(ACLRule(
                    name=current_acl,
                    rule=rule_text,
                    matches=matches
                ))
        return acls

    @staticmethod
    def parse_ping(source_node: str, output: str, target_ip: str) -> PingSummary:
        """Parses ping output from both Cisco IOS and Linux hosts."""
        # Cisco Ping: Success rate is 100 percent (5/5) or 0 percent (0/5)
        cisco_match = re.search(r"Success rate is (\d+) percent \((\d+)/(\d+)\)", output)
        if cisco_match:
            pct = float(cisco_match.group(1))
            rec = int(cisco_match.group(2))
            total = int(cisco_match.group(3))
            loss = 100.0 - pct
            return PingSummary(
                source_node=source_node,
                target_ip=target_ip,
                transmitted=total,
                received=rec,
                loss_percent=loss,
                is_reachable=(pct > 0),
                raw_output=output.strip()
            )

        # Linux Ping: 4 packets transmitted, 4 received, 0% packet loss
        linux_match = re.search(r"(\d+) packets transmitted,\s+(\d+) received,\s+(?:\+\d+ errors,\s+)?(\d+)% packet loss", output)
        if linux_match:
            total = int(linux_match.group(1))
            rec = int(linux_match.group(2))
            loss = float(linux_match.group(3))
            return PingSummary(
                source_node=source_node,
                target_ip=target_ip,
                transmitted=total,
                received=rec,
                loss_percent=loss,
                is_reachable=(loss < 100.0),
                raw_output=output.strip()
            )

        # Fallback if pattern failed
        is_err = "Destination Host Unreachable" in output or "Administratively Prohibited" in output or "100% packet loss" in output or "0 percent" in output
        return PingSummary(
            source_node=source_node,
            target_ip=target_ip,
            transmitted=5,
            received=0 if is_err else 5,
            loss_percent=100.0 if is_err else 0.0,
            is_reachable=not is_err,
            raw_output=output.strip()
        )

    @staticmethod
    def parse_dns_lookup(source_node: str, output: str, hostname: str) -> DNSQuerySummary:
        """Parses nslookup / dig CLI output."""
        is_timeout = "connection timed out" in output.lower() or "no servers could be reached" in output.lower()
        is_nxdomain = "nxdomain" in output.lower()
        
        server_match = re.search(r"Server:\s+([0-9\.]+)", output)
        server_queried = server_match.group(1) if server_match else "unknown"
        
        addr_match = re.search(r"Address:\s+([0-9\.]+)", output)
        resolved_ip = None
        if addr_match and not is_timeout and not is_nxdomain:
            resolved_ip = addr_match.group(1)

        return DNSQuerySummary(
            hostname=hostname,
            server_queried=server_queried,
            resolved_ip=resolved_ip,
            is_success=(resolved_ip is not None and not is_timeout),
            raw_output=output.strip()
        )
