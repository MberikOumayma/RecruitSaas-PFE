<template>
  <div class="hs-root">
    <AppSidebar />
    <main class="hs-main">
      <GlobalHeader title="My Interviews" />
      <div class="app-page">

        <div class="page-header">
          <div>
            <h1 class="page-title">Mes entretiens</h1>
            <p class="page-sub">Suivez vos entretiens planifiés et passés.</p>
          </div>
        </div>

        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-num">{{ counts.total }}</span>
            <span class="stat-lbl">Total</span>
          </div>
          <div class="stat-card">
            <span class="stat-num st-wait">{{ counts.attente }}</span>
            <span class="stat-lbl">En attente</span>
          </div>
          <div class="stat-card">
            <span class="stat-num st-ok">{{ counts.planifie }}</span>
            <span class="stat-lbl">Planifiés</span>
          </div>
          <div class="stat-card">
            <span class="stat-num st-done">{{ counts.termine }}</span>
            <span class="stat-lbl">Terminés</span>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="center-state">
          <div class="spinner"></div><p>Chargement...</p>
        </div>

        <!-- Empty -->
        <div v-else-if="!entretiens.length" class="empty-card">
          <div class="empty-icon">📅</div>
          <p class="empty-title">Aucun entretien</p>
          <p class="empty-sub">Vous recevrez un email dès qu'une entreprise vous invite à un entretien.</p>
          <button class="btn-primary" @click="$router.push('/applications')">Mes candidatures</button>
        </div>

        <!-- Liste entretiens -->
        <div v-else class="interviews-list">

          <!-- En attente de confirmation -->
          <div v-if="enAttente.length" class="section">
            <div class="section-title">
              <span class="section-dot dot-wait"></span>
              En attente de votre confirmation
            </div>
            <div v-for="e in enAttente" :key="e.id" class="interview-card card-wait">
              <div class="card-left">
                <div class="card-avatar">{{ initiales(e.nomEntreprise) }}</div>
              </div>
              <div class="card-body">
                <p class="card-titre">{{ e.titreOffre }}</p>
                <p class="card-entreprise">{{ e.nomEntreprise }}</p>
                <p class="card-info wait-info">Vous avez été invité à choisir un créneau d'entretien.</p>
              </div>
              <div class="card-actions">
                <button class="btn-choose" @click="choisirCreneau(e)">
                  📅 Choisir mon créneau
                </button>
              </div>
            </div>
          </div>

          <!-- Planifiés -->
          <div v-if="planifies.length" class="section">
            <div class="section-title">
              <span class="section-dot dot-ok"></span>
              Entretiens planifiés
            </div>
            <div v-for="e in planifies" :key="e.id" class="interview-card card-ok">
              <div class="card-left">
                <div class="card-avatar">{{ initiales(e.nomEntreprise) }}</div>
              </div>
              <div class="card-body">
                <p class="card-titre">{{ e.titreOffre }}</p>
                <p class="card-entreprise">{{ e.nomEntreprise }}</p>
                <div class="card-date-box">
                  <span class="date-icon">📅</span>
                  <span class="date-val">{{ formatDateFull(e.dateScheduled) }}</span>
                </div>
                <div class="countdown-inline" v-if="getCountdown(e.dateScheduled)">
                  ⏱ {{ getCountdown(e.dateScheduled) }}
                </div>
              </div>
              <div class="card-actions">
                <button
                  class="btn-join"
                  :disabled="!isActive(e.dateScheduled)"
                  @click="rejoindre(e)"
                >
                  🎥 Rejoindre
                </button>
              </div>
            </div>
          </div>

          <!-- Terminés -->
          <div v-if="termines.length" class="section">
            <div class="section-title">
              <span class="section-dot dot-done"></span>
              Entretiens passés
            </div>
            <div v-for="e in termines" :key="e.id" class="interview-card card-done">
              <div class="card-left">
                <div class="card-avatar">{{ initiales(e.nomEntreprise) }}</div>
              </div>
              <div class="card-body">
                <p class="card-titre">{{ e.titreOffre }}</p>
                <p class="card-entreprise">{{ e.nomEntreprise }}</p>
                <p class="card-info">{{ formatDateFull(e.dateScheduled) }}</p>
                <p class="card-info done-msg">Entretien terminé. Le recruteur analysera votre résultat.</p>
              </div>
              <div class="card-status">
                <span class="badge-done">✓ Terminé</span>
              </div>
            </div>
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
  name: 'CandidatInterviews',
  components: { AppSidebar, GlobalHeader },
  data() {
    return { entretiens: [], loading: true }
  },
  computed: {
    enAttente() { return this.entretiens.filter(e => e.statut === 'LienEnvoye') },
    planifies()  { return this.entretiens.filter(e => ['Planifie','EnCours'].includes(e.statut)) },
    termines()   { return this.entretiens.filter(e => e.statut === 'Termine') },
    counts() {
      return {
        total:   this.entretiens.length,
        attente: this.enAttente.length,
        planifie: this.planifies.length,
        termine: this.termines.length
      }
    }
  },
  async created() {
    await this.load()
    this._interval = setInterval(this.load, 30000)
  },
  beforeUnmount() { clearInterval(this._interval) },
  methods: {
    async load() {
      try {
        const r = await api.get('/entretiens/mes-entretiens')
        this.entretiens = r.data || []
      } catch (e) {
        if (e?.response?.status === 401) { this.$router.push('/login'); return }
      } finally { this.loading = false }
    },
    choisirCreneau(e) {
      this.$router.push(`/schedule-interview/${e.lienToken}`)
    },
    rejoindre(e) {
      window.open(`/interview/${e.lienToken}/rejoindre`, '_blank')
    },
    isActive(date) {
      if (!date) return false
      const now  = new Date()
      const d    = new Date(date)
      return now >= new Date(d.getTime() - 5*60000) && now <= new Date(d.getTime() + 35*60000)
    },
    getCountdown(date) {
      if (!date) return null
      const diff = new Date(date) - new Date()
      if (diff <= 0) return null
      const days = Math.floor(diff / 86400000)
      const h    = Math.floor((diff % 86400000) / 3600000)
      const m    = Math.floor((diff % 3600000) / 60000)
      if (days > 0) return `Dans ${days}j ${h}h`
      if (h > 0)    return `Dans ${h}h ${m}min`
      return `Dans ${m} min`
    },
    formatDateFull(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('fr-FR', {
        weekday:'long', day:'numeric', month:'long', year:'numeric',
        hour:'2-digit', minute:'2-digit'
      })
    },
    initiales(n) {
      if (!n) return '?'
      return n.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2)
    },
    scoreColor(s) { return s >= 80 ? '#16a34a' : s >= 50 ? '#d97706' : '#dc2626' }
  }
}
</script>

