import React from 'react';
import { Check, CheckCircle2 } from 'lucide-react';
import { AndroidStatusBar } from '../components/AndroidStatusBar';

interface EmergencyArrivedScreenProps {
  onDone: () => void;
}

export const EmergencyArrivedScreen: React.FC<EmergencyArrivedScreenProps> = ({ onDone }) => {
  return (
    <div className="flex-1 flex flex-col justify-between bg-white px-6 pb-6 pt-1 select-none overflow-hidden">
      <div>
        <AndroidStatusBar theme="light" />

        <div className="flex flex-col items-center text-center mt-8">
          {/* Green Checkmark Circle */}
          <div className="w-20 h-20 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-xl shadow-emerald-500/20 mb-5">
            <Check className="w-10 h-10 stroke-[3.5]" />
          </div>

          <h1 className="font-heading text-xl font-extrabold text-slate-900 tracking-tight mb-1.5">
            Arrived at City Hospital
          </h1>
          <p className="text-xs text-slate-500 max-w-[260px] leading-relaxed mb-6">
            Corridor released. Signals are returning to normal operation.
          </p>

          {/* 3 Metric Summary Boxes */}
          <div className="grid grid-cols-3 gap-2 w-full mb-6">
            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-2.5 flex flex-col items-center">
              <span className="font-mono text-base font-extrabold text-slate-900">7:40</span>
              <span className="text-[10px] text-slate-400 uppercase font-medium mt-0.5">travel time</span>
            </div>

            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-2.5 flex flex-col items-center">
              <span className="font-mono text-base font-extrabold text-blue-600">4</span>
              <span className="text-[10px] text-slate-400 uppercase font-medium mt-0.5">red signals avoided</span>
            </div>

            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-2.5 flex flex-col items-center">
              <span className="font-mono text-base font-extrabold text-emerald-600">≈ 3:20</span>
              <span className="text-[10px] text-slate-400 uppercase font-medium mt-0.5">time saved (est)</span>
            </div>
          </div>

          {/* Safety & Audit Verification List */}
          <div className="w-full bg-slate-50/80 border border-slate-200/70 rounded-2xl p-3.5 space-y-2 text-left">
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Cross-traffic restored</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>No safety violations recorded</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Trip log saved for audit</span>
            </div>
          </div>
        </div>
      </div>

      {/* Done Button */}
      <div className="pt-4">
        <button
          onClick={onDone}
          className="btn-orange text-xs py-3.5 font-bold shadow-md"
        >
          Done
        </button>
      </div>
    </div>
  );
};
