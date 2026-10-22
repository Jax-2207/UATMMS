import React, { useState } from 'react';
import { Save } from 'lucide-react';

export const SafetyPoliciesPage: React.FC = () => {
  const [toggles, setToggles] = useState({
    autoFallback: true,
    modelConfidence: true,
    failedValidation: true,
    operatorApproval: false,
    twoPersonApproval: false,
  });

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Safety Constraints & Fallback Policy</h1>
          <p className="text-slate-400 text-sm">Hard rules the AI can never override</p>
        </div>
        <input
          type="text"
          placeholder="Search junction, vehicle…"
          className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm w-64"
        />
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Hard Safety Constraints */}
        <div className="col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="font-semibold mb-4 text-emerald-400">Hard Safety Constraints</h3>
          <div className="text-xs text-slate-400 mb-6">Enforced by Safety Engine</div>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="text-sm font-medium mb-2 block">Minimum green time</label>
              <input type="number" value={10} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
              <div className="text-xs text-slate-400 mt-1">seconds</div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Maximum cycle length</label>
              <input type="number" value={120} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
              <div className="text-xs text-slate-400 mt-1">seconds</div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Max corridor pre-emption per junction</label>
              <input type="number" value={45} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
              <div className="text-xs text-slate-400 mt-1">seconds</div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Pedestrian clearance time</label>
              <input type="number" value={12} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
              <div className="text-xs text-slate-400 mt-1">seconds</div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">All-red clearance</label>
              <input type="number" value={2} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
              <div className="text-xs text-slate-400 mt-1">seconds</div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Max cross-traffic delay increase</label>
              <input type="number" value={15} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
              <div className="text-xs text-slate-400 mt-1">%</div>
            </div>
          </div>
        </div>

        {/* Emergency Priority Rules */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="font-semibold mb-4">Policy Status</h3>
          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-400">Policy version</label>
              <div className="text-sm font-bold mt-1 text-orange-500">v1.4 active</div>
            </div>
            <div>
              <label className="text-xs text-slate-400">Last changed</label>
              <div className="text-sm font-bold mt-1">Rahul Deshmukh · 3 days ago</div>
            </div>
            <div>
              <label className="text-xs text-slate-400">Violations (30 d)</label>
              <div className="text-sm font-bold mt-1 text-emerald-400">0</div>
            </div>
            <div>
              <label className="text-xs text-slate-400">Fallback activations (30 d)</label>
              <div className="text-sm font-bold mt-1 text-orange-400">2 (sensor outage)</div>
            </div>
            <button className="w-full mt-6 bg-orange-600 text-white font-bold py-2 rounded-lg hover:bg-orange-700 text-sm flex items-center justify-center gap-2">
              <Save className="w-4 h-4" /> Save & publish v1.5
            </button>
            <button className="w-full bg-slate-800 text-slate-300 font-bold py-2 rounded-lg hover:bg-slate-700 text-sm">
              Discard
            </button>
          </div>
        </div>
      </div>

      {/* Emergency Priority Rules - Full Width */}
      <div className="mt-6 bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="font-semibold mb-4">Emergency Priority Rules</h3>
        <p className="text-xs text-slate-400 mb-6">When multiple emergency vehicles overlap, priority is resolved in this order:</p>

        <div className="space-y-3">
          {[
            { num: 1, text: 'Ambulance · critical patient', icon: '🚑' },
            { num: 2, text: 'Fire truck · active fire', icon: '🚒' },
            { num: 3, text: 'Police escort · VIP / special', icon: '🚨' },
            { num: 4, text: 'Other authorised vehicles', icon: '🚗' },
          ].map((item) => (
            <div key={item.num} className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-lg">
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center font-bold">{item.num}</div>
              <span className="text-sm flex-1">{item.text}</span>
              <span className="text-xl">{item.icon}</span>
              <span className="text-slate-500">⋮⋮</span>
            </div>
          ))}
        </div>
      </div>

      {/* Fallback & Failure Handling */}
      <div className="mt-6 bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="font-semibold mb-6">Fallback & Failure Handling</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
            <span className="text-sm">Auto-fallback to fixed-time on sensor loss</span>
            <div
              className={`w-12 h-6 rounded-full cursor-pointer transition-colors ${
                toggles.autoFallback ? 'bg-emerald-600' : 'bg-slate-700'
              }`}
              onClick={() => setToggles({ ...toggles, autoFallback: !toggles.autoFallback })}
            >
              <div className={`w-5 h-5 rounded-full bg-white transition-transform ${
                toggles.autoFallback ? 'translate-x-6' : 'translate-x-1'
              } mt-0.5`}></div>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
            <span className="text-sm">Fallback when model confidence &lt; 70%</span>
            <div
              className={`w-12 h-6 rounded-full cursor-pointer transition-colors ${
                toggles.modelConfidence ? 'bg-emerald-600' : 'bg-slate-700'
              }`}
              onClick={() => setToggles({ ...toggles, modelConfidence: !toggles.modelConfidence })}
            >
              <div className={`w-5 h-5 rounded-full bg-white transition-transform ${
                toggles.modelConfidence ? 'translate-x-6' : 'translate-x-1'
              } mt-0.5`}></div>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
            <span className="text-sm">Fallback after 3 failed safety validations</span>
            <div
              className={`w-12 h-6 rounded-full cursor-pointer transition-colors ${
                toggles.failedValidation ? 'bg-emerald-600' : 'bg-slate-700'
              }`}
              onClick={() => setToggles({ ...toggles, failedValidation: !toggles.failedValidation })}
            >
              <div className={`w-5 h-5 rounded-full bg-white transition-transform ${
                toggles.failedValidation ? 'translate-x-6' : 'translate-x-1'
              } mt-0.5`}></div>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
            <span className="text-sm">Require operator approval for corridors &gt; 5 junctions</span>
            <div
              className={`w-12 h-6 rounded-full cursor-pointer transition-colors ${
                toggles.operatorApproval ? 'bg-emerald-600' : 'bg-slate-700'
              }`}
              onClick={() => setToggles({ ...toggles, operatorApproval: !toggles.operatorApproval })}
            >
              <div className={`w-5 h-5 rounded-full bg-white transition-transform ${
                toggles.operatorApproval ? 'translate-x-6' : 'translate-x-1'
              } mt-0.5`}></div>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
            <span className="text-sm">Require 2-person approval for manual overrides</span>
            <div
              className={`w-12 h-6 rounded-full cursor-pointer transition-colors ${
                toggles.twoPersonApproval ? 'bg-emerald-600' : 'bg-slate-700'
              }`}
              onClick={() => setToggles({ ...toggles, twoPersonApproval: !toggles.twoPersonApproval })}
            >
              <div className={`w-5 h-5 rounded-full bg-white transition-transform ${
                toggles.twoPersonApproval ? 'translate-x-6' : 'translate-x-1'
              } mt-0.5`}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
