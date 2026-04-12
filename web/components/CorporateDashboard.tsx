"use client";

import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, Legend } from 'recharts';
import { ArrowLeft, BarChart3, Calendar, Clock, Download, Filter, LayoutDashboard, TrendingUp, Users } from 'lucide-react';
import Link from 'next/link';
import StrainHeatmaps from './StrainHeatmaps';

export default function CorporateDashboard() {
  const [history, setHistory] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [historyRes, sessionsRes] = await Promise.all([
          fetch('http://127.0.0.1:8000/api/history?limit=500'),
          fetch('http://127.0.0.1:8000/api/sessions?limit=50')
        ]);
        
        const historyData = await historyRes.json();
        const sessionsData = await sessionsRes.json();
        
        setHistory(historyData.reverse());
        setSessions(sessionsData);
      } catch (err) {
        console.error('Failed to fetch data', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <div className="w-12 h-12 bg-indigo-600 rounded-full"></div>
          <p className="text-slate-500 font-medium uppercase tracking-widest text-xs">Loading Analytics...</p>
        </div>
      </div>
    );
  }

  const handleExportPDF = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/generate-report');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `PostureSense_Ergonomic_Report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error('Failed to export PDF', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-12">
        <div className="flex items-center gap-6">
          <Link href="/" className="p-2 bg-slate-900 rounded-lg border border-slate-800 hover:bg-slate-800 transition-colors">
            <ArrowLeft className="w-5 h-5 text-slate-400" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-indigo-500" />
              Corporate Wellness Analytics
            </h1>
            <p className="text-slate-500 text-sm mt-1">High-fidelity ergonomic reporting and trend analysis.</p>
          </div>
        </div>
        <div className="flex gap-3">
           <Link href="/fleet" className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm font-medium hover:bg-slate-800 transition-all">
            <Users className="w-4 h-4 text-indigo-400" /> Fleet View (Mock)
          </Link>
           <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm font-medium hover:bg-slate-800 transition-all">
            <Filter className="w-4 h-4" /> Filter Range
          </button>
          <button 
            onClick={handleExportPDF}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 rounded-lg text-sm font-bold hover:bg-indigo-500 transition-all shadow-lg shadow-indigo-500/20"
          >
            <Download className="w-4 h-4" /> Export PDF Report
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto space-y-8">
        {/* KPI Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <KPICard title="Average Posture Score" value={`${Math.round(history.reduce((acc, h) => acc + h.score, 0) / (history.length || 1))}%`} trend="+2.4%" trendUp={true} />
          <KPICard title="Total Sessions" value={sessions.length.toString()} trend="Steady" trendUp={null} />
          <KPICard title="Ergonomic Minutes" value={sessions.reduce((acc, s) => acc + (s.total_ergonomic_minutes || 0), 0).toString()} trend="+12m" trendUp={true} />
          <KPICard title="Risk Level" value="Low" trend="Improving" trendUp={true} color="text-emerald-400" />
        </div>

        {/* Heatmaps Row */}
        <StrainHeatmaps history={history} />

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Detailed Score Trend */}
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-indigo-400" /> Longitudinal Posture Score
              </h3>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={history}>
                  <defs>
                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="timestamp" hide />
                  <YAxis domain={[0, 100]} stroke="#475569" fontSize={10} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                    itemStyle={{ color: '#e2e8f0' }}
                  />
                  <Area type="monotone" dataKey="score" stroke="#6366f1" fillOpacity={1} fill="url(#colorScore)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* RULA / REBA Scores */}
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <LayoutDashboard className="w-4 h-4 text-emerald-400" /> Ergonomic Assessment (RULA/REBA)
              </h3>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="timestamp" hide />
                  <YAxis domain={[0, 15]} stroke="#475569" fontSize={10} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                  />
                  <Legend verticalAlign="top" height={36}/>
                  <Line type="monotone" dataKey="rula_score" name="RULA Score" stroke="#f59e0b" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="reba_score" name="REBA Score" stroke="#10b981" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

           {/* Blink Rate & Visual Fatigue */}
           <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <Users className="w-4 h-4 text-orange-400" /> Visual Fatigue Metrics (Blink Rate)
              </h3>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={history.slice(-50)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="timestamp" hide />
                  <YAxis stroke="#475569" fontSize={10} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                  />
                  <Bar dataKey="blink_rate" name="Blinks per Minute" fill="#fb923c" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Viewing Geometry */}
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <Clock className="w-4 h-4 text-purple-400" /> Workspace Geometry Trends
              </h3>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="timestamp" hide />
                  <YAxis stroke="#475569" fontSize={10} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                  />
                  <Area type="monotone" dataKey="viewing_angle" name="Viewing Angle (°)" stroke="#a855f7" fill="#a855f7" fillOpacity={0.1} />
                  <Area type="monotone" dataKey="distance_cm" name="Distance (cm)" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Session History Table */}
        <div className="bg-slate-900/50 rounded-2xl border border-slate-800 backdrop-blur-sm overflow-hidden">
          <div className="p-6 border-b border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <Calendar className="w-4 h-4 text-slate-500" /> Historical Sessions
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/50 text-slate-500 uppercase text-[10px] font-bold tracking-widest">
                <tr>
                  <th className="px-6 py-4">Start Time</th>
                  <th className="px-6 py-4">End Time</th>
                  <th className="px-6 py-4">Avg Score</th>
                  <th className="px-6 py-4">Ergo Minutes</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {sessions.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-300">{new Date(s.start_time).toLocaleString()}</td>
                    <td className="px-6 py-4 text-slate-500">{s.end_time ? new Date(s.end_time).toLocaleString() : 'Active'}</td>
                    <td className="px-6 py-4">
                      <span className={`font-bold ${s.avg_score > 85 ? 'text-emerald-400' : s.avg_score > 65 ? 'text-amber-400' : 'text-rose-400'}`}>
                        {Math.round(s.avg_score)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-300">{s.total_ergonomic_minutes} min</td>
                    <td className="px-6 py-4">
                      <div className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase ${s.avg_score > 85 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}`}>
                        {s.avg_score > 85 ? 'Healthy' : 'Moderate'}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-indigo-400 hover:text-indigo-300 font-bold text-xs uppercase tracking-widest">Deep Dive</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

function KPICard({ title, value, trend, trendUp, color = "text-white" }: { title: string, value: string, trend: string, trendUp: boolean | null, color?: string }) {
  return (
    <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">{title}</p>
      <div className="flex items-end justify-between">
        <h4 className={`text-2xl font-bold ${color}`}>{value}</h4>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${trendUp === true ? 'bg-emerald-500/10 text-emerald-500' : trendUp === false ? 'bg-rose-500/10 text-rose-500' : 'bg-slate-800 text-slate-400'}`}>
          {trend}
        </span>
      </div>
    </div>
  );
}
