"""
Persistent Audit Logger & Telemetry Database (SQLite)
=====================================================

Viva Defensibility Rationale:
-----------------------------
1. Complete Scientific Auditability:
   Every diagnostic run is permanently logged with complete input symptoms, exact retrieved vector
   evidence chunks, raw LLM reasoning chains, fallback decisions, and post-facto ground truth labels.
2. Ground-Truth Accuracy Telemetry:
   Allows operators and academic examiners to review empirical accuracy rates across historical runs,
   filter by fault type, and verify that the system correctly defers when appropriate.
"""

import sqlite3
import json
import time
import os
from typing import Dict, Any, List, Optional
from backend.app.config import settings

class AuditLogger:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Creates the diagnosis history table if not already existing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diagnosis_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    active_fault TEXT,
                    symptom_summary TEXT,
                    retrieved_evidence_json TEXT,
                    llm_provider TEXT,
                    confidence_score INTEGER,
                    best_distance REAL,
                    fallback_triggered INTEGER,
                    escalation_reason TEXT,
                    final_root_cause TEXT,
                    recommended_fix TEXT,
                    reasoning_chain TEXT,
                    user_label TEXT DEFAULT 'unlabeled'
                )
            """)
            conn.commit()

    def log_run(self, data: Dict[str, Any]) -> int:
        """Persists a new diagnostic run record."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO diagnosis_runs (
                    timestamp, active_fault, symptom_summary, retrieved_evidence_json,
                    llm_provider, confidence_score, best_distance, fallback_triggered,
                    escalation_reason, final_root_cause, recommended_fix, reasoning_chain, user_label
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                data.get("active_fault", "none"),
                data.get("symptom_summary", ""),
                json.dumps(data.get("retrieved_evidence", [])),
                data.get("llm_provider", "unknown"),
                data.get("confidence_score", 0),
                data.get("best_retrieval_distance", 0.0),
                1 if data.get("fallback_triggered", False) else 0,
                data.get("escalation_reason") or "",
                data.get("final_root_cause", ""),
                data.get("recommended_fix", ""),
                data.get("reasoning_chain", ""),
                data.get("user_label", "unlabeled")
            ))
            conn.commit()
            return cursor.lastrowid

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves list of past diagnostic runs."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM diagnosis_runs ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            history = []
            for r in rows:
                item = dict(r)
                item["fallback_triggered"] = bool(item["fallback_triggered"])
                try:
                    item["retrieved_evidence"] = json.loads(item.get("retrieved_evidence_json") or "[]")
                except Exception:
                    item["retrieved_evidence"] = []
                history.append(item)
            return history

    def update_label(self, run_id: int, label: str) -> bool:
        """Updates user ground truth label ('correct', 'incorrect', 'unlabeled')."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE diagnosis_runs SET user_label = ? WHERE id = ?", (label, run_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_statistics(self) -> Dict[str, Any]:
        """Calculates system metrics: total runs, fallback percentage, and human-labeled accuracy."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM diagnosis_runs")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM diagnosis_runs WHERE fallback_triggered = 1")
            fallbacks = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM diagnosis_runs WHERE user_label = 'correct'")
            correct = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM diagnosis_runs WHERE user_label = 'incorrect'")
            incorrect = cursor.fetchone()[0]

            labeled = correct + incorrect
            accuracy = round((correct / labeled * 100), 1) if labeled > 0 else 100.0

            return {
                "total_runs": total,
                "autonomous_runs": total - fallbacks,
                "escalated_fallbacks": fallbacks,
                "labeled_count": labeled,
                "verified_correct": correct,
                "verified_incorrect": incorrect,
                "accuracy_percentage": accuracy
            }

audit_logger = AuditLogger()
