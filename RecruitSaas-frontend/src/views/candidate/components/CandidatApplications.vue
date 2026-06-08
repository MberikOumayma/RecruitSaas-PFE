<template>
  <div class="hs-root">
    <AppSidebar />
    <main class="hs-main">
      <GlobalHeader title="My Applications" />
      <div class="app-page">

        <div class="app-header">
          <div>
            <h1 class="app-title">My Applications</h1>
            <p class="app-sub">Track all your job applications in one place.</p>
          </div>
          <button class="app-btn-primary" @click="$router.push('/offres')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            New Application
          </button>
        </div>

        <div class="app-stats-grid">
          <div class="app-stat-card app-stat-navy">
            <div class="app-stat-icon-wrap"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
            <div><p class="app-stat-lbl">TOTAL</p><p class="app-stat-num">{{ statusStats[0].count }}</p><p class="app-stat-trend">Applications sent</p></div>
          </div>
          <div class="app-stat-card app-stat-amber">
            <div class="app-stat-icon-wrap"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
            <div><p class="app-stat-lbl">PENDING</p><p class="app-stat-num">{{ statusStats[1].count }}</p><p class="app-stat-trend">Awaiting response</p></div>
          </div>
          <div class="app-stat-card app-stat-green">
            <div class="app-stat-icon-wrap"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div>
            <div><p class="app-stat-lbl">ACCEPTED</p><p class="app-stat-num">{{ statusStats[2].count }}</p><p class="app-stat-trend">Offers received</p></div>
          </div>
          <div class="app-stat-card app-stat-red">
            <div class="app-stat-icon-wrap"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg></div>
            <div><p class="app-stat-lbl">REJECTED</p><p class="app-stat-num">{{ statusStats[3].count }}</p><p class="app-stat-trend">Not selected</p></div>
          </div>
        </div>

        <div class="app-filters">
          <div class="app-search-wrap">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="search" class="app-search" placeholder="Search by job title or company..." />
          </div>
          <div class="app-filter-tabs">
            <button v-for="tab in tabs" :key="tab.value" :class="['app-tab', { 'app-tab-active': activeTab === tab.value }]" @click="activeTab = tab.value">
              {{ tab.label }}<span class="app-tab-count">{{ tabCount(tab.value) }}</span>
            </button>
          </div>
        </div>

        <div v-if="loading" class="app-loading"><div class="app-spinner"></div><p>Loading applications...</p></div>
        <div v-else-if="error" class="app-empty">
          <div class="app-empty-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg></div>
          <p class="app-empty-title">Failed to load applications</p>
          <p class="app-empty-sub">{{ error }}</p>
          <button class="app-btn-primary" @click="loadApplications">Retry</button>
        </div>
        <div v-else-if="filtered.length === 0" class="app-empty">
          <div class="app-empty-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
          <p class="app-empty-title">No applications found</p>
          <p class="app-empty-sub">{{ activeTab === 'all' ? "You haven't applied to any jobs yet." : 'No applications with this status.' }}</p>
          <button class="app-btn-primary" @click="$router.push('/offres')">Browse Jobs</button>
        </div>

        <template v-else>
          <div class="app-table-card">
            <div class="app-table-header">
              <h3 class="app-table-title">Applications List</h3>
              <span class="app-table-count">{{ filtered.length }} result{{ filtered.length > 1 ? 's' : '' }}</span>
            </div>
            <table class="app-table">
              <thead>
                <tr>
                  <th>Position</th><th>Company</th><th>Applied</th><th>Status</th>
                  
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in filtered" :key="app.id" class="app-row">
                  <td>
                    <div class="app-job-cell">
                      <div class="app-job-logo" :style="{ background: logoColor(app.titre) }">{{ app.titre ? app.titre.charAt(0).toUpperCase() : '?' }}</div>
                      <div><p class="app-job-title">{{ app.titre }}</p><p class="app-job-loc">{{ app.localisation }}</p></div>
                    </div>
                  </td>
                  <td>
                    <div class="app-company-cell">
                      <div class="app-company-dot" :style="{ background: logoColor(app.entreprise) }"></div>
                      <p class="app-company">{{ app.entreprise || '—' }}</p>
                    </div>
                  </td>
                  <td><p class="app-date">{{ formatDate(app.date) }}</p></td>
                  <td><span :class="['app-badge', badgeClass(app.statut)]"><span class="app-badge-dot"></span>{{ formatStatut(app.statut) }}</span></td>
                  
                  
                </tr>
              </tbody>
            </table>
            <div class="app-table-footer">
              <p class="app-showing">Showing <strong>{{ filtered.length }}</strong> of <strong>{{ applications.length }}</strong> applications</p>
            </div>
          </div>

          <div class="pipeline-wrapper">
            <CandidatePipelineBoard
              :candidatures="candidaturesForBoard"
              :showHeader="true"
              title="Application Pipeline"
              mode="expert"
              @statut-change="handleStatutChange"
            />
          </div>
        </template>
      </div>
    </main>
  </div>
