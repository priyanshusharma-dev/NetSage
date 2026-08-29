# Cisco IOS Access Control List (ACL) Traffic Filtering Guide

## Document Metadata
- **Category**: Security & Traffic Filtering (OSI Layer 3/4)
- **Device Type**: Cisco IOS Routers & Layer 3 Switches
- **Applicable Commands**: `show ip access-lists`, `show running-config interface <name>`, `ip access-group`

## Problem Description: Traffic Dropped by Access List
Access Control Lists filter traffic based on source IP, destination IP, protocol, and port numbers. When a deny rule matches or the implicit `deny ip any any` at the end of an ACL triggers, legitimate traffic is discarded.
- **Symptom 1**: Pings to destination IP return `Destination Administratively Prohibited` or `U.U.U` (ICMP Unreachable type 3 code 13).
- **Symptom 2**: `show ip access-lists` displays non-zero match counters on specific `deny` statements.
- **Symptom 3**: Layer 1/2 and Layer 3 routes are completely healthy, but TCP/UDP/ICMP payloads are silently dropped at the ingress or egress interface.

## Diagnostic Workflow
1. Run `show ip access-lists` to inspect configured standard/extended ACLs and their hit counts.
2. Run `show ip interface <interface-name>` to identify which ACL is applied and in which direction (`inbound` or `outbound`).
3. Cross-reference source and destination subnets against the permit/deny sequences.

## Recommended Fix & Remediation CLI
Remove the blocking ACL from the interface or amend the rule to permit valid campus traffic:
```ios
configure terminal
! Option A: Remove ACL from interface
interface GigabitEthernet0/0
 no ip access-group RESTRICT_CAMPUS_TRAFFIC in
!
! Option B: Remove the blocking deny rule
ip access-list extended RESTRICT_CAMPUS_TRAFFIC
 no deny ip 192.168.20.0 0.0.0.255 192.168.10.0 0.0.0.255
 permit ip 192.168.20.0 0.0.0.255 192.168.10.0 0.0.0.255
 end
write memory
```
