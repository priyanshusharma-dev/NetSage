"""
Knowledge Base Ingestion Script
===============================

Allows user to review, chunk, and embed source documents into ChromaDB.
Usage:
    python backend/app/kb/ingest.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.app.kb.vector_store import vector_store

def run_ingest():
    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "knowledge_base", "source_docs"))
    print("=" * 70)
    print(" [NetSage] Ingesting Approved Source Documents into Vector Store ")
    print("=" * 70)
    print(f"Source Directory: {source_dir}")
    
    result = vector_store.ingest_directory(source_dir)
    print(f"Status: {result['status']}")
    print(f"Indexed Documents: {result['documents_indexed']}")
    print(f"Total Chunks Stored: {result['chunks_stored']}")
    for f in result['files']:
        print(f"  - [Approved Source] {f}")
    print("=" * 70)
    print("Ingestion Complete.")

if __name__ == "__main__":
    run_ingest()
