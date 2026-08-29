'use client';

import React from 'react';
import { X, Network, Cpu, Database, ShieldAlert, ArrowRight, Activity, Terminal } from 'lucide-react';

interface ArchitectureModalProps {
  onClose: () => void;
}

export default function ArchitectureModal({ onClose }: ArchitectureModalProps) {
  const steps = [
    {
      num: '1',
      title: 'Fault Injection & Topology',
      desc: 'Chaos engine alters Cisco IOSv / Linux simulated nodes across OSI Layers 1-7.',
      icon: <Activity className="w-5 h-5 text-amber-400" />
    },
    {
      num: '2',
      title: 'Active Probing & Parsing',
      desc: 'Netmiko diagnostic scripts gather interface, routing, ACL, ping, and DNS telemetry.',
      icon: <Terminal className="w-5 h-5 text-emerald-400" />
    },
    {
      num: '3',
      title: 'ChromaDB Vector Retrieval',
      desc: 'Top-k technical chunks retrieved via all-MiniLM-L6-v2 embeddings with cosine distance.',
      icon: <Database className="w-5 h-5 text-indigo-400" />
    },
    {
      num: '4',
      title: 'Llama 3 LLM Inference',
      desc: 'Groq Cloud API (with local Ollama fallback) produces structured JSON root-cause & fix.',
      icon: <Cpu className="w-5 h-5 text-sky-400" />
    },
    {
      num: '5',
      title: 'Safety Gatekeeper',
      desc: 'Dual threshold verification prevents hallucinated CLI commands before SQLite logging.',
      icon: <ShieldAlert className="w-5 h-5 text-rose-400" />
    }
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-3xl p-6 border-white/20 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 mb-2">
          <Network className="w-5 h-5 text-sky-400" />
          <h3 className="text-base font-bold text-slate-100">System Architecture & Data Flow</h3>
        </div>
        <p className="text-xs text-slate-400 mb-6">
          Autonomous closed-loop network troubleshooting lifecycle (Defensible Viva Voce Blueprint)
        </p>

        {/* Horizontal Flow Steps */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mb-6">
          {steps.map((s, idx) => (
            <div key={idx} className="p-3 rounded-xl border border-white/10 bg-slate-900/70 relative">
              <div className="flex items-center justify-between mb-2">
                <span className="w-5 h-5 rounded-full bg-sky-950 border border-sky-500/40 text-sky-300 text-[11px] font-mono flex items-center justify-center font-bold">
                  {s.num}
                </span>
                {s.icon}
              </div>
              <div className="text-xs font-bold text-slate-200 mb-1">{s.title}</div>
              <p className="text-[10px] text-slate-400 leading-normal">{s.desc}</p>
            </div>
          ))}
        </div>

        {/* Rationale Callout Box */}
        <div className="p-3.5 rounded-xl border border-sky-500/20 bg-sky-950/20 text-xs text-sky-200 space-y-1.5">
          <div className="font-semibold text-sky-300">Viva Voce Defensibility Highlights:</div>
          <ul className="list-disc pl-4 space-y-1 text-slate-300 text-[11px]">
            <li><strong>Zero Flake In-Memory Simulation:</strong> Reliable presentation even when GNS3 VM hardware drivers are disconnected.</li>
            <li><strong>Explainable RAG:</strong> Vector chunks, cosine distances, and source files are never hidden from the user or examiner.</li>
            <li><strong>Safe Deferral:</strong> Low-confidence or out-of-distribution telemetry gracefully escalates to manual diagnosis.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
