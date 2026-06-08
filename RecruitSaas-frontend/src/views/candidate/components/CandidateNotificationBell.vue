<template>
  <div class="notif-bell-wrap" ref="wrapRef">

    <!-- ── Cloche ── -->
    <button
      class="bell-btn"
      :class="{ 'has-notif': unreadCount > 0, 'open': open }"
      @click="toggle"
      aria-label="Notifications"
    >
      <svg class="bell-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"
          stroke="currentColor" stroke-width="1.8"
          stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"
          stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      </svg>

      <!-- Badge count -->
      <transition name="badge-pop">
        <span v-if="unreadCount > 0" class="bell-badge">
          {{ unreadCount > 9 ? '9+' : unreadCount }}
        </span>
      </transition>

      <!-- Pulse ring quand nouvelles notifs -->
      <span v-if="unreadCount > 0" class="bell-pulse"></span>
    </button>

    <!-- ── Dropdown panel ── -->
    <transition name="panel-slide">
      <div v-if="open" class="notif-panel">

        <!-- Header -->
        <div class="panel-head">
          <div class="panel-head-left">
            <span class="panel-title">Notifications</span>
            <span v-if="unreadCount > 0" class="panel-unread-pill">{{ unreadCount }} new</span>
          </div>
          <button
            v-if="unreadCount > 0"
            class="mark-all-btn"
            @click.stop="markAllRead"
          >
            Mark all read
          </button>
        </div>

        <!-- Loading -->
        <div v-if="!initialized" class="panel-loading">
          <div class="spin-sm"></div>
          <span>Loading…</span>
        </div>

        <!-- Empty -->
        <div v-else-if="notifications.length === 0" class="panel-empty">
          <div class="empty-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"
                stroke="currentColor" stroke-width="1.5"
                stroke-linecap="round" stroke-linejoin="round" opacity="0.4"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"
                stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
            </svg>
          </div>
          <p class="empty-title">All caught up!</p>
          <p class="empty-sub">No new notifications at the moment.</p>
        </div>

        <!-- Liste -->
        <div v-else class="notif-list">
          <div
            v-for="(n, i) in notifications"
            :key="n.id"
            class="notif-item"
            :class="{ unread: !n.isRead, ['type-' + n.type]: true }"
            :style="{ animationDelay: i * 40 + 'ms' }"
            @click="handleClick(n)"
          >
            <!-- Icône type -->
            <div class="notif-icon" :class="'icon-' + n.type">
              
              <!-- application_accepted -->
              <svg v-if="n.type === 'application_accepted'" width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              
              <!-- application_rejected -->
              <svg v-else-if="n.type === 'application_rejected'" width="14" height="14" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              
              <!-- interview_scheduled -->
              <svg v-else-if="n.type === 'interview_scheduled'" width="14" height="14" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
              </svg>
              
              <!-- application_in_progress -->
              <svg v-else-if="n.type === 'application_in_progress'" width="14" height="14" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>

              <!-- ★ quiz_invitation -->
              <svg v-else-if="n.type === 'quiz_invitation'" width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" 
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <polyline points="10 9 9 9 8 9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              
              <!-- default -->
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>

            <!-- Contenu -->
            <div class="notif-body">
              <p class="notif-title">{{ n.title }}</p>
              <p class="notif-text">{{ n.body }}</p>
              <p class="notif-time">{{ timeAgo(n.creeLe) }}</p>
            </div>

            <!-- Dot non-lu -->
            <span v-if="!n.isRead" class="unread-dot"></span>
          </div>
        </div>

        <!-- Footer -->
        <div class="panel-foot">
          <button class="view-all-btn" @click="goToApplications">
            View all applications
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
              <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCandidateNotifications } from '@/composables/useCandidateNotifications'

const router = useRouter()
const { 
  notifications, 
  unreadCount, 
  initialized, 
  markRead, 
  markAllRead, 
  startPolling, 
  stopPolling 
} = useCandidateNotifications()

