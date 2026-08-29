# Layer 3 Routing Loops and Metric Conflicts Troubleshooting Guide

## Document Metadata
- **Category**: Routing & Control Plane (OSI Layer 3)
- **Device Type**: Cisco IOS Routers & Dynamic Routing Protocols (OSPF/Static)
- **Applicable Commands**: `show ip route`, `traceroute <ip>`, `show ip protocols`

## Problem Description: Routing Loop & TTL Expiration
A routing loop occurs when two or more routers forward packets for a specific destination prefix to each other recursively instead of toward the actual destination.
- **Symptom 1**: `traceroute` shows repeating/oscillating IP hops back and forth between two adjacent routers (e.g. Hop 1: 10.1.13.2, Hop 2: 10.1.13.1, Hop 3: 10.1.13.2...).
- **Symptom 2**: Traceroute terminates with `!H` or `Time to live exceeded in transit` after reaching max hop count (TTL decrementing to 0).
- **Symptom 3**: `ping` returns `TTTTT` (Time To Live exceeded).

## Diagnostic Workflow
1. Run `traceroute <destination-ip>` from source to observe path oscillation.
2. Run `show ip route <destination-ip>` on both suspected routers to identify the contradictory next-hop pointers.
3. Check for conflicting static routes or misconfigured route redistribution / administrative distance overrides.

## Recommended Fix & Remediation CLI
Correct the erroneous static route or restore OSPF dynamic path cost on the misconfigured router:
```ios
configure terminal
! Remove conflicting static route
no ip route 192.168.20.0 255.255.255.0 10.1.13.1
!
! Restore proper egress next-hop via Branch router interface (10.1.23.1)
ip route 192.168.20.0 255.255.255.0 10.1.23.1
 end
write memory
```
