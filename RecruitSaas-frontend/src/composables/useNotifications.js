// composables/useNotifications.js
import { ref, computed } from 'vue'
import api from '@/services/api'

const _notifications = ref([])
const _loading       = ref(false)
const _initialized   = ref(false)
let   _pollTimer     = null

function getExpertId() {
  const token = localStorage.getItem('token') || localStorage.getItem('authToken') || ''
  if (!token) return null
  try { return JSON.parse(atob(token.split('.')[1])).expertId ?? null } catch { return null }
}

export function useNotifications() {

  const unreadCount = computed(() => _notifications.value.filter(n => !n.read).length)
  const unread      = computed(() => _notifications.value.filter(n => !n.read))

  async function fetchNotifications() {
    const expertId = getExpertId()
    if (!expertId) return

    _loading.value = true

    try {
      const { data } = await api.get(`/expert/${expertId}/notifications/feed`)
      if (Array.isArray(data)) {
        const savedRead = JSON.parse(localStorage.getItem(`notif_read_${expertId}`) || '[]')
        const allRead   = new Set([
          ...savedRead,
          ..._notifications.value.filter(n => n.read).map(n => n.id)
        ])
        _notifications.value = data.map(n => ({
          ...n,
          read: allRead.has(n.id) || n.read
        }))
      }
    } catch {
      try {
        const [candRes] = await Promise.all([
          api.get(`/expert/${expertId}/candidatures`),
          api.get(`/expert/${expertId}/offres`)
        ])
        const cands = Array.isArray(candRes.data) ? candRes.data : []
        const now   = Date.now()
        const notifs = []

        cands
          .filter(c => c.statut === 'Nouvelle' && c.creeLe)
          .filter(c => now - new Date(c.creeLe).getTime() < 86400000)
          .slice(0, 5)
          .forEach(c => notifs.push({
            id:         `app_${c.id}`,
            type:       'new_application',
            title:      'New application received',
            body:       `${c.candidatNomComplet} applied for "${c.offreTitre}"`,
            creeLe:     c.creeLe,
            read:       false,
            offreId:    c.offreId,
            candidatId: c.id
          }))

        cands
          .filter(c => !c.avisExpert && c.statut !== 'Refusée' && c.statut !== 'Acceptée')
          .slice(0, 3)
          .forEach(c => notifs.push({
            id:         `eval_${c.id}`,
            type:       'eval_reminder',
            title:      'Evaluation pending',
            body:       `${c.candidatNomComplet} is waiting for your review on "${c.offreTitre}"`,
            creeLe:     c.creeLe,
            read:       false,
            offreId:    c.offreId,
            candidatId: c.id
          }))

        const savedRead     = JSON.parse(localStorage.getItem(`notif_read_${expertId}`) || '[]')
        const readSet       = new Set([...savedRead, ..._notifications.value.filter(n => n.read).map(n => n.id)])
        const savedPrefs    = JSON.parse(localStorage.getItem(`notif_prefs_${expertId}`) || '[]')
        const disabledTypes = savedPrefs.filter(p => !p.enabled).map(p => p.id)

        _notifications.value = notifs
          .filter(n => !disabledTypes.includes(n.type))
          .map(n => ({ ...n, read: readSet.has(n.id) }))
          .sort((a, b) => new Date(b.creeLe) - new Date(a.creeLe))

      } catch (e2) {
        console.error('[useNotifications] fallback error', e2)
      }
    } finally {
      _initialized.value = true
      _loading.value     = false
    }
  }

  function markRead(id) {
    const expertId = getExpertId()
    const n = _notifications.value.find(n => n.id === id)
    if (n) {
      n.read = true
      if (expertId) {
        const readIds = _notifications.value.filter(n => n.read).map(n => n.id)
        localStorage.setItem(`notif_read_${expertId}`, JSON.stringify(readIds))
        api.patch(`/expert/${expertId}/notifications/${id}/read`).catch(() => {})
      }
    }
  }

  function markAllRead() {
    const expertId = getExpertId()
    _notifications.value.forEach(n => { n.read = true })
    if (expertId) {
      const readIds = _notifications.value.map(n => n.id)
      localStorage.setItem(`notif_read_${expertId}`, JSON.stringify(readIds))
    }
  }

  function startPolling() {
    if (_pollTimer) return
    fetchNotifications()
    _pollTimer = setInterval(fetchNotifications, 30000)
  }

  function stopPolling() {
    if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null }
  }

  return {
    notifications: _notifications,
    unread,
    unreadCount,
    loading:       _loading,
    initialized:   _initialized,
    fetchNotifications,
    markRead,
    markAllRead,
    startPolling,
    stopPolling
  }
}