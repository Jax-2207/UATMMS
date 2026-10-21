export const API_BASE_URL: string = 
  (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

export const WS_BASE_URL: string = 
  (import.meta as any).env?.VITE_WS_BASE_URL || 'ws://localhost:8000/ws/simulation';

export const DEFAULT_SCENARIO: string = 'bengaluru_core';
