# NetSage: Academic Viva Voce Defense Guide & Architecture Blueprint

## 1. Project Synopsis
**NetSage** is an autonomous network troubleshooting system combining active telemetry probing, Retrieval-Augmented Generation (RAG) over curated networking knowledge bases, and dual-tier LLM inference with a safety fallback gatekeeper.

---

## 2. Core Architectural Questions & Defensible Answers

### Q1: Why use RAG instead of directly fine-tuning an LLM or using raw prompts?
- **Viva Defense Rationale**:
  1. **Hallucination Prevention**: Raw LLMs frequently invent non-existent Cisco IOS commands or configure wrong subnet masks. RAG grounds the prompt in verified syntax and proven troubleshooting workflows.
  2. **Auditability & Explainability**: In mission-critical network operations, operators and auditors must know *why* an action was taken. NetSage explicitly exposes the exact vector chunks, source documents, and cosine distances used in every diagnosis.
  3. **Zero Retraining Overhead**: When new network devices, firmware updates, or company policies are introduced, adding a new markdown document to `knowledge_base/source_docs/` and running `ingest.py` updates the system instantly without expensive retraining or GPU fine-tuning.

---

### Q2: Why use `all-MiniLM-L6-v2` embeddings in ChromaDB?
- **Viva Defense Rationale**:
  1. **Latency & Local Execution**: `all-MiniLM-L6-v2` produces compact 384-dimensional dense vectors with sub-15ms embedding latency on standard laptop CPUs.
  2. **Semantic Similarity on Technical Corpus**: Pretrained on 1B+ sentence pairs, capturing semantic intent across technical jargon (e.g. mapping "administratively down" to "shutdown interface fix").

---

### Q3: What is the purpose of the Fallback Gatekeeper?
- **Viva Defense Rationale**:
  1. **Safe Deferral (Failure-Safe Engineering)**: Unlike naive AI wrappers that always output an answer, NetSage implements a dual-threshold filter:
     - **Threshold A (Retrieval Cosine Distance)**: If $d_{\text{min}} > \theta_{\text{dist}}$ (default 0.85), domain knowledge is deemed insufficient.
     - **Threshold B (LLM Self-Confidence)**: If $C_{\text{LLM}} < \theta_{\text{conf}}$ (default 65%), the LLM's certainty is deemed unacceptably low.
  2. If either condition triggers, NetSage executes the **Defensible Deferral Pattern**, yielding control to human engineers with: `"Insufficient evidence — escalate to manual diagnosis"`.

---

### Q4: Why support both In-Memory Simulation and GNS3 REST API?
- **Viva Defense Rationale**:
  - Eliminates external hypervisor failure risks during live academic demonstrations. The in-memory state engine reproduces authentic Cisco IOS CLI outputs and dynamic state mutations (routing table withdrawal, traceroute TTL loop oscillations, ACL match increments). Switching to live GNS3 is accomplished simply by changing `TOPOLOGY_MODE="GNS3_LIVE"`.

---

## 3. End-to-End Architecture & Data Flow

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
        D -->|Symptom Summary| E[ChromaDB Vector Store (all-MiniLM-L6-v2)]
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

## 4. How to Run & Demonstrate the System

### Step 1: Start FastAPI Backend
```bash
# In project root:
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Start Next.js Frontend
```bash
# In frontend directory:
cd frontend
npm run dev
```
Open `http://localhost:3000` in your web browser.

### Step 3: Demonstrate All 5 Faults & Fallback Gatekeeper
1. Click **Interface Down** -> Click **Run Autonomous Diagnosis** -> Observe `Layer 1/2` root cause, 95% confidence, and `no shutdown` CLI script.
2. Click **ACL Packet Drop** -> Run Diagnosis -> Observe `Layer 3/4` root cause, ACL rule matches, and `no ip access-group` CLI script.
3. Click **Gatekeeper (65%)** button in header -> Slide minimum confidence to `99%` -> Run Diagnosis -> Observe the system **defend itself by deferring to manual diagnosis** (`"Insufficient evidence — escalate to manual diagnosis"`).
4. Review the **Audit Trail & Accuracy Telemetry** table to demonstrate empirical SQLite logging and ground truth labeling.
