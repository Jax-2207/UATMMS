import React from 'react';
import { Wifi, Battery } from 'lucide-react';

interface AndroidStatusBarProps {
  theme?: 'light' | 'dark'; // 'light' means light screen background (dark text), 'dark' means dark/red screen (white text)
}

export const AndroidStatusBar: React.FC<AndroidStatusBarProps> = ({ theme = 'light' }) => {
  const isLight = theme === 'light';
  const textColor = isLight ? 'text-slate-900' : 'text-white';
  const iconColor = isLight ? 'text-slate-800' : 'text-white';

  return (
    <div className={`w-full flex items-center justify-between px-6 pt-3 pb-2 text-[12px] font-semibold select-none z-50 ${textColor}`}>
      {/* Time */}
      <span className="font-mono tracking-tight font-bold">10:24</span>

      {/* Android System Icons */}
      <div className="flex items-center gap-1.5">
        <span className="text-[11px] font-mono tracking-tighter opacity-90 font-bold">5G</span>
        <div className="flex items-end gap-[1.5px] h-3 px-0.5">
          <div className={`w-[2.5px] h-1.5 rounded-sm ${iconColor} bg-current`} />
          <div className={`w-[2.5px] h-2 rounded-sm ${iconColor} bg-current`} />
          <div className={`w-[2.5px] h-2.5 rounded-sm ${iconColor} bg-current`} />
          <div className={`w-[2.5px] h-3 rounded-sm ${iconColor} bg-current`} />
        </div>
        <Wifi className="w-3.5 h-3.5" />
        <div className="flex items-center gap-0.5 ml-0.5">
          <span className="text-[10px] font-mono">100%</span>
          <Battery className="w-4 h-4 rotate-90" />
        </div>
      </div>
    </div>
  );
};
