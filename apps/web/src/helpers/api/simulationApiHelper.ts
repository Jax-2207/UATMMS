import { apiClient } from './apiClient';
import {
  SimulationState,
  NetworkGraphData,
  EmergencyRequestPayload,
  IncidentReportPayload
} from '../../types/simulation';

export const startSimulation = async (
  scenarioId: string = 'bengaluru_core',
  seed: number = 42
): Promise<SimulationState> => {
  return apiClient.post<SimulationState>('/api/v1/simulation/start', {
    scenario_id: scenarioId,
    seed,
    step_length_s: 1.0,
  });
};

export const pauseSimulation = async (): Promise<SimulationState> => {
  return apiClient.post<SimulationState>('/api/v1/simulation/pause');
};

export const resumeSimulation = async (): Promise<SimulationState> => {
  return apiClient.post<SimulationState>('/api/v1/simulation/resume');
};

export const resetSimulation = async (): Promise<SimulationState> => {
  return apiClient.post<SimulationState>('/api/v1/simulation/reset');
};

export const stepSimulation = async (): Promise<SimulationState> => {
  return apiClient.post<SimulationState>('/api/v1/simulation/step');
};

export const getSimulationState = async (): Promise<SimulationState> => {
  return apiClient.get<SimulationState>('/api/v1/simulation/state');
};

export const getNetworkGraph = async (): Promise<NetworkGraphData> => {
  return apiClient.get<NetworkGraphData>('/api/v1/network/graph');
};

export const dispatchEmergency = async (
  payload: EmergencyRequestPayload
): Promise<any> => {
  return apiClient.post('/api/v1/emergencies/dispatch', payload);
};

export const reportIncident = async (
  payload: IncidentReportPayload
): Promise<any> => {
  return apiClient.post('/api/v1/incidents/report', payload);
};
