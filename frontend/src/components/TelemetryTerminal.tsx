'use client';

import React, { useState } from 'react';
import { Terminal, AlertCircle, RefreshCw, CheckCircle2, Activity, Play } from 'lucide-react';

interface TelemetryTerminalProps {
  symptomSummary: string;
  anomalies: string[];
  onRefreshTelemetry: () => Promise<void>;
  isLoading: boolean;
}

export default function TelemetryTerminal({
  symptomSummary,
  anomalies,
  onRefreshTelemetry,
  isLoading
}: TelemetryTerminalProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'anomalies'>('summary');

  return (
    <div className="cyber-card p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-emerald-950/80 border border-emerald-500/30 flex items-center justify-center">
            <Terminal className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-base font-bold tracking-wide text-slate-100 flex items-center gap-2">
              Live Telemetry Stream
              <span className="cyber-badge cyber-badge-emerald text-[9px]">Netmiko Automation</span>
            </h2>
            <p className="text-[11px] text-slate-400">Structured feature extraction across Cisco IOS and Linux POSIX layers</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View Toggles */}
          <div className="flex bg-slate-950 rounded-lg p-0.5 border border-white/10">
            <button
              onClick={() => setActiveTab('summary')}
              className={`text-xs font-mono px-3 py-1 rounded-md transition-colors ${
                activeTab === 'summary'
                  ? 'bg-sky-600 text-white font-bold shadow-[0_0_10px_rgba(2,132,199,0.5)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Telemetry Summary
            </button>
            <button
              onClick={() => setActiveTab('anomalies')}
              className={`text-xs font-mono px-3 py-1 rounded-md flex items-center gap-1.5 transition-colors ${
                activeTab === 'anomalies'
                  ? 'bg-rose-600 text-white font-bold shadow-[0_0_10px_rgba(255,51,102,0.5)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Anomalies
              {anomalies.length > 0 && (
                <span className="w-4 h-4 rounded-full bg-black/50 text-[10px] flex items-center justify-center font-bold">
                  {anomalies.length}
                </span>
              )}
            </button>
          </div>

          <button
            onClick={onRefreshTelemetry}
            disabled={isLoading}
            className="p-1.5 rounded-lg border border-white/10 text-slate-400 hover:text-sky-400 hover:border-sky-500/40 transition-colors"
            title="Refresh Diagnostic Telemetry"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {activeTab === 'summary' ? (
        <div className="cyber-terminal h-[190px] p-4 overflow-y-auto whitespace-pre-wrap leading-relaxed text-xs">
          {symptomSummary || 'No telemetry collected yet. Inject a fault above or run diagnosis to stream live router/host state.'}
        </div>
      ) : (
        <div className="h-[190px] overflow-y-auto space-y-2 pr-1">
          {anomalies.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-400 flex flex-col items-center justify-center gap-2 font-mono">
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              <span>All network interfaces, routing tables, and DNS queries are 100% HEALTHY.</span>
            </div>
          ) : (
            anomalies.map((anom, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl border border-rose-500/30 bg-rose-950/20 text-xs text-rose-300 flex items-start gap-2.5 shadow-[0_0_15px_rgba(255,51,102,0.08)] font-mono"
              >
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5 animate-pulse" />
                <span className="leading-relaxed">{anom}</span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
