"use client";

import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend, PieChart, Pie, Cell } from 'recharts';
import { ArrowLeft, Users, Shield, TrendingUp, AlertTriangle, CheckCircle2, Building2, Search } from 'lucide-react';
import Link from 'next/link';

export default function FleetDashboard() {
  // Mock Team Data
  const teamData = [
    { name: 'Engineering', avgScore: 88, risk: 'Low', headcount: 24, compliance: 92 },
    { name: 'Design', avgScore: 82, risk: 'Low', headcount: 12, compliance: 85 },
    { name: 'Marketing', avgScore: 74, risk: 'Medium', headcount: 18, compliance: 70 },
    { name: 'Sales', avgScore: 68, risk: 'Medium', headcount: 30, compliance: 62 },
    { name: 'Operations', avgScore: 91, risk: 'Low', headcount: 8, compliance: 95 },
  ];

  const chartData = [
    { day: 'Mon', Engineering: 85, Design: 80, Marketing: 72, Sales: 65 },
    { day: 'Tue', Engineering: 88, Design: 82, Marketing: 75, Sales: 68 },
    { day: 'Wed', Engineering: 82, Design: 78, Marketing: 70, Sales: 62 },
    { day: 'Thu', Engineering: 90, Design: 85, Marketing: 78, Sales: 70 },
    { day: 'Fri', Engineering: 86, Design: 81, Marketing: 74, Sales: 66 },
  ];

  const distributionData = [
    { name: 'Healthy (85+)', value: 45, color: '#10b981' },
    { name: 'Caution (70-85)', value: 35, color: '#f59e0b' },
    { name: 'At Risk (<70)', value: 20, color: '#ef4444' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-12">
        <div className="flex items-center gap-6">
          <Link href="/corporate" className="p-2 bg-slate-900 rounded-lg border border-slate-800 hover:bg-slate-800 transition-colors">
            <ArrowLeft className="w-5 h-5 text-slate-400" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
              <Building2 className="w-8 h-8 text-indigo-500" />
              Fleet Wellness Management
            </h1>
            <p className="text-slate-500 text-sm mt-1">Anonymous aggregated insights for organizational health.</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 rounded-lg flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase">
            <Shield className="w-4 h-4" /> 100% Anonymous Mode
          </div>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input type="text" placeholder="Search teams..." className="bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64" />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto space-y-8">
        {/* Org KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Org Average Score</p>
            <div className="flex items-end justify-between">
              <h4 className="text-2xl font-bold">81%</h4>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500">+1.2%</span>
            </div>
          </div>
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Total Users</p>
            <div className="flex items-end justify-between">
              <h4 className="text-2xl font-bold">92</h4>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400">Steady</span>
            </div>
          </div>
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">High Risk Cases</p>
            <div className="flex items-end justify-between">
              <h4 className="text-2xl font-bold text-rose-400">12</h4>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/10 text-rose-500">-2</span>
            </div>
          </div>
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Compliance Rate</p>
            <div className="flex items-end justify-between">
              <h4 className="text-2xl font-bold">78%</h4>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500">+5%</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Team Trends */}
          <div className="lg:col-span-2 bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-400" /> Team Score Trends (Last 7 Days)
            </h3>
            <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="day" stroke="#475569" fontSize={12} />
                  <YAxis domain={[0, 100]} stroke="#475569" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="Engineering" stroke="#6366f1" strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="Design" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="Marketing" stroke="#f59e0b" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="Sales" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Org Distribution */}
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6 flex items-center gap-2">
              <Users className="w-4 h-4 text-emerald-400" /> Organizational Risk Distribution
            </h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={distributionData}
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {distributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-6 p-4 bg-slate-950 rounded-xl border border-slate-800">
               <div className="flex items-center gap-3 text-amber-400 mb-2">
                 <AlertTriangle className="w-4 h-4" />
                 <span className="text-xs font-bold uppercase tracking-wider">Manager Insight</span>
               </div>
               <p className="text-xs text-slate-400 leading-relaxed">
                 The Sales team shows a consistent 15% drop in posture scores after 3 PM. Recommended intervention: Scheduled team stretch at 2:45 PM.
               </p>
            </div>
          </div>
        </div>

        {/* Team Table */}
        <div className="bg-slate-900/50 rounded-2xl border border-slate-800 backdrop-blur-sm overflow-hidden">
          <div className="p-6 border-b border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Departmental Breakdown</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/50 text-slate-500 uppercase text-[10px] font-bold tracking-widest">
                <tr>
                  <th className="px-6 py-4">Department</th>
                  <th className="px-6 py-4">Avg Score</th>
                  <th className="px-6 py-4">Risk Level</th>
                  <th className="px-6 py-4">Headcount</th>
                  <th className="px-6 py-4">Compliance</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {teamData.map((team) => (
                  <tr key={team.name} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-300">{team.name}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span className="font-bold">{team.avgScore}%</span>
                        <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div className={`h-full ${team.avgScore > 85 ? 'bg-emerald-500' : team.avgScore > 75 ? 'bg-amber-500' : 'bg-rose-500'}`} style={{ width: `${team.avgScore}%` }}></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase ${team.risk === 'Low' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}`}>
                        {team.risk}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-400">{team.headcount} users</td>
                    <td className="px-6 py-4 text-slate-300">{team.compliance}%</td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-indigo-400 hover:text-indigo-300 font-bold text-xs uppercase tracking-widest">Generate Report</button>
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
