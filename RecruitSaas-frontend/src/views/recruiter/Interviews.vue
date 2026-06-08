<template>
  <div class="page-layout">
    <AppSidebar />
    <main class="main-content">
      <GlobalHeader title="Recruitment portal" />
      <div class="content-wrap">

        <!-- Header -->
        <div class="page-top">
          <div>
            <h1 class="page-title">Interview Calendar</h1>
            <p class="page-sub">Scheduled interviews with your candidates</p>
          </div>
          <div class="top-filters">
            <select v-model="filtreStatut" class="filter-select">
              <option value="">All statuses</option>
              <option value="LienEnvoye">Invitation sent</option>
              <option value="Planifie">Scheduled</option>
              <option value="EnCours">In progress</option>
              <option value="Termine">Completed</option>
              <option value="Annule">Cancelled</option>
            </select>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="state-wrap">
          <div class="state-card"><div class="state-spinner"></div><p>Loading...</p></div>
        </div>

        <!-- Empty -->
        <div v-else-if="!entretiens.length" class="state-wrap">
          <div class="state-card">
            <VideoIcon :size="32" style="color:#E2E8F0" />
            <p>No interviews scheduled</p>
            <p style="font-size:12px;color:#CBD5E1">Interviews will appear here once candidates pick a time slot.</p>
          </div>
        </div>

        <!-- Grid entretiens -->
        <div v-else class="interviews-grid">
          <div
            v-for="e in filteredEntretiens"
            :key="e.id"
            class="interview-card"
            :class="cardClass(e.statut)"
          >
            <div class="card-left">
              <div class="card-avatar">{{ initiales(e.nomCandidat) }}</div>
            </div>
            <div class="card-body">
              <div class="card-top-row">
                <span class="card-name">{{ e.nomCandidat }}</span>
                <span class="status-badge" :class="statusClass(e.statut)">
                  {{ statusLabel(e.statut) }}
                </span>
              </div>
              <p class="card-offre">{{ e.titreOffre }}</p>
              <div class="card-meta">
                <span v-if="e.dateScheduled" class="meta-item">
                  <CalendarIcon :size="11" />
                  {{ formatDate(e.dateScheduled) }}
                </span>
                <span v-else class="meta-item meta-pending">
                  <ClockIcon :size="11" />
                  Awaiting confirmation
                </span>
              </div>
            </div>
            <div class="card-actions">
              <!-- Bouton rejoindre si entretien actif -->
              <button
                v-if="e.statut === 'Planifie' || e.statut === 'EnCours'"
                class="action-btn btn-join"
                @click="rejoindre(e)"
              >
                <VideoIcon :size="13" /> Join
              </button>
              <button
                v-if="['LienEnvoye','Planifie'].includes(e.statut)"
                class="action-btn btn-cancel"
                @click="annuler(e)"
              >
                Cancel
              </button>
              <button class="action-btn btn-view" @click="voirCandidat(e)">
                View candidate
              </button>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script>
import { VideoIcon, CalendarIcon, ClockIcon } from 'lucide-vue-next'
import AppSidebar   from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import { getEntretiens, annulerEntretien } from '../../services/entretienService'
import { useNotificationStore } from '../../stores/notification'
import { formatRecruiterDateTime, interviewStatusLabel } from '../../utils/recruiterI18n.js'

