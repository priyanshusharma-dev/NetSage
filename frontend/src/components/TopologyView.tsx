'use client';

import React, { useState } from 'react';
import { Router, Server, Laptop, Network, Activity, Terminal, ExternalLink, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { NodeData, LinkData, ActiveFault } from '@/types';

interface TopologyViewProps {
  nodes: NodeData[];
  links: LinkData[];
  activeFaults: ActiveFault[];
  onSelectNode: (node: NodeData) => void;
  onOpenTerminal: (nodeId: string, nodeName: string) => void;
}

export default function TopologyView({ nodes, links, activeFaults, onSelectNode, onOpenTerminal }: TopologyViewProps) {
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'router':
        return <Router className="w-5 h-5 text-sky-400" />;
      case 'switch':
        return <Network className="w-5 h-5 text-indigo-400" />;
      case 'server':
        return <Server className="w-5 h-5 text-purple-400" />;
      default:
        return <Laptop className="w-5 h-5 text-emerald-400" />;
    }
  };

  const isNodeFaulted = (nodeId: string) => {
    return activeFaults.some(f => f.target_node === nodeId);
  };

  const isLinkFaulted = (source: string, target: string) => {
    return activeFaults.some(f => 
      (f.target_node === source && f.type === 'interface_down') ||
      (f.target_node === target && f.type === 'interface_down') ||
      (f.type === 'routing_loop' && (source === 'Core-R3' || target === 'Core-R3'))
    );
  };

  return (
    <div className="cyber-card p-5 relative overflow-hidden">
      {/* Header Bar */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-sky-950/80 border border-sky-500/30 flex items-center justify-center">
            <Activity className="w-4 h-4 text-sky-400 animate-pulse" />
          </div>
          <div>
            <h2 className="text-base font-bold tracking-wide text-slate-100 flex items-center gap-2">
              Autonomous Network Graph
              <span className="cyber-badge cyber-badge-cyan text-[9px]">GNS3 / Topology Engine</span>
            </h2>
            <p className="text-[11px] text-slate-400">Click any node to inspect interfaces or launch interactive Cisco IOS CLI</p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 bg-slate-900/80 px-2.5 py-1 rounded-lg border border-white/5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#10b981]" />
            <span className="text-slate-300 text-[11px]">8 Nodes Active</span>
          </div>
          <div className="flex items-center gap-1.5 bg-slate-900/80 px-2.5 py-1 rounded-lg border border-white/5">
            <span className={`w-2 h-2 rounded-full ${activeFaults.length > 0 ? 'bg-rose-500 animate-ping' : 'bg-slate-600'}`} />
            <span className="text-slate-300 text-[11px]">{activeFaults.length} Faults</span>
          </div>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="w-full h-[420px] bg-[#040711] rounded-xl border border-white/5 relative overflow-hidden flex items-center justify-center">
        {/* Background Grid Mesh */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b15_1px,transparent_1px),linear-gradient(to_bottom,#1e293b15_1px,transparent_1px)] bg-[size:28px_28px] pointer-events-none" />

        <svg className="w-full h-full relative z-10" viewBox="0 0 900 550">
          <defs>
            {/* Gradients */}
            <linearGradient id="linkHealthy" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0284c7" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#00f0ff" stopOpacity="0.7" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.9" />
            </linearGradient>
            <linearGradient id="linkFaulted" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ef4444" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#ff3366" stopOpacity="0.95" />
            </linearGradient>

            {/* Glowing filter */}
            <filter id="neonGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Render Links */}
          {links.map((link, idx) => {
            const src = nodes.find(n => n.id === link.source_node);
            const tgt = nodes.find(n => n.id === link.target_node);
            if (!src || !tgt) return null;
            const faulted = isLinkFaulted(link.source_node, link.target_node);

            const midX = (src.x + tgt.x) / 2;
            const midY = (src.y + tgt.y) / 2;

            return (
              <g key={idx}>
                {/* Base Link Line */}
                <line
                  x1={src.x}
                  y1={src.y}
                  x2={tgt.x}
                  y2={tgt.y}
                  stroke={faulted ? 'url(#linkFaulted)' : 'url(#linkHealthy)'}
                  strokeWidth={faulted ? '3' : '2'}
                  strokeDasharray={faulted ? '6,6' : 'none'}
                  className={faulted ? 'flowing-link' : ''}
                  filter="url(#neonGlow)"
                />

                {/* Subnet Badge pill */}
                <rect
                  x={midX - 45}
                  y={midY - 14}
                  width="90"
                  height="16"
                  rx="4"
                  fill="#060a14"
                  stroke={faulted ? 'rgba(239,68,68,0.4)' : 'rgba(255,255,255,0.08)'}
                  strokeWidth="1"
                />
                <text
                  x={midX}
                  y={midY - 2}
                  fill={faulted ? '#fca5a5' : '#94a3b8'}
                  fontSize="9.5"
                  fontFamily="monospace"
                  textAnchor="middle"
                  fontWeight="600"
                >
                  {link.subnet}
                </text>
              </g>
            );
          })}

          {/* Render Nodes */}
          {nodes.map(node => {
            const faulted = isNodeFaulted(node.id);
            const isHovered = hoveredNodeId === node.id;

            return (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
                className="cursor-pointer transition-all duration-200"
                onMouseEnter={() => setHoveredNodeId(node.id)}
                onMouseLeave={() => setHoveredNodeId(null)}
                onClick={() => onSelectNode(node)}
              >
                {/* Outer Ambient Glow Ring */}
                <circle
                  r={isHovered ? '30' : '26'}
                  fill={faulted ? 'rgba(239, 68, 68, 0.25)' : 'rgba(2, 132, 199, 0.15)'}
                  stroke={faulted ? '#ef4444' : isHovered ? '#00f0ff' : 'rgba(255,255,255,0.1)'}
                  strokeWidth={isHovered ? '2.5' : '1.5'}
                  className={faulted ? 'animate-pulse-ring' : ''}
                />

                {/* Node Center Base */}
                <circle
                  r="19"
                  fill="#080e1e"
                  stroke={faulted ? '#ff3366' : isHovered ? '#00f0ff' : '#0284c7'}
                  strokeWidth="2"
                  filter="url(#neonGlow)"
                />

                {/* Node Icon */}
                <foreignObject x="-10" y="-10" width="20" height="20">
                  <div className="w-full h-full flex items-center justify-center pointer-events-none">
                    {getNodeIcon(node.type)}
                  </div>
                </foreignObject>

                {/* Node Label Card */}
                <rect
                  x="-42"
                  y="26"
                  width="84"
                  height="18"
                  rx="5"
                  fill="#060a14"
                  stroke={faulted ? 'rgba(239,68,68,0.5)' : isHovered ? 'rgba(0,240,255,0.5)' : 'rgba(255,255,255,0.1)'}
                  strokeWidth="1"
                />
                <text
                  y="39"
                  textAnchor="middle"
                  fill={faulted ? '#fca5a5' : isHovered ? '#00f0ff' : '#e2e8f0'}
                  fontSize="10"
                  fontWeight="700"
                  fontFamily="sans-serif"
                >
                  {node.id}
                </text>

                {/* Fault Indicator Tag */}
                {faulted && (
                  <g transform="translate(14, -16)">
                    <circle r="7" fill="#ef4444" stroke="#060a14" strokeWidth="2" />
                    <text y="3" textAnchor="middle" fill="white" fontSize="9" fontWeight="bold">!</text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {/* Floating Quick Action Footer inside Canvas */}
        <div className="absolute bottom-3 left-4 right-4 flex items-center justify-between pointer-events-auto">
          <span className="text-[11px] font-mono text-slate-500 bg-slate-950/80 px-2.5 py-1 rounded-md border border-white/5">
            Topology Model: Cisco IOSv 15.9 & Linux POSIX Endpoints
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onOpenTerminal('HQ-R1', 'HQ Edge Router')}
              className="btn-cyber-ghost text-[11px] py-1 px-2.5 flex items-center gap-1.5 bg-slate-900/90 hover:border-sky-500/40 text-sky-300"
            >
              <Terminal className="w-3.5 h-3.5 text-sky-400" />
              CLI: HQ-R1
            </button>
            <button
              onClick={() => onOpenTerminal('Core-R3', 'Core Transit Router')}
              className="btn-cyber-ghost text-[11px] py-1 px-2.5 flex items-center gap-1.5 bg-slate-900/90 hover:border-sky-500/40 text-sky-300"
            >
              <Terminal className="w-3.5 h-3.5 text-purple-400" />
              CLI: Core-R3
            </button>
            <button
              onClick={() => onOpenTerminal('Host-A', 'HQ Workstation')}
              className="btn-cyber-ghost text-[11px] py-1 px-2.5 flex items-center gap-1.5 bg-slate-900/90 hover:border-sky-500/40 text-emerald-300"
            >
              <Terminal className="w-3.5 h-3.5 text-emerald-400" />
              CLI: Host-A
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
