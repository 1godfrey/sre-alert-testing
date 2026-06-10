const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'

export interface HealthResponse {
  status: 'ok'
  service: string
}

export interface EndpointInfo {
  name: string
  path: string
  target_uptime: number
}

export interface EndpointStats extends EndpointInfo {
  total_requests: number
  success_count: number
  failure_count: number
  observed_success_ratio: number | null
}

export interface StatsResponse {
  endpoints: EndpointStats[]
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`${path} returned HTTP ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function fetchHealth(): Promise<HealthResponse> {
  return getJson<HealthResponse>('/health')
}

export function fetchStats(): Promise<StatsResponse> {
  return getJson<StatsResponse>('/stats')
}

export function fetchEndpoints(): Promise<EndpointInfo[]> {
  return getJson<EndpointInfo[]>('/')
}
