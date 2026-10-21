import { API_BASE_URL } from '../../utils/constants';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`GET ${endpoint} failed (${response.status}): ${errorBody}`);
    }

    return response.json();
  }

  async post<T>(endpoint: string, data?: unknown, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: data !== undefined ? JSON.stringify(data) : undefined,
      ...options,
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`POST ${endpoint} failed (${response.status}): ${errorBody}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
