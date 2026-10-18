import React from 'react';
import { AlertOctagon } from 'lucide-react';
import { AndroidStatusBar } from '../components/AndroidStatusBar';
import { NetworkMap } from '../components/NetworkMap';

interface EmergencyActiveScreenProps {
  onArrived: () => void;
  onReportBlockedRoad: () => void;
}

export const EmergencyActiveScreen: React.FC<EmergencyActiveScreenProps> = ({
  onArrived,
  onReportBlockedRoad,
}) => {
  const waypoints = [
    { id: 'J7', time: '120m', status: 'cleared' },
    { id: 'J3', time: '0:35', status: 'cleared' },
    { id: 'J4', time: '1:40', status: 'active' },
    { id: 'J5', time: '3:10', status: 'upcoming' },
    { id: 'H', time: '8:12', status: 'destination' },
  ];

  return (
    <div className="flex-1 flex flex-col bg-slate-50 select-none overflow-hidden">
      {/* Top Bar with Green Corridor Active Banner */}
      <div className="bg-white border-b border-slate-100">
        <AndroidStatusBar theme="light" />
        
        <div className="px-4 pb-2.5">
          <div className="bg-emerald-600 text-white rounded-xl px-3 py-1.5 flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-white animate-ping" />
              <span className="text-xs font-mono font-bold tracking-tight">
                GREEN CORRIDOR ACTIVE
              </span>
            </div>
            <span className="text-[10px] font-mono font-semibold bg-emerald-700/80 px-2 py-0.5 rounded-full">
              2 / 6 cleared
            </span>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col p-4 gap-3 overflow-y-auto phone-scroll">
        {/* Authoritative Corridor Map */}
        <NetworkMap mode="emergency_active" height={220} />

        {/* Live Speed & ETA Telemetry Card */}
        <div className="card-android p-3.5 flex flex-col gap-3">
          <div className="flex items-start justify-between pb-2 border-b border-slate-100">
            <div>
              <div className="flex items-baseline gap-1.5">
                <span className="font-heading text-3xl font-extrabold text-red-600">8 min</span>
                <span className="text-xs text-slate-500 font-medium">to City Hospital</span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">6.2 km total distance</p>
            </div>

            <div className="text-right">
              <span className="font-heading text-xl font-black text-slate-900 block leading-tight">
                48 km/h
              </span>
              <span className="text-[10px] text-slate-400 uppercase font-semibold">
                current speed
              </span>
            </div>
          </div>

          {/* Sub-bar next signal & grace hold */}
          <div className="flex items-center justify-between text-xs bg-slate-50 rounded-xl px-3 py-1.5 border border-slate-200/60 font-medium">
            <span className="text-slate-700">Next: <strong className="text-slate-900 font-bold">J7 - 120 m</strong></span>
            <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md font-mono text-[10px]">
              Grace hold - 20 s
            </span>
          </div>

          {/* Waypoints progression */}
          <div className="flex items-center justify-between gap-1 overflow-x-auto py-1">
            {waypoints.map((wp) => (
              <div
                key={wp.id}
                className={`flex-1 p-1.5 rounded-lg text-center flex flex-col items-center border ${
                  wp.status === 'cleared'
                    ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                    : wp.status === 'active'
                    ? 'bg-red-50 border-red-400 text-red-700 font-bold shadow-sm'
                    : wp.status === 'destination'
                    ? 'bg-blue-50 border-blue-300 text-blue-800 font-bold'
                    : 'bg-slate-50 border-slate-200 text-slate-500'
                }`}
              >
                <span className="text-[10px] font-mono">{wp.id}</span>
                <span className="text-[9px] font-mono opacity-80">{wp.time}</span>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-2 pt-1">
            <button
              onClick={onReportBlockedRoad}
              className="btn-secondary text-xs py-2.5"
            >
              <AlertOctagon className="w-3.5 h-3.5 text-amber-500" />
              Report blocked road
            </button>
            <button
              onClick={onArrived}
              className="btn-orange text-xs py-2.5 font-bold"
            >
              Arrived
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