const open    = ref(false)
const wrapRef = ref(null)

// ★ Optionnel : son de notification quand nouvelles notifs arrivent
const previousUnread = ref(0)
watch(unreadCount, (newVal, oldVal) => {
  if (newVal > oldVal && newVal > 0 && typeof Audio !== 'undefined') {
    const audio = new Audio('/sounds/notification-soft.mp3')
    audio.volume = 0.2
    audio.play().catch(() => {}) // Ignorer si autoplay bloqué
  }
  previousUnread.value = newVal
})

function toggle() { 
  open.value = !open.value 
}

function handleClick(n) {
  // Marquer comme lue
  markRead(n.id)
  open.value = false
  
  // ★ Navigation selon le type de notification
  if (n.type === 'quiz_invitation' && n.quizToken) {
    // Rediriger vers le quiz avec le token
    router.push(`/quiz/${n.quizToken}`)
  } 
  else if (n.offreId) {
    router.push({ path: '/offres', query: { id: n.offreId } })
  } 
  else if (n.candidatureId) {
    router.push('/applications')
  } 
  else {
    router.push('/applications')
  }
}

function goToApplications() {
  open.value = false
  router.push('/applications')
}

function timeAgo(d) {
  if (!d) return ''
  const diff = Date.now() - new Date(d).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1)  return 'Just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const days = Math.floor(h / 24)
  if (days < 7) return `${days}d ago`
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

// Fermeture clic extérieur
function onOutsideClick(e) {
  if (wrapRef.value && !wrapRef.value.contains(e.target)) {
    open.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', onOutsideClick)
  startPolling()
})

onUnmounted(() => {
  document.removeEventListener('mousedown', onOutsideClick)
  stopPolling()
})
</script>

<style scoped>
/* ── Wrapper ── */
.notif-bell-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

/* ── Cloche ── */
.bell-btn {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 11px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s, transform 0.12s;
  outline: none;
  flex-shrink: 0;
}
.bell-btn:hover,
.bell-btn.open {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #1A2B4C;
}
.bell-btn.has-notif { color: #1A2B4C; border-color: rgba(26,43,76,0.25); }
.bell-btn:active { transform: scale(0.95); }

/* Icône animation légère */
.bell-btn.has-notif .bell-icon {
  animation: bell-sway 2.5s ease-in-out infinite 1s;
  transform-origin: top center;
}
@keyframes bell-sway {
  0%,100% { transform: rotate(0deg); }
  15%      { transform: rotate(14deg); }
  30%      { transform: rotate(-12deg); }
  45%      { transform: rotate(8deg); }
  60%      { transform: rotate(-6deg); }
  75%      { transform: rotate(3deg); }
}

/* Badge count */
.bell-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 18px;
  height: 18px;
  background: #ef4444;
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  border-radius: 99px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 2px solid #fff;
  font-family: inherit;
  line-height: 1;
}
.badge-pop-enter-active { animation: badge-pop 0.3s cubic-bezier(0.34,1.56,0.64,1); }
.badge-pop-leave-active { animation: badge-pop 0.15s ease reverse; }
@keyframes badge-pop { from { transform: scale(0); opacity: 0; } to { transform: scale(1); opacity: 1; } }

/* Pulse ring */
.bell-pulse {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(239,68,68,0.35);
  animation: pulse-ring 2s ease-out infinite;
  pointer-events: none;
}
@keyframes pulse-ring {
  0%   { transform: scale(1); opacity: 0.7; }
  70%  { transform: scale(2.2); opacity: 0; }
  100% { transform: scale(2.2); opacity: 0; }
}

/* ── Panel ── */
.notif-panel {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 360px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
  z-index: 999;
  overflow: hidden;
  transform-origin: top right;
}
.panel-slide-enter-active { animation: panel-in 0.22s cubic-bezier(0.34,1.4,0.64,1); }
.panel-slide-leave-active { animation: panel-in 0.15s ease reverse; }
@keyframes panel-in { from { opacity: 0; transform: scale(0.92) translateY(-6px); } to { opacity: 1; transform: scale(1) translateY(0); } }

