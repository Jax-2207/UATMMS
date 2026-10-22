import React from 'react';


export const AdminOverviewPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Administration Overview</h1>
          <p className="text-slate-400 text-sm">System health · devices · AI models · audit</p>
        </div>
        <input
          type="text"
          placeholder="Search junction, vehicle…"
          className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm w-64"
        />
      </div>

      {/* Top KPIs */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="text-slate-400 text-xs mb-4">System uptime (30 d)</div>
          <div className="text-4xl font-bold text-emerald-500">99.98%</div>
          <div className="text-xs text-emerald-400 mt-2">Target ≥ 99.9%</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="text-slate-400 text-xs mb-4">Junctions under control</div>
          <div className="text-4xl font-bold text-emerald-500">24 / 24</div>
          <div className="text-xs text-emerald-400 mt-2">0 in fallback mode</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="text-slate-400 text-xs mb-4">Cameras online</div>
          <div className="text-4xl font-bold text-orange-500">126 / 128</div>
          <div className="text-xs text-orange-400 mt-2">2 need maintenance</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="text-slate-400 text-xs mb-4">Emergency corridors today</div>
          <div className="text-4xl font-bold text-emerald-500">17</div>
          <div className="text-xs text-emerald-400 mt-2">Avg. 3.4 min saved (demo)</div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Subsystem Health */}
        <div className="col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="font-semibold mb-4">Subsystem Health</h3>
          <div className="space-y-3">
            {[
              { name: 'Perception · YOLO + DeepSORT', detail: '84 ms / frame', status: 'Healthy' },
              { name: 'Prediction · XGBoost / LSTM', detail: 'MAE 3.1 veh', status: 'Healthy' },
              { name: 'Network optimizer', detail: '1.2 s / cycle', status: 'Healthy' },
              { name: 'Safety & fallback engine', detail: '0 violations', status: 'Healthy' },
              { name: 'Signal controller gateway', detail: '24 / 24 linked', status: 'Healthy' },
              { name: 'Emergency GPS ingest', detail: '3.1 s delay', status: 'Degraded' },
              { name: 'Database & cloud', detail: 'Replica lag 120 ms', status: 'Healthy' },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <div className="text-sm font-medium">{item.name}</div>
                  <div className="text-xs text-slate-400">{item.detail}</div>
                </div>
                <span className={`text-xs font-bold px-3 py-1 rounded-full ${
                  item.status === 'Healthy' 
                    ? 'bg-emerald-500/20 text-emerald-400' 
                    : 'bg-orange-500/20 text-orange-400'
                }`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Device Fleet */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="font-semibold mb-4">Device Fleet</h3>
          <div className="space-y-3">
            <div className="p-3 bg-slate-800/50 rounded-lg">
              <div className="text-xs text-slate-400">CCTV cameras</div>
              <div className="text-2xl font-bold mt-1">126 / 128</div>
            </div>
            <div className="p-3 bg-slate-800/50 rounded-lg">
              <div className="text-xs text-slate-400">Road sensors</div>
              <div className="text-2xl font-bold mt-1">212 / 220</div>
            </div>
            <div className="p-3 bg-slate-800/50 rounded-lg">
              <div className="text-xs text-slate-400">Signal controllers</div>
              <div className="text-2xl font-bold mt-1">24 / 24</div>
            </div>
            <div className="p-3 bg-slate-800/50 rounded-lg">
              <div className="text-xs text-slate-400">Emergency GPS units</div>
              <div className="text-2xl font-bold mt-1">38 / 40</div>
            </div>
            <button className="w-full mt-4 bg-orange-600 text-white font-bold py-2 rounded-lg hover:bg-orange-700 text-sm">
              + Register device
            </button>
          </div>
        </div>

        {/* Audit Log */}
        <div className="col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Recent Audit Log</h3>
            <button className="text-orange-500 text-xs font-bold">View all</button>
          </div>
          <div className="space-y-2">
            {[
              '10:21 S. Patil verified incident at J12',
              '10:14 Corridor #A1 created (8 min ETA)',
              '10:02 P. Kulkarni approved J7 timing +10 s',
              '09:47 Model v2.3 prediction retrained',
              '09:30 Safety policy: min green 10 s unchanged',
              '09:12 New user invited: Sneha More',
            ].map((log, idx) => (
              <div key={idx} className="text-sm text-slate-300 py-2 border-b border-slate-800/50 last:border-0">
                {log}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
