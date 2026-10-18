import { useState } from 'react';
import { Smartphone, RotateCcw, Monitor } from 'lucide-react';
import { AndroidNavBar, type NavTab } from './components/AndroidNavBar';

// Screens
import { WelcomeScreen } from './screens/WelcomeScreen';
import { DriverHomeScreen } from './screens/DriverHomeScreen';
import { DriverRoutesScreen } from './screens/DriverRoutesScreen';
import { DriverAlertsScreen } from './screens/DriverAlertsScreen';
import { DriverEmergencyTakeoverScreen } from './screens/DriverEmergencyTakeoverScreen';
import { EmergencyRequestScreen } from './screens/EmergencyRequestScreen';
import { EmergencyActiveScreen } from './screens/EmergencyActiveScreen';
import { EmergencyArrivedScreen } from './screens/EmergencyArrivedScreen';
import { PoliceIncidentsScreen } from './screens/PoliceIncidentsScreen';

export type ScreenId = 
  | 'welcome'
  | 'driver_home'
  | 'driver_routes'
  | 'driver_alerts'
  | 'driver_emergency'
  | 'emergency_request'
  | 'emergency_active'
  | 'emergency_arrived'
  | 'police_incidents';

export function App() {
  const [screen, setScreen] = useState<ScreenId>('welcome');
  const [role, setRole] = useState<'driver' | 'emergency' | 'police'>('driver');
  const [activeTab, setActiveTab] = useState<NavTab>('home');
  const [showDeviceFrame, setShowDeviceFrame] = useState<boolean>(true);

  // Handle Role Selection from Welcome Screen
  const handleSelectRole = (newRole: 'driver' | 'emergency' | 'police') => {
    setRole(newRole);
    if (newRole === 'driver') {
      setScreen('driver_home');
      setActiveTab('home');
    } else if (newRole === 'emergency') {
      setScreen('emergency_request');
      setActiveTab('request');
    } else if (newRole === 'police') {
      setScreen('police_incidents');
      setActiveTab('incidents');
    }
  };

  // Handle Tab Switch inside Android Navigation Bar
  const handleSelectTab = (tab: NavTab) => {
    setActiveTab(tab);
    if (role === 'driver') {
      if (tab === 'home') setScreen('driver_home');
      else if (tab === 'routes') setScreen('driver_routes');
      else if (tab === 'alerts') setScreen('driver_alerts');
      else if (tab === 'profile') setScreen('welcome');
    } else if (role === 'emergency') {
      if (tab === 'request') setScreen('emergency_request');
      else if (tab === 'active') setScreen('emergency_active');
      else if (tab === 'profile') setScreen('welcome');
    } else if (role === 'police') {
      if (tab === 'incidents') setScreen('police_incidents');
      else if (tab === 'maps') setScreen('police_incidents');
      else if (tab === 'profile') setScreen('welcome');
    }
  };

  // Flow Triggers
  const handleTriggerEmergencyTakeover = () => {
    setScreen('driver_emergency');
  };

  const handleDismissTakeover = () => {
    setScreen('driver_home');
    setActiveTab('home');
  };

  const handlePlanRoute = () => {
    setScreen('driver_routes');
    setActiveTab('routes');
  };

  const handleReportIncident = () => {
    setScreen('driver_alerts');
    setActiveTab('alerts');
  };

  const handleRequestCorridor = () => {
    setScreen('emergency_active');
    setActiveTab('active');
  };

  const handleArrived = () => {
    setScreen('emergency_arrived');
  };

  const handleEmergencyDone = () => {
    setScreen('emergency_request');
    setActiveTab('request');
  };

  const screensMeta: { id: ScreenId; label: string; roleTag: string }[] = [
    { id: 'welcome', label: '1. Welcome', roleTag: 'Entry' },
    { id: 'driver_home', label: '2. Home', roleTag: 'Driver' },
    { id: 'driver_routes', label: '3. Routes', roleTag: 'Driver' },
    { id: 'driver_alerts', label: '4. Alerts', roleTag: 'Driver' },
    { id: 'driver_emergency', label: '5. Give Way (Takeover)', roleTag: 'Emergency' },
    { id: 'emergency_request', label: '6. Request Corridor', roleTag: 'Ambulance' },
    { id: 'emergency_active', label: '7. Active Corridor', roleTag: 'Ambulance' },
    { id: 'emergency_arrived', label: '8. Mission Arrived', roleTag: 'Ambulance' },
    { id: 'police_incidents', label: '9. Field Incidents', roleTag: 'Police' },
  ];

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-slate-950 p-2 md:p-6 text-slate-100 select-none">
      {/* Top Reviewer Controls & Screen Switcher Bar */}
      <div className="w-full max-w-5xl mb-4 flex flex-wrap items-center justify-between gap-3 bg-slate-900/90 border border-white/10 rounded-2xl p-3 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-orange-600 flex items-center justify-center font-bold text-xs text-white">
            UA
          </div>
          <div>
            <h2 className="font-heading font-extrabold text-xs text-white tracking-wide">
              UATMMS Android Mobile Client
            </h2>
            <p className="text-[10px] text-slate-400">
              Interactive Figma Flow Implementation
            </p>
          </div>
        </div>

        {/* Quick Screen Switcher Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto max-w-full py-1">
          {screensMeta.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setScreen(s.id);
                if (s.id.startsWith('driver_')) {
                  setRole('driver');
                  if (s.id === 'driver_home') setActiveTab('home');
                  if (s.id === 'driver_routes') setActiveTab('routes');
                  if (s.id === 'driver_alerts') setActiveTab('alerts');
                } else if (s.id.startsWith('emergency_')) {
                  setRole('emergency');
                  if (s.id === 'emergency_request') setActiveTab('request');
                  if (s.id === 'emergency_active') setActiveTab('active');
                } else if (s.id.startsWith('police_')) {
                  setRole('police');
                  setActiveTab('incidents');
                }
              }}
              className={`text-[10px] font-medium px-2.5 py-1 rounded-lg border whitespace-nowrap transition-all ${
                screen === s.id
                  ? 'bg-orange-600 border-orange-500 text-white font-bold shadow-sm'
                  : 'bg-slate-800/80 border-white/5 text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {/* View Options */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setScreen('welcome')}
            className="flex items-center gap-1 text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 rounded-lg border border-white/10 transition-colors"
            title="Reset to Welcome Screen"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>

          <button
            onClick={() => setShowDeviceFrame(!showDeviceFrame)}
            className="flex items-center gap-1 text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 rounded-lg border border-white/10 transition-colors"
            title="Toggle Android Device Frame"
          >
            {showDeviceFrame ? (
              <>
                <Monitor className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden sm:inline">Full Frame</span>
              </>
            ) : (
              <>
                <Smartphone className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden sm:inline">Phone Frame</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Android Device Shell Container */}
      <div className={showDeviceFrame ? 'android-device-frame' : 'w-full max-w-md h-[844px] bg-white rounded-3xl overflow-hidden shadow-2xl flex flex-col relative'}>
        {/* Camera Punch Hole */}
        <div className="android-punch-hole" />

        {/* Active Screen View */}
        <div className="flex-1 flex flex-col overflow-hidden relative">
          {screen === 'welcome' && (
            <WelcomeScreen onSelectRole={handleSelectRole} />
          )}

          {screen === 'driver_home' && (
            <DriverHomeScreen
              onPlanRoute={handlePlanRoute}
              onReportIncident={handleReportIncident}
              onTriggerEmergencyTakeover={handleTriggerEmergencyTakeover}
            />
          )}

          {screen === 'driver_routes' && (
            <DriverRoutesScreen
              onBack={() => {
                setScreen('driver_home');
                setActiveTab('home');
              }}
              onStartNavigation={() => {
                // Keep on screen with active state
              }}
            />
          )}

          {screen === 'driver_alerts' && (
            <DriverAlertsScreen
              onTriggerEmergencyTakeover={handleTriggerEmergencyTakeover}
            />
          )}

          {screen === 'driver_emergency' && (
            <DriverEmergencyTakeoverScreen
              onDismiss={handleDismissTakeover}
            />
          )}

          {screen === 'emergency_request' && (
            <EmergencyRequestScreen
              onRequestCorridor={handleRequestCorridor}
            />
          )}

          {screen === 'emergency_active' && (
            <EmergencyActiveScreen
              onArrived={handleArrived}
              onReportBlockedRoad={() => {
                setScreen('driver_alerts');
                setActiveTab('alerts');
              }}
            />
          )}

          {screen === 'emergency_arrived' && (
            <EmergencyArrivedScreen
              onDone={handleEmergencyDone}
            />
          )}

          {screen === 'police_incidents' && (
            <PoliceIncidentsScreen
              onRequestAmbulance={() => {
                setRole('emergency');
                setScreen('emergency_request');
                setActiveTab('request');
              }}
            />
          )}
        </div>

        {/* Android Bottom Navigation Bar (Hidden on Welcome & Takeover Screens) */}
        {screen !== 'welcome' && screen !== 'driver_emergency' && (
          <AndroidNavBar
            mode={role}
            activeTab={activeTab}
            onSelectTab={handleSelectTab}
          />
        )}
      </div>
    </div>
  );
}

export default App;
