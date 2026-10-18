import React from 'react';
import { Home, Navigation, Bell, User, Siren, Shield, Map } from 'lucide-react';

export type NavTab = 
  | 'home' 
  | 'routes' 
  | 'alerts' 
  | 'profile' 
  | 'request' 
  | 'active' 
  | 'incidents' 
  | 'maps';

interface AndroidNavBarProps {
  mode: 'driver' | 'emergency' | 'police';
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
}

export const AndroidNavBar: React.FC<AndroidNavBarProps> = ({ mode, activeTab, onSelectTab }) => {
  let tabs: { id: NavTab; label: string; icon: React.ReactNode }[] = [];

  if (mode === 'driver') {
    tabs = [
      { id: 'home', label: 'Home', icon: <Home className="w-5 h-5" /> },
      { id: 'routes', label: 'Routes', icon: <Navigation className="w-5 h-5" /> },
      { id: 'alerts', label: 'Alerts', icon: <Bell className="w-5 h-5" /> },
      { id: 'profile', label: 'Profile', icon: <User className="w-5 h-5" /> },
    ];
  } else if (mode === 'emergency') {
    tabs = [
      { id: 'request', label: 'Request', icon: <Siren className="w-5 h-5" /> },
      { id: 'active', label: 'Active', icon: <Navigation className="w-5 h-5" /> },
      { id: 'profile', label: 'Profile', icon: <User className="w-5 h-5" /> },
    ];
  } else if (mode === 'police') {
    tabs = [
      { id: 'incidents', label: 'Incidents', icon: <Shield className="w-5 h-5" /> },
      { id: 'maps', label: 'Maps', icon: <Map className="w-5 h-5" /> },
      { id: 'profile', label: 'Profile', icon: <User className="w-5 h-5" /> },
    ];
  }

  return (
    <div className="w-full bg-white border-t border-slate-100 flex flex-col pt-1.5 pb-2 px-4 select-none shrink-0 z-40">
      <div className="flex items-center justify-around">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              className="flex flex-col items-center justify-center gap-0.5 py-1 px-3 rounded-xl transition-all cursor-pointer relative"
            >
              <div className={`${isActive ? 'text-orange-600' : 'text-slate-400'}`}>
                {tab.icon}
              </div>
              <span className={`text-[10px] font-medium ${isActive ? 'text-orange-600 font-bold' : 'text-slate-500'}`}>
                {tab.label}
              </span>
              {isActive && (
                <span className="w-1.5 h-1.5 rounded-full bg-orange-600 absolute -bottom-1" />
              )}
            </button>
          );
        })}
      </div>
      {/* Android System Home Gesture Bar */}
      <div className="android-nav-pill mt-2" />
    </div>
  );
};
