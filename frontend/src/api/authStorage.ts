const TOKEN_KEY = 'intellirag_access_token'

export const authStorage = {
  getToken(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY)
    } catch {
      return null
    }
  },
  setToken(token: string): void {
    try {
      localStorage.setItem(TOKEN_KEY, token)
    } catch {
    }
  },
  removeToken(): void {
    try {
      localStorage.removeItem(TOKEN_KEY)
    } catch {
    }
  }
}