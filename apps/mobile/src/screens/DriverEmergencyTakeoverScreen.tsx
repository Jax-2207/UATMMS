import React from 'react';
import { Plus } from 'lucide-react';

interface DriverEmergencyTakeoverScreenProps {
  onDismiss: () => void;
}

export const DriverEmergencyTakeoverScreen: React.FC<DriverEmergencyTakeoverScreenProps> = ({
  onDismiss,
}) => {
  return (
    <div className="flex-1 flex flex-col justify-between bg-gradient-to-b from-red-600 to-red-700 text-white p-6 select-none overflow-hidden relative">
      {/* Background pulsing radar circles */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
        <div className="w-72 h-72 rounded-full border-2 border-white animate-ping" />
        <div className="w-96 h-96 rounded-full border border-white" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center text-center my-auto px-2">
        {/* Large White Badge with Red Cross */}
        <div className="relative mb-6">
          <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center shadow-2xl text-red-600">
            <Plus className="w-14 h-14 stroke-[3.5]" />
          </div>
          <div className="absolute -inset-2 rounded-full border-2 border-white/40 animate-pulse pointer-events-none" />
        </div>

        {/* Headings */}
        <h1 className="font-heading text-2xl font-black text-white tracking-tight mb-2">
          Ambulance approaching
        </h1>
        <p className="text-xs text-red-100 font-medium max-w-[260px] leading-relaxed mb-8">
          Keep left and give way.<br />
          Do not stop in the junction.
        </p>

        {/* 3 Metric Cards */}
        <div className="grid grid-cols-3 gap-2.5 w-full mb-8">
          <div className="bg-white/15 backdrop-blur-md border border-white/20 rounded-2xl p-2.5 flex flex-col items-center">
            <span className="font-mono text-base font-extrabold text-white">450 m</span>
            <span className="text-[10px] text-red-200 uppercase font-medium">distance</span>
          </div>

          <div className="bg-white/15 backdrop-blur-md border border-white/20 rounded-2xl p-2.5 flex flex-col items-center">
            <span className="font-mono text-base font-extrabold text-white">40 s</span>
            <span className="text-[10px] text-red-200 uppercase font-medium">ETA</span>
          </div>

          <div className="bg-white/15 backdrop-blur-md border border-white/20 rounded-2xl p-2.5 flex flex-col items-center">
            <span className="font-mono text-xs font-bold text-white mt-0.5">From behind</span>
            <span className="text-[10px] text-red-200 uppercase font-medium mt-1">direction</span>
          </div>
        </div>

        {/* Informational Note */}
        <p className="text-[11px] text-red-200/90 leading-relaxed text-center px-2">
          Signals ahead are being cleared to keep the corridor moving. Thank you for helping save a life.
        </p>
      </div>

      {/* Bottom Dismiss Action */}
      <div className="relative z-10 w-full pt-4">
        <button
          onClick={onDismiss}
          className="btn-white text-slate-900 font-extrabold text-sm py-3.5"
        >
          Got it
        </button>
        <div className="android-nav-pill white mt-4" />
      </div>
    </div>
  );
};
