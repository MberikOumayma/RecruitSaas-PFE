<!-- Route : /schedule-interview/:token (candidat connecté) -->
<template>
  <div class="hs-root">
    <AppSidebar />
    <main class="hs-main">
      <GlobalHeader title="My Applications" />
      <div class="app-page">

        <!-- Loading -->
        <div v-if="loading" class="center-state">
          <div class="app-spinner"></div>
          <p>Chargement de votre invitation...</p>
        </div>

        <!-- Erreur -->
        <div v-else-if="error" class="state-card state-error">
          <div class="state-icon">✕</div>
          <h2>Lien invalide</h2>
          <p>{{ error }}</p>
          <button class="btn-primary" @click="$router.push('/applications')">Mes candidatures</button>
        </div>

        <!-- Confirmé -->
        <div v-else-if="confirmed" class="state-card state-success">
          <div class="state-icon">✓</div>
          <h2>Entretien confirmé !</h2>
          <p class="confirm-date">{{ formatDateFull(selectedSlot) }}</p>
          <p class="confirm-sub">Votre entretien est planifié. Vous recevrez un rappel par email. Le lien d'accès s'activera à l'heure exacte.</p>
          <div class="countdown-box" v-if="countdown">
            <span class="cd-label">Commence dans</span>
            <span class="cd-val">{{ countdown }}</span>
          </div>
          <button class="btn-primary" @click="$router.push('/applications')">
            Retour à mes candidatures
          </button>
        </div>

        <!-- Calendrier -->
        <div v-else class="schedule-wrap">

          <!-- Bandeau info entretien -->
          <div class="interview-banner">
            <div class="banner-left">
              <div class="banner-avatar">🤖</div>
              <div>
                <h2 class="banner-title">Invitation à un entretien</h2>
                <p class="banner-sub">{{ data.titreOffre }} — {{ data.nomEntreprise }}</p>
              </div>
            </div>
            <div class="banner-meta">
              <span class="meta-pill">⏱ 30 min</span>
              <span class="meta-pill">🎥 Virtuel</span>
            </div>
          </div>

          <!-- Calendrier de sélection -->
          <div class="cal-card">
            <div class="cal-top">
              <div>
                <h3 class="cal-title">Choisissez votre créneau</h3>
                <p class="cal-sub">Sélectionnez le créneau disponible qui vous convient le mieux.</p>
              </div>
              <div class="week-nav">
                <button class="nav-btn" @click="prevWeek" :disabled="!canGoPrev">&#8249;</button>
                <span class="week-label">{{ weekLabel }}</span>
                <button class="nav-btn" @click="nextWeek" :disabled="!canGoNext">&#8250;</button>
              </div>
            </div>

            <!-- Grille -->
            <div class="cal-grid">
              <div class="cal-header-row">
                <div v-for="day in weekDays" :key="day.iso" class="cal-day-header" :class="{ 'col-today': day.isToday }">
                  <span class="dh-name">{{ day.name }}</span>
                  <span class="dh-num" :class="{ 'dh-today': day.isToday }">{{ day.num }}</span>
                </div>
              </div>
              <div class="cal-body-row">
                <div v-for="day in weekDays" :key="day.iso" class="cal-day-col" :class="{ 'col-today': day.isToday }">
                  <template v-if="slotsByDay[day.iso] && slotsByDay[day.iso].length">
                    <button
                      v-for="slot in slotsByDay[day.iso]"
                      :key="slot.iso"
                      class="slot-btn"
                      :class="{ 'slot-selected': selectedSlot && selectedSlot.iso === slot.iso }"
                      @click="selectedSlot = slot"
                    >
                      {{ slot.time }}
                    </button>
                  </template>
                  <div v-else class="day-empty">—</div>
                </div>
              </div>
            </div>

            <!-- Aucun créneau cette semaine -->
            <div v-if="!hasSlotThisWeek" class="no-slots">
              <p>Aucun créneau disponible cette semaine</p>
              <button v-if="canGoNext" class="btn-next" @click="nextWeek">Semaine suivante →</button>
            </div>
          </div>

          <!-- Confirmation -->
          <div class="confirm-panel" v-if="selectedSlot">
            <div class="confirm-info">
              <span class="confirm-icon">📅</span>
              <div>
                <p class="confirm-label">Créneau sélectionné</p>
                <p class="confirm-date-val">{{ formatDateFull(selectedSlot) }}</p>
              </div>
            </div>
            <button class="btn-primary btn-confirm" @click="confirmer" :disabled="confirming">
              {{ confirming ? 'Confirmation...' : 'Confirmer ce créneau' }}
            </button>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<script>
