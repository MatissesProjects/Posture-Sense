"use client";

import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell } from 'recharts';

export default function PostureTrends() {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/history?limit=100');
        const data = await res.json();
        // Reverse to show oldest to newest in chart
        setHistory(data.reverse());
      } catch (err) {
        console.error('Failed to fetch history', err);
      }
    };

    fetchHistory();
    const interval = setInterval(fetchHistory, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  // Calculate Distribution
  const neutral = history.filter(h => h.score >= 85).length;
  const lowRisk = history.filter(h => h.score < 85 && h.score >= 65).length;
  const highRisk = history.filter(h => h.score < 65).length;

  const pieData = [
    { name: 'Neutral', value: neutral, color: '#10b981' },
    { name: 'Low Risk', value: lowRisk, color: '#f59e0b' },
    { name: 'High Risk', value: highRisk, color: '#ef4444' }
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6">
      <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <h3 className="text-sm font-semibold text-slate-500 mb-6 uppercase tracking-wider">Score Trend (Last 100 Entries)</h3>
        <div className="h-[200px] w-full">
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
              <YAxis domain={[0, 100]} hide />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Area type="monotone" dataKey="score" stroke="#6366f1" fillOpacity={1} fill="url(#colorScore)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <h3 className="text-sm font-semibold text-slate-500 mb-4 uppercase tracking-wider">Posture Distribution</h3>
        <div className="flex items-center justify-between">
          <div className="h-[150px] w-1/2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  innerRadius={40}
                  outerRadius={60}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="w-1/2 space-y-2">
            {pieData.map(d => (
              <div key={d.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: d.color }}></div>
                  <span className="text-slate-400">{d.name}</span>
                </div>
                <span className="font-bold">{Math.round((d.value / history.length) * 100)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
