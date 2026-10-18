import React, { useState } from 'react';
import { Siren, AlertTriangle, Clock, Zap, CheckCircle2 } from 'lucide-react';
import { AndroidStatusBar } from '../components/AndroidStatusBar';

interface DriverAlertsScreenProps {
  onTriggerEmergencyTakeover: () => void;
}

export const DriverAlertsScreen: React.FC<DriverAlertsScreenProps> = ({
  onTriggerEmergencyTakeover,
}) => {
  const [selectedType, setSelectedType] = useState<string>('Accident');
  const [submitted, setSubmitted] = useState<boolean>(false);

  const alerts = [
    {
      id: 1,
      title: 'Ambulance approaching',
      detail: 'Give way - 450 m - ETA 40 s',
      time: '10s',
      urgent: true,
      icon: <Siren className="w-4 h-4 text-red-600 animate-pulse" />
    },
    {
      id: 2,
      title: 'Accident at J12',
      detail: 'Diversion via J9 → J8 → J11',
      time: '2 min',
      urgent: false,
      icon: <AlertTriangle className="w-4 h-4 text-amber-500" />
    },
    {
      id: 3,
      title: 'Heavy congestion at J7',
      detail: 'Expected to clear in 12 min',
      time: '5 min',
      urgent: false,
      icon: <Clock className="w-4 h-4 text-orange-500" />
    },
    {
      id: 4,
      title: 'Green wave on Station Road',
      detail: 'Hold 40 km/h for fewer stops',
      time: '9 min',
      urgent: false,
      icon: <Zap className="w-4 h-4 text-emerald-500" />
    }
  ];

  const handleSubmit = () => {
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <div className="flex-1 flex flex-col bg-slate-50 select-none overflow-hidden">
      {/* Top Header */}
      <div className="bg-white border-b border-slate-100">
        <AndroidStatusBar theme="light" />
        <div className="px-5 pb-3">
          <h2 className="font-heading font-extrabold text-base text-slate-900 leading-tight">
            Alerts
          </h2>
          <p className="text-[10px] text-slate-400">
            Live updates for your area
          </p>
        </div>
      </div>

      <div className="flex-1 flex flex-col p-4 gap-3.5 overflow-y-auto phone-scroll">
        {/* Alert List */}
        <div className="space-y-2">
          {alerts.map((a) => (
            <div
              key={a.id}
              onClick={a.urgent ? onTriggerEmergencyTakeover : undefined}
              className={`p-3 rounded-2xl border transition-all ${
                a.urgent 
                  ? 'bg-red-50/70 border-red-300 shadow-sm cursor-pointer hover:bg-red-50' 
                  : 'bg-white border-slate-200/80'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-2.5">
                  <div className="mt-0.5">{a.icon}</div>
                  <div>
                    <h4 className={`text-xs font-bold ${a.urgent ? 'text-red-700' : 'text-slate-800'}`}>
                      {a.title}
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      {a.detail}
                    </p>
                  </div>
                </div>
                <span className="text-[10px] font-mono text-slate-400 shrink-0">
                  {a.time}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Report an Incident Box */}
        <div className="card-android p-3.5 flex flex-col gap-2.5">
          <span className="font-heading font-bold text-xs text-slate-900">
            Report an incident
          </span>

          {/* Incident Type Chips */}
          <div className="flex items-center gap-2">
            {['Accident', 'Breakdown', 'Waterlogging'].map((type) => {
              const isSelected = selectedType === type;
              return (
                <button
                  key={type}
                  onClick={() => setSelectedType(type)}
                  className={`text-[11px] px-3 py-1.5 rounded-xl border transition-all font-medium cursor-pointer ${
                    isSelected
                      ? 'bg-orange-50 border-orange-500 text-orange-700 font-bold'
                      : 'bg-slate-50 border-slate-200 text-slate-600'
                  }`}
                >
                  {type}
                </button>
              );
            })}
          </div>

          {/* Location field */}
          <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-2.5 flex items-center justify-between text-xs">
            <div>
              <span className="text-[9px] text-slate-400 uppercase font-semibold block">Location</span>
              <span className="text-slate-800 font-medium">Current location - near J7</span>
            </div>
            <button className="text-[10px] font-bold text-orange-600 hover:underline">
              Change
            </button>
          </div>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            className="btn-orange text-xs py-2.5 mt-0.5"
          >
            {submitted ? (
              <span className="flex items-center gap-1.5 text-white">
                <CheckCircle2 className="w-4 h-4" /> Report Submitted
              </span>
            ) : (
              'Submit report'
            )}
          </button>

          <p className="text-[10px] text-slate-400 text-center leading-tight">
            Reports are verified by AI and traffic police before action is taken.
          </p>
        </div>
      </div>
    </div>
  );
};
