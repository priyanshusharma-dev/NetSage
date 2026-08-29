# Layer 7 DNS Resolution & Name-Server Failure Troubleshooting Guide

## Document Metadata
- **Category**: Application Layer Name Resolution (OSI Layer 7)
- **Device Type**: Linux Hosts, Windows Clients & Enterprise DNS Resolvers
- **Applicable Commands**: `nslookup <hostname>`, `dig <hostname>`, `cat /etc/resolv.conf`, `ip name-server`

## Problem Description: DNS Resolver Timeout & Unreachability
When an endpoint's configured nameserver is down, misconfigured, or unreachable over the network, domain lookups fail even if underlying Layer 1–3 IP reachability is intact.
- **Symptom 1**: Direct IP pings (e.g. `ping 192.168.10.53`) work successfully, but hostname pings (e.g. `ping internal.corp.local`) fail with `cannot resolve host`.
- **Symptom 2**: `nslookup` or `dig` returns `;; connection timed out; no servers could be reached` or `Querying DNS Server failed after 3 attempts`.
- **Symptom 3**: Inspecting `/etc/resolv.conf` reveals a non-existent or invalid nameserver IP (e.g. `192.0.2.53`).

## Diagnostic Workflow
1. Run `nslookup internal.corp.local` to test DNS queries.
2. Check the configured nameserver using `cat /etc/resolv.conf` (Linux) or `show hosts` (Cisco).
3. Ping the nameserver IP directly to distinguish between network reachability vs server daemon fault.

## Recommended Fix & Remediation CLI
Update the resolver configuration to point to the active corporate DNS server (`192.168.10.53`):
```bash
# On Linux Host:
sudo sed -i 's/nameserver .*/nameserver 192.168.10.53/' /etc/resolv.conf

# Or using resolvconf / NetworkManager:
echo "nameserver 192.168.10.53" | sudo tee /etc/resolv.conf

# On Cisco IOS:
configure terminal
no ip name-server 192.0.2.53
ip name-server 192.168.10.53
end
write memory
```
