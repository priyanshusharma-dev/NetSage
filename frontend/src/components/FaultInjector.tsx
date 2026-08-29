'use client';

import React, { useState } from 'react';
import { Zap, RotateCcw, ShieldAlert, Cpu, Globe, RefreshCw, Layers, Flame } from 'lucide-react';

interface FaultInjectorProps {
  onInject: (faultType: string, params?: any) => Promise<void>;
  onReset: () => Promise<void>;
  activeFaults: any[];
  isLoading: boolean;
}

export default function FaultInjector({ onInject, onReset, activeFaults, isLoading }: FaultInjectorProps) {
  const [injectingType, setInjectingType] = useState<string | null>(null);

  const faults = [
    {
      id: 'interface_down',
      title: 'Interface Down',
      layer: 'Layer 1/2',
      target: 'HQ-R1 (Gi0/1)',
      icon: <Zap className="w-4 h-4 text-amber-400" />,
      desc: 'Simulates physical link failure or admin shutdown of HQ LAN interface.'
    },
    {
      id: 'subnet_misconfig',
      title: 'Subnet / GW Error',
      layer: 'Layer 3',
      target: 'Host-B',
      icon: <Layers className="w-4 h-4 text-sky-400" />,
      desc: 'Injects invalid default gateway (192.168.20.254) and bad subnet mask.'
    },
    {
      id: 'acl_blocking',
      title: 'ACL Traffic Drop',
      layer: 'Layer 3/4',
      target: 'HQ-R1 (Gi0/0)',
      icon: <ShieldAlert className="w-4 h-4 text-rose-400" />,
      desc: 'Applies extended ACL RESTRICT_CAMPUS_TRAFFIC dropping inter-subnet packets.'
    },
    {
      id: 'routing_loop',
      title: 'Routing Loop',
      layer: 'Layer 3',
      target: 'Core-R3',
      icon: <RefreshCw className="w-4 h-4 text-purple-400" />,
      desc: 'Injects conflicting static route causing TTL expiration loops between Core & HQ.'
    },
    {
      id: 'dns_failure',
      title: 'DNS Resolver Fail',
      layer: 'Layer 7',
      target: 'Host-A',
      icon: <Globe className="w-4 h-4 text-emerald-400" />,
      desc: 'Points nameserver to unreachable IP (192.0.2.53), causing query timeouts.'
    }
  ];

  const handleInject = async (type: string) => {
    setInjectingType(type);
    try {
      await onInject(type);
    } finally {
      setInjectingType(null);
    }
  };

  return (
    <div className="cyber-card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-amber-950/80 border border-amber-500/30 flex items-center justify-center">
            <Flame className="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <h2 className="text-base font-bold tracking-wide text-slate-100 flex items-center gap-2">
              Chaos Fault Injection Deck
              <span className="cyber-badge cyber-badge-rose text-[9px]">OSI Layers 1–7</span>
            </h2>
            <p className="text-[11px] text-slate-400">Trigger deterministic network failures to test autonomous AI diagnosis & safe deferral</p>
          </div>
        </div>

        <button
          onClick={onReset}
          disabled={isLoading}
          className="btn-cyber-danger text-xs px-3.5 py-1.5 flex items-center gap-1.5"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset Baseline Topology
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3.5">
        {faults.map(f => {
          const isActive = activeFaults.some(af => af.type === f.id);
          const isCurrentLoading = injectingType === f.id;

          return (
            <div
              key={f.id}
              onClick={() => !isLoading && handleInject(f.id)}
              className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between group ${
                isActive
                  ? 'bg-rose-950/50 border-rose-500/70 shadow-[0_0_20px_rgba(255,51,102,0.3)] ring-1 ring-rose-500/50'
                  : 'bg-slate-900/70 border-white/5 hover:border-sky-500/40 hover:bg-slate-800/80 hover:shadow-[0_0_15px_rgba(0,240,255,0.1)]'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-black/40 border border-white/5 group-hover:border-sky-500/30 transition-colors">
                      {f.icon}
                    </div>
                    <span className="text-xs font-bold text-slate-100">{f.title}</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-slate-400 font-mono font-bold">
                    {f.layer}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-2 mb-3">{f.desc}</p>
              </div>

              <div className="flex items-center justify-between pt-2.5 border-t border-white/5">
                <span className="text-[10px] text-slate-400 font-mono">Target: {f.target}</span>
                {isActive ? (
                  <span className="cyber-badge cyber-badge-rose text-[9px] py-0.5 px-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping" />
                    ACTIVE
                  </span>
                ) : (
                  <span className="text-[10px] font-mono text-sky-400 group-hover:text-cyan-300 font-bold flex items-center gap-0.5">
                    {isCurrentLoading ? 'Injecting...' : 'Inject Fault →'}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
