export interface Vehicle {
  vehicle_id: string;
  edge_id: string;
  lane_index: number;
  position_m: number;
  speed_mps: number;
  vehicle_type: 'passenger_car' | 'two_wheeler' | 'auto_rickshaw' | 'city_bus' | 'emergency_ambulance' | string;
}

export interface JunctionSignal {
  junction_id: string;
  current_phase_index: number;
  current_phase_name: string;
  elapsed_time_s: number;
  min_green_s: number;
  max_green_s: number;
}

export interface SimulationState {
  run_id: string;
  status: 'running' | 'paused' | 'stopped' | 'error';
  step: number;
  simulation_time_s: number;
  active_vehicle_count: number;
  average_speed_mps: number;
  average_waiting_time_s: number;
  vehicles: Vehicle[];
  signals: JunctionSignal[];
  metadata: {
    engine?: string;
    mode?: string;
    scenario_id?: string;
    backend_version?: string;
  };
}

export interface NetworkNode {
  id: string;
  name: string;
  x: number;
  y: number;
  lat: number;
  lon: number;
  signalized: boolean;
  phases: string[];
}

export interface NetworkLink {
  id: string;
  source: string;
  target: string;
  street_name: string;
  length_m: number;
  speed_limit_kph: number;
  lanes: number;
  priority: number;
}

export interface NetworkGraphData {
  network_name: string;
  junction_count: number;
  edge_count: number;
  nodes: NetworkNode[];
  links: NetworkLink[];
}

export interface EmergencyRequestPayload {
  vehicle_id: string;
  vehicle_type: 'ambulance' | 'fire_brigade' | 'police';
  origin_edge_id: string;
  destination_edge_id: string;
  urgency_level: number;
  notes?: string;
}

export interface IncidentReportPayload {
  incident_type: 'blocked_lane' | 'accident' | 'animal_crossing' | 'rash_driving' | 'signal_failure';
  edge_id: string;
  lane_index?: number;
  severity: number;
  description?: string;
}
