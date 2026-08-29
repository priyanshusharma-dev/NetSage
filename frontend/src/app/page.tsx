'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  RotateCcw,
  Sliders,
  Network,
  Clock,
  Wifi
} from 'lucide-react';

import TopologyView from '@/components/TopologyView';
import FaultInjector from '@/components/FaultInjector';
import DiagnosisPanel from '@/components/DiagnosisPanel';
import EvidenceViewer from '@/components/EvidenceViewer';
import TelemetryTerminal from '@/components/TelemetryTerminal';
import AuditHistory from '@/components/AuditHistory';
import ThresholdSettings from '@/components/ThresholdSettings';
import ArchitectureModal from '@/components/ArchitectureModal';
import InteractiveTerminalModal from '@/components/InteractiveTerminalModal';

import {
  TopologyState,
  DiagnosisResult,
  EvidenceChunk,
  TelemetryState,
  AuditRecord,
  SystemStats,
  ThresholdConfig,
  NodeData
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1';

export default function NetSageDashboard() {
  const [topology, setTopology] = useState<TopologyState>({
    nodes: [],
    links: [],
    active_faults: [],
    mode: 'SIMULATED'
  });

  const [diagnosis, setDiagnosis] = useState<DiagnosisResult | null>(null);
  const [evidence, setEvidence] = useState<EvidenceChunk[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryState>({
    summary: '',
    anomalies: []
  });

  const [history, setHistory] = useState<AuditRecord[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [thresholds, setThresholds] = useState<ThresholdConfig>({
    maxDistance: 0.85,
    minConfidence: 65
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [diagnosing, setDiagnosing] = useState<boolean>(false);
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [showArch, setShowArch] = useState<boolean>(false);
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);
  const [activeTerminalNode, setActiveTerminalNode] = useState<{ id: string; name: string } | null>(null);

  // Time ticker
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTimer = () => {
      setTimeStr(new Date().toLocaleTimeString());
    };
    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, []);

  // Fetch initial topology and status
  const fetchTopology = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/topology/status`);
      if (res.ok) {
        const data: TopologyState = await res.json();
        setTopology(data);
      }
    } catch (e) {
      console.warn('Backend unavailable, using local mock state:', e);
    }
  }, []);

  // Fetch history & statistics
  const fetchHistoryAndStats = useCallback(async () => {
    try {
      const [histRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/history?limit=25`),
        fetch(`${API_BASE}/stats`)
      ]);
      if (histRes.ok) {
        const histData: AuditRecord[] = await histRes.json();
        setHistory(histData);
      }
      if (statsRes.ok) {
        const statsData: SystemStats = await statsRes.json();
        setStats(statsData);
      }
    } catch (e) {
      console.warn('Error fetching history/stats:', e);
    }
  }, []);

  // Fetch thresholds
  const fetchThresholds = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/config/thresholds`);
      if (res.ok) {
        const data = await res.json();
        setThresholds({
          maxDistance: Number(data.max_retrieval_distance),
          minConfidence: Number(data.min_confidence_threshold)
        });
      }
    } catch (e) {
      console.warn('Error fetching thresholds:', e);
    }
  }, []);

  // Fetch telemetry
  const fetchTelemetry = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/telemetry`);
      if (res.ok) {
        const data = await res.json();
        setTelemetry({
          summary: data.condensed_symptom_text || '',
          anomalies: data.anomalies_detected || []
        });
      }
    } catch (e) {
      console.warn('Error fetching telemetry:', e);
    }
  }, []);

  useEffect(() => {
    fetchTopology();
    fetchHistoryAndStats();
    fetchThresholds();
    fetchTelemetry();
  }, [fetchTopology, fetchHistoryAndStats, fetchThresholds, fetchTelemetry]);

  // Handle fault injection
  const handleInjectFault = async (faultType: string, params?: Record<string, unknown>) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/fault/inject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fault_type: faultType, params: params || {} })
      });
      if (res.ok) {
        await fetchTopology();
        await fetchTelemetry();
      }
    } catch (e) {
      console.error('Fault injection error:', e);
    } finally {
      setLoading(false);
    }
  };

  // Handle reset
  const handleResetTopology = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/fault/reset`, { method: 'POST' });
      if (res.ok) {
        setDiagnosis(null);
        setEvidence([]);
        await fetchTopology();
        await fetchTelemetry();
      }
    } catch (e) {
      console.error('Reset error:', e);
    } finally {
      setLoading(false);
    }
  };

  // Handle diagnosis run
  const handleRunDiagnosis = async () => {
    setDiagnosing(true);
    try {
      const res = await fetch(`${API_BASE}/diagnose`, { method: 'POST' });
      if (res.ok) {
        const data: DiagnosisResult = await res.json();
        setDiagnosis(data);
        setEvidence(data.retrieved_evidence || []);
        await fetchHistoryAndStats();
        await fetchTelemetry();
      }
    } catch (e) {
      console.error('Diagnosis error:', e);
    } finally {
      setDiagnosing(false);
    }
  };

  // Handle ground truth label update
  const handleLabelRun = async (runId: number, label: string) => {
    try {
      const res = await fetch(`${API_BASE}/history/${runId}/label`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label })
      });
      if (res.ok) {
        await fetchHistoryAndStats();
      }
    } catch (e) {
      console.error('Label update error:', e);
    }
  };

  // Handle threshold updates
  const handleUpdateThresholds = async (maxDist: number, minConf: number) => {
    try {
      const res = await fetch(`${API_BASE}/config/thresholds`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          max_retrieval_distance: maxDist,
          min_confidence_threshold: minConf
        })
      });
      if (res.ok) {
        setThresholds({ maxDistance: maxDist, minConfidence: minConf });
      }
    } catch (e) {
      console.error('Threshold update error:', e);
    }
  };

  return (
    <div className="min-h-screen flex flex-col selection:bg-cyan-500 selection:text-black">
      {/* Top Cyber Navigation Header */}
      <header className="cyber-header sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-[0_0_20px_rgba(0,240,255,0.4)] border border-sky-400/40">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-tight text-white glow-cyan font-sans">
                NetSage
              </h1>
              <span className="cyber-badge cyber-badge-cyan text-[9px]">Autonomous AI NOC</span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">LLM-Assisted Network Troubleshooting & Safety Gatekeeper</p>
          </div>
        </div>

        {/* Action Controls & Real-Time Telemetry Badges */}
        <div className="flex items-center gap-3">
          {/* Live Clock & Latency */}
          <div className="hidden lg:flex items-center gap-3 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-white/10 text-xs font-mono">
            <div className="flex items-center gap-1.5 text-slate-400">
              <Clock className="w-3.5 h-3.5 text-sky-400" />
              <span>{timeStr}</span>
            </div>
            <div className="flex items-center gap-1.5 text-emerald-400">
              <Wifi className="w-3.5 h-3.5" />
              <span>&lt; 2ms RTT</span>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-white/10 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#10b981]" />
            <span className="text-slate-300 text-[11px]">Mode: {topology.mode || 'SIMULATED'}</span>
          </div>

          <button
            onClick={() => setShowArch(true)}
            className="btn-cyber-ghost text-xs px-3 py-1.5 flex items-center gap-1.5"
          >
            <Network className="w-3.5 h-3.5 text-sky-400" />
            Architecture
          </button>

          <button
            onClick={() => setShowSettings(true)}
            className="btn-cyber-ghost text-xs px-3 py-1.5 flex items-center gap-1.5"
          >
            <Sliders className="w-3.5 h-3.5 text-purple-400" />
            Gatekeeper ({thresholds.minConfidence}%)
          </button>

          <button
            onClick={handleResetTopology}
            disabled={loading}
            className="btn-cyber-danger text-xs px-3 py-1.5 flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset Topology
          </button>
        </div>
      </header>

      {/* Main Content Dashboard */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        {/* Row 1: Chaos Injection Control Deck */}
        <FaultInjector
          onInject={handleInjectFault}
          onReset={handleResetTopology}
          activeFaults={topology.active_faults || []}
          isLoading={loading}
        />

        {/* Row 2: Topology Graph & AI Diagnosis Engine */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Topology Canvas & Live Telemetry (7 cols) */}
          <div className="lg:col-span-7 space-y-6">
            <TopologyView
              nodes={topology.nodes || []}
              links={topology.links || []}
              activeFaults={topology.active_faults || []}
              onSelectNode={node => setSelectedNode(node)}
              onOpenTerminal={(nodeId, nodeName) => setActiveTerminalNode({ id: nodeId, name: nodeName })}
            />
            <TelemetryTerminal
              symptomSummary={telemetry.summary}
              anomalies={telemetry.anomalies}
              onRefreshTelemetry={fetchTelemetry}
              isLoading={loading}
            />
          </div>

          {/* Right Column: AI Diagnosis Panel & Vector Evidence (5 cols) */}
          <div className="lg:col-span-5 space-y-6">
            <DiagnosisPanel
              diagnosis={diagnosis}
              isLoading={diagnosing}
              onRunDiagnosis={handleRunDiagnosis}
              onApplyFix={handleResetTopology}
            />
            <EvidenceViewer evidence={evidence} />
          </div>
        </div>

        {/* Row 3: Persistent SQLite Audit Trail & Accuracy Analytics */}
        <AuditHistory
          history={history}
          stats={stats}
          onLabelRun={handleLabelRun}
        />
      </main>

      {/* Node Detail Drawer / Inspection Modal */}
      {selectedNode && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="cyber-card w-full max-w-lg p-6 border-sky-500/30 relative animate-in fade-in zoom-in-95 duration-200">
            <button
              onClick={() => setSelectedNode(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              ✕
            </button>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-100">{selectedNode.name}</h3>
                <span className="cyber-badge cyber-badge-cyan text-[9px]">{selectedNode.type}</span>
              </div>

              <button
                onClick={() => {
                  setActiveTerminalNode({ id: selectedNode.id, name: selectedNode.name });
                  setSelectedNode(null);
                }}
                className="btn-cyber-primary text-xs px-3 py-1.5 flex items-center gap-1.5"
              >
                Launch CLI Console
              </button>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div className="p-3 bg-slate-950 rounded-xl border border-white/5 space-y-1.5">
                <div className="text-slate-400 font-bold uppercase text-[10px] tracking-wider mb-1">
                  Interfaces & Line Protocols
                </div>
                {Object.entries(selectedNode.interfaces || {}).map(([intName, iface]) => (
                  <div key={intName} className="flex justify-between py-1 border-b border-white/5 last:border-0">
                    <span className="text-slate-300 font-semibold">{intName}:</span>
                    <span className="text-sky-300">{iface.ip_address}</span>
                    <span className={iface.status === 'up' ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                      {iface.status} / {iface.protocol || 'up'}
                    </span>
                  </div>
                ))}
              </div>

              {selectedNode.default_gateway && (
                <div className="flex justify-between p-3 bg-slate-950 rounded-xl border border-white/5">
                  <span className="text-slate-400">Default Gateway:</span>
                  <span className="text-slate-200 font-bold">{selectedNode.default_gateway}</span>
                </div>
              )}

              {selectedNode.dns_server && (
                <div className="flex justify-between p-3 bg-slate-950 rounded-xl border border-white/5">
                  <span className="text-slate-400">DNS Nameserver:</span>
                  <span className="text-purple-300 font-bold">{selectedNode.dns_server}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Interactive Live Terminal Session Modal */}
      {activeTerminalNode && (
        <InteractiveTerminalModal
          nodeId={activeTerminalNode.id}
          nodeName={activeTerminalNode.name}
          onClose={() => setActiveTerminalNode(null)}
        />
      )}

      {/* Threshold Config Modal */}
      {showSettings && (
        <ThresholdSettings
          currentDistance={thresholds.maxDistance}
          currentConfidence={thresholds.minConfidence}
          onUpdate={handleUpdateThresholds}
          onClose={() => setShowSettings(false)}
        />
      )}

      {/* Architecture Data Flow Modal */}
      {showArch && (
        <ArchitectureModal onClose={() => setShowArch(false)} />
      )}

      {/* Cyber Footer */}
      <footer className="py-4 text-center text-xs text-slate-500 border-t border-white/5 bg-[#03060c] font-mono">
        NetSage Autonomous Troubleshooting System — Computer Networking Academic Viva Voce Project
      </footer>
    </div>
  );
}
