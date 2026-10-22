import React from 'react';
import { Download } from 'lucide-react';

export const AdminAnalyticsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Analytics & Reports</h1>
          <p className="text-slate-400 text-sm">Baseline: fixed-time signals · Treatment: UATMMS (demo data until pilot)</p>
        </div>
        <input
          type="text"
          placeholder="Search junction, vehicle…"
          className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm w-64"
        />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-5 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="text-slate-400 text-xs mb-4">Avg. waiting time</div>
          <div className="text-4xl font-bold text-orange-500">↓ 42%</div>
          <div className="text-xs text-slate-400 mt-2">28 s vs 48 s</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="text-slate-400 text-xs mb-4">Avg. travel time</div>
          <div className="text-4xl font-bold text-orange-500">↓ 35%</div>
          <div className="text-xs text-slate-400 mt-2">6.3 vs 9.7 min</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="text-slate-400 text-xs mb-4">Throughput</div>
          <div className="text-4xl font-bold text-emerald-500">↑ 18%</div>
          <div className="text-xs text-slate-400 mt-2">3,420 veh/hr</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="text-slate-400 text-xs mb-4">Emergency travel time</div>
          <div className="text-4xl font-bold text-orange-500">↓ 38%</div>
          <div className="text-xs text-slate-400 mt-2">8.1 vs 13.1 min</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="text-slate-400 text-xs mb-4">Safety violations</div>
          <div className="text-4xl font-bold text-emerald-500">0</div>
          <div className="text-xs text-slate-400 mt-2">30-day total</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {/* Chart 1: 24-hour waiting time */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 col-span-2">
          <h3 className="font-semibold mb-4 text-sm">Avg. waiting time over 24 h</h3>
          <div className="flex items-end justify-around h-48 bg-slate-800/50 rounded-lg p-4">
            <div className="flex flex-col items-center gap-2">
              <div className="w-8 h-32 bg-slate-700 rounded-t-lg"></div>
              <span className="text-[10px] text-slate-400">Fixed-time</span>
            </div>
            <div className="flex flex-col items-center gap-2">
              <div className="w-8 h-24 bg-orange-600 rounded-t-lg"></div>
              <span className="text-[10px] text-slate-400">Adaptive</span>
            </div>
            <div className="flex flex-col items-center gap-2">
              <div className="w-8 h-16 bg-emerald-600 rounded-t-lg"></div>
              <span className="text-[10px] text-slate-400">UATMMS</span>
            </div>
          </div>
          <div className="flex gap-4 justify-center mt-4 text-xs">
            <div className="flex items-center gap-2"><div className="w-3 h-3 bg-slate-700 rounded"></div>Fixed-time</div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 bg-orange-600 rounded"></div>Adaptive</div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 bg-emerald-600 rounded"></div>UATMMS</div>
          </div>
        </div>

        {/* Chart 2: Weekly Response Time */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="font-semibold mb-4 text-sm">Emergency response time weekly (min)</h3>
          <div className="flex items-end justify-around h-48 bg-slate-800/50 rounded-lg p-4 gap-2">
            {['W1', 'W2', 'W3', 'W4'].map((week) => (
              <div key={week} className="flex-1 flex flex-col items-center gap-2">
                <div className="flex gap-1 w-full">
                  <div className="flex-1 h-20 bg-slate-600 rounded-t-sm"></div>
                  <div className="flex-1 h-32 bg-emerald-600 rounded-t-sm"></div>
                </div>
                <span className="text-[10px] text-slate-400">{week}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Export Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export report
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
            <span className="text-sm">PDF summary</span>
            <button className="text-orange-500 text-xs font-bold hover:text-orange-600">Download ↓</button>
          </div>
          <div className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
            <span className="text-sm">CSV raw data</span>
            <button className="text-orange-500 text-xs font-bold hover:text-orange-600">Download ↓</button>
          </div>
          <div className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
            <span className="text-sm">Pilot comparison</span>
            <button className="text-orange-500 text-xs font-bold hover:text-orange-600">Download ↓</button>
          </div>
        </div>
      </div>
    </div>
  );
};
