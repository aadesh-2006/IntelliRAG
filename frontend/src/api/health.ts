import { fetchApi } from './client'

export interface HealthStatus {
  status: string
  service: string
  version: string
  environment: string
}

export async function checkBackendHealth(): Promise<HealthStatus> {
  return fetchApi<HealthStatus>('/api/health')
}
