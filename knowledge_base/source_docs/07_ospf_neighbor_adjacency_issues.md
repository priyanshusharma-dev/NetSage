# OSPF Routing Protocol Adjacency & Neighbor State Guide

## Document Metadata
- **Category**: Dynamic Routing Protocols (OSI Layer 3)
- **Device Type**: Cisco IOS Core & Edge Routers
- **Applicable Commands**: `show ip ospf neighbor`, `show ip ospf interface`, `show ip protocols`, `debug ip ospf adj`

## Problem Description: OSPF Neighbor Adjacency Failures
OSPF requires strict parameter matching between adjacent router interfaces to form full database synchronization (`FULL/DR` or `FULL/BDR`). If parameters conflict, neighbors get stuck in `INIT`, `2WAY`, or `EXSTART/EXCHANGE` states.
- **Symptom 1**: `show ip ospf neighbor` shows neighbor state stuck in `EXSTART/EXCHANGE` (typically caused by interface MTU mismatch preventing large Database Description packets from being acknowledged).
- **Symptom 2**: Neighbors stuck in `INIT` state (indicates one-way communication, e.g. an access-list blocking multicast `224.0.0.5` in one direction).
- **Symptom 3**: `show ip ospf neighbor` returns empty output despite physical links being up (Hello/Dead timer mismatch, Area ID mismatch, or passive-interface configuration).

## Diagnostic Workflow
1. Execute `show ip ospf neighbor` to inspect active neighbor relationships and current state transitions.
2. Check interface parameters with `show ip ospf interface <name>`: verify Area ID, Network Type (Broadcast vs Point-to-Point), and Hello/Dead timer intervals (default: 10s / 40s).
3. If stuck in `EXSTART`, verify interface MTU using `show interfaces <name>`.

## Recommended Fix & Remediation CLI
Correct timer, Area ID, or MTU ignore on the affected router interface:
```ios
configure terminal
interface GigabitEthernet0/0
 ip ospf 1 area 0
 ip ospf hello-interval 10
 ip ospf dead-interval 40
 ! If MTU differences cannot be resolved immediately:
 ip ospf mtu-ignore
 end
write memory
```
