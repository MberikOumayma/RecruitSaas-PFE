import { reactive } from 'vue'
import api from '../services/api'

function decodePayload(token) {
  const part = token.split('.')[1]
  if (!part) return null
  return JSON.parse(atob(part))
}

/** Returns true if token is missing, malformed, or past exp. */
export function isTokenExpired(token) {
  if (!token) return true
  try {
    const payload = decodePayload(token)
    if (!payload?.exp) return false
    return Date.now() >= payload.exp * 1000
  } catch {
    return true
  }
}

function mergeUserFromProfile(base, profile) {
  if (!profile) return base
  return {
    ...base,
    username: profile.fullName || profile.FullName || base?.username || 'User',
    fullName: profile.fullName || profile.FullName || base?.fullName,
    email: profile.email || profile.Email || base?.email,
    photoUrl: profile.photoUrl || profile.PhotoUrl || base?.photoUrl,
    role: profile.role || profile.Role || base?.role,
  }
}

export const authStore = reactive({
  user: null,
  token: localStorage.getItem('token'),

  init() {
    this.token = localStorage.getItem('token')
    if (!this.token) {
      this.user = null
      return
    }
    if (isTokenExpired(this.token)) {
      this.logout()
      return
    }
    try {
      const payload = decodePayload(this.token)
      this.user = {
        username:
          payload.userName ||
          payload["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"] ||
          'User',
        role:
          payload.role ||
          payload["http://schemas.microsoft.com/ws/2008/06/identity/claims/role"] ||
          'Tenant',
      }
    } catch (e) {
      console.error('Failed to decode token', e)
      this.logout()
    }
  },

  applyAuthResponse(data) {
    if (!data || !this.user) return
    this.user = mergeUserFromProfile(this.user, data)
  },

  async fetchCurrentUser() {
    if (!this.token || isTokenExpired(this.token)) return
    try {
      const { data } = await api.get('/auth/me')
      this.user = mergeUserFromProfile(this.user || {}, data)
    } catch (e) {
      console.warn('Could not load user profile', e)
    }
  },

  /**
   * Persists JWT and optional login payload (fullName, email, photoUrl).
   */
  setToken(token, fromLogin = {}) {
    this.token = token
    localStorage.setItem('token', token)
    this.init()
    const name = fromLogin.userName?.trim?.() || fromLogin.fullName?.trim?.()
    if (name && this.user) this.user.username = name
    this.applyAuthResponse(fromLogin)
  },

  logout() {
    this.token = null
    this.user = null
    localStorage.clear()
  },
})

authStore.init()
authStore.fetchCurrentUser()
