<!-- Route publique : /interview/:token -->
<template>
  <div class="page">

    <!-- Loading -->
    <div class="center-card" v-if="loading">
      <div class="spinner"></div>
      <p>Chargement...</p>
    </div>

    <!-- Erreur -->
    <div class="center-card" v-else-if="error">
      <div class="icon-circle icon-red">✕</div>
      <h2>Lien invalide</h2>
      <p>{{ error }}</p>
    </div>

    <!-- Confirmé -->
    <div class="center-card" v-else-if="confirmed">
      <div class="icon-circle icon-green">✓</div>
      <h2>Entretien confirmé !</h2>
      <p class="confirm-date">{{ formatDateFull(selectedSlot) }}</p>
      <p class="confirm-sub">Vous recevrez un rappel par email avant l'entretien. Le lien d'accès s'activera à l'heure exacte.</p>
      <div class="countdown-box" v-if="countdown">
        <span class="cd-label">Commence dans</span>
        <span class="cd-val">{{ countdown }}</span>
      </div>
    </div>

    <!-- Calendrier de sélection -->
    <div class="schedule-layout" v-else>

      <!-- Colonne gauche — infos -->
      <div class="info-col">
        <div class="brand">
          <div class="brand-dot"></div>
          <span>RecruitSaaS</span>
        </div>
        <div class="interviewer-card">
          <img src="https://i.imgur.com/YkQUxiZ.png" class="avatar" alt="AI" />
          <h2 class="interviewer-name">Recruteur IA</h2>
          <p class="interviewer-role">{{ data.titreOffre }}</p>
          <div class="info-rows">
            <div class="info-row"><span class="info-icon">⏱</span><span>30 minutes</span></div>
            <div class="info-row"><span class="info-icon">🎥</span><span>Entretien virtuel</span></div>
            <div class="info-row" v-if="data.nomEntreprise"><span class="info-icon">🏢</span><span>{{ data.nomEntreprise }}</span></div>
          </div>
        </div>
        <div class="selected-preview" v-if="selectedSlot">
          <p class="preview-label">Créneau sélectionné</p>
          <p class="preview-date">{{ formatDateFull(selectedSlot) }}</p>
          <button class="btn-confirm" @click="confirmer" :disabled="confirming">
            {{ confirming ? 'Confirmation...' : 'Confirmer ce créneau' }}
          </button>
        </div>
      </div>

      <!-- Colonne droite — calendrier -->
      <div class="calendar-col">
        <div class="cal-header">
          <h2 class="cal-title">Choisissez votre créneau</h2>
          <div class="week-nav">
            <button class="nav-btn" @click="prevWeek" :disabled="!canGoPrev">&#8249;</button>
            <span class="week-label">{{ weekLabel }}</span>
            <button class="nav-btn" @click="nextWeek" :disabled="!canGoNext">&#8250;</button>
          </div>
        </div>

        <!-- Grille calendrier -->
        <div class="cal-grid">
          <!-- Headers jours -->
          <div class="cal-grid-header">
            <div v-for="day in weekDays" :key="day.iso" class="day-header" :class="{ 'day-today': day.isToday }">
              <span class="day-name">{{ day.name }}</span>
              <span class="day-num" :class="{ 'day-num-today': day.isToday }">{{ day.num }}</span>
            </div>
          </div>

          <!-- Colonnes créneaux -->
          <div class="cal-grid-body">
            <div v-for="day in weekDays" :key="day.iso" class="day-col">
              <div v-if="slotsByDay[day.iso] && slotsByDay[day.iso].length">
                <button
                  v-for="slot in slotsByDay[day.iso]"
                  :key="slot.iso"
                  class="slot-btn"
                  :class="{ 'slot-selected': selectedSlot && selectedSlot.iso === slot.iso }"
                  @click="selectSlot(slot)"
                >
                  {{ slot.time }}
                </button>
              </div>
              <div v-else class="day-empty">—</div>
            </div>
          </div>
        </div>

        <!-- Aucun créneau cette semaine -->
        <div class="no-slots-week" v-if="!hasSlotThisWeek">
          <p>Aucun créneau disponible cette semaine</p>
          <button class="btn-next-week" @click="nextWeek" v-if="canGoNext">Semaine suivante →</button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'InterviewSchedule',
  data() {
    return {
      token:        null,
      loading:      true,
      error:        null,
      data:         {},
      allSlots:     [], // [{ iso, time, date }]
      selectedSlot: null,
      confirming:   false,
      confirmed:    false,
      countdown:    null,
      _cdInterval:  null,
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
          iso:     this.toLocalDateIso(d),
          name:    d.toLocaleDateString('fr-FR', { weekday: 'short' }),
          num:     d.getDate(),
          isToday: d.toDateString() === today.toDateString()
        }
      })
    },
    weekLabel() {
      const end = new Date(this.currentMonday)
      end.setDate(end.getDate() + 6)
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
      const nextMonday = new Date(this.currentMonday)
      nextMonday.setDate(nextMonday.getDate() + 7)
      const nextDayKeys = Array.from({ length: 7 }, (_, i) => {
        const d = new Date(nextMonday); d.setDate(nextMonday.getDate() + i)
        return this.toLocalDateIso(d)
      })
      return this.allSlots.some(s => nextDayKeys.includes(this.toLocalDateIso(new Date(s.iso))))
    }
  },
  async created() {
    this.token = this.$route.params.token
    await this.loadCreneaux()
    // Aller automatiquement à la première semaine avec des créneaux
    this.goToFirstAvailableWeek()
  },
  beforeUnmount() {
    if (this._cdInterval) clearInterval(this._cdInterval)
  },
  methods: {
    async loadCreneaux() {
      try {
        const res = await api.get(`/entretiens/public/${this.token}/creneaux`)
        this.data = res.data
        // Convertit les créneaux en slots
        this.allSlots = (res.data.creneauxDisponibles || []).map(iso => {
          const d = new Date(iso)
          return {
            iso,
            time: d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
            date: d
          }
        })
      } catch (e) {
        this.error = e.response?.data?.message || 'Lien invalide ou expiré.'
      } finally {
        this.loading = false
      }
    },
    goToFirstAvailableWeek() {
      if (!this.allSlots.length) return
      const sorted = [...this.allSlots].sort((a, b) => new Date(a.iso) - new Date(b.iso))
      this.currentMonday = this.getMonday(new Date(sorted[0].iso))
    },
    toLocalDateIso(d) {
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    },
    getMonday(d) {
      const day = new Date(d)
      const dow = (day.getDay() + 6) % 7
      day.setDate(day.getDate() - dow)
      day.setHours(0, 0, 0, 0)
      return day
    },
    prevWeek() {
      const d = new Date(this.currentMonday)
      d.setDate(d.getDate() - 7)
      this.currentMonday = d
    },
    nextWeek() {
      const d = new Date(this.currentMonday)
      d.setDate(d.getDate() + 7)
      this.currentMonday = d
    },
    selectSlot(slot) {
      this.selectedSlot = slot
    },
    async confirmer() {
      if (!this.selectedSlot) return
      this.confirming = true
      try {
        await api.post(`/entretiens/public/${this.token}/confirmer`, {
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
* { box-sizing: border-box; }
.page { min-height: 100vh; background: #F0F2F7; font-family: 'DM Sans', sans-serif; display: flex; align-items: center; justify-content: center; padding: 24px; }

/* Center cards */
.center-card { background: #fff; border-radius: 20px; padding: 48px 56px; text-align: center; border: 0.5px solid #E8EDF4; display: flex; flex-direction: column; align-items: center; gap: 16px; max-width: 440px; width: 100%; }
.center-card h2 { font-size: 20px; font-weight: 700; color: #0F172A; margin: 0; }
.center-card p  { font-size: 14px; color: #64748B; margin: 0; }
.icon-circle { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 700; }
.icon-red   { background: #FCEBEB; color: #E24B4A; }
.icon-green { background: #E1F5EE; color: #1D9E75; }
.spinner { width: 32px; height: 32px; border: 2.5px solid #E2E8F0; border-top-color: #1A2B4C; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Confirmation */
.confirm-date { font-size: 16px; font-weight: 700; color: #1A2B4C; margin: 0; }
.confirm-sub  { font-size: 13px; color: #64748B; margin: 0; max-width: 320px; line-height: 1.6; }
.countdown-box { background: #E1F5EE; border-radius: 12px; padding: 14px 28px; text-align: center; }
.cd-label { display: block; font-size: 11px; color: #085041; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
.cd-val   { font-size: 24px; font-weight: 800; color: #1D9E75; }

/* Layout */
.schedule-layout { display: grid; grid-template-columns: 280px 1fr; gap: 20px; max-width: 1000px; width: 100%; align-items: start; }
@media (max-width: 760px) { .schedule-layout { grid-template-columns: 1fr; } }

/* Info col */
.info-col { background: #1A2B4C; border-radius: 20px; padding: 28px; display: flex; flex-direction: column; gap: 24px; }
.brand { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: #B5D4F4; }
.brand-dot { width: 8px; height: 8px; border-radius: 50%; background: #1D9E75; }
.interviewer-card { text-align: center; }
.avatar { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; border: 3px solid rgba(255,255,255,0.15); margin-bottom: 12px; }
.interviewer-name { font-size: 18px; font-weight: 700; color: #fff; margin: 0 0 4px; }
.interviewer-role { font-size: 13px; color: #B5D4F4; margin: 0 0 16px; }
.info-rows { display: flex; flex-direction: column; gap: 8px; }
.info-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: rgba(255,255,255,0.75); }
.info-icon { font-size: 14px; }

.selected-preview { background: rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; }
.preview-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #5DCAA5; margin: 0 0 6px; }
.preview-date  { font-size: 13px; font-weight: 600; color: #fff; margin: 0 0 14px; line-height: 1.4; text-transform: capitalize; }
.btn-confirm { width: 100%; padding: 12px; background: #1D9E75; color: #fff; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; font-family: inherit; }
.btn-confirm:hover:not(:disabled) { background: #17865f; }
.btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

/* Calendar col */
.calendar-col { background: #fff; border-radius: 20px; border: 0.5px solid #E8EDF4; overflow: hidden; }
.cal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px 16px; border-bottom: 0.5px solid #F1F5F9; }
.cal-title { font-size: 16px; font-weight: 700; color: #0F172A; margin: 0; }
.week-nav { display: flex; align-items: center; gap: 8px; }
.week-label { font-size: 13px; font-weight: 600; color: #475569; min-width: 140px; text-align: center; }
.nav-btn { width: 30px; height: 30px; border-radius: 8px; border: 0.5px solid #E2E8F0; background: #F8FAFC; cursor: pointer; font-size: 18px; color: #475569; display: flex; align-items: center; justify-content: center; }
.nav-btn:hover:not(:disabled) { background: #F1F5F9; }
.nav-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* Cal grid */
.cal-grid { padding: 0 16px 16px; }
.cal-grid-header { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; padding: 12px 0 8px; }
.day-header { text-align: center; }
.day-header.day-today .day-num { background: #1A2B4C; color: #fff; }
.day-name { display: block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #94A3B8; margin-bottom: 4px; }
.day-num  { display: inline-flex; width: 28px; height: 28px; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: #0F172A; border-radius: 50%; }

.cal-grid-body { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; min-height: 120px; }
.day-col { display: flex; flex-direction: column; gap: 4px; }
.day-empty { text-align: center; color: #E2E8F0; font-size: 18px; padding-top: 12px; }

.slot-btn { width: 100%; padding: 8px 4px; border-radius: 8px; border: 1.5px solid #E2E8F0; background: #F8FAFC; font-size: 12px; font-weight: 700; color: #334155; cursor: pointer; font-family: inherit; transition: all 0.15s; }
.slot-btn:hover { border-color: #1A2B4C; background: #EEF2FA; color: #1A2B4C; }
.slot-btn.slot-selected { background: #1A2B4C; color: #fff; border-color: #1A2B4C; }

.no-slots-week { text-align: center; padding: 24px; color: #94A3B8; font-size: 13px; }
.btn-next-week { margin-top: 8px; padding: 7px 16px; background: #F1F5F9; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; color: #1A2B4C; font-family: inherit; }
</style>