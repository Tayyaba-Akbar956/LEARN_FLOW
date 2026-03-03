import { betterAuth } from 'better-auth/client'

export interface User {
  id: string
  email: string
  name: string
  role: 'student' | 'teacher'
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

// Better Auth client configuration
export const authClient = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:8000',
  credentials: 'include',
})

// Token management
export const tokenManager = {
  getToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('auth_token')
  },

  setToken(token: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem('auth_token', token)
  },

  removeToken(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem('auth_token')
  },

  decodeToken(token: string): User | null {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return {
        id: payload.sub,
        email: payload.email,
        name: payload.name,
        role: payload.role,
      }
    } catch {
      return null
    }
  },
}

// Authentication methods
export const auth = {
  async login(email: string, password: string): Promise<{ user: User; token: string }> {
    const response = await authClient.signIn.email({
      email,
      password,
    })

    if (!response.data?.token) {
      throw new Error('Authentication failed')
    }

    const token = response.data.token
    tokenManager.setToken(token)

    const user = tokenManager.decodeToken(token)
    if (!user) {
      throw new Error('Invalid token')
    }

    return { user, token }
  },

  async logout(): Promise<void> {
    await authClient.signOut()
    tokenManager.removeToken()
  },

  async getCurrentUser(): Promise<User | null> {
    const token = tokenManager.getToken()
    if (!token) return null

    return tokenManager.decodeToken(token)
  },

  async refreshToken(): Promise<string | null> {
    try {
      const response = await authClient.session()
      if (response.data?.token) {
        tokenManager.setToken(response.data.token)
        return response.data.token
      }
      return null
    } catch {
      return null
    }
  },

  isAuthenticated(): boolean {
    return !!tokenManager.getToken()
  },

  hasRole(role: 'student' | 'teacher'): boolean {
    const token = tokenManager.getToken()
    if (!token) return false

    const user = tokenManager.decodeToken(token)
    return user?.role === role
  },
}

// Session monitoring consent
export interface ConsentState {
  hasConsented: boolean
  consentedAt: string | null
}

export const consentManager = {
  getConsent(): ConsentState {
    if (typeof window === 'undefined') {
      return { hasConsented: false, consentedAt: null }
    }

    const consent = localStorage.getItem('session_monitoring_consent')
    if (!consent) {
      return { hasConsented: false, consentedAt: null }
    }

    try {
      return JSON.parse(consent)
    } catch {
      return { hasConsented: false, consentedAt: null }
    }
  },

  setConsent(consented: boolean): void {
    if (typeof window === 'undefined') return

    const state: ConsentState = {
      hasConsented: consented,
      consentedAt: consented ? new Date().toISOString() : null,
    }

    localStorage.setItem('session_monitoring_consent', JSON.stringify(state))
  },

  hasConsented(): boolean {
    return this.getConsent().hasConsented
  },

  clearConsent(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem('session_monitoring_consent')
  },
}