/* Panel header */
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px 12px;
  border-bottom: 1px solid #f1f5f9;
}
.panel-head-left { display: flex; align-items: center; gap: 8px; }
.panel-title {
  font-size: 0.92rem;
  font-weight: 800;
  color: #0f172a;
  font-family: 'Plus Jakarta Sans', 'Inter', system-ui, sans-serif;
}
.panel-unread-pill {
  background: #eff6ff;
  color: #2563eb;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 99px;
  font-family: inherit;
}
.mark-all-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.73rem;
  font-weight: 600;
  color: #3b82f6;
  padding: 4px 8px;
  border-radius: 6px;
  font-family: inherit;
  transition: background 0.12s;
}
.mark-all-btn:hover { background: #eff6ff; }

/* Loading */
.panel-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 24px 18px;
  color: #94a3b8;
  font-size: 0.82rem;
  font-family: inherit;
}
.spin-sm {
  width: 14px; height: 14px;
  border: 2px solid #e2e8f0;
  border-top-color: #1A2B4C;
  border-radius: 50%;
  animation: spin 0.65s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Empty */
.panel-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 20px;
  gap: 6px;
}
.empty-icon { width: 52px; height: 52px; background: #f8fafc; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 4px; color: #94a3b8; }
.empty-title { font-size: 0.88rem; font-weight: 700; color: #1e293b; margin: 0; font-family: inherit; }
.empty-sub   { font-size: 0.76rem; color: #94a3b8; margin: 0; font-family: inherit; }

/* Liste */
.notif-list { max-height: 380px; overflow-y: auto; }
.notif-list::-webkit-scrollbar { width: 4px; }
.notif-list::-webkit-scrollbar-track { background: transparent; }
.notif-list::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 99px; }

/* Item */
.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  padding: 13px 18px;
  border-bottom: 1px solid #f8fafc;
  cursor: pointer;
  transition: background 0.12s;
  position: relative;
  animation: item-in 0.3s both;
}
.notif-item:last-child { border-bottom: none; }
.notif-item:hover { background: #f8fafc; }
.notif-item.unread { background: #fefbff; }
.notif-item.unread:hover { background: #f5f0ff; }

@keyframes item-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

/* Icône type */
.notif-icon {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}
.icon-application_accepted    { background: #f0fdf4; color: #16a34a; }
.icon-application_rejected    { background: #fef2f2; color: #ef4444; }
.icon-interview_scheduled     { background: #eff6ff; color: #2563eb; }
.icon-application_in_progress { background: #fefce8; color: #ca8a04; }
.icon-quiz_invitation         { background: #f0f9ff; color: #0284c7; }  /* ★ Quiz */
.icon-default                 { background: #f8fafc; color: #64748b; }

/* Body */
.notif-body { flex: 1; min-width: 0; }
.notif-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 2px;
  font-family: 'Plus Jakarta Sans', 'Inter', system-ui, sans-serif;
  line-height: 1.3;
}
.notif-text {
  font-size: 0.74rem;
  color: #475569;
  margin: 0 0 4px;
  font-family: inherit;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.notif-time { font-size: 0.66rem; color: #94a3b8; margin: 0; font-family: inherit; }

/* Dot non-lu */
.unread-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #3b82f6;
  flex-shrink: 0;
  margin-top: 6px;
}

/* Footer */
.panel-foot {
  padding: 10px 18px 12px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: center;
}
.view-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.76rem;
  font-weight: 700;
  color: #64748b;
  font-family: 'Plus Jakarta Sans', 'Inter', system-ui, sans-serif;
  padding: 5px 10px;
  border-radius: 7px;
  transition: background 0.12s, color 0.12s;
}
.view-all-btn:hover { background: #f1f5f9; color: #1A2B4C; }
</style>