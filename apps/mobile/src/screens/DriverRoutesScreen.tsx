import React, { useState } from 'react';
import { ArrowLeft, Sparkles, Navigation } from 'lucide-react';
import { AndroidStatusBar } from '../components/AndroidStatusBar';
import { NetworkMap } from '../components/NetworkMap';

interface DriverRoutesScreenProps {
  onBack: () => void;
  onStartNavigation: () => void;
}

export const DriverRoutesScreen: React.FC<DriverRoutesScreenProps> = ({
  onBack,
  onStartNavigation,
}) => {
  const [selectedRoute, setSelectedRoute] = useState<number>(0);
  const [navigating, setNavigating] = useState<boolean>(false);

  const routes = [
    {
      title: 'Fastest',
      time: '14 min',
      dist: '5.8 km',
      summary: 'Via J8 → J7 → J8 → J4 • 2 signals likely red',
      color: 'blue'
    },
    {
      title: 'Least congestion',
      time: '17 min',
      dist: '6.4 km',
      summary: 'Avoids J7 heavy queue',
      color: 'slate'
    },
    {
      title: 'Pedestrian-safe',
      time: '19 min',
      dist: '6.9 km',
      summary: 'Longer crossings, fewer turning conflicts',
      color: 'slate'
    }
  ];

  return (
    <div className="flex-1 flex flex-col bg-slate-50 select-none overflow-hidden">
      {/* Top Bar */}
      <div className="bg-white border-b border-slate-100">
        <AndroidStatusBar theme="light" />
        <div className="px-4 pb-3 flex items-center gap-3">
          <button
            onClick={onBack}
            className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-700 active:scale-95"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h2 className="font-heading font-bold text-sm text-slate-900 leading-tight">
              Plan route
            </h2>
            <p className="text-[10px] text-slate-400">
              Smart routing uses live + predicted traffic
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col p-4 gap-3 overflow-y-auto phone-scroll">
        {/* Origin & Destination Inputs */}
        <div className="card-android p-3 flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-semibold text-slate-400 w-10">From</span>
            <div className="flex-1 bg-slate-50 border border-slate-200/80 rounded-xl px-3 py-1.5 text-xs text-slate-800 font-medium">
              My location - J7
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-semibold text-slate-400 w-10">To</span>
            <div className="flex-1 bg-slate-50 border border-slate-200/80 rounded-xl px-3 py-1.5 text-xs text-slate-800 font-medium">
              Kolhapur Railway Station
            </div>
          </div>
        </div>

        {/* Map Preview */}
        <NetworkMap mode="driver_route" height={160} />

        {/* Route Alternatives */}
        <div className="space-y-2">
          {routes.map((r, idx) => {
            const isSelected = selectedRoute === idx;
            return (
              <div
                key={idx}
                onClick={() => setSelectedRoute(idx)}
                className={`p-3 rounded-2xl border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-blue-50/50 border-blue-500 shadow-sm'
                    : 'bg-white border-slate-200/70 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold ${isSelected ? 'text-blue-700' : 'text-slate-800'}`}>
                      {r.title}
                    </span>
                    {isSelected && (
                      <span className="text-[9px] bg-blue-600 text-white font-bold px-1.5 py-0.5 rounded-full">
                        Selected
                      </span>
                    )}
                  </div>
                  <span className="text-xs font-mono font-bold text-slate-900">
                    {r.time} • <span className="text-slate-500 font-normal">{r.dist}</span>
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  {r.summary}
                </p>
              </div>
            );
          })}
        </div>

        {/* AI Insight Box */}
        <div className="bg-emerald-50/80 border border-emerald-200/80 rounded-2xl p-2.5 flex items-start gap-2">
          <Sparkles className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          <p className="text-[10px] text-emerald-800 font-medium leading-relaxed">
            Signals at J8 and J4 are predicted green on arrival (network-level timing).
          </p>
        </div>

        {/* Action Button */}
        <button
          onClick={() => {
            setNavigating(true);
            onStartNavigation();
          }}
          className="btn-orange text-xs py-3 mt-1"
        >
          <Navigation className="w-4 h-4" />
          {navigating ? 'Navigation Active (Follow Blue Route)' : 'Start navigation'}
        </button>
      </div>
    </div>
  );
};
