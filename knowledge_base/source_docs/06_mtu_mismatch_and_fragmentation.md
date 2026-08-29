# MTU Mismatch, Path MTU Discovery & Packet Fragmentation Guide

## Document Metadata
- **Category**: Data-Link & Transport Layer Sizing (OSI Layer 2/3/4)
- **Device Type**: Cisco IOS Routers, Layer 3 Switches & WAN Links
- **Applicable Commands**: `ping <ip> size <bytes> df-bit`, `show interfaces <name>`, `ip mtu <bytes>`, `ip tcp adjust-mss`

## Problem Description: MTU Black Hole & Large Packet Drop
When intermediate WAN links or tunnel endpoints (GRE/IPsec) have a lower Maximum Transmission Unit (MTU) than the default 1500 bytes and Path MTU Discovery (PMTUD) is blocked by firewalls dropping ICMP Type 3 Code 4 (Fragmentation Needed), large TCP payloads or large ICMP packets are silently dropped while standard small pings (64/100 bytes) continue to succeed.
- **Symptom 1**: Standard 100-byte ICMP pings succeed with 100% receipt, but large file transfers (HTTP/HTTPS/SSH) stall or hang indefinitely after the initial TCP 3-way handshake.
- **Symptom 2**: Executing `ping 10.1.13.2 size 1500 df-bit` fails with `Packet needs to be fragmented but DF set` or 100% loss.
- **Symptom 3**: `show interfaces` indicates MTU mismatches (e.g. MTU 1400 on router vs MTU 1500 on host).

## Diagnostic Workflow
1. Perform an ICMP MTU sweep: `ping <destination-ip> size 1472 df-bit` and decrease size incrementally to identify the maximum supported unfragmented payload.
2. Check interface MTU settings using `show interfaces GigabitEthernet0/0` on all hops along the path.
3. Verify if an upstream firewall is dropping ICMP "Fragmentation Needed and DF set" messages.

## Recommended Fix & Remediation CLI
Align MTU across transit interfaces or enable TCP MSS clamping on ingress gateway interfaces:
```ios
configure terminal
interface GigabitEthernet0/0
 ip mtu 1500
 ip tcp adjust-mss 1460
 end
write memory
```
