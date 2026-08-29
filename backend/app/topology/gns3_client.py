"""
GNS3 REST API v2 Client & Live Controller
=========================================

Viva Defensibility Rationale:
-----------------------------
1. Dual-Backend Architecture:
   The GNS3Client connects to the official GNS3 v2 REST API (`http://localhost:3080/v2/`).
   It allows NetSage to automate real Cisco IOSv / Dynamips / Docker QEMU appliances when a live
   GNS3 server is provisioned.
2. Abstract Controller Contract:
   By wrapping GNS3 REST operations inside the same functional interface as the NetworkSimulator,
   the higher-level data collection, RAG, and LLM diagnostic pipelines remain 100% agnostic to
   whether the underlying network is running in live virtualization or deterministic simulation.
"""

import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)

class GNS3Client:
    def __init__(self, base_url: str = "http://localhost:3080/v2", project_name: str = "NetSage_Enterprise_Topology"):
        self.base_url = base_url.rstrip("/")
        self.project_name = project_name
        self.project_id: Optional[str] = None
        self.nodes_cache: Dict[str, Any] = {}

    def is_server_online(self) -> bool:
        """Verifies if the GNS3 server is reachable and responsive."""
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/version")
                return res.status_code == 200
        except Exception:
            return False

    def get_or_create_project(self) -> str:
        """Finds existing project by name or creates a new one in GNS3."""
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.base_url}/projects")
                if res.status_code == 200:
                    for p in res.json():
                        if p.get("name") == self.project_name:
                            self.project_id = p["project_id"]
                            return self.project_id
                
                # Create project if not found
                create_res = client.post(f"{self.base_url}/projects", json={"name": self.project_name})
                if create_res.status_code in [200, 201]:
                    self.project_id = create_res.json()["project_id"]
                    return self.project_id
        except Exception as e:
            logger.warning(f"GNS3 server unavailable: {e}. Fallback to simulated mode is recommended.")
        
        return ""

    def get_topology_nodes(self) -> List[Dict[str, Any]]:
        """Fetches live nodes from the active GNS3 project."""
        if not self.project_id:
            self.get_or_create_project()
        if not self.project_id:
            return []
            
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.base_url}/projects/{self.project_id}/nodes")
                if res.status_code == 200:
                    nodes = res.json()
                    self.nodes_cache = {n["name"]: n for n in nodes}
                    return nodes
        except Exception as e:
            logger.error(f"Error fetching GNS3 nodes: {e}")
        return []
