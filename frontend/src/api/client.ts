import { authStorage } from './authStorage'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const cleanBase = BASE_URL.endsWith('/') ? BASE_URL.slice(0, -1) : BASE_URL
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  const url = `${cleanBase}${cleanEndpoint}`

  const token = authStorage.getToken()
  const authHeaders: Record<string, string> = token
    ? { Authorization: `Bearer ${token}` }
    : {}

  const isFormData = options?.body instanceof FormData
  const defaultHeaders: Record<string, string> = isFormData
    ? {}
    : { 'Content-Type': 'application/json' }

  const response = await fetch(url, {
    headers: {
      ...defaultHeaders,
      ...authHeaders,
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`
    try {
      const errorData = await response.json()
      if (errorData && errorData.detail) {
        errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail)
      }
    } catch {
      try {
        const errorText = await response.text()
        if (errorText) errorMessage = errorText
      } catch {
      }
    }
    throw new Error(errorMessage)
  }

  if (response.status === 204) {
    return {} as T
  }

  return response.json()
}