export default {
  name: 'Interviews',
  components: { AppSidebar, GlobalHeader, VideoIcon, CalendarIcon, ClockIcon },
  setup() {
    const ns = useNotificationStore()
    return {
      toast: {
        success: m => ns.addToast({ type: 'success', message: m }),
        error:   m => ns.addToast({ type: 'error',   message: m })
      }
    }
  },
  data() {
    return { entretiens: [], loading: true, filtreStatut: '' }
  },
  computed: {
    filteredEntretiens() {
      if (!this.filtreStatut) return this.entretiens
      return this.entretiens.filter(e => e.statut === this.filtreStatut)
    }
  },
  async created() {
    await this.load()
    // Rafraîchit toutes les 30 secondes
    this._interval = setInterval(this.load, 30000)
  },
  beforeUnmount() {
    clearInterval(this._interval)
  },
  methods: {
    async load() {
      try {
        const r = await getEntretiens()
        this.entretiens = r.data
      } catch { this.toast.error('Failed to load interviews') }
      finally { this.loading = false }
    },
    async annuler(e) {
      if (!confirm(`Cancel the interview with ${e.nomCandidat}?`)) return
      try {
        await annulerEntretien(e.id)
        e.statut = 'Annule'
        this.toast.success('Interview cancelled')
      } catch { this.toast.error('Something went wrong') }
    },
    rejoindre(e) {
      // Ouvre la page de supervision (côté recruteur)
      window.open(`/interview-watch/${e.id}`, '_blank')
    },
    voirCandidat(e) {
      this.$router.push(`/recruiter/candidates/${e.candidatureId}`)
    },
    initiales(nom) {
      if (!nom) return '?'
      return nom.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2)
    },
    formatDate(d) {
      if (!d) return ''
      return formatRecruiterDateTime(d)
    },
    statusLabel(s) {
      return interviewStatusLabel(s)
    },
    statusClass(s) {
      return { LienEnvoye:'st-blue', Planifie:'st-green', EnCours:'st-teal', Termine:'st-grey', Annule:'st-red', EnAttente:'st-amber' }[s] || ''
    },
    cardClass(s) {
      return { EnCours: 'card-active', Annule: 'card-cancelled', Termine: 'card-done' }[s] || ''
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
.page-layout  { display:flex; min-height:100vh; background:#F0F2F7; font-family:'DM Sans',sans-serif; }
.main-content { flex:1; display:flex; flex-direction:column; }
.content-wrap { flex:1; padding:22px 28px; max-width:1400px; margin:0 auto; width:100%; box-sizing:border-box; }

.page-top     { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:24px; }
.page-title   { font-size:20px; font-weight:700; color:#0F172A; margin:0 0 4px; }
.page-sub     { font-size:13px; color:#94A3B8; margin:0; }
.top-filters  { display:flex; gap:10px; }
.filter-select { padding:7px 12px; border:0.5px solid #E2E8F0; border-radius:8px; font-size:13px; font-family:inherit; color:#334155; background:#fff; cursor:pointer; }

.state-wrap { display:flex; justify-content:center; padding:60px 0; }
.state-card { display:flex; flex-direction:column; align-items:center; gap:12px; background:#fff; border-radius:14px; padding:40px 60px; border:0.5px solid #E8EDF4; color:#64748B; font-size:14px; text-align:center; }
.state-spinner { width:28px; height:28px; border:2.5px solid #E2E8F0; border-top-color:#454a83; border-radius:50%; animation:spin 0.8s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }

.interviews-grid { display:flex; flex-direction:column; gap:10px; }

.interview-card { background:#fff; border-radius:12px; border:0.5px solid #E8EDF4; padding:16px 20px; display:flex; align-items:center; gap:16px; }
.interview-card.card-active    { border-left:3px solid #1D9E75; }
.interview-card.card-cancelled { opacity:0.6; }
.interview-card.card-done      { background:#FAFAFA; }

.card-left   { flex-shrink:0; }
.card-avatar { width:40px; height:40px; border-radius:50%; background:#1A2B4C; color:#B5D4F4; display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:700; }

.card-body     { flex:1; min-width:0; }
.card-top-row  { display:flex; align-items:center; gap:10px; margin-bottom:3px; }
.card-name     { font-size:14px; font-weight:700; color:#0F172A; }
.card-offre    { font-size:12px; color:#64748B; margin:0 0 6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.card-meta     { display:flex; gap:12px; }
.meta-item     { display:inline-flex; align-items:center; gap:4px; font-size:11px; color:#64748B; }
.meta-pending  { color:#EF9F27; }

.status-badge { font-size:10px; font-weight:700; padding:2px 8px; border-radius:99px; }
.st-blue  { background:#E6F1FB; color:#0C447C; }
.st-green { background:#EAF3DE; color:#27500A; }
.st-teal  { background:#E1F5EE; color:#085041; }
.st-grey  { background:#F1F5F9; color:#64748B; }
.st-red   { background:#FCEBEB; color:#791F1F; }
.st-amber { background:#FAEEDA; color:#633806; }

.card-actions { display:flex; gap:8px; flex-shrink:0; }
.action-btn   { padding:6px 12px; border-radius:8px; font-size:12px; font-weight:600; cursor:pointer; font-family:inherit; border:0.5px solid transparent; }
.btn-join   { background:#1A2B4C; color:#fff; display:inline-flex; align-items:center; gap:5px; }
.btn-join:hover { background:#243d6a; }
.btn-cancel { background:#FCEBEB; color:#791F1F; border-color:#F09595; }
.btn-cancel:hover { background:#F7C1C1; }
.btn-view   { background:#F8FAFC; color:#475569; border-color:#E2E8F0; }
.btn-view:hover { background:#F1F5F9; }
</style>