import React from 'react';
import { Car, Siren, Shield, ChevronRight } from 'lucide-react';
import { AndroidStatusBar } from '../components/AndroidStatusBar';

interface WelcomeScreenProps {
  onSelectRole: (role: 'driver' | 'emergency' | 'police') => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSelectRole }) => {
  return (
    <div className="flex-1 flex flex-col justify-between bg-white px-6 pb-6 pt-1 select-none">
      <div>
        <AndroidStatusBar theme="light" />

        {/* Brand Logo & Header */}
        <div className="mt-6 flex flex-col items-start gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-slate-900 flex items-center justify-center shadow-md">
              <div className="flex flex-col gap-1 items-center">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_6px_#ef4444]" />
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
              </div>
            </div>
            <span className="font-heading font-extrabold text-xl tracking-tight text-slate-900">UATMMS</span>
          </div>

          <div className="space-y-1.5 mt-2">
            <h1 className="font-heading text-2xl font-extrabold text-slate-900 leading-tight">
              Smarter signals.<br />
              Safer roads.<br />
              Faster responses.
            </h1>
            <p className="text-xs text-slate-500 leading-relaxed max-w-[280px]">
              Live traffic, safe routes and emergency green corridors.
            </p>
          </div>
        </div>

        {/* Continue As Selection Cards */}
        <div className="mt-8 space-y-3">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Continue as
          </span>

          {/* Role 1: Driver / Commuter */}
          <button
            onClick={() => onSelectRole('driver')}
            className="w-full text-left card-android p-4 flex items-center justify-between border border-slate-200/80 hover:border-orange-500/50 hover:shadow-md transition-all cursor-pointer group"
          >
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                <Car className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading font-bold text-sm text-slate-900 group-hover:text-orange-600 transition-colors">
                  Driver / Commuter
                </h3>
                <p className="text-[11px] text-slate-500">Live traffic, alerts and smart routes</p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
          </button>

          {/* Role 2: Ambulance / Fire Crew */}
          <button
            onClick={() => onSelectRole('emergency')}
            className="w-full text-left card-android p-4 flex items-center justify-between border border-slate-200/80 hover:border-red-500/50 hover:shadow-md transition-all cursor-pointer group"
          >
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-red-50 text-red-600 flex items-center justify-center shrink-0">
                <Siren className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading font-bold text-sm text-slate-900 group-hover:text-red-600 transition-colors">
                  Ambulance / Fire crew
                </h3>
                <p className="text-[11px] text-slate-500">Request a green corridor</p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
          </button>

          {/* Role 3: Traffic Police (Field) */}
          <button
            onClick={() => onSelectRole('police')}
            className="w-full text-left card-android p-4 flex items-center justify-between border border-slate-200/80 hover:border-amber-500/50 hover:shadow-md transition-all cursor-pointer group"
          >
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center shrink-0">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading font-bold text-sm text-slate-900 group-hover:text-amber-700 transition-colors">
                  Traffic Police (field)
                </h3>
                <p className="text-[11px] text-slate-500">Verify incidents on the ground</p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-4 text-center">
        <p className="text-[11px] text-slate-400">
          Staff consoles (Operator, Admin, Hospital) are on the web app.
        </p>
        <div className="android-nav-pill mt-4" />
      </div>
    </div>
  );
};
