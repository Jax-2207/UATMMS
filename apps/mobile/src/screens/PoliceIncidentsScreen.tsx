import React, { useState } from 'react';
import { CheckCircle2, Siren, Sliders } from 'lucide-react';
import { NetworkMap } from '../components/NetworkMap';

interface PoliceIncidentsScreenProps {
  onRequestAmbulance: () => void;
}

export const PoliceIncidentsScreen: React.FC<PoliceIncidentsScreenProps> = ({
  onRequestAmbulance,
}) => {
  const [onDuty, setOnDuty] = useState<boolean>(true);
  const [confirmed, setConfirmed] = useState<boolean>(false);

  return (
    <div className="flex-1 flex flex-col bg-slate-50 select-none overflow-hidden">
      {/* Header */}
      <div className="bg-white border-b border-slate-100 pt-3">
        <div className="px-5 pb-3 flex items-center justify-between">
          <div>
            <h2 className="font-heading font-extrabold text-base text-slate-900 leading-tight">
              Field incidents
            </h2>
            <p className="text-[10px] text-slate-400 font-medium">
              Insp. S. Patil - Patrol P-12
            </p>
          </div>

          {/* On Duty Toggle Pill */}
          <button
            onClick={() => setOnDuty(!onDuty)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold border transition-all ${
              onDuty
                ? 'bg-emerald-50 border-emerald-300 text-emerald-700'
                : 'bg-slate-100 border-slate-300 text-slate-500'
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${onDuty ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`} />
            {onDuty ? 'On duty' : 'Off duty'}
          </button>
        </div>
      </div>

      <div className="flex-1 flex flex-col p-4 gap-3 overflow-y-auto phone-scroll">
        {/* Map Thumbnail */}
        <NetworkMap mode="police" height={150} />

        {/* Urgent Critical Incident Card */}
        <div className="card-android p-3.5 border-l-4 border-l-red-500 flex flex-col gap-2.5">
          <div className="flex items-center justify-between">
            <span className="font-heading font-bold text-xs text-slate-900">
              Accident - J12
            </span>
            <span className="text-[9px] font-mono font-bold bg-red-100 text-red-700 border border-red-200 px-2 py-0.5 rounded-full">
              Critical
            </span>
          </div>

          <p className="text-[11px] text-slate-500">
            1.2 km away • ETA 2 min • Vision AI (84%)
          </p>

          <button
            onClick={() => setConfirmed(!confirmed)}
            className={`btn-orange text-xs py-2.5 ${confirmed ? 'bg-emerald-600' : ''}`}
          >
            {confirmed ? (
              <span className="flex items-center gap-1.5 text-white">
                <CheckCircle2 className="w-4 h-4" /> Confirmed on Scene
              </span>
            ) : (
              'Confirm at scene'
            )}
          </button>

          <div className="grid grid-cols-2 gap-2 pt-0.5">
            <button
              onClick={onRequestAmbulance}
              className="btn-secondary text-[11px] py-1.5 justify-center text-red-600 border-red-200 bg-red-50/50"
            >
              <Siren className="w-3.5 h-3.5" />
              Request ambulance
            </button>
            <button
              className="btn-secondary text-[11px] py-1.5 justify-center text-slate-600"
            >
              <Sliders className="w-3.5 h-3.5" />
              Manual override
            </button>
          </div>
        </div>

        {/* Medium Anomaly Card */}
        <div className="card-android p-3 flex flex-col gap-1 border-l-4 border-l-amber-400">
          <div className="flex items-center justify-between">
            <span className="font-heading font-bold text-xs text-slate-900">
              Abnormal slowdown - J3
            </span>
            <span className="text-[9px] font-mono font-bold bg-amber-100 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full">
              Medium
            </span>
          </div>
          <p className="text-[11px] text-slate-500">
            3.5 km • Anomaly model 76%
          </p>
        </div>

        {/* Handled Card */}
        <div className="card-android p-3 flex flex-col gap-1 border-l-4 border-l-blue-400 opacity-80">
          <div className="flex items-center justify-between">
            <span className="font-heading font-bold text-xs text-slate-900">
              Stalled vehicle - J8
            </span>
            <span className="text-[9px] font-mono font-bold bg-blue-100 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full">
              Handled
            </span>
          </div>
          <p className="text-[11px] text-slate-500">
            On scene - P-07
          </p>
        </div>
      </div>
    </div>
  );
};
