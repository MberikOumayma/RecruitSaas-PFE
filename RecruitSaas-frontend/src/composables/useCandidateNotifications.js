// composables/useCandidateNotifications.js
import { ref, computed } from 'vue'
import api from '@/services/api'

const _notifications = ref([])
const _loading       = ref(false)
const _initialized   = ref(false)
let   _pollTimer     = null

// ── Cache des statuts précédents pour détecter les changements ──
let _previousStatuts = {}   // { [candidatureId]: statut }
let _statusPollTimer = null

function getCandidateId() {
  const token = localStorage.getItem('token') || localStorage.getItem('authToken') || ''
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.candidatId ?? payload.nameid ?? payload.sub ?? null
  } catch { return null }
}

export function useCandidateNotifications() {

  const unreadCount = computed(() => _notifications.value.filter(n => !n.isRead).length)
  const unread      = computed(() => _notifications.value.filter(n => !n.isRead))

  async function fetchNotifications() {
    const candidatId = getCandidateId()
    if (!candidatId) return
    _loading.value = true
    try {
      const { data } = await api.get('/candidat/notifications')
      if (Array.isArray(data)) {
        const savedRead = JSON.parse(
          localStorage.getItem(`notif_read_candidat_${candidatId}`) || '[]'
        )
        const allRead = new Set(savedRead)
        _notifications.value = data.map(n => ({
          ...n,
          isRead: n.isRead || allRead.has(n.id)
        }))
      }
    } catch (e) {
      console.error('[useCandidateNotifications] fetch error:', e)
    } finally {
      _initialized.value = true
      _loading.value     = false
    }
  }

  // ── ★ POLL STATUTS toutes les 30s ──────────────────────────────────────
  // Appelle GET /candidat/mes-candidatures, compare avec le cache,
  // et crée une notification locale si un statut a changé.
  async function _checkStatusChanges() {
    try {
      const { data } = await api.get('/candidat/mes-candidatures')
      const list = Array.isArray(data) ? data : (data?.data || data?.items || data?.value || [])

      for (const item of list) {
        const id       = item.id
        const newStat  = item.statut || 'Nouvelle'
        const prevStat = _previousStatuts[id]

        if (prevStat === undefined) {
          // Premier fetch : on initialise le cache sans notifier
          _previousStatuts[id] = newStat
          continue
        }

        if (prevStat !== newStat) {
          // ★ Statut changé → on met à jour le cache et on notifie localement
          _previousStatuts[id] = newStat
          _pushLocalNotification(item, newStat)
        }
      }
    } catch (e) {
      console.warn('[useCandidateNotifications] status poll error:', e)
    }
  }

  // Crée une notification dans _notifications sans appel API
  // (le backend a déjà créé la vraie notif via UpdateStatut)
  // On fetch depuis l'API pour avoir la notif officielle
  function _pushLocalNotification(item, newStatut) {
    const s = newStatut.toLowerCase().trim()
    let type, title, body

    if (['acceptée', 'accepté', 'accepted'].includes(s)) {
      type  = 'application_accepted'
      title = '🎉 Application Accepted!'
      body  = `Your application for "${item.titreOffre || item.titre}" has been accepted.`
    } else if (['refusée', 'refusé', 'rejected'].includes(s)) {
      type  = 'application_rejected'
      title = 'Application Not Selected'
      body  = `Your application for "${item.titreOffre || item.titre}" was not selected.`
    } else if (['entretien', 'interview'].includes(s)) {
      type  = 'interview_scheduled'
      title = '📅 Interview Scheduled'
      body  = `An interview has been scheduled for "${item.titreOffre || item.titre}".`
    } else if (['en cours', 'screening'].includes(s)) {
      type  = 'application_in_progress'
      title = '⏳ Application In Review'
      body  = `Your application for "${item.titreOffre || item.titre}" is being reviewed.`
    } else {
      return // "Nouvelle" ou inconnu → pas de notif
    }

    // Injecte directement dans le store local (optimistic),
    // puis re-fetch pour synchroniser avec le vrai ID backend
    const tempNotif = {
      id:           crypto.randomUUID(),
      type,
      title,
      body,
      isRead:       false,
      creeLe:       new Date().toISOString(),
      offreId:      item.offreId || null,
      candidatureId: item.id
    }

    _notifications.value = [tempNotif, ..._notifications.value]

    // Re-fetch 1s après pour remplacer la notif temp par la vraie
    setTimeout(fetchNotifications, 1000)
  }

  async function markRead(id) {
    const candidatId = getCandidateId()
    const n = _notifications.value.find(n => n.id === id)
    if (!n || n.isRead) return
    n.isRead = true
    if (candidatId) {
      const readIds = _notifications.value.filter(n => n.isRead).map(n => n.id)
      localStorage.setItem(`notif_read_candidat_${candidatId}`, JSON.stringify(readIds))
    }
    try {
      await api.patch(`/candidat/notifications/${id}/read`)
    } catch (e) {
      console.error('[useCandidateNotifications] markRead error:', e)
      n.isRead = false
    }
  }

  async function markAllRead() {
    const candidatId = getCandidateId()
    _notifications.value.forEach(n => { n.isRead = true })
    if (candidatId) {
      const readIds = _notifications.value.map(n => n.id)
      localStorage.setItem(`notif_read_candidat_${candidatId}`, JSON.stringify(readIds))
    }
    try {
      await api.patch('/candidat/notifications/mark-all-read')
    } catch (e) {
      console.error('[useCandidateNotifications] markAllRead error:', e)
    }
  }

  // ── Démarrer les deux pollings ───────────────────────────────────────────
  function startPolling(intervalMs = 60000) {
    if (_pollTimer) return
    fetchNotifications()
    _pollTimer = setInterval(fetchNotifications, intervalMs)

    // ★ Polling statuts toutes les 60s
    _checkStatusChanges()  // premier check immédiat (init cache)
    _statusPollTimer = setInterval(_checkStatusChanges, 60000)
  }

  function stopPolling() {
    if (_pollTimer)       { clearInterval(_pollTimer);       _pollTimer = null }
    if (_statusPollTimer) { clearInterval(_statusPollTimer); _statusPollTimer = null }
  }

  async function refreshNow() {
    await fetchNotifications()
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
    stopPolling,
    refreshNow,
  }
}