# NetSage ⚡ Autonomous AI Network Troubleshooting System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14%2B-black?logo=next.js&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange?logo=chroma&logoColor=white)
![Groq Llama 3](https://img.shields.io/badge/Groq-Llama_3.3_70B-purple?logo=meta&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**An autonomous LLM-assisted network diagnostics and automated remediation platform with RAG vector retrieval, configurable safety gatekeeping, and real-time topology visualization.**

[Live Web UI](#-quick-start) • [Architecture](#-architecture) • [Supported Faults](#-supported-fault-taxonomy) • [Viva Defense Guide](#-viva-voce-defensibility)

</div>

---

## 📖 Overview

**NetSage** is a solo university research project for a Computer Networking curriculum that demonstrates an end-to-end **closed-loop autonomous network troubleshooting system**. 

Unlike naive LLM wrappers that hallucinate commands, NetSage introduces an **explainable RAG architecture** combined with a **Statistical Fallback Gatekeeper** that refuses to emit unverified remediation commands when diagnostic certainty falls below threshold boundaries.

### 🌟 Key Features
- **Deterministic 8-Node Campus Topology**: Simulates realistic Cisco IOS and Linux POSIX nodes (`HQ-R1`, `Core-R3`, `Branch-R2`, `SW1`, `SW2`, `Host-A`, `Host-B`, `DNS-Server`). Supports in-memory simulation and live GNS3 REST API v2.
- **Chaos Engineering Fault Deck**: Programmatic injection across OSI Layers 1 through 7 (`interface_down`, `subnet_misconfig`, `acl_blocking`, `routing_loop`, `dns_failure`).
- **Active Telemetry Extraction**: Netmiko-driven command parsing (`show ip route`, `show ip int br`, `ping`, `traceroute`, `nslookup`).
- **Domain RAG via ChromaDB**: `sentence-transformers/all-MiniLM-L6-v2` dense vector retrieval over curated networking knowledge bases.
- **Dual-Tier LLM Orchestration**: Primary cloud inference via **Groq Llama 3.3 70B**, automated failover to **Local Ollama**, and an air-gapped deterministic expert engine.
- **Safety Gatekeeper (Defensible Deferral)**: Multi-threshold guardrail ($d_{\text{min}} > 0.85$ or $C_{\text{LLM}} < 65\%$) that yields control to human engineers with: `"Insufficient evidence — escalate to manual diagnosis"`.
- **Interactive Web Terminal Console**: Real-time Cisco IOS exec shell on any node from the web browser.
- **Persistent SQLite Audit Logger**: Ground-truth accuracy telemetry tracking with one-click verification labeling.

---

## 🏛 Architecture

```mermaid
flowchart TD
    subgraph Control_Plane ["Control Plane & Chaos Engine"]
        A[Fault Injector: 5 OSI Layer Faults] -->|Mutate State| B[Cisco IOS / Linux Network Topology]
    end

    subgraph Data_Plane ["Telemetry & Probing Plane"]
        B -->|CLI Probes| C[Netmiko Diagnostic Runner]
        C -->|show ip route, ping, nslookup| D[Structured Feature Parser & Anomaly Extractor]
    end

    subgraph Cognitive_Plane ["AI Cognitive & RAG Plane"]
        D -->|Symptom Summary| E[ChromaDB Vector Store: all-MiniLM-L6-v2]
        E -->|Top-k Chunks + Cosine Dist| F[Prompt Config Builder]
        F -->|JSON Schema Prompt| G[Dual LLM Router: Groq Llama 3 / Ollama]
        G -->|Self-Confidence & Root Cause JSON| H[Fallback Gatekeeper]
    end

    subgraph Safety_Plane ["Safety & Audit Plane"]
        H -->|Sim Dist > Max OR Conf < Min| I[Escalate to Manual NOC Review]
        H -->|Passed Checks| J[Autonomous Root Cause & CLI Remediation]
        I --> K[(SQLite Persistent Audit DB)]
        J --> K
        K --> L[Next.js Interactive Dashboard]
    end
```

---

## 🎯 Supported Fault Taxonomy

| OSI Layer | Fault Identifier | Injected Failure Mechanism | Diagnostic Signature | Recommended Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **Layer 1/2** | `interface_down` | Administrative shutdown on gateway interface | `show ip int br` reports `administratively down`, 0% ping | `configure terminal`<br>`interface Gi0/1`<br>`no shutdown` |
| **Layer 3** | `subnet_misconfig` | Mismatched default gateway & invalid subnet mask | Host ping returns `Destination Host Unreachable` | `sudo ip route add default via 192.168.20.1` |
| **Layer 3/4** | `acl_blocking` | Extended ACL filtering inter-subnet IP packets | ICMP probe returns `Destination Administratively Prohibited` | `configure terminal`<br>`interface Gi0/0`<br>`no ip access-group RESTRICT_CAMPUS_TRAFFIC in` |
| **Layer 3** | `routing_loop` | Conflicting static route pointer between Core & HQ | `traceroute` shows repeating hops & TTL exceeded (`!H`) | `no ip route 192.168.20.0 255.255.255.0 10.1.13.1`<br>`ip route 192.168.20.0 255.255.255.0 10.1.23.1` |
| **Layer 7** | `dns_failure` | Nameserver pointed to unreachable IP (`192.0.2.53`) | `nslookup` connection timed out after 3 attempts | `echo 'nameserver 192.168.10.53' \| sudo tee /etc/resolv.conf` |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/your-username/NetSage.git
cd NetSage

# Install Python dependencies
pip install -r backend/requirements.txt
pip install chromadb sentence-transformers

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Start Backend & Frontend Services
```bash
# Terminal 1: Launch FastAPI Backend (Port 8000)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Launch Next.js Dashboard (Port 3000)
cd frontend
npm run dev
```

Open **`http://localhost:3000`** in your browser. (Interactive API docs at **`http://localhost:8000/docs`**).

---

## 🎓 Viva Voce Defensibility

Key talking points for academic examination:
1. **Explainable AI**: The system never obscures RAG retrieval. Exact vector chunks, cosine distances, and source documents are exposed in both the UI and SQLite audit logs.
2. **Failure-Safe AI (Safe Deferral)**: Demonstrates defensive engineering by computing uncertainty boundaries and refusing to hallucinate dangerous CLI commands.
3. **Dual-Backend Zero-Flake Design**: Operates seamlessly in deterministic simulated mode for live presentations without requiring heavy virtualization hypervisors.
4. **Detailed Defense Resources**: See **[docs/VIVA_DEFENSE_GUIDE.md](docs/VIVA_DEFENSE_GUIDE.md)** and **[docs/documented_failure_cases.md](docs/documented_failure_cases.md)**.

---

## 📂 Project Structure

```text
NetSage/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints
│   │   ├── collector/       # Netmiko telemetry & regex parsers
│   │   ├── kb/              # ChromaDB vector store & all-MiniLM-L6-v2 embeddings
│   │   ├── rag/             # Prompt engineering, LLM router & Fallback Gatekeeper
│   │   ├── topology/        # 8-node Campus topology & simulation state engine
│   │   ├── config.py        # Centralized settings & thresholds
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # Automated test suites (unit & e2e)
│   └── requirements.txt     # Backend Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js 14 App Router (page.tsx, globals.css)
│   │   └── components/      # UI components (TopologyView, Terminal, Radial Gauge, etc.)
│   └── package.json         # Frontend Node dependencies
├── knowledge_base/
│   └── source_docs/         # Curated markdown troubleshooting guides
├── docs/                    # Viva voce examination guide & failure case analysis
├── .env.example             # Template environment variables
├── .gitignore               # Standard repository ignore rules
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
