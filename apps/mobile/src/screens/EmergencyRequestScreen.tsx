import React, { useState } from 'react';
import { MapPin, Siren, Check } from 'lucide-react';

interface EmergencyRequestScreenProps {
  onRequestCorridor: () => void;
}

export const EmergencyRequestScreen: React.FC<EmergencyRequestScreenProps> = ({
  onRequestCorridor,
}) => {
  const [vehicleType, setVehicleType] = useState<string>('Ambulance');
  const [selectedHospital, setSelectedHospital] = useState<number>(0);
  const [severity, setSeverity] = useState<string>('Critical');

  const hospitals = [
    { name: 'City Hospital', time: '8 min', dist: '6.2 km', recommended: true },
    { name: 'Sanjeevani Hospital', time: '11 min', dist: '7.5 km', recommended: false },
    { name: 'Govt. Hospital', time: '14 min', dist: '9.4 km', recommended: false },
  ];

  return (
    <div className="flex-1 flex flex-col bg-slate-50 select-none overflow-hidden">
      {/* Header */}
      <div className="bg-white border-b border-slate-100 pt-3">
        <div className="px-5 pb-3">
          <h2 className="font-heading font-extrabold text-base text-slate-900 leading-tight">
            Request green corridor
          </h2>
          <p className="text-[10px] text-slate-400 font-medium">
            Ambulance #A1 - Fleet 108
          </p>
        </div>
      </div>

      <div className="flex-1 flex flex-col p-4 gap-3.5 overflow-y-auto phone-scroll">
        {/* Vehicle Type Selector */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] font-semibold text-slate-400 uppercase">
            Vehicle type
          </span>
          <div className="grid grid-cols-4 gap-1.5">
            {['Ambulance', 'Fire', 'Police', 'Other'].map((t) => {
              const isSelected = vehicleType === t;
              return (
                <button
                  key={t}
                  onClick={() => setVehicleType(t)}
                  className={`py-1.5 px-2 rounded-xl text-xs font-semibold border transition-all ${
                    isSelected
                      ? 'bg-red-50 border-red-500 text-red-600 shadow-sm'
                      : 'bg-white border-slate-200 text-slate-600'
                  }`}
                >
                  {t}
                </button>
              );
            })}
          </div>
        </div>

        {/* GPS Locked Banner */}
        <div className="bg-emerald-50 border border-emerald-200/80 rounded-2xl p-2.5 flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-sm">
            <MapPin className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-bold text-emerald-900">GPS locked - Shivaji Chowk</span>
            </div>
            <p className="text-[10px] text-emerald-700">Live location shared with control room</p>
          </div>
        </div>

        {/* Destination Header */}
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-semibold text-slate-400 uppercase">
              Destination
            </span>
            <span className="text-[10px] text-orange-600 font-bold cursor-pointer">Change</span>
          </div>
          <div className="bg-white border border-slate-200/80 rounded-xl px-3 py-2 text-xs font-semibold text-slate-800">
            City Hospital - ER
          </div>
        </div>

        {/* Fastest Safe Route Options */}
        <div className="flex flex-col gap-2">
          <span className="text-[10px] font-semibold text-slate-400 uppercase">
            Fastest safe route (live + predicted traffic)
          </span>

          <div className="space-y-1.5">
            {hospitals.map((h, idx) => {
              const isSelected = selectedHospital === idx;
              return (
                <div
                  key={idx}
                  onClick={() => setSelectedHospital(idx)}
                  className={`p-2.5 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-blue-50/60 border-blue-500 shadow-sm'
                      : 'bg-white border-slate-200/80'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                      isSelected ? 'border-blue-600 bg-blue-600 text-white' : 'border-slate-300'
                    }`}>
                      {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                    </div>
                    <div>
                      <span className="text-xs font-bold text-slate-900 block leading-tight">
                        {h.name}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">
                        {h.time} • {h.dist}
                      </span>
                    </div>
                  </div>

                  {h.recommended && (
                    <span className="text-[9px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                      Recommended
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Severity */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] font-semibold text-slate-400 uppercase">
            Severity
          </span>
          <div className="grid grid-cols-3 gap-2">
            {['Critical', 'High', 'Normal'].map((s) => {
              const isSelected = severity === s;
              return (
                <button
                  key={s}
                  onClick={() => setSeverity(s)}
                  className={`py-1.5 rounded-xl text-xs font-bold border transition-all ${
                    isSelected
                      ? s === 'Critical'
                        ? 'bg-red-50 border-red-500 text-red-600'
                        : 'bg-orange-50 border-orange-500 text-orange-600'
                      : 'bg-white border-slate-200 text-slate-600'
                  }`}
                >
                  {s}
                </button>
              );
            })}
          </div>
        </div>

        {/* Request Button */}
        <button
          onClick={onRequestCorridor}
          className="btn-red text-xs py-3 mt-1 shadow-lg"
        >
          <Siren className="w-4 h-4" />
          Request green corridor
        </button>
      </div>
    </div>
  );
};
