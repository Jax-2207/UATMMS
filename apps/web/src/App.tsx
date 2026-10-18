import { useState, useEffect } from 'react';
import { 
  Activity, 
  ShieldCheck, 
  Siren, 
  Play, 
  Pause, 
  RotateCcw, 
  FastForward, 
  Radio, 
  Clock, 
  Layers, 
  MapPin, 
  Sliders, 
  CheckCircle2, 
  XCircle,
  Car,
  ChevronRight
} from 'lucide-react';

interface Junction {
  id: string;
  name: string;
  currentPhase: 'NS_GREEN' | 'EW_GREEN' | 'ALL_RED' | 'YELLOW';
  elapsed: number;
  queueVehicles: number;
  minGreen: number;
}

interface EventLog {
  id: string;
  timestamp: string;
  type: 'safety' | 'emergency' | 'incident' | 'system';
  message: string;
  status: 'approved' | 'rejected' | 'info';
}

export function App() {
  const [role, setRole] = useState<'Operator' | 'Admin' | 'Police' | 'Ambulance'>('Operator');
  const [simRunning, setSimRunning] = useState<boolean>(false);
  const [simTime, setSimTime] = useState<number>(0);
  const [stepCount, setStepCount] = useState<number>(0);
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  
  // Simulation Metrics
  const [vehicleCount, setVehicleCount] = useState<number>(14);
  const [avgSpeed, setAvgSpeed] = useState<number>(11.2);
  const [waitingTime, setWaitingTime] = useState<number>(3.8);
  const [activeCorridors, setActiveCorridors] = useState<number>(1);
  const [safetyViolations] = useState<number>(0);

  // Junctions
  const [junctions, setJunctions] = useState<Junction[]>([
    { id: 'J1', name: 'MG Road Junction', currentPhase: 'NS_GREEN', elapsed: 14, queueVehicles: 4, minGreen: 10 },
    { id: 'J2', name: 'Brigade Road Junction', currentPhase: 'EW_GREEN', elapsed: 8, queueVehicles: 7, minGreen: 10 },
    { id: 'J3', name: 'Residency Road', currentPhase: 'YELLOW', elapsed: 2, queueVehicles: 5, minGreen: 10 },
    { id: 'J4', name: 'Church Street', currentPhase: 'NS_GREEN', elapsed: 22, queueVehicles: 2, minGreen: 10 },
    { id: 'J5', name: 'Commercial Street', currentPhase: 'ALL_RED', elapsed: 1, queueVehicles: 6, minGreen: 10 },
    { id: 'J6', name: 'Lavelle Road', currentPhase: 'EW_GREEN', elapsed: 18, queueVehicles: 3, minGreen: 10 },
  ]);

  // Logs
  const [logs, setLogs] = useState<EventLog[]>([
    { id: '1', timestamp: '12:02:15', type: 'system', message: 'UATMMS Modular Engine & Safety Validator initialized.', status: 'info' },
    { id: '2', timestamp: '12:02:18', type: 'safety', message: 'J1_MG_Road: Phase transition checked. 10s Min-Green invariant satisfied.', status: 'approved' },
    { id: '3', timestamp: '12:02:22', type: 'emergency', message: 'AMB-108 dispatched from MG Road to Victoria Hospital. Corridor scheduled.', status: 'approved' },
    { id: '4', timestamp: '12:02:25', type: 'safety', message: 'Rejected instant flip on J2: conflicting movements require 3s yellow + 2s all-red.', status: 'rejected' },
  ]);

  // WebSocket Connection Attempt to FastAPI backend
  useEffect(() => {
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket('ws://localhost:8000/ws/simulation');
      ws.onopen = () => setWsConnected(true);
      ws.onclose = () => setWsConnected(false);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.status === 'running') setSimRunning(true);
          setSimTime(data.simulation_time_s || 0);
          setStepCount(data.step || 0);
          setVehicleCount(data.active_vehicle_count || 0);
          setAvgSpeed(data.average_speed_mps || 0);
          setWaitingTime(data.average_waiting_time_s || 0);
        } catch (e) {
          console.error(e);
        }
      };
    } catch {
      setWsConnected(false);
    }
    return () => {
      if (ws) ws.close();
    };
  }, []);

  // Local fallback clock when running in preview
  useEffect(() => {
    if (!simRunning || wsConnected) return;
    const interval = setInterval(() => {
      setSimTime(t => t + 1);
      setStepCount(s => s + 1);
      setJunctions(prev => prev.map(j => ({
        ...j,
        elapsed: (j.elapsed + 1) % 40,
        currentPhase: (j.elapsed + 1) > 35 ? 'YELLOW' : (j.elapsed + 1) > 20 ? 'EW_GREEN' : 'NS_GREEN'
      })));
    }, 1000);
    return () => clearInterval(interval);
  }, [simRunning, wsConnected]);

  // Actions
  const handleStart = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/simulation/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: 'default_6junctions', seed: 42 })
      });
    } catch {}
    setSimRunning(true);
    addLog('system', 'Simulation started [Scenario: 6-Junction Urban Grid, Seed: 42]', 'info');
  };

  const handlePause = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/simulation/pause', { method: 'POST' });
    } catch {}
    setSimRunning(false);
    addLog('system', 'Simulation paused by operator.', 'info');
  };

  const handleStep = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/simulation/step', { method: 'POST' });
    } catch {}
    setSimTime(t => t + 1);
    setStepCount(s => s + 1);
    addLog('system', 'Manual step forward (+1.0s)', 'info');
  };

  const handleReset = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/simulation/reset', { method: 'POST' });
    } catch {}
    setSimRunning(false);
    setSimTime(0);
    setStepCount(0);
    addLog('system', 'Simulation reset to baseline initial conditions.', 'info');
  };

  const handleEmergencyTrigger = async () => {
    const ambId = `AMB-${Math.floor(100 + Math.random() * 900)}`;
    try {
      await fetch('http://localhost:8000/api/v1/emergencies/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vehicle_id: ambId,
          vehicle_type: 'ambulance',
          origin_edge_id: 'E_MG_Road_North',
          destination_edge_id: 'E_Victoria_Hospital',
          urgency_level: 1
        })
      });
    } catch {}
    setActiveCorridors(c => c + 1);
    addLog('emergency', `Priority Corridor requested for ${ambId}. Route computed. Safety check PASSED.`, 'approved');
  };

  const handleIncidentInject = async (type: string) => {
    try {
      await fetch('http://localhost:8000/api/v1/incidents/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          incident_type: type,
          edge_id: 'E_Brigade_Main',
          severity: 3,
          description: `Simulated ${type.replace('_', ' ')} injected.`
        })
      });
    } catch {}
    addLog('incident', `Incident injected: ${type.replace('_', ' ').toUpperCase()} on Brigade Road. Rerouting activated.`, 'rejected');
  };

  const addLog = (type: EventLog['type'], message: string, status: EventLog['status']) => {
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    setLogs(prev => [
      { id: Date.now().toString(), timestamp: timeStr, type, message, status },
      ...prev.slice(0, 19)
    ]);
  };

  return (
    <div className="min-h-screen flex flex-col p-4 md:p-6 gap-5 max-w-[1700px] mx-auto">
      {/* Top Header Bar */}
      <header className="glass-panel p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/30 border border-cyan-500/30 text-cyan-400">
            <Radio className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl md:text-2xl font-extrabold tracking-tight text-white">
                UATMMS <span className="text-cyan-400 font-light text-base md:text-lg">| Command Centre</span>
              </h1>
              <span className="badge-neon badge-cyan">Phase 0 Skeleton</span>
            </div>
            <p className="text-xs text-slate-400">
              Universal Automatic Traffic Management and Manipulation System
            </p>
          </div>
        </div>

        {/* Status Indicators & Clock */}
        <div className="flex flex-wrap items-center gap-3 md:gap-5">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-black/40 border border-white/5 text-xs font-mono">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">SUMO Clock:</span>
            <span className="text-white font-semibold">{simTime.toFixed(1)}s (Step {stepCount})</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-black/40 border border-white/5 text-xs">
            <span className={wsConnected ? "pulse-green" : "pulse-cyan"}></span>
            <span className="text-slate-300 font-medium">
              {wsConnected ? "FastAPI Live" : "Local Standalone Preview"}
            </span>
          </div>

          {/* Role Selector */}
          <div className="flex items-center bg-slate-900/90 rounded-lg p-1 border border-white/10 text-xs">
            <span className="px-2 text-slate-400 font-medium">Role:</span>
            {(['Operator', 'Admin', 'Police', 'Ambulance'] as const).map(r => (
              <button
                key={r}
                onClick={() => setRole(r)}
                className={`px-2.5 py-1 rounded-md transition-all font-medium ${
                  role === r ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm' : 'text-slate-300 hover:text-white'
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Primary Metrics Banner */}
      <section className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
        <div className="glass-panel p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Active Network Vehicles</span>
            <Car className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{vehicleCount}</span>
            <span className="text-xs text-emerald-400 font-medium">+3 vs baseline</span>
          </div>
        </div>

        <div className="glass-panel p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Mean Network Speed</span>
            <Activity className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{avgSpeed.toFixed(1)}</span>
            <span className="text-xs text-slate-400 font-medium">m/s (38.8 km/h)</span>
          </div>
        </div>

        <div className="glass-panel p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Average Waiting Time</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-amber-300">{waitingTime.toFixed(1)}s</span>
            <span className="text-xs text-emerald-400 font-medium">-18% latency</span>
          </div>
        </div>

        <div className="glass-panel p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Emergency Corridors</span>
            <Siren className="w-4 h-4 text-purple-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-purple-300">{activeCorridors} Active</span>
            <span className="text-xs text-purple-400 font-medium">0s red hold</span>
          </div>
        </div>

        <div className="glass-panel p-3.5 flex flex-col justify-between col-span-2 md:col-span-1 border-emerald-500/20">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Safety Validator Status</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-emerald-400">{safetyViolations}</span>
            <span className="text-xs text-emerald-300 font-medium">Hard Gate Enforced</span>
          </div>
        </div>
      </section>

      {/* Main Command Workspace */}
      <main className="grid grid-cols-1 lg:grid-cols-12 gap-5 flex-1">
        {/* Left Column: Role Actions & Live Audit Stream (3 Cols) */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          {/* Quick Actions Panel */}
          <div className="glass-panel p-4 flex flex-col gap-3">
            <div className="flex items-center justify-between pb-2 border-b border-white/5">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-cyan-400" /> {role} Actions
              </span>
              <span className="badge-neon badge-cyan">RBAC Active</span>
            </div>

            <button 
              onClick={handleEmergencyTrigger}
              className="btn-danger w-full justify-center"
            >
              <Siren className="w-4 h-4" /> Trigger Ambulance Corridor
            </button>

            <div className="flex flex-col gap-1.5 pt-2">
              <span className="text-[11px] text-slate-400 font-medium">Inject Indian-Road Conditions:</span>
              <div className="grid grid-cols-2 gap-2">
                <button 
                  onClick={() => handleIncidentInject('blocked_lane')}
                  className="btn-secondary text-xs py-1.5 px-2 justify-center"
                >
                  Blocked Lane
                </button>
                <button 
                  onClick={() => handleIncidentInject('animal_crossing')}
                  className="btn-secondary text-xs py-1.5 px-2 justify-center"
                >
                  Animal Crossing
                </button>
                <button 
                  onClick={() => handleIncidentInject('rash_driving')}
                  className="btn-secondary text-xs py-1.5 px-2 justify-center"
                >
                  Rash Driving
                </button>
                <button 
                  onClick={() => handleIncidentInject('accident')}
                  className="btn-secondary text-xs py-1.5 px-2 justify-center text-red-300 border-red-500/30"
                >
                  Accident Crash
                </button>
              </div>
            </div>
          </div>

          {/* Live Safety & Event Log */}
          <div className="glass-panel p-4 flex flex-col flex-1 min-h-[340px]">
            <div className="flex items-center justify-between pb-2 border-b border-white/5 mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Safety & Event Stream
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Live</span>
            </div>

            <div className="flex flex-col gap-2 overflow-y-auto max-h-[420px] pr-1">
              {logs.map(log => (
                <div 
                  key={log.id} 
                  className={`p-2.5 rounded-lg border text-xs flex flex-col gap-1 ${
                    log.status === 'rejected'
                      ? 'bg-red-950/20 border-red-500/30 text-red-200'
                      : log.type === 'emergency'
                      ? 'bg-purple-950/20 border-purple-500/30 text-purple-200'
                      : 'bg-black/30 border-white/5 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between font-mono text-[10px] text-slate-400">
                    <span>{log.timestamp}</span>
                    <span className="uppercase">{log.type}</span>
                  </div>
                  <div className="flex items-start gap-1.5 mt-0.5">
                    {log.status === 'approved' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />}
                    {log.status === 'rejected' && <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0 mt-0.5" />}
                    {log.status === 'info' && <ChevronRight className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />}
                    <span className="leading-snug">{log.message}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center Column: Digital Twin / Interactive Simulation View (6 Cols) */}
        <div className="lg:col-span-6 flex flex-col gap-4">
          <div className="glass-panel p-4 flex flex-col flex-1 min-h-[480px]">
            {/* Simulation Header Controls */}
            <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/5 gap-2">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                <span className="font-heading font-semibold text-sm text-white">
                  Multi-Intersection Digital Twin Canvas
                </span>
                <span className="badge-neon badge-green">6-Junction Connected Grid</span>
              </div>

              {/* Simulation Playback Toolbar */}
              <div className="flex items-center gap-2">
                {!simRunning ? (
                  <button onClick={handleStart} className="btn-primary py-1 px-3 text-xs">
                    <Play className="w-3.5 h-3.5 fill-current" /> Start Run
                  </button>
                ) : (
                  <button onClick={handlePause} className="btn-secondary py-1 px-3 text-xs border-amber-500/40 text-amber-300">
                    <Pause className="w-3.5 h-3.5" /> Pause
                  </button>
                )}
                <button onClick={handleStep} className="btn-secondary py-1 px-2 text-xs" title="Step forward 1 second">
                  <FastForward className="w-3.5 h-3.5" />
                </button>
                <button onClick={handleReset} className="btn-secondary py-1 px-2 text-xs" title="Reset simulation">
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Simulated Road Topology Visualizer */}
            <div className="relative flex-1 mt-4 rounded-xl bg-slate-950/80 border border-white/5 overflow-hidden flex flex-col items-center justify-center p-6 min-h-[360px]">
              {/* Subtle Grid Background */}
              <div 
                className="absolute inset-0 opacity-15"
                style={{
                  backgroundImage: 'radial-gradient(circle, #00f2fe 1px, transparent 1px)',
                  backgroundSize: '24px 24px'
                }}
              />

              {/* Green Corridor Active Banner */}
              {activeCorridors > 0 && (
                <div className="absolute top-4 left-4 z-10 flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-900/60 border border-purple-500/40 backdrop-blur-md">
                  <Siren className="w-4 h-4 text-purple-300 animate-spin" />
                  <span className="text-xs font-mono font-bold text-purple-200">
                    PRIORITY GREEN CORRIDOR ENGAGED: AMB-108
                  </span>
                </div>
              )}

              {/* Graphical Representation of Connected Intersections */}
              <div className="relative z-10 grid grid-cols-3 gap-8 md:gap-14 my-auto">
                {junctions.map((j) => (
                  <div key={j.id} className="flex flex-col items-center gap-2">
                    <div className="relative p-3.5 rounded-xl bg-slate-900/90 border border-cyan-500/20 shadow-lg flex flex-col items-center gap-2 min-w-[110px]">
                      {/* Junction ID badge */}
                      <span className="text-[11px] font-mono text-cyan-400 font-bold">{j.id}</span>
                      
                      {/* Signal Head */}
                      <div className="flex gap-1.5 p-1.5 rounded-full bg-black/60 border border-white/10">
                        <div className={`w-3.5 h-3.5 rounded-full ${j.currentPhase.includes('RED') ? 'bg-red-500 shadow-[0_0_8px_#ef4444]' : 'bg-red-950/40'}`} />
                        <div className={`w-3.5 h-3.5 rounded-full ${j.currentPhase === 'YELLOW' ? 'bg-amber-400 shadow-[0_0_8px_#f59e0b]' : 'bg-amber-950/40'}`} />
                        <div className={`w-3.5 h-3.5 rounded-full ${j.currentPhase.includes('GREEN') ? 'bg-emerald-400 shadow-[0_0_8px_#10b981]' : 'bg-emerald-950/40'}`} />
                      </div>

                      {/* Name & Elapsed */}
                      <span className="text-[10px] text-slate-300 text-center font-medium leading-tight">
                        {j.name.replace(' Junction', '')}
                      </span>
                      <span className="text-[9px] font-mono text-slate-400">
                        Hold: {j.elapsed}s
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Status Footer on Canvas */}
              <div className="absolute bottom-3 left-4 right-4 flex items-center justify-between text-[11px] text-slate-400 border-t border-white/5 pt-2">
                <span>Microscopic Engine: Eclipse SUMO + TraCI Adapter</span>
                <span>Controller: Max-Pressure & Safe Deterministic Fallback</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Junction Inspector & Network Graph (3 Cols) */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          <div className="glass-panel p-4 flex flex-col flex-1">
            <div className="flex items-center justify-between pb-2 border-b border-white/5 mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-cyan-400" /> Junction Telemetry
              </span>
              <span className="badge-neon badge-green">NetworkX Graph</span>
            </div>

            <div className="flex flex-col gap-2.5 overflow-y-auto max-h-[520px] pr-1">
              {junctions.map(j => (
                <div key={j.id} className="p-2.5 rounded-lg bg-black/30 border border-white/5 flex flex-col gap-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-xs text-white">{j.name}</span>
                    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                      j.currentPhase.includes('GREEN') 
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : j.currentPhase === 'YELLOW'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-red-500/20 text-red-300 border border-red-500/30'
                    }`}>
                      {j.currentPhase}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>Queue Length:</span>
                    <span className="font-mono text-slate-200">{j.queueVehicles} veh</span>
                  </div>

                  {/* Queue progress bar */}
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-cyan-500 to-amber-500 h-full rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(100, (j.queueVehicles / 10) * 100)}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-500 pt-0.5">
                    <span>Min-Green Constraint: {j.minGreen}s</span>
                    <span>Safety: OK</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="glass-panel py-3 px-4 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
        <div className="flex items-center gap-4">
          <span>UATMMS Core Architecture v0.1.0</span>
          <span>•</span>
          <span>FastAPI Modular Monolith</span>
          <span>•</span>
          <span>SUMO Source of Truth</span>
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px] text-slate-500">
          <span>Target City Grid: Bangalore Urban CBD (6–12 Intersections)</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