</template>

<script>
import AppSidebar from '../../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../../components/layout/GlobalHeader.vue'
import CandidatePipelineBoard from '../../../components/CandidatePipelineBoard.vue'
import api from '../../../services/api'

export default {
  name: 'CandidatApplications',
  components: { AppSidebar, GlobalHeader, CandidatePipelineBoard },
  data() {
    return {
      loading: false, error: null, search: '', activeTab: 'all', applications: [],
      tabs: [
        { label: 'All', value: 'all' }, { label: 'Pending', value: 'pending' },
        { label: 'Interview', value: 'interview' }, { label: 'Accepted', value: 'accepted' },
        { label: 'Rejected', value: 'rejected' },
      ]
    }
  },
  computed: {
    filtered() {
      let list = this.applications
      if (this.search) { const q = this.search.toLowerCase(); list = list.filter(a => (a.titre||'').toLowerCase().includes(q) || (a.entreprise||'').toLowerCase().includes(q)) }
      if (this.activeTab !== 'all') list = list.filter(a => this.normalizeStatut(a.statut) === this.activeTab)
      return list
    },
    statusStats() {
      const total    = this.applications.length
      const pending  = this.applications.filter(a => this.normalizeStatut(a.statut) === 'pending').length
      const accepted = this.applications.filter(a => this.normalizeStatut(a.statut) === 'accepted').length
      const rejected = this.applications.filter(a => this.normalizeStatut(a.statut) === 'rejected').length
      return [{ label:'Total', count:total },{ label:'Pending', count:pending },{ label:'Accepted', count:accepted },{ label:'Rejected', count:rejected }]
    },
    candidaturesForBoard() {
      return this.applications.map(a => ({
        id: a.id, statut: a.statut || 'Nouvelle',
        candidatNomComplet: a.titre, offreTitre: a.entreprise, creeLe: a.date,
        avisExpert: (a.scoreIA !== null && a.scoreIA !== undefined) ? { score: a.scoreIA / 20 } : null,
        offreId: a.id
      }))
    }
  },
  async mounted() {
    const token = localStorage.getItem('token')
    if (!token) { this.$router.push('/login'); return }
    await this.loadApplications()
  },
  methods: {
    async loadApplications() {
      this.loading = true; this.error = null
      try {
        const response = await api.get('/candidatures/mes-candidatures')
        const raw  = response.data
        const list = Array.isArray(raw) ? raw : (raw?.data || raw?.items || raw?.value || [])
        this.applications = list.map(a => ({
          id:           a.id,
          titre:        a.titreOffre    || a.titre      || '—',
          entreprise:   a.nomEntreprise || a.entreprise || '—',
          statut:       a.statut        || 'Nouvelle',
          date:         a.creeLe        || a.date       || null,
          localisation: a.localisation  || '',
          scoreIA:      (a.scoreIA !== undefined && a.scoreIA !== null) ? a.scoreIA : null,
        }))
      } catch (e) {
        if (e?.response?.status === 401) { localStorage.removeItem('token'); this.$router.push('/login'); return }
        this.error = e?.response?.data?.message || e?.message || 'Unable to load your applications.'
      } finally { this.loading = false }
    },

    // ✅ Ajouté depuis le code du collègue
    async handleStatutChange({ id, statut }) {
      const app = this.applications.find(a => a.id === id)
      if (!app) return
      const previousStatut = app.statut
      app.statut = statut
      try {
        await api.patch(`/candidat/${id}/statut`, { statut })
      } catch (e) {
        console.error('[CandidatApplications] Failed to persist statut change:', e)
        app.statut = previousStatut
      }
    },

    normalizeStatut(statut) {
      const s = (statut || '').toLowerCase().trim()
      if (['acceptée','accepte','accepted','accepté'].includes(s)) return 'accepted'
      if (['refusée','refusee','rejected','refusé'].includes(s))   return 'rejected'
      if (['entretien','interview'].includes(s))                    return 'interview'
      return 'pending'
    },
    formatStatut(statut) {
      const map = { accepted:'Accepted', rejected:'Rejected', interview:'Interview', screening:'Screening', pending:'Pending' }
      return map[this.normalizeStatut(statut)] || statut || 'Pending'
    },
    tabCount(val) { if (val === 'all') return this.applications.length; return this.applications.filter(a => this.normalizeStatut(a.statut) === val).length },
    logoColor(t) {
      if (!t) return '#1e3a5f'
      const colors = ['#1A2B4C','#1a3c2e','#3b1f4e','#2e1f1a','#0d4f8c']
      let h = 0; for (let i = 0; i < t.length; i++) h = t.charCodeAt(i) + ((h << 5) - h)
      return colors[Math.abs(h) % colors.length]
    },
    badgeClass(statut) { const s = this.normalizeStatut(statut); return { accepted:'badge-accepted', rejected:'badge-rejected', interview:'badge-interview' }[s] || 'badge-pending' },
    scoreColor(score)  { return score >= 75 ? '#16a34a' : score >= 50 ? '#d97706' : '#dc2626' },
    formatDate(d) {
      if (!d) return '—'
      const diff = Math.floor((Date.now() - new Date(d)) / 86400000)
      if (diff === 0) return 'Today'; if (diff === 1) return '1 day ago'; if (diff < 30) return `${diff} days ago`; if (diff < 365) return `${Math.floor(diff/30)} month(s) ago`
      return new Date(d).toLocaleDateString('en-GB')
    },
    viewDetails(app) { this.$router.push(`/candidatures/${app.id}`) },
    openAiInterview(app) {
      this.$router.push({ path: '/candidate/entretien-ia', query: app?.id ? { candidatureId: String(app.id) } : {} })
    }
  }
}
</script>

