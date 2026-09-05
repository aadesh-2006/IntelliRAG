import { fetchApi } from './client'
import { authStorage } from './authStorage'

export interface User {
  id: string
  email: string
  created_at: string
  updated_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export async function registerUser(email: string, password: string): Promise<User> {
  return fetchApi<User>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export async function loginUser(email: string, password: string): Promise<TokenResponse> {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)

  const tokenData = await fetchApi<TokenResponse>('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  })
  authStorage.setToken(tokenData.access_token)
  return tokenData
}

export async function getCurrentUser(): Promise<User> {
  return fetchApi<User>('/api/auth/me')
}

export function logoutUser(): void {
  authStorage.removeToken()
}