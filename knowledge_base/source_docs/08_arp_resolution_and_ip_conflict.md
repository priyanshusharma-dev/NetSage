# ARP Resolution, MAC Table Aging & Duplicate IP Conflict Guide

## Document Metadata
- **Category**: Address Resolution & Data Link (OSI Layer 2/3)
- **Device Type**: Linux Endpoints, Windows Clients & Cisco Access Switches
- **Applicable Commands**: `ip neigh show`, `arp -a`, `show ip arp`, `show mac address-table`

## Problem Description: Duplicate IP Conflicts & Incomplete ARP Entries
When two endpoints are configured with the same static IP address on a shared broadcast segment, or when a default gateway's MAC address is overwritten by gratuitous ARP or static entries, IP traffic experiences intermittent packet loss and sporadic session resets.
- **Symptom 1**: `ip neigh show` or `arp -a` reports `INCOMPLETE` or displays alternating MAC addresses for the same IP.
- **Symptom 2**: Intermittent ping loss (e.g. 50% packet loss, ping replies toggle between distinct hardware MACs).
- **Symptom 3**: Syslog on Cisco switches displays `%IP-4-DUP_ADDR: Duplicate address 192.168.10.10 on GigabitEthernet0/1, sourced by 5254.0012.3456`.

## Diagnostic Workflow
1. Inspect the local ARP cache: `ip neigh show` on Linux or `show ip arp` on Cisco IOS.
2. Clear the ARP cache to force fresh resolution: `sudo ip neigh flush all` or `clear arp-cache`.
3. Check switch MAC address table with `show mac address-table dynamic address <mac>` to trace the physical switchport of the rogue device.

## Recommended Fix & Remediation CLI
Reassign the conflicting host to a unique, available static IP or reconfigure DHCP:
```bash
# Flush stale ARP table
sudo ip neigh flush all

# Assign unique static IP address
sudo ip addr flush dev eth0
sudo ip addr add 192.168.10.15/24 dev eth0
sudo ip link set eth0 up
sudo ip route add default via 192.168.10.1 dev eth0
```