<style scoped>
* { box-sizing: border-box; }
.hs-root { display:flex; min-height:100vh; background:#f1f5f9; font-family:'Inter',sans-serif; }
.hs-main { flex:1; min-width:0; display:flex; flex-direction:column; overflow:hidden; }
.app-page { flex:1; overflow-y:auto; padding:32px; }

.page-header { margin-bottom:24px; }
.page-title  { font-size:22px; font-weight:700; color:#0f172a; margin:0 0 4px; }
.page-sub    { font-size:13px; color:#64748b; margin:0; }

.stats-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:24px; }
.stat-card  { background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; text-align:center; }
.stat-num   { display:block; font-size:28px; font-weight:800; color:#0f172a; }
.stat-num.st-wait { color:#f97316; }
.stat-num.st-ok   { color:#1A2B4C; }
.stat-num.st-done { color:#16a34a; }
.stat-lbl   { display:block; font-size:11px; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.05em; margin-top:4px; }

.center-state { display:flex; flex-direction:column; align-items:center; gap:12px; padding:60px; color:#94a3b8; }
.spinner { width:28px; height:28px; border:2.5px solid #e2e8f0; border-top-color:#1A2B4C; border-radius:50%; animation:spin 0.7s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }

.empty-card  { background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:48px; text-align:center; display:flex; flex-direction:column; align-items:center; gap:12px; }
.empty-icon  { font-size:40px; }
.empty-title { font-size:16px; font-weight:700; color:#475569; margin:0; }
.empty-sub   { font-size:13px; color:#94a3b8; margin:0; max-width:320px; }

.interviews-list { display:flex; flex-direction:column; gap:24px; }
.section { display:flex; flex-direction:column; gap:10px; }
.section-title { display:flex; align-items:center; gap:8px; font-size:13px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px; }
.section-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.dot-wait { background:#f97316; }
.dot-ok   { background:#1A2B4C; }
.dot-done { background:#16a34a; }

.interview-card { background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; display:flex; align-items:center; gap:16px; }
.card-wait { border-left:4px solid #f97316; }
.card-ok   { border-left:4px solid #1A2B4C; }
.card-done { border-left:4px solid #16a34a; opacity:0.9; }

.card-avatar { width:44px; height:44px; border-radius:50%; background:#1A2B4C; color:#B5D4F4; display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:700; flex-shrink:0; }
.card-body   { flex:1; min-width:0; }
.card-titre  { font-size:15px; font-weight:700; color:#0f172a; margin:0 0 2px; }
.card-entreprise { font-size:12px; color:#64748b; margin:0 0 8px; }
.card-info   { font-size:12px; color:#94a3b8; margin:0; }
.wait-info   { color:#f97316; font-weight:600; }

.card-date-box { display:flex; align-items:center; gap:6px; margin:4px 0; }
.date-icon { font-size:14px; }
.date-val  { font-size:13px; font-weight:600; color:#0f172a; text-transform:capitalize; }
.countdown-inline { font-size:12px; color:#1A2B4C; font-weight:700; margin-top:4px; }

.score-box  { display:flex; align-items:center; gap:8px; margin-top:8px; }
.score-lbl  { font-size:11px; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.05em; }
.score-val  { font-size:18px; font-weight:800; }
.transcript-box  { background:#f8fafc; border-radius:8px; padding:10px 12px; margin-top:8px; }
.transcript-lbl  { font-size:10px; color:#94a3b8; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; margin:0 0 4px; }
.transcript-text { font-size:12px; color:#475569; line-height:1.5; margin:0; }

.card-actions { flex-shrink:0; }
.card-status  { flex-shrink:0; }
.btn-primary { display:inline-flex; align-items:center; background:#1A2B4C; color:#fff; border:none; border-radius:9px; padding:10px 18px; font-size:13px; font-weight:700; cursor:pointer; font-family:inherit; }
.btn-primary:hover { background:#243d6a; }
.btn-choose { padding:9px 16px; background:#fff7ed; color:#c2410c; border:1px solid #fed7aa; border-radius:9px; font-size:13px; font-weight:700; cursor:pointer; font-family:inherit; white-space:nowrap; }
.btn-choose:hover { background:#ffedd5; }
.btn-join   { padding:9px 16px; background:#1A2B4C; color:#fff; border:none; border-radius:9px; font-size:13px; font-weight:700; cursor:pointer; font-family:inherit; white-space:nowrap; }
.btn-join:hover:not(:disabled) { background:#243d6a; }
.btn-join:disabled { opacity:0.4; cursor:not-allowed; }
.badge-done { background:#f0fdf4; color:#16a34a; font-size:12px; font-weight:700; padding:5px 12px; border-radius:99px; border:1px solid #bbf7d0; }

@media(max-width:768px) { .stats-grid { grid-template-columns:repeat(2,1fr); } .app-page { padding:16px; } }
</style>