import AppSidebar   from '../../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../../components/layout/GlobalHeader.vue'
import api          from '../../../services/api'

export default {
  name: 'ScheduleInterview',
  components: { AppSidebar, GlobalHeader },
  data() {
    return {
      loading:       true,
      error:         null,
      data:          {},
      allSlots:      [],
      selectedSlot:  null,
      confirming:    false,
      confirmed:     false,
      countdown:     null,
      _cdInterval:   null,
      currentMonday: this.getMonday(new Date())
    }
  },
  computed: {
    weekDays() {
      const today = new Date(); today.setHours(0, 0, 0, 0)
      return Array.from({ length: 7 }, (_, i) => {
        const d = new Date(this.currentMonday)
        d.setDate(this.currentMonday.getDate() + i)
        return {
          // Date calendaire locale (pas UTC) pour coller aux libellés lun./dim. et aux créneaux
          iso:     this.toLocalDateIso(d),
          name:    d.toLocaleDateString('fr-FR', { weekday: 'short' }),
          num:     d.getDate(),
          isToday: d.toDateString() === today.toDateString()
        }
      })
    },
    weekLabel() {
      const end = new Date(this.currentMonday); end.setDate(end.getDate() + 6)
      const o = { day: 'numeric', month: 'short' }
      return `${this.currentMonday.toLocaleDateString('fr-FR', o)} – ${end.toLocaleDateString('fr-FR', o)}`
    },
    slotsByDay() {
      const map = {}
      this.allSlots.forEach(s => {
        const key = this.toLocalDateIso(new Date(s.iso))
        if (!map[key]) map[key] = []
        map[key].push(s)
      })
      return map
    },
    hasSlotThisWeek() {
      return this.weekDays.some(d => this.slotsByDay[d.iso]?.length > 0)
    },
    canGoPrev() {
      const today = this.getMonday(new Date())
      return this.currentMonday > today
    },
    canGoNext() {
      const next = new Date(this.currentMonday); next.setDate(next.getDate() + 7)
      const dayKeys = Array.from({ length: 7 }, (_, i) => {
        const d = new Date(next); d.setDate(next.getDate() + i)
        return this.toLocalDateIso(d)
      })
      return this.allSlots.some(s => dayKeys.includes(this.toLocalDateIso(new Date(s.iso))))
    }
  },
  async created() {
    const token = this.$route.params.token
    try {
      const res = await api.get(`/entretiens/public/${token}/creneaux`)
      this.data     = res.data
      this.allSlots = (res.data.creneauxDisponibles || []).map(iso => ({
        iso,
        time: new Date(iso).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        date: new Date(iso)
      }))
      // Aller à la première semaine avec des créneaux
      if (this.allSlots.length) {
        const sorted = [...this.allSlots].sort((a, b) => new Date(a.iso) - new Date(b.iso))
        this.currentMonday = this.getMonday(new Date(sorted[0].iso))
      }
    } catch (e) {
      this.error = e.response?.data?.message || 'Lien invalide ou expiré.'
    } finally {
      this.loading = false
    }
  },
  beforeUnmount() { if (this._cdInterval) clearInterval(this._cdInterval) },
  methods: {
    toLocalDateIso(d) {
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    },
    getMonday(d) {
      const day = new Date(d); day.setHours(0,0,0,0)
      const dow = (day.getDay() + 6) % 7
      day.setDate(day.getDate() - dow)
      return day
    },
    prevWeek() { const d = new Date(this.currentMonday); d.setDate(d.getDate()-7); this.currentMonday = d },
    nextWeek() { const d = new Date(this.currentMonday); d.setDate(d.getDate()+7); this.currentMonday = d },
    async confirmer() {
      if (!this.selectedSlot) return
      this.confirming = true
      try {
        const token = this.$route.params.token
        await api.post(`/entretiens/public/${token}/confirmer`, {
          dateChoisie: this.selectedSlot.iso
        })
        this.confirmed = true
        this.startCountdown(this.selectedSlot.date)
      } catch {
        alert('Erreur lors de la confirmation. Veuillez réessayer.')
      } finally {
        this.confirming = false
      }
    },
    startCountdown(targetDate) {
      const update = () => {
        const diff = new Date(targetDate) - new Date()
        if (diff <= 0) { this.countdown = 'Maintenant !'; clearInterval(this._cdInterval); return }
        const d = Math.floor(diff / 86400000)
        const h = Math.floor((diff % 86400000) / 3600000)
        const m = Math.floor((diff % 3600000) / 60000)
        this.countdown = d > 0 ? `${d}j ${h}h ${m}min` : `${h}h ${m}min`
      }
      update()
      this._cdInterval = setInterval(update, 60000)
    },
    formatDateFull(slot) {
      if (!slot) return ''
      const d = new Date(slot.iso || slot)
      return d.toLocaleDateString('fr-FR', { weekday:'long', day:'numeric', month:'long', year:'numeric', hour:'2-digit', minute:'2-digit' })
    }
  }
}
</script>

