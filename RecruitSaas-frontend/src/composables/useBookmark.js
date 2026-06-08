// src/composables/useBookmark.js
// Utilise ce composable dans OffreList (ou n'importe quel composant)
// pour gérer le toggle bookmark d'une offre via l'API.

import { ref } from 'vue'
import { saveJob, unsaveJob, checkSaved } from '../services/savedJobsApi'

/**
 * @param {number} offreId
 * @param {boolean} initialState  — passe `true` si tu sais déjà que l'offre est sauvegardée
 */
export function useBookmark(offreId, initialState = false) {
  const isSaved  = ref(initialState)
  const loading  = ref(false)

  async function initStatus() {
    try {
      isSaved.value = await checkSaved(offreId)
    } catch { /* non authentifié → on ignore */ }
  }

  async function toggle() {
    if (loading.value) return
    loading.value = true
    try {
      if (isSaved.value) {
        await unsaveJob(offreId)
        isSaved.value = false
      } else {
        await saveJob(offreId)
        isSaved.value = true
      }
      // Notifier SavedJobsView de se recharger
      window.dispatchEvent(new CustomEvent('saved-jobs-changed', {
        detail: { offreId, saved: isSaved.value }
      }))
    } catch (e) {
      console.error('[useBookmark] toggle error:', e)
    } finally {
      loading.value = false
    }
  }

  return { isSaved, loading, toggle, initStatus }
}