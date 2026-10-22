import React, { useState } from 'react';
import { AlertCircle, Send, MapPin } from 'lucide-react';

export const HospitalCoordinationPage: React.FC = () => {
  const [severity, setSeverity] = useState('Critical');

  return (
    <div className="min-h-screen bg-white p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Emergency Coordination</h1>
          <p className="text-slate-600 text-sm">City Hospital · ER dispatch & arrival readiness</p>
        </div>
        <input
          type="text"
          placeholder="Search junction, vehicle…"
          className="px-4 py-2 rounded-lg bg-slate-100 border border-slate-300 text-sm w-64"
        />
      </div>

      <div className="grid grid-cols-3 gap-8">
        {/* Left: Incoming Ambulances */}
        <div>
          <h2 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600" />
            Incoming Ambulances
            <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">1 active</span>
          </h2>

          <div className="bg-red-50 border-2 border-red-300 rounded-xl p-4 mb-6">
            <h3 className="font-bold text-red-900 mb-4">Ambulance #A1</h3>
            <div className="space-y-3 text-sm">
              <div>
                <div className="text-xs text-red-700 font-semibold">Patient Details</div>
                <div className="text-red-900">Male, ~58 · chest pain · triage: critical</div>
              </div>
              <div>
                <div className="text-xs text-red-700 font-semibold">ETA</div>
                <div className="text-red-900 font-bold">8 min 12 s (live)</div>
              </div>
              <div>
                <div className="text-xs text-red-700 font-semibold">Position</div>
                <div className="text-red-900">Between J7 and J3</div>
              </div>
              <div>
                <div className="text-xs text-red-700 font-semibold">Green corridor</div>
                <div className="text-red-900 font-bold">Active 3 / 6 cleared</div>
              </div>
              <div>
                <div className="text-xs text-red-700 font-semibold">Assigned bay</div>
                <div className="text-red-900 font-bold">ER-2 cardiac team</div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-white rounded-lg border border-red-200">
              <div className="text-xs text-red-700 font-semibold mb-2">ER Readiness for #A1</div>
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2 text-emerald-700">
                  <span className="text-emerald-600">✓</span> Cardiac team alerted
                </div>
                <div className="flex items-center gap-2 text-emerald-700">
                  <span className="text-emerald-600">✓</span> Bay ER 2 cleared
                </div>
                <div className="flex items-center gap-2 text-slate-600">
                  <span className="text-slate-400">○</span> Blood bank notified
                </div>
                <div className="flex items-center gap-2 text-slate-600">
                  <span className="text-slate-400">○</span> Triage nurse at entrance
                </div>
              </div>
            </div>

            <button className="w-full mt-4 bg-orange-600 text-white font-bold py-2 rounded-lg hover:bg-orange-700 text-sm">
              Notify ER team
            </button>
          </div>

          {/* Bed Availability */}
          <div className="bg-slate-50 border border-slate-300 rounded-xl p-4">
            <h3 className="font-bold text-slate-900 mb-4 text-sm">Bed Availability</h3>
            <div className="space-y-3 text-sm">
              <div>
                <div className="flex justify-between text-xs text-slate-600 mb-1">
                  <span>Emergency beds</span>
                  <span className="font-bold text-slate-900">4 / 12 free</span>
                </div>
                <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div className="h-full w-1/3 bg-orange-500 rounded-full"></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs text-slate-600 mb-1">
                  <span>ICU</span>
                  <span className="font-bold text-slate-900">2 / 8 free</span>
                </div>
                <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div className="h-full w-1/4 bg-red-500 rounded-full"></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs text-slate-600 mb-1">
                  <span>Operation theatre</span>
                  <span className="font-bold text-slate-900">1 / 3 free</span>
                </div>
                <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div className="h-full w-1/3 bg-orange-500 rounded-full"></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs text-slate-600 mb-1">
                  <span>Trauma bays</span>
                  <span className="font-bold text-slate-900">2 / 4 free</span>
                </div>
                <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div className="h-full w-1/2 bg-emerald-500 rounded-full"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Center: Request Form & Map */}
        <div>
          {/* Request Form */}
          <h2 className="font-bold text-slate-900 mb-4">Request Ambulance + Green Corridor</h2>

          <div className="bg-slate-50 border border-slate-300 rounded-xl p-4 mb-6 space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-600 block mb-2">Pickup location</label>
              <input
                type="text"
                value="Shivaji Chowk, Kolhapur"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 bg-white"
              />
              <button className="text-xs text-orange-600 font-bold mt-2">Pin</button>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-600 block mb-2">Destination</label>
              <input
                type="text"
                value="City Hospital · ER"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 bg-white"
                readOnly
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-600 block mb-2">Severity</label>
              <div className="flex gap-2">
                {['Critical', 'High', 'Normal'].map((s) => (
                  <button
                    key={s}
                    onClick={() => setSeverity(s)}
                    className={`flex-1 px-3 py-2 rounded-lg text-xs font-bold border transition-colors ${
                      severity === s
                        ? s === 'Critical'
                          ? 'bg-red-100 border-red-600 text-red-700'
                          : 'bg-orange-100 border-orange-600 text-orange-700'
                        : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-600 block mb-2">Patient notes (optional)</label>
              <textarea
                value="Chest pain, conscious"
                rows={3}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 bg-white"
              ></textarea>
            </div>

            <button className="w-full bg-orange-600 text-white font-bold py-3 rounded-lg hover:bg-orange-700 flex items-center justify-center gap-2">
              <Send className="w-4 h-4" />
              Dispatch + create green corridor
            </button>
          </div>

          {/* Live Map */}
          <div className="bg-slate-100 border border-slate-300 rounded-xl p-4 h-64 flex items-center justify-center">
            <div className="text-center">
              <MapPin className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-sm text-slate-600">Live ambulance tracking map</p>
              <p className="text-xs text-slate-500 mt-1">Updated 1 s ago</p>
            </div>
          </div>
        </div>

        {/* Right: Live Tracking */}
        <div>
          <h2 className="font-bold text-slate-900 mb-4">Live ambulance tracking</h2>

          <div className="bg-white border-2 border-slate-300 rounded-xl overflow-hidden mb-6" style={{ height: '400px' }}>
            <svg viewBox="0 0 300 400" className="w-full h-full" style={{ background: '#f8fafc' }}>
              {/* Grid */}
              <defs>
                <pattern id="gridMap" width="30" height="30" patternUnits="userSpaceOnUse">
                  <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#e2e8f0" strokeWidth="0.5" />
                </pattern>
              </defs>
              <rect width="300" height="400" fill="url(#gridMap)" />

              {/* Roads */}
              <line x1="30" y1="100" x2="270" y2="100" stroke="#94a3b8" strokeWidth="3" />
              <line x1="80" y1="30" x2="80" y2="370" stroke="#94a3b8" strokeWidth="3" />
              <line x1="220" y1="30" x2="220" y2="370" stroke="#94a3b8" strokeWidth="3" />

              {/* Route Path (Green Corridor) */}
              <path
                d="M 80 100 L 80 200 L 220 200 L 220 100"
                stroke="#10b981"
                strokeWidth="4"
                fill="none"
                strokeDasharray="8,4"
              />

              {/* Junctions */}
              {[
                { x: 80, y: 100, label: 'J7' },
                { x: 80, y: 200, label: 'J3' },
                { x: 220, y: 200, label: 'J4' },
                { x: 220, y: 100, label: 'J6' },
              ].map((j) => (
                <g key={j.label}>
                  <circle cx={j.x} cy={j.y} r="5" fill="#64748b" stroke="#1e293b" strokeWidth="2" />
                  <text x={j.x + 15} y={j.y + 4} fontSize="12" fill="#0f172a" fontWeight="bold">
                    {j.label}
                  </text>
                </g>
              ))}

              {/* Hospital */}
              <rect x="240" y="80" width="35" height="35" fill="#3b82f6" rx="2" />
              <text x="257.5" y="108" fontSize="16" fill="white" fontWeight="bold" textAnchor="middle">
                H
              </text>
              <text x="257.5" y="125" fontSize="10" fill="#0f172a" textAnchor="middle">
                City Hospital
              </text>

              {/* Ambulance Position */}
              <circle cx="95" cy="140" r="8" fill="#ef4444" stroke="#991b1b" strokeWidth="2" />
              <text x="95" y="165" fontSize="10" fill="#0f172a" textAnchor="middle" fontWeight="bold">
                ETA 4 min
              </text>
            </svg>
          </div>

          {/* Waypoint Timeline */}
          <div className="bg-slate-50 border border-slate-300 rounded-xl p-4">
            <h3 className="font-bold text-slate-900 mb-3 text-sm">Waypoint Timeline</h3>
            <div className="space-y-2">
              {[
                { j: 'J7', time: '1:20', status: 'passed' },
                { j: 'J3', time: '3:05', status: 'current' },
                { j: 'J4', time: '5:10', status: 'next' },
                { j: 'J5', time: '6:40', status: 'upcoming' },
                { j: 'H', time: '8:12', status: 'destination' },
              ].map((wp) => (
                <div key={wp.j} className={`flex items-center gap-3 p-2 rounded-lg text-xs ${
                  wp.status === 'current' 
                    ? 'bg-orange-100 border border-orange-300' 
                    : 'hover:bg-white'
                }`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-white ${
                    wp.status === 'current' ? 'bg-orange-600' :
                    wp.status === 'passed' ? 'bg-emerald-600' :
                    wp.status === 'destination' ? 'bg-blue-600' :
                    'bg-slate-400'
                  }`}>
                    {wp.j}
                  </div>
                  <div className="flex-1">
                    <div className="font-bold text-slate-900">{wp.j}</div>
                    <div className="text-slate-600">{wp.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
