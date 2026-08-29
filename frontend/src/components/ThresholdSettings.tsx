'use client';

import React, { useState } from 'react';
import { Sliders, X, Save, ShieldCheck } from 'lucide-react';

interface ThresholdSettingsProps {
  currentDistance: number;
  currentConfidence: number;
  onUpdate: (maxDistance: number, minConfidence: number) => Promise<void>;
  onClose: () => void;
}

export default function ThresholdSettings({
  currentDistance,
  currentConfidence,
  onUpdate,
  onClose
}: ThresholdSettingsProps) {
  const [distance, setDistance] = useState(currentDistance);
  const [confidence, setConfidence] = useState(currentConfidence);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onUpdate(distance, confidence);
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-md p-6 border-white/20 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 mb-4">
          <Sliders className="w-5 h-5 text-sky-400" />
          <h3 className="text-base font-bold text-slate-100">Safety Gatekeeper Thresholds</h3>
        </div>

        <p className="text-xs text-slate-400 mb-6 leading-relaxed">
          Viva Defensibility Demonstration: Adjust these statistical parameters to observe how NetSage prevents hallucinated network commands by escalating low-confidence diagnoses to human operators.
        </p>

        <div className="space-y-5">
          {/* Min Confidence Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="font-semibold text-slate-300">Minimum LLM Confidence Score</span>
              <span className="font-mono font-bold text-sky-400">{confidence}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="1"
              value={confidence}
              onChange={e => setConfidence(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-500"
            />
            <span className="text-[10px] text-slate-500">
              Diagnoses below this score trigger &quot;Insufficient evidence — escalate to manual&quot;.
            </span>
          </div>

          {/* Max Retrieval Distance Slider */}
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="font-semibold text-slate-300">Max RAG Vector Cosine Distance</span>
              <span className="font-mono font-bold text-purple-400">{distance.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="1.5"
              step="0.05"
              value={distance}
              onChange={e => setDistance(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <span className="text-[10px] text-slate-500">
              Cosine distances above this threshold denote poor semantic similarity.
            </span>
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-8 pt-4 border-t border-white/10">
          <button onClick={onClose} className="btn-secondary text-xs px-3 py-1.5">
            Cancel
          </button>
          <button onClick={handleSave} disabled={saving} className="btn-primary text-xs px-4 py-1.5 flex items-center gap-1.5">
            <Save className="w-3.5 h-3.5" />
            {saving ? 'Saving...' : 'Apply Thresholds'}
          </button>
        </div>
      </div>
    </div>
  );
}