<style scoped>
* { box-sizing: border-box; }
.hs-root { display:flex; min-height:100vh; background:#f1f5f9; font-family:'Inter',sans-serif; }
.hs-main { flex:1; min-width:0; display:flex; flex-direction:column; overflow:hidden; }
.app-page { flex:1; overflow-y:auto; padding:32px; }

/* States */
.center-state { display:flex; flex-direction:column; align-items:center; gap:12px; padding:80px 0; color:#94a3b8; font-size:14px; }
.state-card { background:#fff; border-radius:16px; border:1px solid #e2e8f0; padding:48px; max-width:480px; margin:0 auto; text-align:center; display:flex; flex-direction:column; align-items:center; gap:16px; }
.state-card h2 { font-size:20px; font-weight:700; color:#0f172a; margin:0; }
.state-card p  { font-size:14px; color:#64748b; margin:0; }
.state-icon { width:52px; height:52px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:20px; font-weight:700; }
.state-error .state-icon   { background:#fee2e2; color:#dc2626; }
.state-success .state-icon { background:#dcfce7; color:#16a34a; }
.confirm-date { font-size:15px; font-weight:700; color:#1A2B4C; }
.confirm-sub  { font-size:13px; color:#64748b; max-width:320px; line-height:1.6; }
.countdown-box { background:#f0fdf4; border-radius:10px; padding:12px 24px; text-align:center; }
.cd-label { display:block; font-size:10px; color:#16a34a; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; }
.cd-val   { font-size:22px; font-weight:800; color:#16a34a; }

/* Schedule wrap */
.schedule-wrap { max-width: 900px; margin: 0 auto; display:flex; flex-direction:column; gap:20px; }

/* Banner */
.interview-banner { background:#1A2B4C; border-radius:14px; padding:20px 24px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; }
.banner-left  { display:flex; align-items:center; gap:14px; }
.banner-avatar { width:44px; height:44px; border-radius:50%; background:rgba(255,255,255,0.1); display:flex; align-items:center; justify-content:center; font-size:20px; }
.banner-title { font-size:16px; font-weight:700; color:#fff; margin:0 0 2px; }
.banner-sub   { font-size:13px; color:#B5D4F4; margin:0; }
.banner-meta  { display:flex; gap:8px; }
.meta-pill    { background:rgba(255,255,255,0.1); color:#B5D4F4; font-size:12px; font-weight:600; padding:5px 12px; border-radius:99px; }

/* Cal card */
.cal-card { background:#fff; border-radius:14px; border:1px solid #e2e8f0; overflow:hidden; }
.cal-top  { display:flex; justify-content:space-between; align-items:flex-start; padding:20px 24px 16px; border-bottom:1px solid #f1f5f9; flex-wrap:wrap; gap:12px; }
.cal-title { font-size:15px; font-weight:700; color:#0f172a; margin:0 0 4px; }
.cal-sub   { font-size:12px; color:#94a3b8; margin:0; }
.week-nav  { display:flex; align-items:center; gap:8px; }
.week-label { font-size:13px; font-weight:600; color:#475569; min-width:150px; text-align:center; }
.nav-btn   { width:30px; height:30px; border-radius:7px; border:1px solid #e2e8f0; background:#f8fafc; cursor:pointer; font-size:18px; color:#475569; display:flex; align-items:center; justify-content:center; }
.nav-btn:hover:not(:disabled) { background:#f1f5f9; }
.nav-btn:disabled { opacity:0.3; cursor:not-allowed; }

/* Grid */
.cal-grid { padding:0 16px 16px; }
.cal-header-row { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; padding:12px 0 8px; }
.cal-day-header { text-align:center; }
.cal-day-header.col-today .dh-num { background:#1A2B4C; color:#fff; }
.dh-name { display:block; font-size:10px; font-weight:700; text-transform:uppercase; color:#94a3b8; letter-spacing:0.06em; margin-bottom:4px; }
.dh-num  { display:inline-flex; width:28px; height:28px; align-items:center; justify-content:center; font-size:13px; font-weight:700; color:#0f172a; border-radius:50%; }
.dh-today { background:#1A2B4C; color:#fff; }

.cal-body-row { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; min-height:100px; }
.cal-day-col { display:flex; flex-direction:column; gap:4px; }
.cal-day-col.col-today { background:rgba(26,43,76,0.02); border-radius:8px; }
.day-empty { text-align:center; color:#e2e8f0; font-size:16px; padding-top:8px; }

.slot-btn { width:100%; padding:8px 4px; border-radius:7px; border:1.5px solid #e2e8f0; background:#f8fafc; font-size:12px; font-weight:700; color:#334155; cursor:pointer; font-family:inherit; transition:all 0.12s; }
.slot-btn:hover { border-color:#1A2B4C; background:#eef2fa; color:#1A2B4C; }
.slot-btn.slot-selected { background:#1A2B4C; color:#fff; border-color:#1A2B4C; }

.no-slots { text-align:center; padding:20px; color:#94a3b8; font-size:13px; }
.btn-next { margin-top:8px; padding:7px 16px; background:#f1f5f9; border:none; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; color:#1A2B4C; font-family:inherit; }

/* Confirm panel */
.confirm-panel { background:#fff; border-radius:14px; border:1px solid #e2e8f0; padding:16px 20px; display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; }
.confirm-info  { display:flex; align-items:center; gap:12px; }
.confirm-icon  { font-size:24px; }
.confirm-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#94a3b8; margin:0 0 3px; }
.confirm-date-val { font-size:14px; font-weight:700; color:#0f172a; margin:0; text-transform:capitalize; }

/* Buttons */
.btn-primary { display:inline-flex; align-items:center; gap:7px; background:#1A2B4C; color:#fff; border:none; border-radius:9px; padding:11px 22px; font-size:14px; font-weight:700; cursor:pointer; font-family:inherit; }
.btn-primary:hover:not(:disabled) { background:#243d6a; }
.btn-primary:disabled { opacity:0.5; cursor:not-allowed; }
.btn-confirm { padding:12px 28px; }

.app-spinner { width:28px; height:28px; border:2.5px solid #e2e8f0; border-top-color:#1A2B4C; border-radius:50%; animation:spin 0.7s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }
</style>