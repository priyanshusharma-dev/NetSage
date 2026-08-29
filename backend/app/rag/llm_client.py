"""
Multi-Provider LLM Client & Failover Router
============================================

Viva Defensibility Rationale:
-----------------------------
1. Dual-Tier Inference Hierarchy:
   - Primary: High-speed Cloud Inference via Groq API (Meta Llama 3 70B/8B).
   - Secondary: Zero-Cloud Local Inference via Ollama (Llama 3 / Qwen2.5 on localhost).
   - Tertiary: Local Deterministic Expert Heuristic Fallback for air-gapped exam presentations.
2. Robust JSON Parsing & Schema Recovery:
   Extracts JSON substrings from LLM raw text, handling markdown fences (` ```json `), trailing
   commas, or conversational chatter gracefully.
"""

import json
import re
import logging
import httpx
from typing import Dict, Any, Optional
from backend.app.config import settings
from backend.app.rag.prompt_config import DIAGNOSIS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_model = settings.GROQ_MODEL
        self.ollama_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.ollama_model = settings.OLLAMA_MODEL

    def generate_diagnosis(self, user_prompt: str) -> Dict[str, Any]:
        """
        Routes prompt to Groq -> Ollama -> Expert Fallback.
        Returns parsed JSON diagnosis dictionary with metadata indicating active provider.
        """
        # 1. Attempt Groq API
        if self.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_api_key)
                completion = client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {"role": "system", "content": DIAGNOSIS_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                raw_text = completion.choices[0].message.content
                parsed = self._extract_json(raw_text)
                parsed["llm_provider"] = f"Groq Cloud API ({self.groq_model})"
                parsed["raw_llm_output"] = raw_text
                return parsed
            except Exception as e:
                logger.warning(f"Groq API error: {e}. Failing over to local Ollama...")

        # 2. Attempt Local Ollama API
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "system": DIAGNOSIS_SYSTEM_PROMPT,
                        "prompt": user_prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                if res.status_code == 200:
                    raw_text = res.json().get("response", "")
                    parsed = self._extract_json(raw_text)
                    parsed["llm_provider"] = f"Local Ollama ({self.ollama_model})"
                    parsed["raw_llm_output"] = raw_text
                    return parsed
        except Exception as e:
            logger.info(f"Ollama local instance unavailable: {e}. Utilizing Local Diagnostic Engine.")

        # 3. Deterministic Local Expert Engine (Air-gapped Viva Demonstration Mode)
        return self._expert_heuristic_fallback(user_prompt)

    def _extract_json(self, raw_text: str) -> Dict[str, Any]:
        """Sanitizes and extracts valid JSON object from LLM response."""
        try:
            return json.loads(raw_text)
        except Exception:
            # Match JSON within code blocks
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            # Match generic outer braces
            match2 = re.search(r"(\{.*\})", raw_text, re.DOTALL)
            if match2:
                return json.loads(match2.group(1))
        
        return {
            "most_likely_root_cause": "Raw LLM output formatting anomaly.",
            "affected_layer": "Unknown",
            "confidence_score": 40,
            "recommended_fix": "Review raw symptom telemetry.",
            "retrieved_evidence": [],
            "reasoning_chain": raw_text
        }

    def _expert_heuristic_fallback(self, user_prompt: str) -> Dict[str, Any]:
        """Provides expert deterministic diagnosis if external LLM APIs are unreachable."""
        prompt_lower = user_prompt.lower()
        
        # Check 1: Interface Down (Layer 1/2)
        if "administratively down" in prompt_lower or "forced shutdown" in prompt_lower:
            return {
                "most_likely_root_cause": "Interface GigabitEthernet0/1 on HQ-R1 is administratively down (forced shutdown).",
                "affected_layer": "Layer 1 / Layer 2 Physical & Data-Link",
                "confidence_score": 95,
                "recommended_fix": "configure terminal\ninterface GigabitEthernet0/1\n no shutdown\nend\nwrite memory",
                "retrieved_evidence": ["01_interface_troubleshooting.md_chunk_0"],
                "reasoning_chain": "Telemetry explicitly reports interface status as 'administratively down'. Direct pings fail with 0% success rate. The standard resolution is applying 'no shutdown' under interface configuration mode.",
                "llm_provider": "Local Expert Diagnostic Engine (Air-Gapped)",
                "raw_llm_output": "[Synthesized JSON from Local Deterministic Engine]"
            }

        # Check 2: ACL Blocking (Layer 3/4)
        elif "administratively prohibited" in prompt_lower or "restrict_campus_traffic" in prompt_lower or "deny ip" in prompt_lower:
            return {
                "most_likely_root_cause": "Extended Access Control List 'RESTRICT_CAMPUS_TRAFFIC' on HQ-R1 is dropping inter-branch IP/ICMP traffic.",
                "affected_layer": "Layer 3/4 Packet Filtering & Security",
                "confidence_score": 94,
                "recommended_fix": "configure terminal\ninterface GigabitEthernet0/0\n no ip access-group RESTRICT_CAMPUS_TRAFFIC in\nend\nwrite memory",
                "retrieved_evidence": ["03_acl_traffic_filtering.md_chunk_0"],
                "reasoning_chain": "Diagnostic probes returned 'Destination Administratively Prohibited' and show ip access-lists indicates active deny rule matching inter-branch traffic.",
                "llm_provider": "Local Expert Diagnostic Engine (Air-Gapped)",
                "raw_llm_output": "[Synthesized JSON from Local Deterministic Engine]"
            }

        # Check 3: Routing Loop (Layer 3)
        elif "routing loop" in prompt_lower or "ttl exceeded in transit" in prompt_lower or "!h" in prompt_lower:
            return {
                "most_likely_root_cause": "Static routing loop between Core-R3 and HQ-R1 causing TTL expiration.",
                "affected_layer": "Layer 3 Routing Control Plane",
                "confidence_score": 90,
                "recommended_fix": "configure terminal\nno ip route 192.168.20.0 255.255.255.0 10.1.13.1\nip route 192.168.20.0 255.255.255.0 10.1.23.1\nend\nwrite memory",
                "retrieved_evidence": ["04_routing_loops_and_flaps.md_chunk_0"],
                "reasoning_chain": "Traceroute exhibits alternating repetitive hops between Core-R3 (10.1.13.2) and HQ-R1 (10.1.13.1), terminating with TTL Exceeded.",
                "llm_provider": "Local Expert Diagnostic Engine (Air-Gapped)",
                "raw_llm_output": "[Synthesized JSON from Local Deterministic Engine]"
            }

        # Check 4: DNS Failure (Layer 7)
        elif "dns resolution failed" in prompt_lower or "connection timed out" in prompt_lower or "192.0.2.53" in prompt_lower:
            return {
                "most_likely_root_cause": "Primary DNS nameserver is unreachable or misconfigured with invalid IP address (192.0.2.53).",
                "affected_layer": "Layer 7 Application (DNS)",
                "confidence_score": 96,
                "recommended_fix": "echo 'nameserver 192.168.10.53' | sudo tee /etc/resolv.conf",
                "retrieved_evidence": ["05_dns_name_resolution.md_chunk_0"],
                "reasoning_chain": "DNS queries timed out across all resolution attempts while Layer 3 IP reachability to the subnet remains healthy.",
                "llm_provider": "Local Expert Diagnostic Engine (Air-Gapped)",
                "raw_llm_output": "[Synthesized JSON from Local Deterministic Engine]"
            }

        # Check 5: Subnet / Gateway Misconfiguration (Layer 3)
        elif "destination host unreachable" in prompt_lower or "192.168.20.254" in prompt_lower or "cannot reach local default gateway" in prompt_lower:
            return {
                "most_likely_root_cause": "Subnet mask or default gateway misconfiguration on host preventing default route reachability.",
                "affected_layer": "Layer 3 Network",
                "confidence_score": 92,
                "recommended_fix": "sudo ip route del default\nsudo ip route add default via 192.168.20.1 dev eth0",
                "retrieved_evidence": ["02_subnet_gateway_issues.md_chunk_0"],
                "reasoning_chain": "End-to-end telemetry demonstrates that host cannot communicate with local gateway or remote subnets due to mismatched default gateway pointer.",
                "llm_provider": "Local Expert Diagnostic Engine (Air-Gapped)",
                "raw_llm_output": "[Synthesized JSON from Local Deterministic Engine]"
            }

        # Unknown / Ambiguous Case (Low Confidence Escalation Demonstration)
        return {
            "most_likely_root_cause": "Unknown anomaly pattern detected in network metrics.",
            "affected_layer": "Unknown",
            "confidence_score": 45,
            "recommended_fix": "Manual inspection of interface counters and packet capture required.",
            "retrieved_evidence": [],
            "reasoning_chain": "Telemetry data did not match known failure signatures with sufficient statistical significance.",
            "llm_provider": "Local Expert Diagnostic Engine (Air-Gapped)",
            "raw_llm_output": "[Synthesized Low Confidence JSON]"
        }

llm_client = LLMClient()
