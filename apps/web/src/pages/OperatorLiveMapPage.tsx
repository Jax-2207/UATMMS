import React, { useState } from 'react';


export const OperatorLiveMapPage: React.FC = () => {
  const [mode, setMode] = useState<'Traffic' | 'Signals' | 'Cameras' | 'Incidents' | 'Emergency'>('Traffic');
  const [selectedJunction] = useState('J7');

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Live Traffic Control Center</h1>
          <p className="text-slate-400 text-xs">Kolhapur City Network · 24 intersections · 128 cameras</p>
        </div>
        <input
          type="text"
          placeholder="Search junction, vehicle…"
          className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm w-64"
        />
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        {/* Network Overview */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="text-xs font-semibold text-slate-400 mb-4">Network Overview</h3>
          <div className="space-y-2">
            <div>
              <div className="text-xs text-slate-400">Intersections</div>
              <div className="text-2xl font-bold">24</div>
            </div>
            <div>
              <div className="text-xs text-slate-400">Cameras online</div>
              <div className="text-2xl font-bold">126 / 128</div>
            </div>
            <div>
              <div className="text-xs text-slate-400">Vehicles tracked</div>
              <div className="text-2xl font-bold">1,842</div>
            </div>
            <div>
              <div className="text-xs text-slate-400">Network load</div>
              <div className="text-2xl font-bold">72%</div>
            </div>
          </div>
        </div>

        {/* Active Emergencies */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="text-xs font-semibold text-slate-400 mb-4">Active Emergencies</h3>
          <div className="space-y-2">
            <div className="p-2 bg-red-950/20 border border-red-500/20 rounded">
              <div className="text-xs text-red-400 font-bold">Ambulance #A1</div>
              <div className="text-[10px] text-red-300">To City Hospital</div>
              <div className="text-[10px] text-red-200 mt-1">ETA 4 min</div>
            </div>
            <div className="p-2 bg-orange-950/20 border border-orange-500/20 rounded">
              <div className="text-xs text-orange-400 font-bold">Fire Truck #F1</div>
              <div className="text-[10px] text-orange-300">To Fire Incident</div>
              <div className="text-[10px] text-orange-200 mt-1">ETA 7 min</div>
            </div>
          </div>
        </div>

        {/* Active Incidents */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="text-xs font-semibold text-slate-400 mb-4">Active Incidents</h3>
          <div className="p-3 bg-red-950/20 border border-red-500/20 rounded-lg">
            <div className="text-sm font-bold text-red-400">Accident detected</div>
            <div className="text-xs text-red-300 mt-1">Junction J12 · 2 min ago</div>
            <button className="text-xs text-red-400 font-bold mt-2 hover:text-red-300">Verify →</button>
          </div>
        </div>

        {/* System Performance */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="text-xs font-semibold text-slate-400 mb-4">System Performance</h3>
          <div className="space-y-2 text-xs">
            <div>
              <div className="text-slate-400">Avg. waiting</div>
              <div className="font-bold text-emerald-400">28 s ↓ 42%</div>
            </div>
            <div>
              <div className="text-slate-400">Avg. travel</div>
              <div className="font-bold text-emerald-400">6.3 min ↓ 35%</div>
            </div>
            <div>
              <div className="text-slate-400">Throughput</div>
              <div className="font-bold text-emerald-400">3,420 veh/hr ↑ 18%</div>
            </div>
            <div>
              <div className="text-slate-400">Prediction</div>
              <div className="font-bold text-emerald-400">92% accurate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Map Area */}
      <div className="grid grid-cols-3 gap-4">
        {/* Map & Mode Tabs */}
        <div className="col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex gap-2">
              {(['Traffic', 'Signals', 'Cameras', 'Incidents', 'Emergency'] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={`text-xs px-3 py-1.5 rounded-lg transition-all ${
                    mode === m
                      ? 'bg-orange-600 text-white font-bold'
                      : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Map Visualization */}
          <div className="relative w-full h-96 bg-slate-800 rounded-lg border border-slate-700 overflow-hidden flex items-center justify-center">
            <svg viewBox="0 0 400 300" className="w-full h-full">
              {/* Grid */}
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#334155" strokeWidth="0.5" />
                </pattern>
              </defs>
              <rect width="400" height="300" fill="url(#grid)" />

              {/* Roads */}
              <line x1="50" y1="80" x2="350" y2="80" stroke="#475569" strokeWidth="2" />
              <line x1="100" y1="30" x2="100" y2="270" stroke="#475569" strokeWidth="2" />
              <line x1="250" y1="30" x2="250" y2="270" stroke="#475569" strokeWidth="2" />

              {/* Junctions */}
              {[
                { x: 100, y: 80, label: 'J7', status: 'active' },
                { x: 250, y: 80, label: 'J4', status: 'normal' },
                { x: 100, y: 150, label: 'J8', status: 'normal' },
                { x: 250, y: 150, label: 'J3', status: 'normal' },
              ].map((j) => (
                <g key={j.label}>
                  <circle cx={j.x} cy={j.y} r="6" fill={j.status === 'active' ? '#22c55e' : '#94a3b8'} />
                  <text x={j.x + 12} y={j.y + 4} fontSize="10" fill="#e2e8f0" fontWeight="bold">
                    {j.label}
                  </text>
                </g>
              ))}

              {/* Corridor Path */}
              <path
                d="M 100 80 L 100 150 L 250 150 L 250 80"
                stroke="#22c55e"
                strokeWidth="3"
                fill="none"
                strokeDasharray="5,5"
              />

              {/* Hospital */}
              <rect x="320" y="60" width="30" height="30" fill="#3b82f6" rx="2" />
              <text x="325" y="85" fontSize="10" fill="white" fontWeight="bold" textAnchor="middle">
                H
              </text>
            </svg>
          </div>

          <p className="text-xs text-slate-400 mt-4">
            <span className="font-semibold">System Mode:</span>
            <span className="ml-2">
              <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded">Normal</span>
            </span>
          </p>
        </div>

        {/* Selected Junction Inspector */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold">Selected Junction · {selectedJunction}</h3>
            <button className="text-xs text-slate-400 hover:text-white">×</button>
          </div>

          {/* Current Status */}
          <div className="space-y-3">
            <div>
              <div className="text-xs text-slate-400">Current status</div>
              <div className="text-sm font-bold text-emerald-400 mt-1">Green (28s left)</div>
            </div>

            <div>
              <div className="text-xs text-slate-400">Next phase</div>
              <div className="text-sm font-bold mt-1">Yellow (5s) → Red (42s)</div>
            </div>

            <div>
              <div className="text-xs text-slate-400">Traffic density</div>
              <div className="text-sm font-bold mt-1">High · 78 veh/min</div>
            </div>

            <div>
              <div className="text-xs text-slate-400">Queue length</div>
              <div className="text-sm font-bold mt-1">24 vehicles</div>
            </div>

            <div>
              <div className="text-xs text-slate-400">Average speed</div>
              <div className="text-sm font-bold mt-1">18 km/h</div>
            </div>

            <div>
              <div className="text-xs text-slate-400">AI recommendation</div>
              <div className="text-sm font-bold text-orange-400 mt-1">Extend green +10s</div>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 space-y-2">
            <button className="w-full bg-emerald-600 text-white font-bold py-2 rounded-lg hover:bg-emerald-700 text-sm">
              Approve
            </button>
            <button className="w-full bg-slate-800 text-slate-300 font-bold py-2 rounded-lg hover:bg-slate-700 text-sm">
              Override
            </button>
          </div>

          {/* Signal Timing */}
          <div className="mt-6 pt-6 border-t border-slate-800">
            <h4 className="text-xs font-semibold text-slate-400 mb-3">Signal Timing (dynamic)</h4>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span>North South</span>
                <span className="font-bold">42s</span>
              </div>
              <div className="flex justify-between">
                <span>East–West</span>
                <span className="font-bold">28s</span>
              </div>
              <div className="flex justify-between">
                <span>Left turn</span>
                <span className="font-bold">15s</span>
              </div>
              <div className="flex justify-between">
                <span>Pedestrian</span>
                <span className="font-bold">12s</span>
              </div>
            </div>
          </div>

          {/* AI Predictions */}
          <div className="mt-6 pt-6 border-t border-slate-800">
            <h4 className="text-xs font-semibold text-slate-400 mb-3">AI Prediction · next 10 min</h4>
            <div className="h-16 bg-slate-800 rounded-lg flex items-center justify-center text-xs text-slate-400">
              Congestion forecast
            </div>
          </div>
        </div>
      </div>

      {/* AI Decisions Log */}
      <div className="mt-4 bg-slate-900 border border-slate-800 rounded-xl p-4">
        <h3 className="font-semibold text-sm mb-3">AI Decisions (live)</h3>
        <div className="space-y-2 text-xs">
          {[
            '10:24:12 Extended green at J6 for Ambulance #A1',
            '10:23:58 Predicted congestion at J12 (accident)',
            '10:23:40 Rerouted 12% traffic to alternate roads',
          ].map((decision, idx) => (
            <div key={idx} className="text-slate-400 py-1 border-b border-slate-800/50 last:border-0">
              {decision}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
