import React from 'react';
import { LogOut } from 'lucide-react';

interface SidebarProps {
  role: 'admin' | 'operator' | 'police' | 'hospital';
  currentPage: string;
  onNavigate: (page: string) => void;
  userName: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ role, currentPage, onNavigate, userName }) => {
  const getMenuItems = () => {
    switch (role) {
      case 'admin':
        return [
          { id: 'overview', label: 'Overview', icon: '●' },
          { id: 'users', label: 'Users & Roles', icon: '●' },
          { id: 'safety', label: 'Safety Policies', icon: '●' },
          { id: 'analytics', label: 'Analytics', icon: '●' },
        ];
      case 'operator':
        return [
          { id: 'live-map', label: 'Live Map', icon: '●' },
          { id: 'emergency', label: 'Emergency', icon: '●' },
          { id: 'incidents', label: 'Incidents', icon: '●' },
          { id: 'signal-control', label: 'Signal Control', icon: '●' },
        ];
      case 'police':
        return [
          { id: 'command-view', label: 'Command View', icon: '●' },
          { id: 'incident-queue', label: 'Incident Queue', icon: '●' },
        ];
      case 'hospital':
        return [
          { id: 'coordination', label: 'Coordination', icon: '●' },
        ];
      default:
        return [];
    }
  };

  const menuItems = getMenuItems();

  const getRoleTitle = () => {
    switch (role) {
      case 'admin': return 'ADMIN CONSOLE';
      case 'operator': return 'OPERATOR CONSOLE';
      case 'police': return 'POLICE CONSOLE';
      case 'hospital': return 'HOSPITAL CONSOLE';
      default: return '';
    }
  };

  return (
    <div className="w-56 bg-slate-900 border-r border-slate-800 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-500 via-amber-500 to-emerald-500 flex items-center justify-center">
            <span className="font-bold text-xs text-white">U</span>
          </div>
          <div>
            <div className="text-sm font-bold text-white">UATMMS</div>
            <div className="text-xs text-slate-400">Traffic Intelligence</div>
          </div>
        </div>
      </div>

      {/* Console Title */}
      <div className="px-6 py-4 border-b border-slate-800">
        <div className="text-xs font-bold text-orange-500 uppercase tracking-wide">{getRoleTitle()}</div>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-6">
        <div className="space-y-2">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                currentPage === item.id
                  ? 'bg-orange-600 text-white'
                  : 'text-slate-400 hover:text-slate-300 hover:bg-slate-800/50'
              }`}
            >
              <span className="text-xs">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </div>
      </nav>

      {/* User Profile Footer */}
      <div className="p-6 border-t border-slate-800">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center font-bold text-xs text-white">
            {userName.charAt(0)}
          </div>
          <div>
            <div className="text-xs font-semibold text-white">{userName}</div>
            <div className="text-[10px] text-slate-400 capitalize">{role}</div>
          </div>
        </div>
        <button className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800/50 transition-all">
          <LogOut className="w-3.5 h-3.5" />
          Sign out
        </button>
      </div>
    </div>
  );
};
