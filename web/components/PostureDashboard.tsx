"use client";

import React, { useState, useEffect, useRef } from 'react';
import PostureCanvas from './PostureCanvas';
import PostureTrends from './PostureTrends';
import FatigueForecast from './FatigueForecast';
import Link from 'next/link';
import { Activity, Camera, Settings, Shield, ShieldOff, RefreshCw, Maximize2, Monitor, ArrowUpCircle, CheckCircle2, AlertCircle, Flame, Target, Smile, Meh, Frown, Volume2, VolumeX, Timer, Keyboard, BrainCircuit, BarChart3, Compass, Thermometer } from 'lucide-react';

export default function PostureDashboard() {
  const [data, setData] = useState<any>(null);
  const [calibrating, setCalibrating] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [privacyActive, setPrivacyActive] = useState(false);
  const lastNudgeRef = useRef<string | null>(null);

  const [activeStretch, setActiveStretch] = useState<string | null>(null);
  const [stretchTimer, setStretchTimer] = useState(0);

  const handleCalibrate = async () => {
    setCalibrating(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/calibrate', { method: 'POST' });
      const result = await res.json();
      if (result.success) { console.log("Calibrated"); }
    } catch (err) {
      console.error('Calibration failed', err);
    } finally {
      setTimeout(() => setCalibrating(false), 1000);
    }
  };

  const handleToggleMirror = async () => {
    try { await fetch('http://127.0.0.1:8000/api/toggle-mirror', { method: 'POST' }); } catch (err) {}
  };

  const handleTogglePrivacy = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/toggle-privacy', { method: 'POST' });
      const result = await res.json();
      setPrivacyActive(result.privacy_mode);
    } catch (err) {}
  };

  const analysis = data?.analysis || {};
  const score = analysis.score || 0;
  const feedback = analysis.feedback || "Initializing...";
  const placementSuggestion = analysis.placement_suggestion || "Analyzing...";
  const isStanding = analysis.is_standing || false;
  const calibrated = analysis.calibrated || false;
  const distance = analysis.distance_cm || 0;
  const angle = analysis.viewing_angle || 0;
  const typingScore = analysis.typing_score || 100;
  const cva = analysis.metrics?.cva || 0;
  const protractionScore = analysis.metrics?.protraction_score || 100;
  const lateralLean = analysis.metrics?.lateral_lean || 0;
  const lateralLeanScore = analysis.metrics?.lateral_lean_score || 100;
  const nudge = analysis.nudge || null;
  const stretchType = analysis.stretch_type || null;
  const blinkRate = analysis.blink_rate || 0;
  const sessionDuration = analysis.session_duration || 0;
  const eyeStrainWarning = analysis.eye_strain_warning || null;
  const stats = analysis.stats || { streak: 0, today_avg_score: 0, today_ergonomic_minutes: 0, total_ergonomic_minutes: 0, fatigue_prediction: null };

  // Sound and Title Alerts
  useEffect(() => {
    if (nudge && nudge !== lastNudgeRef.current) {
      if (soundEnabled) {
        try {
          const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
          const oscillator = audioContext.createOscillator();
          const gainNode = audioContext.createGain();
          const panner = audioContext.createStereoPanner ? audioContext.createStereoPanner() : null;
          
          if (panner) {
            // Pan sound toward the direction of the lean to nudge user back
            // lateralLean is mid_s_x - mid_h_x. If positive, leaning RIGHT (so pan LEFT)
            // Clamp to -1 to 1 range. 0.05 is significant.
            const panValue = Math.max(-1, Math.min(1, lateralLean * -10));
            panner.pan.setValueAtTime(panValue, audioContext.currentTime);
            oscillator.connect(panner);
            panner.connect(gainNode);
          } else {
            oscillator.connect(gainNode);
          }
          
          gainNode.connect(audioContext.destination);
          oscillator.type = 'sine';
          oscillator.frequency.setValueAtTime(440, audioContext.currentTime);
          gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
          oscillator.start();
          oscillator.stop(audioContext.currentTime + 0.2);
        } catch (e) {}
      }
      lastNudgeRef.current = nudge;
    } else if (!nudge) {
      lastNudgeRef.current = null;
    }

    if (nudge) {
      const originalTitle = "Posture-Sense";
      let isAlert = false;
      const interval = setInterval(() => {
        document.title = isAlert ? "⚠️ ALERT!" : originalTitle;
        isAlert = !isAlert;
      }, 1000);
      return () => { clearInterval(interval); document.title = originalTitle; };
    }
  }, [nudge, soundEnabled]);

  useEffect(() => {
    if (stretchType && !activeStretch) {
      setActiveStretch(stretchType);
      setStretchTimer(20);
    }
  }, [stretchType, activeStretch]);

  useEffect(() => {
    if (stretchTimer > 0) {
      const t = setTimeout(() => setStretchTimer(stretchTimer - 1), 1000);
      return () => clearTimeout(t);
    } else if (activeStretch && stretchTimer === 0) {
      setActiveStretch(null);
    }
  }, [stretchTimer, activeStretch]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {activeStretch && (
        <div className="fixed inset-0 z-[100] bg-indigo-900/95 flex flex-col items-center justify-center p-10 text-center animate-in fade-in duration-500">
          <div className="bg-slate-900 p-12 rounded-[3rem] border-4 border-indigo-500 shadow-[0_0_50px_rgba(99,102,241,0.5)] max-w-2xl w-full">
            <Timer className="w-20 h-20 text-indigo-400 mb-6 mx-auto animate-pulse" />
            <h2 className="text-5xl font-black mb-4 uppercase tracking-tighter">
              {activeStretch === "vision_recovery" ? "Look Away!" : "Movement Break"}
            </h2>
            <div className="text-2xl font-medium text-slate-300 mb-10 leading-relaxed">
              {activeStretch === "vision_recovery" 
                ? "Look at something 20 feet away to rest your eyes." 
                : activeStretch === "thoracic_extension"
                ? "Perform a thoracic extension: stretch your mid-back over your chair."
                : activeStretch === "vertical_gaze_neutralizer"
                ? "Neck Reset: Look down and gently tuck your chin to neutralize vertical strain."
                : activeStretch === "standing_backbend"
                ? "Standing Backbend: Place hands on hips and lean back slightly to reset your spine."
                : "Take a deep breath and realign your spine."}
            </div>
            <div className="text-8xl font-black text-white tabular-nums">{stretchTimer}s</div>
            <button onClick={() => setActiveStretch(null)} className="mt-10 text-slate-500 hover:text-white transition-colors uppercase text-sm font-bold tracking-widest">
              Skip Break
            </button>
          </div>
        </div>
      )}

      {nudge && !activeStretch && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-rose-600 text-white p-4 text-center font-bold text-xl animate-bounce shadow-2xl flex items-center justify-center gap-4">
          <AlertCircle className="w-8 h-8" /> {nudge}
        </div>
      )}

      <header className="max-w-7xl mx-auto flex justify-between items-center mb-10">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg shadow-lg shadow-indigo-500/20">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Posture-Sense</h1>
            <div className="flex items-center gap-2 text-orange-500 text-xs font-bold uppercase tracking-widest mt-1">
              <Flame className="w-3 h-3 fill-current" /> {stats.streak} DAY STREAK
            </div>
          </div>
        </div>
        <div className="flex gap-4">
          <Link href="/corporate" className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg transition-all border border-slate-700 text-slate-300">
            <BarChart3 className="w-4 h-4 text-indigo-400" /> Analytics
          </Link>
          <button onClick={handleTogglePrivacy} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all border ${privacyActive ? 'bg-rose-600 border-rose-500 text-white' : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'}`}>
            {privacyActive ? <ShieldOff className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
            {privacyActive ? 'Privacy Active' : 'Privacy Shield'}
          </button>
          <button onClick={() => setSoundEnabled(!soundEnabled)} className={`p-2 rounded-lg border transition-all ${soundEnabled ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-400' : 'bg-slate-800 border-slate-700 text-slate-500'}`}>
            {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
          </button>
          <button onClick={handleToggleMirror} className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg transition-all border border-slate-700">
            <Maximize2 className="w-4 h-4" /> Mirror
          </button>
          <button onClick={handleCalibrate} className={`flex items-center gap-2 px-6 py-2 rounded-lg font-semibold transition-all shadow-lg ${calibrating ? 'bg-indigo-900 cursor-wait' : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-500/20'}`}>
            <RefreshCw className={`w-4 h-4 ${calibrating ? 'animate-spin' : ''}`} />
            {calibrating ? 'Calibrating...' : 'Calibrate'}
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 backdrop-blur-sm relative group">
              <h3 className="text-sm font-semibold text-slate-500 mb-2 uppercase tracking-wider">Live Tracker</h3>
              {privacyActive ? (
                <div className="w-full aspect-video bg-slate-950 rounded-xl flex flex-col items-center justify-center border border-slate-800 text-slate-500 gap-4">
                  <ShieldOff className="w-16 h-16 opacity-20" />
                  <p className="font-bold uppercase tracking-widest text-xs">Camera Access Blocked</p>
                </div>
              ) : (
                <PostureCanvas onData={setData} />
              )}
              {!privacyActive && (
                <div className="absolute bottom-8 right-8 bg-slate-900/90 p-3 rounded-full border border-slate-700 shadow-2xl transition-all group-hover:scale-110">
                  <PostureAvatar score={score} />
                </div>
              )}
            </div>

            <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 backdrop-blur-sm flex flex-col">
              <h3 className="text-sm font-semibold text-slate-500 mb-2 uppercase tracking-wider">Workspace Geometry</h3>
              <WorkspaceVisualizer data={data} />
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-8 gap-4">
            <MetricCard icon={<Activity className="text-blue-400" />} label="Mode" value={isStanding ? "Standing" : "Sitting"} />
            <MetricCard icon={<Maximize2 className="text-emerald-400" />} label="Distance" value={`${distance}cm`} />
            <MetricCard icon={<Monitor className="text-orange-400" />} label="Angle" value={`${angle}°`} />
            <MetricCard icon={<Compass className={`transition-colors ${cva < 50 ? 'text-rose-500' : 'text-indigo-400'}`} />} label="CVA" value={`${Math.round(cva)}°`} />
            <MetricCard icon={<Thermometer className={`transition-colors ${protractionScore < 70 ? 'text-rose-500' : 'text-emerald-400'}`} />} label="Shoulders" value={`${Math.round(protractionScore)}%`} />
            <MetricCard icon={<ArrowUpCircle className={`transition-colors ${lateralLeanScore < 75 ? 'text-rose-500' : 'text-blue-400'}`} />} label="Symmetry" value={`${Math.round(lateralLeanScore)}%`} />
            <MetricCard icon={<Keyboard className={`transition-colors ${typingScore < 70 ? 'text-rose-500' : 'text-emerald-400'}`} />} label="Typing" value={`${typingScore}%`} />
            <MetricCard icon={<Activity className={`transition-colors ${blinkRate < 10 ? 'text-rose-500 animate-pulse' : 'text-indigo-400'}`} />} label="Blinks" value={`${blinkRate}/m`} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FatigueForecast prediction={stats.fatigue_prediction} />
            
            {/* Track 019: Transition Advisor */}
            <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <RefreshCw className={`w-5 h-5 ${stats.transition_data?.remaining_minutes < 5 ? 'text-orange-400 animate-spin-slow' : 'text-indigo-400'}`} />
                  <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Transition Advisor</h3>
                </div>
                {stats.recovery_boost > 0 && (
                  <div className="bg-emerald-500/10 text-emerald-500 text-[10px] font-bold px-2 py-0.5 rounded border border-emerald-500/20">
                    +{stats.recovery_boost}% RECOVERY BOOST
                  </div>
                )}
              </div>
              
              {stats.transition_data?.current_mode ? (
                <div className="space-y-4">
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Time {stats.transition_data.current_mode === 'sitting' ? 'Seated' : 'Standing'}</p>
                      <p className="text-2xl font-black">{Math.round(stats.transition_data.duration_minutes)}m <span className="text-sm text-slate-500 font-normal">/ {Math.round(stats.transition_data.limit_minutes)}m limit</span></p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-400 mb-1">Remaining</p>
                      <p className={`text-xl font-bold ${stats.transition_data.remaining_minutes < 5 ? 'text-orange-400' : 'text-slate-200'}`}>{Math.round(stats.transition_data.remaining_minutes)}m</p>
                    </div>
                  </div>
                  <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-1000 ${stats.transition_data.remaining_minutes < 5 ? 'bg-orange-500' : 'bg-indigo-500'}`} 
                      style={{ width: `${Math.min(100, (stats.transition_data.duration_minutes / stats.transition_data.limit_minutes) * 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs font-medium text-slate-300 italic">
                    {stats.transition_data.recommendation}
                  </p>
                </div>
              ) : (
                <p className="text-sm text-slate-500 italic">Calibrating transition model...</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-indigo-600/10 border border-indigo-500/20 p-4 rounded-xl flex items-center gap-4">
              <div className="bg-indigo-500/20 p-2 rounded-lg text-indigo-400"><Target className="w-6 h-6" /></div>
              <div>
                <div className="text-[10px] text-indigo-300/60 font-bold uppercase">Daily Goal</div>
                <div className="text-lg font-bold text-indigo-200">{stats.today_ergonomic_minutes}/60 <span className="text-xs font-normal">min</span></div>
              </div>
            </div>
            <div className="bg-emerald-600/10 border border-emerald-500/20 p-4 rounded-xl flex items-center gap-4">
              <div className="bg-emerald-500/20 p-2 rounded-lg text-emerald-400"><Activity className="w-6 h-6" /></div>
              <div>
                <div className="text-[10px] text-emerald-300/60 font-bold uppercase">Today's Avg</div>
                <div className="text-lg font-bold text-emerald-200">{stats.today_avg_score}%</div>
              </div>
            </div>
            <div className="bg-amber-600/10 border border-amber-500/20 p-4 rounded-xl flex items-center gap-4">
              <div className="bg-amber-500/20 p-2 rounded-lg text-amber-400"><Flame className="w-6 h-6" /></div>
              <div>
                <div className="text-[10px] text-amber-300/60 font-bold uppercase">All-Time</div>
                <div className="text-lg font-bold text-amber-200">{stats.total_ergonomic_minutes} <span className="text-xs font-normal">min</span></div>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            {data?.environment?.recommendations?.map((rec: string, idx: number) => (
              <div key={idx} className="p-3 bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 rounded-xl flex items-center gap-3 animate-in slide-in-from-left duration-300">
                <Monitor className="w-5 h-5 text-indigo-400" />
                <span className="font-semibold text-sm">{rec}</span>
              </div>
            ))}
            {eyeStrainWarning && (
              <div className="p-3 bg-amber-500/10 border border-amber-500/30 text-amber-400 rounded-xl flex items-center gap-3">
                <AlertCircle className="w-5 h-5" />
                <span className="font-semibold">{eyeStrainWarning}</span>
              </div>
            )}
            <div className={`p-4 rounded-xl border flex items-center gap-4 transition-all duration-500 ${placementSuggestion.includes("Perfect") ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-orange-500/10 border-orange-500/30 text-orange-400'}`}>
              {placementSuggestion.includes("Perfect") ? <CheckCircle2 className="w-6 h-6" /> : <AlertCircle className="w-6 h-6" />}
              <span className="font-semibold text-lg">{placementSuggestion}</span>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-xl flex flex-col items-center text-center">
            <h2 className="text-xl font-medium text-slate-400 mb-6">Ergonomic Score</h2>
            <div className="relative mb-6">
               <svg className="w-48 h-48 transform -rotate-90">
                <circle cx="96" cy="96" r="88" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-slate-800" />
                <circle cx="96" cy="96" r="88" stroke="currentColor" strokeWidth="12" fill="transparent" strokeDasharray={552.92} strokeDashoffset={552.92 - (552.92 * score) / 100} className={`transition-all duration-500 ease-out ${score > 85 ? 'text-emerald-500' : score > 65 ? 'text-yellow-500' : 'text-rose-500'}`} />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center"><span className="text-5xl font-bold">{Math.round(score)}%</span></div>
            </div>
            <p className={`text-lg font-medium px-4 py-2 rounded-full ${score > 85 ? 'bg-emerald-500/10 text-emerald-400' : score > 65 ? 'bg-yellow-500/10 text-yellow-400' : 'bg-rose-500/10 text-rose-400'}`}>
              {score > 85 ? 'Excellent Alignment' : score > 65 ? 'Needs Adjustment' : 'Critical Strain'}
            </p>
          </div>

          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2"><Activity className="w-5 h-5 text-indigo-400" /> Posture Feedback</h3>
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 min-h-[80px] flex items-center text-slate-300 leading-relaxed">{feedback}</div>
          </div>

          <PostureTrends />

          {/* Track 008: Privacy Settings */}
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <h3 className="text-sm font-semibold text-slate-500 mb-4 uppercase tracking-wider flex items-center gap-2">
              <Shield className="w-4 h-4" /> Privacy Controls
            </h3>
            <button 
              onClick={async () => {
                if (confirm("Are you sure? This will permanently delete all your posture history.")) {
                  const res = await fetch('http://127.0.0.1:8000/api/delete-all-data', { method: 'DELETE' });
                  if ((await res.json()).success) alert("All data deleted.");
                }
              }}
              className="w-full py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-bold rounded-lg border border-rose-500/20 transition-all"
            >
              Delete All My Data
            </button>
            <p className="mt-4 text-[10px] text-slate-600 text-center leading-relaxed">
              All processing is local. View our <a href="#" className="underline">Privacy Policy</a>.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

function PostureAvatar({ score }: { score: number }) {
  if (score > 85) return <Smile className="w-10 h-10 text-emerald-400 animate-pulse" />;
  if (score > 65) return <Meh className="w-10 h-10 text-amber-400" />;
  return <Frown className="w-10 h-10 text-rose-500 animate-bounce" />;
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

function WorkspaceVisualizer({ data }: { data: any }) {
  if (!data?.workspace || !data?.workspace.monitors) return (
    <div className="flex-1 flex items-center justify-center text-slate-600 italic text-sm">Awaiting workspace data...</div>
  );

  const { workspace, window, ess } = data;
  const { monitors, bounds, webcam } = workspace;
  
  const scale = 200 / Math.max(bounds.width, bounds.height);
  const offsetX = -bounds.min_x * scale;
  const offsetY = -bounds.min_y * scale;

  return (
    <div className="flex-1 flex flex-col items-center justify-center py-4">
      <div className="relative bg-slate-800 rounded border-2 border-slate-700 shadow-inner" style={{ width: bounds.width * scale, height: bounds.height * scale }}>
        {monitors.map((m: any) => (
          <div key={m.id} className="absolute border border-slate-500 bg-slate-700/40 flex items-center justify-center text-[8px] font-bold text-slate-400 overflow-hidden"
            style={{ left: offsetX + m.x * scale, top: offsetY + m.y * scale, width: m.width * scale, height: m.height * scale }}>
            M{m.id}
          </div>
        ))}
        {window && (
          <div className="absolute bg-indigo-500/50 border border-indigo-400 shadow-[0_0_8px_rgba(99,102,241,0.5)] transition-all duration-300 rounded-sm z-10"
            style={{ left: offsetX + window.x * scale, top: offsetY + window.y * scale, width: window.width * scale, height: window.height * scale }}>
            <div className="w-full h-full flex items-center justify-center overflow-hidden px-1"><span className="text-[6px] font-medium text-white truncate">{window.title}</span></div>
          </div>
        )}
        {monitors[webcam?.anchor_monitor_index] && (
          <div className="absolute w-2 h-1 bg-red-500 rounded-full shadow-[0_0_5px_red] z-20"
            style={{ left: offsetX + (monitors[webcam.anchor_monitor_index].x + monitors[webcam.anchor_monitor_index].width * webcam.offset_x_pct) * scale - 4,
                     top: offsetY + (monitors[webcam.anchor_monitor_index].y + webcam.offset_y_px) * scale - 2 }} />
        )}
        {ess && (
          <div className="absolute left-0 right-0 border-t-2 border-dotted border-emerald-400/80 z-30 pointer-events-none"
            style={{ top: offsetY + ess.target_y * scale }}>
            <div className="absolute -top-3 right-1 text-[7px] text-emerald-400 font-bold uppercase tracking-tighter bg-slate-900 px-1 rounded-sm">Target</div>
          </div>
        )}
      </div>
      <p className="mt-4 text-[10px] text-slate-500 font-medium uppercase tracking-widest">Workspace Model</p>
    </div>
  );
}
