"use client";

import React, { useState } from 'react';
import PostureCanvas from './PostureCanvas';
import { Activity, Camera, Settings, Shield, RefreshCw, Maximize2, Monitor, ArrowUpCircle, CheckCircle2, AlertCircle } from 'lucide-react';

export default function PostureDashboard() {
  const [data, setData] = useState<any>(null);
  const [calibrating, setCalibrating] = useState(false);

  const handleCalibrate = async () => {
    setCalibrating(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/calibrate', { method: 'POST' });
      const result = await res.json();
      if (result.success) {
        // Show success toast or feedback
      }
    } catch (err) {
      console.error('Calibration failed', err);
    } finally {
      setTimeout(() => setCalibrating(false), 1000);
    }
  };

  const handleToggleMirror = async () => {
    try {
      await fetch('http://127.0.0.1:8000/api/toggle-mirror', { method: 'POST' });
    } catch (err) {
      console.error('Toggle mirror failed', err);
    }
  };

  const score = data?.analysis?.score || 0;
  const feedback = data?.analysis?.feedback || "Initializing...";
  const placementSuggestion = data?.analysis?.placement_suggestion || "Analyzing window placement...";
  const isStanding = data?.analysis?.is_standing || false;
  const calibrated = data?.analysis?.calibrated || false;
  const distance = data?.analysis?.distance_cm || 0;
  const angle = data?.analysis?.viewing_angle || 0;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-10">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg shadow-lg shadow-indigo-500/20">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Posture-Sense</h1>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={handleToggleMirror}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg transition-all"
          >
            <Maximize2 className="w-4 h-4" /> Mirror
          </button>
          <button 
            onClick={handleCalibrate}
            className={`flex items-center gap-2 px-6 py-2 rounded-lg font-semibold transition-all shadow-lg ${
              calibrating 
                ? 'bg-indigo-900 cursor-wait' 
                : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-500/20'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${calibrating ? 'animate-spin' : ''}`} />
            {calibrating ? 'Calibrating...' : 'Calibrate'}
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Visualizers */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Skeleton Canvas */}
            <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 backdrop-blur-sm">
              <h3 className="text-sm font-semibold text-slate-500 mb-2 uppercase tracking-wider">Live Tracker</h3>
              <PostureCanvas onData={setData} />
            </div>

            {/* Monitor Layout Visualizer */}
            <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 backdrop-blur-sm flex flex-col">
              <h3 className="text-sm font-semibold text-slate-500 mb-2 uppercase tracking-wider">Workspace Geometry</h3>
              <WorkspaceVisualizer data={data} />
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard 
              icon={<Activity className="text-blue-400" />} 
              label="Mode" 
              value={isStanding ? "Standing" : "Sitting"} 
            />
            <MetricCard 
              icon={<Maximize2 className="text-emerald-400" />} 
              label="Distance" 
              value={`${distance} cm`} 
            />
             <MetricCard 
              icon={<Monitor className="text-orange-400" />} 
              label="View Angle" 
              value={`${angle}°`} 
            />
            <MetricCard 
              icon={<Settings className="text-purple-400" />} 
              label="Status" 
              value={calibrated ? "Calibrated" : "Raw"} 
            />
          </div>

          {/* Placement Suggestion Bar */}
          <div className={`p-4 rounded-xl border flex items-center gap-4 transition-all duration-500 ${
            placementSuggestion.includes("Perfect") 
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
              : 'bg-orange-500/10 border-orange-500/30 text-orange-400'
          }`}>
            {placementSuggestion.includes("Perfect") ? <CheckCircle2 className="w-6 h-6" /> : <AlertCircle className="w-6 h-6" />}
            <span className="font-semibold text-lg">{placementSuggestion}</span>
          </div>
        </div>

        {/* Right Column: Score and Analysis */}
        <div className="space-y-8">
          <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-xl flex flex-col items-center text-center">
            <h2 className="text-xl font-medium text-slate-400 mb-6">Ergonomic Score</h2>
            <div className="relative mb-6">
               <svg className="w-48 h-48 transform -rotate-90">
                <circle
                  cx="96"
                  cy="96"
                  r="88"
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="transparent"
                  className="text-slate-800"
                />
                <circle
                  cx="96"
                  cy="96"
                  r="88"
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="transparent"
                  strokeDasharray={552.92}
                  strokeDashoffset={552.92 - (552.92 * score) / 100}
                  className={`transition-all duration-500 ease-out ${
                    score > 85 ? 'text-emerald-500' : score > 65 ? 'text-yellow-500' : 'text-rose-500'
                  }`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-5xl font-bold">{Math.round(score)}%</span>
              </div>
            </div>
            <p className={`text-lg font-medium px-4 py-2 rounded-full ${
              score > 85 ? 'bg-emerald-500/10 text-emerald-400' : score > 65 ? 'bg-yellow-500/10 text-yellow-400' : 'bg-rose-500/10 text-rose-400'
            }`}>
              {score > 85 ? 'Excellent Alignment' : score > 65 ? 'Needs Adjustment' : 'Critical Strain'}
            </p>
          </div>

          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-400" />
              Posture Feedback
            </h3>
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 min-h-[80px] flex items-center text-slate-300 leading-relaxed">
              {feedback}
            </div>
          </div>

          <div className="bg-indigo-900/20 p-6 rounded-2xl border border-indigo-500/20">
            <h3 className="text-lg font-semibold mb-2 text-indigo-300">Smart Stretch Suggestion</h3>
            <p className="text-sm text-indigo-200/70 mb-4 italic">Detected long session looking at Top Monitor.</p>
            <div className="flex items-center gap-3 bg-indigo-500/20 p-3 rounded-lg border border-indigo-500/30">
              <ArrowUpCircle className="w-5 h-5 text-indigo-400 animate-bounce" />
              <span className="font-medium">Perform 5 Chin Tucks</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function WorkspaceVisualizer({ data }: { data: any }) {
  if (!data?.workspace || !data?.workspace.top) return (
    <div className="flex-1 flex items-center justify-center text-slate-600 italic text-sm">
      Awaiting workspace data...
    </div>
  );

  const { workspace, window, ess } = data;
  const totalHeight = workspace.total_height;
  const topH = workspace.top.height;
  const bottomH = workspace.bottom.height;

  // Scaling factor for visualization
  const scale = 200 / totalHeight;

  return (
    <div className="flex-1 flex flex-col items-center justify-center py-4">
      <div className="relative w-40 bg-slate-800 rounded border-2 border-slate-700 overflow-hidden" style={{ height: totalHeight * scale }}>
        {/* Top Monitor */}
        <div className="absolute top-0 left-0 w-full border-b border-slate-600 bg-slate-700/30 flex items-center justify-center text-[10px] font-bold text-slate-500" style={{ height: topH * scale }}>
          TOP
        </div>
        {/* Bottom Monitor */}
        <div className="absolute bottom-0 left-0 w-full bg-slate-700/30 flex items-center justify-center text-[10px] font-bold text-slate-500" style={{ height: bottomH * scale }}>
          BOTTOM
        </div>

        {/* Active Window */}
        {window && (
          <div 
            className="absolute left-2 right-2 bg-indigo-500/40 border border-indigo-400 shadow-[0_0_10px_rgba(99,102,241,0.4)] transition-all duration-300 rounded-sm"
            style={{ 
              top: window.y * scale, 
              height: window.height * scale 
            }}
          >
            <div className="w-full h-full flex items-center justify-center overflow-hidden px-1">
               <span className="text-[8px] font-medium text-white whitespace-nowrap truncate">{window.title}</span>
            </div>
          </div>
        )}

        {/* Ergonomic Sweet Spot (ESS) Target */}
        {ess && (
          <div 
            className="absolute left-0 right-0 border-t-2 border-dashed border-emerald-400/60 z-20"
            style={{ top: ess.target_y * scale }}
          >
            <div className="absolute -top-3 right-1 text-[8px] text-emerald-400 font-bold uppercase tracking-tighter">Target</div>
          </div>
        )}
      </div>
      <p className="mt-4 text-[10px] text-slate-500 font-medium">VERTICAL STACK MODEL</p>
    </div>
  );
}

function MetricCard({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) {
  return (
    <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col items-center gap-2 hover:border-slate-700 transition-all">
      <div className="p-2 bg-slate-950 rounded-lg">{icon}</div>
      <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">{label}</span>
      <span className="text-base font-bold text-slate-200">{value}</span>
    </div>
  );
}
