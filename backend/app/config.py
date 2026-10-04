"""
NetSage Configuration Module
============================

Viva Defensibility Rationale:
-----------------------------
1. Environment Isolation: Decouples operational settings (GNS3 endpoints, LLM API keys,
   fallback thresholds) from core algorithmic modules.
2. Mode Selection ('SIMULATED' vs 'GNS3_LIVE'): Allows flawless demonstration during
   examinations without requiring heavy virtual machine hypervisors running, while retaining
   production-grade API hooks for live GNS3 environments.
3. Centralized Thresholds: Confidence and retrieval similarity thresholds are parameterised
   to prove defensive engineering principles (preventing LLM hallucination in mission-critical
   network operations).
"""

import os
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # Operating Mode: SIMULATED (in-memory realistic mock) or GNS3_LIVE (live GNS3 v2 REST API)
    TOPOLOGY_MODE: Literal["SIMULATED", "GNS3_LIVE"] = os.getenv("TOPOLOGY_MODE", "SIMULATED")
    
    # GNS3 Server Configuration
    GNS3_SERVER_URL: str = os.getenv("GNS3_SERVER_URL", "http://localhost:3080")
    GNS3_PROJECT_NAME: str = os.getenv("GNS3_PROJECT_NAME", "NetSage_Enterprise_Topology")
    
    # Live Device Telnet/SSH Credentials for Netmiko
    DEVICE_USERNAME: str = os.getenv("DEVICE_USERNAME", "admin")
    DEVICE_PASSWORD: str = os.getenv("DEVICE_PASSWORD", "cisco")
    DEVICE_SECRET: str = os.getenv("DEVICE_SECRET", "cisco")
    
    # LLM Providers
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db"))
    )
    
    # Fallback Gatekeeper Thresholds
    # Max cosine distance for RAG retrieval (lower is closer; threshold 0.85 allows relevant docs)
    MAX_RETRIEVAL_DISTANCE: float = float(os.getenv("MAX_RETRIEVAL_DISTANCE", "0.85"))
    # Minimum LLM self-assessed confidence score (0-100 scale)
    MIN_CONFIDENCE_THRESHOLD: int = int(os.getenv("MIN_CONFIDENCE_THRESHOLD", "65"))
    
    # Database path for SQLite audit logging
    DATABASE_PATH: str = os.getenv(
        "DATABASE_PATH",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "netsage_audit.db"))
    )

settings = Settings()
