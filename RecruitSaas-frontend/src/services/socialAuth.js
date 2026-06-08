const API_ORIGIN = import.meta.env.VITE_API_ORIGIN || "http://localhost:5202"

const PROVIDER_LABELS = {
  google: "Google",
  facebook: "Facebook",
  linkedin: "LinkedIn"
}

/**
 * @returns {Promise<string[]>}
 */
export async function fetchConfiguredProviders() {
  try {
    const res = await fetch(`${API_ORIGIN}/api/auth/external/providers`, {
      credentials: "include"
    })
    if (!res.ok) return []
    const data = await res.json()
    return Array.isArray(data.providers) ? data.providers : []
  } catch {
    return []
  }
}

/**
 * Redirects the browser to the backend OAuth challenge.
 * @param {'google'|'facebook'|'linkedin'} provider
 * @param {string} [returnUrl]
 */
export function loginWithProvider(provider, returnUrl = "/dashboard") {
  const params = new URLSearchParams()
  if (returnUrl) params.set("returnUrl", returnUrl)
  const qs = params.toString()
  window.location.href = `${API_ORIGIN}/api/auth/external/${provider}${qs ? `?${qs}` : ""}`
}

export function getProviderLabel(provider) {
  return PROVIDER_LABELS[provider] || provider
}

export function getApiOrigin() {
  return API_ORIGIN
}
