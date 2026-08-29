'use client';

import React, { useState } from 'react';
import {
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  Copy,
  Check,
  Terminal,
  Cpu,
  Download,
  Wrench,
  ArrowRight,
  Database,
  Search,
  Bot
} from 'lucide-react';

interface DiagnosisResult {
  status: string;
  fallback_triggered: boolean;
  escalation_reason?: string;
  final_root_cause: string;
  confidence_score: number;
  confidence_threshold: number;
  best_retrieval_distance: number;
  distance_threshold: number;
  affected_layer?: string;
  recommended_fix: string;
  reasoning_chain?: string;
  llm_provider?: string;
  retrieved_evidence?: any[];
}

interface DiagnosisPanelProps {
  diagnosis: DiagnosisResult | null;
  isLoading: boolean;
  onRunDiagnosis: () => Promise<void>;
  onApplyFix?: () => Promise<void>;
}

export default function DiagnosisPanel({
  diagnosis,
  isLoading,
  onRunDiagnosis,
  onApplyFix
}: DiagnosisPanelProps) {
  const [copied, setCopied] = useState(false);
  const [fixing, setFixing] = useState(false);
  const [fixedApplied, setFixedApplied] = useState(false);

  const handleCopy = () => {
    if (diagnosis?.recommended_fix) {
      navigator.clipboard.writeText(diagnosis.recommended_fix);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleApplyFix = async () => {
    if (!onApplyFix) return;
    setFixing(true);
    try {
      await onApplyFix();
      setFixedApplied(true);
      setTimeout(() => setFixedApplied(false), 3000);
    } finally {
      setFixing(false);
    }
  };

  const exportReport = () => {
    if (!diagnosis) return;
    const content = `# NetSage Autonomous Diagnostic Incident Report
Timestamp: ${new Date().toISOString()}
LLM Provider: ${diagnosis.llm_provider || 'Groq Llama 3 / Ollama'}
Status: ${diagnosis.status}

## Root Cause Analysis
- **Root Cause**: ${diagnosis.final_root_cause}
- **Affected OSI Layer**: ${diagnosis.affected_layer || 'Layer 3'}
- **Confidence Score**: ${diagnosis.confidence_score}% (Threshold: ${diagnosis.confidence_threshold}%)
- **RAG Cosine Distance**: ${diagnosis.best_retrieval_distance} (Max Threshold: ${diagnosis.distance_threshold})

## Recommended Remediation CLI
\`\`\`
${diagnosis.recommended_fix}
\`\`\`

## Reasoning Chain
${diagnosis.reasoning_chain || 'N/A'}
`;

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `netsage-diagnosis-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Radial confidence meter SVG calculations
  const confidence = diagnosis?.confidence_score || 0;
  const radius = 32;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (confidence / 100) * circumference;

  const getStrokeColor = (score: number) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ff3366';
  };

  return (
    <div className="cyber-card p-5 h-full flex flex-col justify-between">
      <div>
        {/* Header & Primary Diagnosis CTA */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-sky-950/80 border border-sky-500/30 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-sky-400" />
            </div>
            <div>
              <h2 className="text-base font-bold tracking-wide text-slate-100">AI Diagnostic Engine</h2>
              <p className="text-[11px] text-slate-400">RAG Semantic Search + Llama 3 Inference</p>
            </div>
          </div>

          <button
            onClick={onRunDiagnosis}
            disabled={isLoading}
            className="btn-cyber-primary text-xs px-4 py-2 flex items-center gap-2"
          >
            <Cpu className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            {isLoading ? 'Diagnosing...' : 'Run Autonomous Diagnosis'}
          </button>
        </div>

        {/* Empty State */}
        {!diagnosis && !isLoading && (
          <div className="py-14 text-center text-slate-400 border border-dashed border-white/10 rounded-xl bg-slate-950/40 p-6">
            <div className="w-12 h-12 rounded-2xl bg-sky-950/40 border border-sky-500/20 flex items-center justify-center mx-auto mb-3">
              <Bot className="w-6 h-6 text-sky-400" />
            </div>
            <p className="text-sm font-semibold text-slate-200">System Ready for Telemetry Ingestion</p>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto leading-relaxed">
              Inject a fault or click &quot;Run Autonomous Diagnosis&quot; to initiate active Netmiko CLI probing, ChromaDB RAG vector retrieval, and LLM reasoning.
            </p>
          </div>
        )}

        {/* Live Loading Pipeline Animation */}
        {isLoading && (
          <div className="py-10 space-y-4 border border-white/10 rounded-xl bg-slate-950/50 p-6">
            <div className="text-center space-y-1 mb-4">
              <div className="text-sm font-bold text-sky-400 flex items-center justify-center gap-2">
                <Cpu className="w-4 h-4 animate-spin text-sky-400" />
                <span>Autonomous Diagnostic Pipeline Executing</span>
              </div>
              <p className="text-xs text-slate-500 font-mono">Querying network interfaces and neural vector stores...</p>
            </div>

            {/* Pipeline Stage Indicators */}
            <div className="space-y-2 text-xs font-mono">
              <div className="p-2 rounded-lg bg-slate-900 border border-sky-500/30 flex items-center gap-2 text-sky-300">
                <Search className="w-3.5 h-3.5 text-sky-400 animate-pulse" />
                <span>1. Active CLI Probing (show ip route, ping, nslookup)</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-900 border border-indigo-500/30 flex items-center gap-2 text-indigo-300">
                <Database className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
                <span>2. ChromaDB RAG Vector Matching (all-MiniLM-L6-v2)</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-900 border border-purple-500/30 flex items-center gap-2 text-purple-300">
                <Bot className="w-3.5 h-3.5 text-purple-400 animate-pulse" />
                <span>3. Meta Llama 3 Inference & Confidence Scoring</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-900 border border-emerald-500/30 flex items-center gap-2 text-emerald-300">
                <ShieldAlert className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                <span>4. Fallback Gatekeeper Safety Evaluation</span>
              </div>
            </div>
          </div>
        )}

        {/* Diagnosis Results Card */}
        {diagnosis && !isLoading && (
          <div className="space-y-4">
            {/* Fallback Banner vs Verified Badge */}
            {diagnosis.fallback_triggered ? (
              <div className="p-3.5 rounded-xl border border-rose-500/50 bg-rose-950/30 flex items-start gap-3 shadow-[0_0_20px_rgba(255,51,102,0.15)]">
                <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0 mt-0.5 animate-bounce" />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-black text-rose-300 uppercase tracking-wider font-mono">
                      Gatekeeper Defensible Deferral Active
                    </span>
                  </div>
                  <p className="text-xs text-rose-200/90 mt-1 leading-relaxed">
                    {diagnosis.escalation_reason || 'Statistical confidence threshold not satisfied. Hallucination guardrail active.'}
                  </p>
                </div>
              </div>
            ) : (
              <div className="p-3 rounded-xl border border-emerald-500/30 bg-emerald-950/20 flex items-center justify-between shadow-[0_0_15px_rgba(16,185,129,0.15)]">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold text-emerald-300 uppercase tracking-wider font-mono">
                    Autonomous Diagnosis Verified
                  </span>
                </div>
                <span className="text-[11px] text-slate-400 font-mono">
                  {diagnosis.llm_provider || 'Groq Llama 3 70B'}
                </span>
              </div>
            )}

            {/* Metrics Row with Radial Score Gauge */}
            <div className="grid grid-cols-12 gap-3">
              {/* Circular Radial Gauge (4 cols) */}
              <div className="col-span-5 p-3 rounded-xl border border-white/10 bg-[#040711] flex items-center gap-3">
                <div className="relative w-16 h-16 shrink-0 flex items-center justify-center">
                  <svg className="w-16 h-16 -rotate-90" viewBox="0 0 72 72">
                    <circle
                      cx="36"
                      cy="36"
                      r={radius}
                      fill="transparent"
                      stroke="#1e293b"
                      strokeWidth="6"
                    />
                    <circle
                      cx="36"
                      cy="36"
                      r={radius}
                      fill="transparent"
                      stroke={getStrokeColor(diagnosis.confidence_score)}
                      strokeWidth="6"
                      strokeDasharray={circumference}
                      strokeDashoffset={strokeDashoffset}
                      strokeLinecap="round"
                      className="transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div className="absolute text-center">
                    <span className="text-sm font-black font-mono text-slate-100">
                      {diagnosis.confidence_score}%
                    </span>
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase font-mono font-bold text-slate-400">Confidence</div>
                  <div className="text-[11px] text-slate-300 font-medium mt-0.5">
                    {diagnosis.confidence_score >= 80 ? 'High Certainty' : diagnosis.confidence_score >= 60 ? 'Moderate' : 'Low (Escalate)'}
                  </div>
                  <div className="text-[9px] text-slate-500 font-mono mt-0.5">Min: {diagnosis.confidence_threshold}%</div>
                </div>
              </div>

              {/* RAG Vector Cosine Distance (4 cols) */}
              <div className="col-span-4 p-3 rounded-xl border border-white/10 bg-[#040711] flex flex-col justify-between">
                <div>
                  <div className="text-[10px] uppercase font-mono text-slate-400">RAG Cosine Dist</div>
                  <div className="text-xl font-black text-sky-400 font-mono mt-0.5">
                    {diagnosis.best_retrieval_distance.toFixed(3)}
                  </div>
                </div>
                <div className="text-[9px] text-slate-500 font-mono">Max limit: {diagnosis.distance_threshold}</div>
              </div>

              {/* OSI Layer Boundary (3 cols) */}
              <div className="col-span-3 p-3 rounded-xl border border-white/10 bg-[#040711] flex flex-col justify-between">
                <div>
                  <div className="text-[10px] uppercase font-mono text-slate-400">OSI Domain</div>
                  <div className="text-xs font-bold text-purple-300 font-mono mt-1 truncate">
                    {diagnosis.affected_layer || 'Layer 3'}
                  </div>
                </div>
                <div className="text-[9px] text-slate-500 font-mono">Fault Layer</div>
              </div>
            </div>

            {/* Root Cause Card */}
            <div className="p-3.5 rounded-xl border border-white/10 bg-slate-900/60">
              <div className="text-xs font-bold text-slate-300 mb-1 flex items-center justify-between">
                <span>Inferred Root Cause</span>
                <span className="text-[10px] font-mono text-slate-500">Autonomous Inference</span>
              </div>
              <p className="text-sm font-semibold text-slate-100 leading-relaxed">
                {diagnosis.final_root_cause}
              </p>
            </div>

            {/* Remediation CLI Box */}
            <div className="p-3.5 rounded-xl border border-white/10 bg-[#03060c] relative">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5 text-xs font-mono text-slate-300 font-bold">
                  <Terminal className="w-3.5 h-3.5 text-sky-400" />
                  <span>Recommended Remediation CLI Script</span>
                </div>
                <div className="flex items-center gap-2">
                  {onApplyFix && !diagnosis.fallback_triggered && (
                    <button
                      onClick={handleApplyFix}
                      disabled={fixing}
                      className="btn-cyber-ghost text-[10px] py-1 px-2 text-emerald-400 border-emerald-500/30 hover:bg-emerald-950/40 flex items-center gap-1"
                    >
                      <Wrench className="w-3 h-3" />
                      {fixing ? 'Applying...' : fixedApplied ? 'Applied & Verified!' : 'Apply Auto-Fix'}
                    </button>
                  )}
                  <button
                    onClick={handleCopy}
                    className="text-[11px] font-mono text-slate-400 hover:text-sky-400 flex items-center gap-1 transition-colors px-2 py-0.5 rounded bg-white/5"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    {copied ? 'Copied' : 'Copy'}
                  </button>
                </div>
              </div>
              <pre className="text-xs font-mono text-sky-300 whitespace-pre-wrap leading-relaxed overflow-x-auto bg-black/60 p-3 rounded-lg border border-white/5">
                {diagnosis.recommended_fix}
              </pre>
            </div>

            {/* Footer Export & Reasoning Chain */}
            <div className="flex items-center justify-between pt-1">
              <div className="text-[11px] text-slate-400 truncate max-w-xs font-mono">
                Reasoning: {diagnosis.reasoning_chain?.slice(0, 70)}...
              </div>
              <button
                onClick={exportReport}
                className="btn-cyber-ghost text-xs px-2.5 py-1 flex items-center gap-1.5 text-slate-300 hover:text-sky-300"
              >
                <Download className="w-3 h-3 text-sky-400" />
                Export Report
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
