"use client";

import React from 'react';
import { Activity, Monitor, Shield, User } from 'lucide-react';

interface StrainHeatmapsProps {
  history: any[];
}

export default function StrainHeatmaps({ history }: StrainHeatmapsProps) {
  // Aggregate strain scores (0-100, where 100 is perfect, lower is more strain)
  const aggregate = history.reduce((acc, h) => {
    const m = h.metrics || {};
    acc.neck += m.neck_tilt_lat !== undefined ? (100 - m.neck_tilt_lat * 2000) : 100;
    acc.shoulders += m.shoulder_diff !== undefined ? (100 - m.shoulder_diff * 1000) : 100;
    acc.back += m.slouch_score || 100;
    acc.wrists += m.typing_score || 100;
    acc.count += 1;
    return acc;
  }, { neck: 0, shoulders: 0, back: 0, wrists: 0, count: 0 });

  const count = aggregate.count || 1;
  const scores = {
    neck: Math.max(0, aggregate.neck / count),
    shoulders: Math.max(0, aggregate.shoulders / count),
    back: Math.max(0, aggregate.back / count),
    wrists: Math.max(0, aggregate.wrists / count),
  };

  const getColor = (score: number) => {
    if (score > 85) return '#10b981'; // emerald-500
    if (score > 70) return '#f59e0b'; // amber-500
    return '#ef4444'; // rose-500
  };

  // Workspace Zones based on viewing angle
  // Top: angle > 10, Bottom: angle < -10, Center: -10 to 10
  const zones = history.reduce((acc, h) => {
    const a = h.viewing_angle;
    if (a > 10) acc.top += 1;
    else if (a < -10) acc.bottom += 1;
    else acc.center += 1;
    acc.count += 1;
    return acc;
  }, { top: 0, center: 0, bottom: 0, count: 0 });

  const zoneCount = zones.count || 1;
  const zonePct = {
    top: (zones.top / zoneCount) * 100,
    center: (zones.center / zoneCount) * 100,
    bottom: (zones.bottom / zoneCount) * 100,
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Body Strain Heatmap */}
      <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6 flex items-center gap-2">
          <User className="w-4 h-4 text-indigo-400" /> Biomechanical Strain Heatmap
        </h3>
        <div className="flex items-center justify-around h-[300px]">
          <div className="relative w-40 h-64">
            {/* Simple Stylized Person SVG */}
            <svg viewBox="0 0 100 200" className="w-full h-full">
              {/* Head/Neck */}
              <circle cx="50" cy="30" r="15" fill={getColor(scores.neck)} opacity="0.8" />
              <rect x="45" y="45" width="10" height="10" fill={getColor(scores.neck)} />
              
              {/* Shoulders */}
              <rect x="25" y="55" width="50" height="15" rx="5" fill={getColor(scores.shoulders)} />
              
              {/* Torso/Back */}
              <rect x="30" y="70" width="40" height="60" rx="5" fill={getColor(scores.back)} />
              
              {/* Arms */}
              <rect x="15" y="55" width="10" height="50" rx="5" fill={getColor(scores.shoulders)} />
              <rect x="75" y="55" width="10" height="50" rx="5" fill={getColor(scores.shoulders)} />
              
              {/* Wrists/Hands */}
              <circle cx="20" cy="110" r="8" fill={getColor(scores.wrists)} />
              <circle cx="80" cy="110" r="8" fill={getColor(scores.wrists)} />

              {/* Legs (Static) */}
              <rect x="32" y="135" width="12" height="60" rx="4" fill="#1e293b" />
              <rect x="56" y="135" width="12" height="60" rx="4" fill="#1e293b" />
            </svg>
          </div>

          <div className="space-y-4">
            <LegendItem label="Cervical (Neck)" score={scores.neck} color={getColor(scores.neck)} />
            <LegendItem label="Thoracic (Shoulders)" score={scores.shoulders} color={getColor(scores.shoulders)} />
            <LegendItem label="Lumbar (Lower Back)" score={scores.back} color={getColor(scores.back)} />
            <LegendItem label="Carpal (Wrists)" score={scores.wrists} color={getColor(scores.wrists)} />
          </div>
        </div>
      </div>

      {/* Workspace Heatmap */}
      <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6 flex items-center gap-2">
          <Monitor className="w-4 h-4 text-emerald-400" /> Workspace Utilization Heatmap
        </h3>
        <div className="flex flex-col items-center justify-center h-[300px] gap-4">
          <div className="w-full max-w-xs space-y-2">
            <div className={`h-24 rounded-xl border-2 transition-all flex items-center justify-center ${zonePct.top > 40 ? 'bg-indigo-500/20 border-indigo-500' : 'bg-slate-800/40 border-slate-700'}`}>
              <div className="text-center">
                <p className="text-[10px] font-bold uppercase tracking-tighter text-slate-500">Top Monitor Zone</p>
                <p className="text-xl font-black">{Math.round(zonePct.top)}%</p>
              </div>
            </div>
            <div className={`h-24 rounded-xl border-2 transition-all flex items-center justify-center ${zonePct.center > 40 ? 'bg-emerald-500/20 border-emerald-500' : 'bg-slate-800/40 border-slate-700'}`}>
               <div className="text-center">
                <p className="text-[10px] font-bold uppercase tracking-tighter text-slate-500">Primary Focus Zone</p>
                <p className="text-xl font-black">{Math.round(zonePct.center)}%</p>
              </div>
            </div>
            <div className={`h-16 rounded-xl border-2 transition-all flex items-center justify-center ${zonePct.bottom > 20 ? 'bg-amber-500/20 border-amber-500' : 'bg-slate-800/40 border-slate-700'}`}>
               <div className="text-center">
                <p className="text-[10px] font-bold uppercase tracking-tighter text-slate-500">Laptop/Bottom Zone</p>
                <p className="text-xl font-black">{Math.round(zonePct.bottom)}%</p>
              </div>
            </div>
          </div>
          <p className="text-[10px] text-slate-500 italic">Distribution based on cervical viewing angle history.</p>
        </div>
      </div>
    </div>
  );
}

function LegendItem({ label, score, color }: { label: string, score: number, color: string }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></div>
        <span className="text-xs font-semibold text-slate-300">{label}</span>
      </div>
      <div className="w-32 h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div className="h-full transition-all duration-1000" style={{ width: `${score}%`, backgroundColor: color }}></div>
      </div>
    </div>
  );
}
