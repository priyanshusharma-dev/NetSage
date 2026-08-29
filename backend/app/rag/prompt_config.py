"""
LLM Prompt Configuration & Engineering
======================================

Viva Defensibility Rationale:
-----------------------------
1. Decoupled Prompt Lifecycle:
   Network engineers and evaluators can iterate on diagnostic heuristics, few-shot examples,
   and system constraints without modifying pipeline code.
2. Structured JSON Output Contract:
   Forces deterministic JSON output schema containing:
   - `most_likely_root_cause`: High-precision technical root cause summary
   - `confidence_score`: Explicit 0-100 self-assessment integer
   - `recommended_fix`: Concrete CLI remediation commands
   - `retrieved_evidence`: Exact list of chunk IDs and document sources utilized
   - `reasoning_chain`: Step-by-step OSI Layer deduction
"""

DIAGNOSIS_SYSTEM_PROMPT = """You are NetSage, an expert autonomous network diagnostic engine.
Your task is to analyze network telemetry, symptom anomalies, ping matrix results, and retrieved knowledge base chunks to determine the exact root cause of the network fault and produce concrete remediation CLI commands.

### Instructions:
1. Base your diagnosis strictly on the provided Symptom Data and Retrieved Knowledge Base Evidence.
2. If evidence is ambiguous, contradictory, or insufficient, set a low `confidence_score` (< 60) and explain why in `reasoning_chain`.
3. Quote specific evidence sources in `retrieved_evidence`.
4. You MUST respond with ONLY a valid JSON object matching the following structure:

{
  "most_likely_root_cause": "Concise 1-2 sentence description of the exact fault (e.g. Interface GigabitEthernet0/1 administratively down on HQ-R1)",
  "affected_layer": "Layer 1 / Layer 2 / Layer 3 / Layer 4 / Layer 7",
  "confidence_score": 85,
  "recommended_fix": "Step-by-step CLI commands to resolve the issue (e.g. configure terminal\\ninterface Gi0/1\\nno shutdown\\nend)",
  "retrieved_evidence": [
    "01_interface_troubleshooting.md_chunk_0"
  ],
  "reasoning_chain": "Detailed breakdown of the observed symptoms, cross-referenced against the knowledge base."
}
"""

def build_diagnosis_user_prompt(symptom_text: str, retrieved_chunks: list) -> str:
    """Builds the formatted user prompt with telemetry and top-k retrieved chunks."""
    evidence_blocks = []
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        chunk_id = chunk.get("id", f"chunk_{idx}")
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        category = meta.get("category", "General")
        distance = chunk.get("distance", 0.0)
        similarity = chunk.get("similarity_score", 1.0)
        
        evidence_blocks.append(
            f"--- EVIDENCE CHUNK #{idx} [ID: {chunk_id} | Source: {source} | Category: {category} | Cosine Dist: {distance} | Sim: {similarity}] ---\n"
            f"{chunk.get('content', '')}\n"
        )

    evidence_str = "\n".join(evidence_blocks) if evidence_blocks else "No relevant knowledge base chunks found."

    return f"""### LIVE NETWORK SYMPTOM TELEMETRY:
{symptom_text}

### RETRIEVED KNOWLEDGE BASE EVIDENCE (Top-k Chunks):
{evidence_str}

Analyze the symptoms and knowledge base evidence, determine the root cause, assign a confidence score (0-100), and output the remediation JSON."""
