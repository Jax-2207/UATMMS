import React from 'react';
import { Search, Siren, ChevronRight } from 'lucide-react';
import { AndroidStatusBar } from '../components/AndroidStatusBar';
import { NetworkMap } from '../components/NetworkMap';

interface DriverHomeScreenProps {
  onPlanRoute: () => void;
  onReportIncident: () => void;
  onTriggerEmergencyTakeover: () => void;
}

export const DriverHomeScreen: React.FC<DriverHomeScreenProps> = ({
  onPlanRoute,
  onReportIncident,
  onTriggerEmergencyTakeover,
}) => {
  return (
    <div className="flex-1 flex flex-col bg-slate-50 select-none overflow-hidden">
      {/* Status Bar */}
      <div className="bg-white">
        <AndroidStatusBar theme="light" />
      </div>

      <div className="flex-1 flex flex-col p-4 gap-3 overflow-y-auto phone-scroll">
        {/* Top Search Bar */}
        <div className="flex items-center gap-2.5 bg-white rounded-2xl px-3.5 py-2.5 shadow-sm border border-slate-200/80">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Where to?"
            readOnly
            onClick={onPlanRoute}
            className="flex-1 bg-transparent text-xs text-slate-800 placeholder-slate-400 outline-none cursor-pointer"
          />
          <div className="w-7 h-7 rounded-full bg-orange-600 text-white font-bold text-[10px] flex items-center justify-center shadow-sm">
            JW
          </div>
        </div>

        {/* Emergency Alert Banner */}
        <button
          onClick={onTriggerEmergencyTakeover}
          className="w-full text-left bg-gradient-to-r from-red-600 to-rose-700 text-white rounded-2xl p-3 shadow-md flex items-center justify-between gap-3 cursor-pointer transition-transform active:scale-[0.99]"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center shrink-0">
              <Siren className="w-4 h-4 text-white animate-bounce" />
            </div>
            <div>
              <h4 className="font-heading font-bold text-xs text-white">
                Ambulance approaching nearby
              </h4>
              <p className="text-[10px] text-red-100">Tap to see how to give way</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-white/80 shrink-0" />
        </button>

        {/* Network Map View */}
        <NetworkMap mode="driver_home" height={210} />

        {/* Traffic Around You Bottom Card */}
        <div className="card-android p-3.5 flex flex-col gap-3">
          <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
            <span className="font-heading font-bold text-xs text-slate-900">
              Traffic around you
            </span>
            <span className="text-[10px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
              Moderate
            </span>
          </div>

          <div className="space-y-2.5 text-xs">
            {/* J7 Item */}
            <div className="flex items-start gap-2">
              <span className="w-2 h-2 rounded-full bg-orange-500 mt-1 shrink-0" />
              <div>
                <span className="font-bold text-slate-800">J7 - your junction</span>
                <p className="text-[11px] text-slate-500">Heavy • wait ~12 min</p>
              </div>
            </div>

            {/* J12 Item */}
            <div className="flex items-start gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500 mt-1 shrink-0" />
              <div>
                <span className="font-bold text-slate-800">J12 - Gandhi Chowk</span>
                <p className="text-[11px] text-slate-500">Accident • diversion active</p>
              </div>
            </div>

            {/* J4 Item */}
            <div className="flex items-start gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mt-1 shrink-0" />
              <div>
                <span className="font-bold text-slate-800">J4 - Station Road</span>
                <p className="text-[11px] text-slate-500">Smooth • green wave likely</p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-2 pt-1">
            <button onClick={onPlanRoute} className="btn-orange text-xs py-2.5">
              Plan route
            </button>
            <button onClick={onReportIncident} className="btn-secondary text-xs py-2.5">
              Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
