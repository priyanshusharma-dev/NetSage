'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Terminal, X, CornerDownLeft, Play, Cpu, Trash2 } from 'lucide-react';

interface InteractiveTerminalModalProps {
  nodeId: string;
  nodeName: string;
  onClose: () => void;
}

export default function InteractiveTerminalModal({ nodeId, nodeName, onClose }: InteractiveTerminalModalProps) {
  const [command, setCommand] = useState('');
  const [history, setHistory] = useState<Array<{ cmd: string; output: string }>>([]);
  const [executing, setExecuting] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Suggested quick commands based on node type
  const isRouter = nodeId.includes('R') || nodeId.includes('SW');
  const suggestions = isRouter
    ? ['show ip interface brief', 'show ip route', 'show ip access-lists', 'ping 10.1.13.2', 'traceroute 192.168.20.20', 'show version']
    : ['ip addr', 'ip route', 'ping 192.168.10.1', 'ping 192.168.20.20', 'nslookup internal.corp.local'];

  const executeCmd = async (cmdToRun: string) => {
    const cleanCmd = cmdToRun.trim();
    if (!cleanCmd || executing) return;

    setExecuting(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/cli/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_id: nodeId, command: cleanCmd })
      });

      if (res.ok) {
        const data = await res.json();
        setHistory(prev => [...prev, { cmd: cleanCmd, output: data.output }]);
      } else {
        setHistory(prev => [...prev, { cmd: cleanCmd, output: '% CLI execution error.' }]);
      }
    } catch (e) {
      setHistory(prev => [...prev, { cmd: cleanCmd, output: `% Network connection error to node ${nodeId}.` }]);
    } finally {
      setExecuting(false);
      setCommand('');
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, executing]);

  useEffect(() => {
    inputRef.current?.focus();
    // Initial welcome command
    executeCmd(isRouter ? 'show ip interface brief' : 'ip addr');
  }, [nodeId]);

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="cyber-card w-full max-w-4xl h-[600px] flex flex-col p-6 border-sky-500/30 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-sky-950 border border-sky-500/40 flex items-center justify-center">
              <Terminal className="w-4 h-4 text-sky-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-100 font-mono">{nodeId} CLI Console</h3>
                <span className="cyber-badge cyber-badge-cyan text-[10px]">
                  {isRouter ? 'Cisco IOSv Exec' : 'Linux POSIX Shell'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">{nodeName} • Interactive Diagnostic Session</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setHistory([])}
              className="btn-cyber-ghost text-xs px-2.5 py-1.5 text-slate-400 hover:text-slate-200"
              title="Clear Terminal"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg border border-white/10 text-slate-400 hover:text-white hover:border-white/20 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Quick Suggestion Pills */}
        <div className="py-2.5 flex items-center gap-2 overflow-x-auto shrink-0 border-b border-white/5">
          <span className="text-[11px] text-slate-500 font-mono whitespace-nowrap">Quick Commands:</span>
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => executeCmd(s)}
              disabled={executing}
              className="text-[11px] font-mono px-2.5 py-1 rounded-md bg-slate-900 border border-white/10 text-sky-300 hover:bg-sky-950 hover:border-sky-500/50 whitespace-nowrap transition-all"
            >
              {s}
            </button>
          ))}
        </div>

        {/* Terminal Output Area */}
        <div className="cyber-terminal flex-1 my-3 p-4 overflow-y-auto space-y-3 font-mono text-xs">
          <div className="text-slate-500">
            Connected to {nodeId} (NetSage Diagnostic Telnet Engine). Type commands below or click quick suggestions.
          </div>

          {history.map((item, idx) => (
            <div key={idx} className="space-y-1">
              <div className="flex items-center gap-2 text-emerald-400 font-bold">
                <span>{isRouter ? `${nodeId}#` : `${nodeId}:~$`}</span>
                <span className="text-slate-100">{item.cmd}</span>
              </div>
              <pre className="text-sky-300/90 whitespace-pre-wrap pl-3 leading-relaxed border-l-2 border-sky-500/20">
                {item.output}
              </pre>
            </div>
          ))}

          {executing && (
            <div className="flex items-center gap-2 text-amber-400 text-xs animate-pulse">
              <Cpu className="w-3.5 h-3.5 animate-spin" />
              <span>Executing on {nodeId}...</span>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Command Input Bar */}
        <form
          onSubmit={e => {
            e.preventDefault();
            executeCmd(command);
          }}
          className="flex items-center gap-2 shrink-0 pt-2"
        >
          <span className="font-mono text-xs text-emerald-400 font-bold px-2 py-2 bg-slate-950 rounded-lg border border-white/5">
            {isRouter ? `${nodeId}#` : `${nodeId}:~$`}
          </span>
          <input
            ref={inputRef}
            type="text"
            value={command}
            onChange={e => setCommand(e.target.value)}
            placeholder="Type command (e.g. show ip route, ping, traceroute)..."
            className="flex-1 bg-black/60 border border-white/10 rounded-xl px-3.5 py-2.5 text-xs font-mono text-sky-200 placeholder:text-slate-600 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
          />
          <button
            type="submit"
            disabled={!command.trim() || executing}
            className="btn-cyber-primary text-xs px-4 py-2.5 flex items-center gap-1.5"
          >
            <CornerDownLeft className="w-3.5 h-3.5" />
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
