"use client";

import React, { useState } from 'react';
import PostureCanvas from './PostureCanvas';
import { Activity, Camera, Settings, Shield, RefreshCw, Maximize2 } from 'lucide-react';

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
  const isStanding = data?.analysis?.is_standing || false;
  const calibrated = data?.analysis?.calibrated || false;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-10">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg">
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
        {/* Left Column: Visualizer */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <PostureCanvas onData={setData} />
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <MetricCard 
              icon={<Activity className="text-blue-400" />} 
              label="Mode" 
              value={isStanding ? "Standing" : "Sitting"} 
            />
            <MetricCard 
              icon={<Camera className="text-emerald-400" />} 
              label="Status" 
              value={calibrated ? "Calibrated" : "Uncalibrated"} 
            />
            <MetricCard 
              icon={<Settings className="text-purple-400" />} 
              label="FPS" 
              value="30" 
            />
          </div>
        </div>

        {/* Right Column: Score and Analysis */}
        <div className="space-y-8">
          <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-xl flex flex-col items-center text-center">
            <h2 className="text-xl font-medium text-slate-400 mb-6">Real-Time Posture Score</h2>
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
              Live Feedback
            </h3>
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 min-h-[80px] flex items-center text-slate-300">
              {feedback}
            </div>
          </div>

          <div className="bg-indigo-900/20 p-6 rounded-2xl border border-indigo-500/20">
            <h3 className="text-lg font-semibold mb-2 text-indigo-300">Tips for Stacked Monitors</h3>
            <ul className="text-sm text-indigo-200/70 space-y-2 list-disc list-inside">
              <li>Keep your eyes level with the gap between monitors.</li>
              <li>Use the top monitor only for temporary tasks.</li>
              <li>Perform chin tucks every 20 minutes.</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}

function MetricCard({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) {
  return (
    <div className="bg-slate-900 p-4 rounded-xl border border-slate-800 flex flex-col items-center gap-2">
      <div className="p-2 bg-slate-950 rounded-lg">{icon}</div>
      <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">{label}</span>
      <span className="text-lg font-bold">{value}</span>
    </div>
  );
}
