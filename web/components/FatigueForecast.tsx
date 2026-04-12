"use client";

import React from 'react';
import { TrendingDown, TrendingUp, Zap, ShieldCheck } from 'lucide-react';

export default function FatigueForecast({ prediction }: { prediction: any }) {
  if (!prediction) return (
    <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 flex items-center justify-center text-slate-500 italic text-sm">
      Training AI fatigue model...
    </div>
  );

  const { imminent, predicted_score, confidence } = prediction;
  const isStable = !imminent;

  return (
    <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Fatigue Forecast</h3>
        <div className={`flex items-center gap-1 px-2 py-1 rounded text-[10px] font-bold ${isStable ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
          {isStable ? <ShieldCheck className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
          {isStable ? 'STABLE' : 'SLUMP IMMINENT'}
        </div>
      </div>

      <div className="flex items-end gap-4">
        <div>
          <div className="text-3xl font-black text-slate-100">{Math.round(predicted_score)}%</div>
          <div className="text-[10px] text-slate-500 font-medium">PREDICTED (T+15m)</div>
        </div>
        
        <div className="flex-1 space-y-2 pb-1">
          <div className="flex justify-between text-[9px] font-bold text-slate-600">
            <span>MODEL CONFIDENCE</span>
            <span>{Math.round(confidence * 100)}%</span>
          </div>
          <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-indigo-500 transition-all duration-1000" 
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
        </div>
      </div>

      {!isStable && (
        <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-center gap-3 text-xs text-rose-300">
          <Zap className="w-4 h-4 fill-current" />
          <span>AI predicts a posture drop soon. Stand up for a moment!</span>
        </div>
      )}
    </div>
  );
}
