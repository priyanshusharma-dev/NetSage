# IP Addressing, Subnet Mask & Default Gateway Troubleshooting Guide

## Document Metadata
- **Category**: Network Layer Addressing (OSI Layer 3)
- **Device Type**: Linux Hosts, Windows Clients & Cisco Gateways
- **Applicable Commands**: `ip addr`, `ip route`, `route -n`, `ping <gateway>`

## Problem Description: Subnet Mask & Default Gateway Mismatch
A host cannot communicate outside its local subnet if its configured default gateway is incorrect, outside its subnet boundary, or unreachable due to an invalid subnet mask (e.g. /25 vs /24).
- **Symptom 1**: Host ping to local IP address succeeds (loopback and self IP work).
- **Symptom 2**: Host ping to its default gateway fails with `Destination Host Unreachable` or 100% packet loss.
- **Symptom 3**: Cross-subnet communication to remote networks or external servers fails completely.

## Diagnostic Workflow
1. Check host network configuration using `ip addr show` or `ifconfig`.
2. Inspect the active default route using `ip route show` or `route -n`.
3. Verify that the configured gateway IP address belongs to the subnet defined by the host's IP and subnet mask.
4. Verify ARP resolution to gateway using `ip neigh show` or `arp -a`.

## Recommended Fix & Remediation CLI
On the affected host, reconfigure the correct default gateway and matching subnet mask:
```bash
# Reconfigure default gateway to point to router interface (e.g. 192.168.20.1)
sudo ip route del default
sudo ip route add default via 192.168.20.1 dev eth0

# Or reconfigure full static IP and mask:
sudo ip addr flush dev eth0
sudo ip addr add 192.168.20.20/24 dev eth0
sudo ip link set eth0 up
sudo ip route add default via 192.168.20.1 dev eth0
```