<style scoped>
.hs-root { display: flex; min-height: 100vh; background: #f1f5f9; font-family: 'Inter', sans-serif; }
.hs-main { flex: 1; min-width: 0; display: flex; flex-direction: column; overflow: hidden; }
.app-page { flex: 1; overflow-y: auto; padding: 32px; }
.app-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; }
.app-title  { font-size: 22px; font-weight: 700; color: #0f172a; margin: 0 0 4px; }
.app-sub    { font-size: 13px; color: #64748b; margin: 0; }
.app-btn-primary { display: inline-flex; align-items: center; gap: 7px; background: #1A2B4C; color: white; border: none; border-radius: 8px; padding: 10px 18px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }
.app-btn-primary:hover { opacity: 0.88; }
.app-stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.app-stat-card  { border-radius: 12px; padding: 20px; display: flex; align-items: center; gap: 14px; color: white; }
.app-stat-navy  { background: linear-gradient(135deg, #1A2B4C, #0e1e38); }
.app-stat-amber { background: linear-gradient(135deg, #92400e, #b45309); }
.app-stat-green { background: linear-gradient(135deg, #14532d, #166534); }
.app-stat-red   { background: linear-gradient(135deg, #7f1d1d, #991b1b); }
.app-stat-icon-wrap { width: 44px; height: 44px; border-radius: 10px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.app-stat-lbl   { font-size: 9px; font-weight: 700; letter-spacing: 0.1em; color: rgba(255,255,255,0.6); margin: 0 0 4px; }
.app-stat-num   { font-size: 28px; font-weight: 800; line-height: 1; margin: 0 0 4px; }
.app-stat-trend { font-size: 11px; color: rgba(255,255,255,0.5); margin: 0; }
.app-filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
.app-search-wrap { display: flex; align-items: center; gap: 8px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 9px 14px; flex: 1; min-width: 240px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.app-search { border: none; outline: none; font-size: 13px; color: #334155; width: 100%; font-family: inherit; background: transparent; }
.app-search::placeholder { color: #94a3b8; }
.app-filter-tabs { display: flex; gap: 4px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.app-tab { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 6px; border: none; background: none; font-size: 12px; font-weight: 500; color: #64748b; cursor: pointer; font-family: inherit; transition: all 0.15s; }
.app-tab:hover { background: #f1f5f9; color: #0f172a; }
.app-tab-active { background: #1A2B4C !important; color: white !important; }
.app-tab-count { background: #f1f5f9; color: #64748b; font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 9999px; }
.app-tab-active .app-tab-count { background: rgba(255,255,255,0.2); color: white; }
.app-table-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; margin-bottom: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.app-table-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #f1f5f9; }
.app-table-title { font-size: 14px; font-weight: 700; color: #0f172a; margin: 0; }
.app-table-count { font-size: 12px; color: #94a3b8; background: #f1f5f9; padding: 3px 10px; border-radius: 9999px; }
.app-table { width: 100%; border-collapse: collapse; text-align: left; }
.app-table th { padding: 11px 20px; background: #1A2B4C; color: white; font-size: 9px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }
.th-center { text-align: center; }
.app-table td { padding: 14px 20px; border-bottom: 1px solid #f8fafc; vertical-align: middle; }
.app-row:last-child td { border-bottom: none; }
.app-row:hover { background: #f8fafc; }
.app-job-cell { display: flex; align-items: center; gap: 10px; }
.app-job-logo { width: 38px; height: 38px; border-radius: 8px; flex-shrink: 0; color: white; font-weight: 700; font-size: 15px; display: flex; align-items: center; justify-content: center; }
.app-job-title { font-size: 13px; font-weight: 600; color: #0f172a; margin: 0 0 3px; }
.app-job-loc   { font-size: 11px; color: #94a3b8; margin: 0; }
.app-company-cell { display: flex; align-items: center; gap: 7px; }
.app-company-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.app-company { font-size: 13px; color: #475569; margin: 0; font-weight: 500; }
.app-date    { font-size: 12px; color: #64748b; margin: 0; }
.app-badge   { display: inline-flex; align-items: center; gap: 5px; font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 9999px; }
.app-badge-dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }
.badge-pending   { background: #fef3c7; color: #b45309; }
.badge-accepted  { background: #dcfce7; color: #166534; }
.badge-rejected  { background: #fee2e2; color: #991b1b; }
.badge-interview { background: #dbeafe; color: #1d4ed8; }
.badge-screening { background: #f3e8ff; color: #7c3aed; }
.app-score     { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: #475569; }
.app-score-bar { width: 52px; height: 5px; background: #f1f5f9; border-radius: 9999px; overflow: hidden; flex-shrink: 0; }
.app-score-fill { height: 100%; border-radius: 9999px; transition: width 0.4s; }
.app-score-none { font-size: 12px; color: #cbd5e1; }
.app-actions-cell { display: inline-flex; align-items: center; gap: 6px; justify-content: center; flex-wrap: wrap; }
.app-action-btn { width: 32px; height: 32px; border: 1px solid #e2e8f0; background: none; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; color: #64748b; transition: all 0.15s; }
.app-action-btn:hover { background: #1A2B4C; color: white; border-color: #1A2B4C; }
.app-action-ia { min-width: 32px; padding: 0 6px; font-size: 10px; font-weight: 700; letter-spacing: 0.04em; color: #0f766e; border-color: #99f6e4; background: #f0fdfa; }
.app-action-ia:hover { background: #0d9488; color: white; border-color: #0d9488; }
.app-table-footer { padding: 12px 20px; background: #f8fafc; border-top: 1px solid #f1f5f9; }
.app-showing { font-size: 12px; color: #94a3b8; margin: 0; }
.app-showing strong { color: #475569; }
.pipeline-wrapper { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); margin-bottom: 24px; overflow-x: auto; }
.app-loading { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px; color: #94a3b8; font-size: 13px; }
.app-empty   { background: white; border-radius: 12px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px; text-align: center; }
.app-empty-icon  { width: 64px; height: 64px; background: #f1f5f9; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.app-empty-title { font-size: 16px; font-weight: 700; color: #475569; margin: 0; }
.app-empty-sub   { font-size: 13px; color: #94a3b8; margin: 0; max-width: 300px; line-height: 1.5; }
.app-spinner { width: 28px; height: 28px; border: 3px solid #e2e8f0; border-top-color: #1A2B4C; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 1024px) { .app-stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .app-page { padding: 16px; } .app-stats-grid { grid-template-columns: 1fr; } .app-filters { flex-direction: column; } }
</style>