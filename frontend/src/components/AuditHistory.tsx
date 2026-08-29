'use client';

import React, { useState } from 'react';
import { History, Check, X, ShieldAlert, CheckCircle2, TrendingUp, BarChart3, Search, Filter } from 'lucide-react';

interface AuditRun {
  id: number;
  timestamp: string;
  active_fault: string;
  confidence_score: number;
  best_distance: number;
  fallback_triggered: boolean;
  final_root_cause: string;
  llm_provider: string;
  user_label: string;
}

interface StatsData {
  total_runs: number;
  autonomous_runs: number;
  escalated_fallbacks: number;
  accuracy_percentage: number;
}

interface AuditHistoryProps {
  history: AuditRun[];
  stats: StatsData | null;
  onLabelRun: (runId: number, label: string) => Promise<void>;
}

export default function AuditHistory({ history, stats, onLabelRun }: AuditHistoryProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredHistory = history.filter(run => {
    const text = (run.active_fault + ' ' + run.final_root_cause + ' ' + run.llm_provider).toLowerCase();
    return text.includes(searchTerm.toLowerCase());
  });

  return (
    <div className="cyber-card p-5">
      {/* Header & Stats Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-purple-950/80 border border-purple-500/30 flex items-center justify-center">
            <History className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <h2 className="text-base font-bold tracking-wide text-slate-100 flex items-center gap-2">
              Persistent Audit Database & Telemetry
              <span className="cyber-badge cyber-badge-purple text-[9px]">SQLite Engine</span>
            </h2>
            <p className="text-[11px] text-slate-400">Ground-truth validation and historical model performance tracking</p>
          </div>
        </div>

        {stats && (
          <div className="flex items-center gap-3 text-xs flex-wrap">
            <div className="px-3 py-1.5 rounded-xl bg-slate-900/90 border border-white/5 flex items-center gap-2 shadow-inner">
              <BarChart3 className="w-4 h-4 text-sky-400" />
              <span className="text-slate-400 font-mono">Total Runs:</span>
              <span className="font-bold text-slate-200 font-mono">{stats.total_runs}</span>
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-slate-900/90 border border-white/5 flex items-center gap-2 shadow-inner">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span className="text-slate-400 font-mono">Safe Deferrals:</span>
              <span className="font-bold text-amber-300 font-mono">{stats.escalated_fallbacks}</span>
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-emerald-950/50 border border-emerald-500/40 flex items-center gap-2 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-300 font-mono font-semibold">Empirical Accuracy:</span>
              <span className="font-bold text-emerald-400 font-mono">{stats.accuracy_percentage}%</span>
            </div>
          </div>
        )}
      </div>

      {/* History Table */}
      <div className="overflow-x-auto rounded-xl border border-white/5">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-950/80 border-b border-white/10 text-slate-400 font-mono text-[11px]">
              <th className="py-3 px-3.5">Run ID</th>
              <th className="py-3 px-3.5">Timestamp</th>
              <th className="py-3 px-3.5">Active Fault</th>
              <th className="py-3 px-3.5">Confidence</th>
              <th className="py-3 px-3.5">Gatekeeper Decision</th>
              <th className="py-3 px-3.5">Root Cause Verdict</th>
              <th className="py-3 px-3.5 text-right">Ground Truth</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-slate-300 bg-[#040711]">
            {filteredHistory.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-10 text-center text-slate-500 font-mono text-xs">
                  No diagnostic runs recorded in SQLite database.
                </td>
              </tr>
            ) : (
              filteredHistory.map(run => (
                <tr key={run.id} className="hover:bg-slate-900/60 transition-colors">
                  <td className="py-3 px-3.5 font-mono text-slate-400 font-bold">#{run.id}</td>
                  <td className="py-3 px-3.5 font-mono text-slate-400 whitespace-nowrap">{run.timestamp}</td>
                  <td className="py-3 px-3.5 font-mono text-sky-300 font-semibold">{run.active_fault}</td>
                  <td className="py-3 px-3.5 font-mono font-bold">
                    <span className={run.confidence_score >= 80 ? 'text-emerald-400' : 'text-amber-400'}>
                      {run.confidence_score}%
                    </span>
                  </td>
                  <td className="py-3 px-3.5">
                    {run.fallback_triggered ? (
                      <span className="cyber-badge cyber-badge-rose text-[9px]">
                        Escalated to Manual
                      </span>
                    ) : (
                      <span className="cyber-badge cyber-badge-emerald text-[9px]">
                        Autonomous Verified
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-3.5 max-w-sm truncate text-slate-200 font-medium" title={run.final_root_cause}>
                    {run.final_root_cause}
                  </td>
                  <td className="py-3 px-3.5 text-right">
                    <div className="inline-flex items-center gap-1.5 justify-end">
                      <button
                        onClick={() => onLabelRun(run.id, 'correct')}
                        className={`p-1.5 rounded-lg transition-all ${
                          run.user_label === 'correct'
                            ? 'bg-emerald-600 text-white shadow-[0_0_10px_rgba(16,185,129,0.5)]'
                            : 'bg-white/5 text-slate-400 hover:text-emerald-400 hover:bg-white/10'
                        }`}
                        title="Mark Verified Correct (Ground Truth)"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => onLabelRun(run.id, 'incorrect')}
                        className={`p-1.5 rounded-lg transition-all ${
                          run.user_label === 'incorrect'
                            ? 'bg-rose-600 text-white shadow-[0_0_10px_rgba(255,51,102,0.5)]'
                            : 'bg-white/5 text-slate-400 hover:text-rose-400 hover:bg-white/10'
                        }`}
                        title="Mark Incorrect (Ground Truth)"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
