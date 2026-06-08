// ✅ @/utils/savedOffres.js
import axios from 'axios'

// 🎯 Utiliser le MÊME port que vos autres APIs fonctionnelles
const API_BASE_URL = 'http://localhost:5202/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Clé localStorage pour le cache local des IDs sauvegardées
const SAVED_JOBS_KEY = 'saved_jobs_cache'

// Interceptor pour ajouter le token JWT (utilisez 'token' comme api.js)
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Gestionnaire d'erreurs global
const handleError = (error) => {
  if (error.response?.status === 401) {
    localStorage.removeItem('token')
    window.dispatchEvent(new CustomEvent('auth-required'))
  }
  return Promise.reject(error)
}

api.interceptors.response.use(res => res, handleError)

// ─────────────────────────────────────────────────────────────
// ✅ FONCTIONS PRIVÉES (cache localStorage)
// ─────────────────────────────────────────────────────────────

function _getSavedIdsFromCache() {
  try {
    const raw = localStorage.getItem(SAVED_JOBS_KEY)
    if (!raw) return new Set()
    const parsed = JSON.parse(raw)
    return new Set(Array.isArray(parsed) ? parsed : [])
  } catch {
    return new Set()
  }
}

function _saveIdsToCache(ids) {
  try {
    localStorage.setItem(SAVED_JOBS_KEY, JSON.stringify(Array.from(ids)))
  } catch (e) {
    console.warn('[savedOffres] Failed to update cache:', e)
  }
}

// ─────────────────────────────────────────────────────────────
// ✅ FONCTIONS EXPORTÉES (utilisées par les composants Vue)
// ─────────────────────────────────────────────────────────────

/**
 * ✅ Récupérer le nombre d'offres sauvegardées (pour le badge sidebar)
 * @returns {number}
 */
export const getSavedCount = () => {
  return _getSavedIdsFromCache().size
}

/**
 * Récupérer la liste complète des offres sauvegardées depuis l'API
 * @returns {Promise<Array>}
 */
export const fetchSavedJobs = async () => {
  const response = await api.get('/savedjobs')
  const data = response.data || []
  
  // Mettre à jour le cache local
  const ids = new Set(data.map(sj => String(sj.offreId)))
  _saveIdsToCache(ids)
  
  return data
}

/**
 * Sauvegarder une offre
 * @param {string|Guid} offreId 
 * @returns {Promise<Object>}
 */
export const saveJob = async (offreId) => {
  const response = await api.post('/savedjobs', { offreId })
  
  // Mettre à jour le cache local
  const ids = _getSavedIdsFromCache()
  ids.add(String(offreId))
  _saveIdsToCache(ids)
  
  // Notifier les autres composants
  window.dispatchEvent(new CustomEvent('saved-jobs-changed', {
    detail: { offreId, saved: true }
  }))
  
  return response.data
}

/**
 * Retirer une offre des sauvegardées
 * @param {string|Guid} offreId 
 * @returns {Promise<void>}
 */
export const unsaveJob = async (offreId) => {
  await api.delete(`/savedjobs/${offreId}`)
  
  // Mettre à jour le cache local
  const ids = _getSavedIdsFromCache()
  ids.delete(String(offreId))
  _saveIdsToCache(ids)
  
  // Notifier les autres composants
  window.dispatchEvent(new CustomEvent('saved-jobs-changed', {
    detail: { offreId, saved: false }
  }))
}

/**
 * Vérifier si une offre est sauvegardée (lecture cache uniquement)
 * @param {string|Guid} offreId 
 * @returns {boolean}
 */
export const isJobSaved = (offreId) => {
  return _getSavedIdsFromCache().has(String(offreId))
}

/**
 * Forcer la synchronisation du cache avec l'API
 * @returns {Promise<Set<string>>}
 */
export const syncSavedCache = async () => {
  try {
    const savedJobs = await fetchSavedJobs()
    const ids = new Set(savedJobs.map(sj => String(sj.offreId)))
    _saveIdsToCache(ids)
    return ids
  } catch {
    return _getSavedIdsFromCache()
  }
}