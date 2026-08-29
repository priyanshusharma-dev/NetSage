'use client';

import React, { useState } from 'react';
import { BookOpen, FileText, ChevronDown, ChevronUp, Layers, CheckCircle2, Search, ExternalLink } from 'lucide-react';

interface EvidenceChunk {
  id: string;
  content: string;
  metadata: {
    source?: string;
    category?: string;
    section?: string;
    chunk_index?: number;
  };
  distance: number;
  similarity_score: number;
}

interface EvidenceViewerProps {
  evidence: EvidenceChunk[];
}

export default function EvidenceViewer({ evidence }: EvidenceViewerProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const filteredEvidence = evidence.filter(chunk => {
    const text = (chunk.content + ' ' + (chunk.metadata?.source || '') + ' ' + (chunk.metadata?.category || '')).toLowerCase();
    return text.includes(searchTerm.toLowerCase());
  });

  return (
    <div className="cyber-card p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-indigo-950/80 border border-indigo-500/30 flex items-center justify-center">
            <BookOpen className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-base font-bold tracking-wide text-slate-100 flex items-center gap-2">
              Retrieved Knowledge Evidence
              <span className="cyber-badge cyber-badge-purple text-[9px]">ChromaDB Vector Store</span>
            </h2>
            <p className="text-[11px] text-slate-400">Dense semantic embeddings generated with sentence-transformers all-MiniLM-L6-v2</p>
          </div>
        </div>

        <span className="cyber-badge cyber-badge-cyan text-[10px]">
          {evidence.length} Top-K Chunks
        </span>
      </div>

      {evidence.length === 0 ? (
        <div className="py-8 text-center text-xs text-slate-500 bg-slate-950/40 rounded-xl border border-dashed border-white/5 font-mono">
          Run diagnosis to inspect retrieved knowledge base vectors and cosine distances.
        </div>
      ) : (
        <div className="space-y-3">
          {filteredEvidence.map((chunk, idx) => {
            const isExpanded = expandedId === chunk.id || idx === 0;
            const meta = chunk.metadata || {};
            const simPct = Math.round(chunk.similarity_score * 100);

            return (
              <div
                key={chunk.id || idx}
                className="border border-white/10 rounded-xl bg-slate-900/60 overflow-hidden transition-all hover:border-sky-500/30"
              >
                {/* Accordion Header */}
                <div
                  onClick={() => toggleExpand(chunk.id)}
                  className="p-3 flex items-center justify-between cursor-pointer hover:bg-slate-800/60 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-lg bg-indigo-950/80 border border-indigo-500/40 text-indigo-300 text-xs font-mono flex items-center justify-center font-bold shadow-[0_0_10px_rgba(168,85,247,0.2)]">
                      #{idx + 1}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <FileText className="w-3.5 h-3.5 text-slate-400" />
                        <span className="text-xs font-bold text-slate-200">{meta.source || 'Knowledge Chunk'}</span>
                        <span className="cyber-badge cyber-badge-purple text-[9px] py-0.5 px-2">
                          {meta.category || 'General'}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Chunk ID: {chunk.id} • Section: {meta.section || 'Troubleshooting Guide'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {/* Distance & Similarity Bar */}
                    <div className="text-right">
                      <div className="text-xs font-mono font-bold text-sky-400">
                        Dist: {chunk.distance.toFixed(3)}
                      </div>
                      <div className="w-20 bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1 border border-white/5">
                        <div
                          className="bg-gradient-to-r from-sky-400 to-indigo-400 h-full rounded-full"
                          style={{ width: `${simPct}%` }}
                        />
                      </div>
                    </div>

                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </div>

                {/* Expanded Chunk Details */}
                {isExpanded && (
                  <div className="p-4 border-t border-white/5 bg-[#03060d] text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-wrap">
                    <div className="text-[10px] uppercase font-bold text-indigo-400 mb-2 pb-1 border-b border-white/5">
                      Ground Truth Reference Context:
                    </div>
                    {chunk.content}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
