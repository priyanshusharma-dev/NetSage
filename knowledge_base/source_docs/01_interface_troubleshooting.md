# Cisco IOS & Enterprise Network Interface Troubleshooting Guide

## Document Metadata
- **Category**: Physical and Data-Link Layer (OSI Layer 1/2)
- **Device Type**: Cisco IOS Routers & Switches
- **Applicable Commands**: `show ip interface brief`, `show interfaces <name>`, `shutdown`, `no shutdown`

## Problem Description: Administratively Down Interface
When an interface displays `Status: administratively down` and `Protocol: down`, the interface has been explicitly disabled using the Cisco IOS `shutdown` configuration command.
- **Symptom 1**: `show ip interface brief` indicates `administratively down` under Status.
- **Symptom 2**: Direct pings to any device connected to that interface fail with 0% success rate (loss 100%).
- **Symptom 3**: The router will automatically remove any directly connected route corresponding to this interface from its routing table (`show ip route`).

## Diagnostic Workflow
1. Run `show ip interface brief` to identify interfaces marked `administratively down`.
2. Run `show interfaces <interface-id>` to check link counters and verify duplex/speed negotiation.
3. Verify if connected devices or local subnets have lost access to their default gateway.

## Recommended Fix & Remediation CLI
Enter global configuration mode on the affected router and execute `no shutdown`:
```ios
configure terminal
interface GigabitEthernet0/1
 no shutdown
 end
write memory
```
After executing `no shutdown`, verify that the interface transitions to `Status: up` and `Protocol: up`.
