<template>
  <div class="page-layout">
    <AppSidebar />
    <main class="main-content">
      <GlobalHeader title="Recruitment portal" />
      <div class="content">
        <div class="page-heading">
          <div>
            <h3 class="page-title">Job Applications</h3>
            <p class="page-sub">Manage and review incoming applications across all open roles.</p>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-card"><p class="stat-label">Total Applications</p><div class="stat-value-row"><h4 class="stat-value text-white">{{ stats.total }}</h4><BarChart2Icon :size="24" /></div></div>
          <div class="stat-card"><p class="stat-label">Pending</p><div class="stat-value-row"><h4 class="stat-value text-white">{{ stats.enAttente }}</h4><ClockIcon :size="24" /></div></div>
          <div class="stat-card"><p class="stat-label">Accepted</p><div class="stat-value-row"><h4 class="stat-value text-white">{{ stats.acceptees }}</h4><CheckCircleIcon :size="24" /></div></div>
          <div class="stat-card"><p class="stat-label">Rejected</p><div class="stat-value-row"><h4 class="stat-value text-white">{{ stats.refusees }}</h4><XCircleIcon :size="24" /></div></div>
          <div class="stat-card"><p class="stat-label">Average AI Score</p><div class="stat-value-row"><h4 class="stat-value text-tertiary">{{ stats.scoreMoyenIA != null ? Math.round(stats.scoreMoyenIA) + '%' : 'N/A' }}</h4><BrainIcon :size="24" /></div></div>
        </div>

        <div class="filters-card">
          <div class="filters-grid">
            <div class="filter-group">
              <label class="filter-label">Company</label>
              <select class="filter-select" v-model="filters.entrepriseId" @change="applyFilters">
                <option value="">All Companies</option>
                <option v-for="e in entreprises" :key="e.id" :value="e.id">{{ e.nom }}</option>
              </select>
            </div>
            <div class="filter-group">
              <label class="filter-label">Job Offer</label>
              <div class="input-with-icon">
                <input type="text" class="filter-input" placeholder="Search by job title" v-model="filters.nomOffre" @change="applyFilters" />
                <ChevronDownIcon :size="16" class="select-caret" />
              </div>
            </div>
            <div class="filter-group">
              <label class="filter-label">Status</label>
              <select class="filter-select" v-model="filters.statut" @change="applyFilters">
                <option value="">All Statuses</option>
                <option value="Nouvelle">New</option>
                <option value="En cours">In progress</option>
                <option value="Présélectionné">Shortlisted</option>
                <option value="Entretien">Interview</option>
                <option value="Acceptée">Accepted</option>
                <option value="Refusée">Rejected</option>
              </select>
            </div>
            <div class="filter-group">
              <label class="filter-label">AI Score</label>
              <select class="filter-select" v-model="filters.scoreRange" @change="applyFilters">
                <option value="">Any Score</option>
                <option value="high">High (&gt;80%)</option>
                <option value="medium">Medium (50-80%)</option>
                <option value="low">Low (&lt;50%)</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="error" class="error-banner">{{ error }}</div>

        <div class="table-card">
          <div class="table-responsive">
            <table class="applications-table">
              <thead>
                <tr>
                  <th>Candidate Name</th><th>Job Offer Title</th><th>Company</th>
                  <th>Date Applied</th><th>Status</th><th>AI Score</th>
                  <th class="col-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading"><td colspan="7" class="loading-cell">Loading...</td></tr>
                <tr v-else-if="candidatures.length === 0"><td colspan="7" class="loading-cell">No applications found.</td></tr>
                <tr v-for="c in candidatures" :key="c.id" class="table-row-hover">
                  <td>
                    <div class="candidate-info">
                      <div class="candidate-avatar">
                        <img
                          :src="candidateAvatarSrc(c)"
                          :alt="c.nomCandidat"
                          @error="onCandidateAvatarError($event, c)"
                        />
                      </div>
                      <div><p class="candidate-name">{{ c.nomCandidat }}</p><p class="candidate-email">{{ c.emailCandidat }}</p></div>
                    </div>
                  </td>
                  <td><p class="cell-text-bold">{{ c.titreOffre }}</p></td>
                  <td><p class="cell-text">{{ c.nomEntreprise }}</p></td>
                  <td><p class="cell-text">{{ formatDate(c.creeLe) }}</p></td>
                  <td>
                    <span class="status-badge" :class="'badge-' + getStatusClass(c.statut)">
                      <span class="status-dot" :class="'bg-' + getStatusClass(c.statut)"></span>
                      {{ statusLabel(c.statut) }}
                    </span>
                  </td>
                  <td>
                    <div class="score-wrapper" v-if="c.scoreIA != null">
                      <div class="progress-bar-bg"><div class="progress-bar-fill" :class="'bg-' + getScoreClass(c.scoreIA)" :style="{ width: getScoreValue(c.scoreIA) + '%' }"></div></div>
                      <span class="score-text" :class="'text-' + getScoreClass(c.scoreIA)">{{ formatScore(c.scoreIA) }}</span>
                    </div>
                    <button v-else class="action-btn text-primary btn-bg-hover" title="Calculate" @click="handleRecalculateScore(c.id)" style="font-size:11px;padding:4px 8px;border-radius:4px;border:1px solid #E2E8F0;background:#fff;">
                      <BrainIcon :size="14" style="margin-right:4px;" /> Calculate
                    </button>
                  </td>
                  <td class="col-right">
                    <div class="actions">
                      <button class="action-btn text-primary btn-bg-hover" title="View Details" @click="goToDetails(c.id)">
                        <EyeIcon :size="16" /><span class="action-text">View</span>
                      </button>
                      <button class="action-btn text-secondary btn-bg-hover" title="Move Stage" @click="openPipelineModal(c)">
                        <ArrowRightLeftIcon :size="16" />
                      </button>
                       <CandidateActionsDropdown  :candidate="c" @action="handleDropdownAction" />
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination-bar">
            <p class="pagination-info">Showing <span class="font-bold">{{ candidatures.length }}</span> of <span class="font-bold">{{ stats.total }}</span> applications</p>
          </div>
        </div>
      </div>

      <div v-if="showPipelineModal" class="pipeline-overlay" @click.self="closePipelineModal">
        <div class="pipeline-modal">
          <div class="pipeline-modal-header">
            <div>
              <h3 class="pipeline-modal-title">Move to Stage</h3>
              <p class="pipeline-modal-sub" v-if="selectedCandidature">
                {{ selectedCandidature.nomCandidat }}<span class="sep">·</span>{{ selectedCandidature.titreOffre }}
              </p>
            </div>
            <button class="modal-close-btn" @click="closePipelineModal">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            </button>
          </div>
          <div class="pipeline-modal-body">
            <CandidatePipelineBoard :candidatures="selectedCandidatureForBoard" :show-header="false" mode="full" :enableDrag="true" @select="handleCardClick" @status-change="handlePipelineStatusChange" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import CandidateActionsDropdown from '../../components/common/CandidateActionsDropdown.vue'
import CandidatePipelineBoard from '../../components/CandidatePipelineBoard.vue'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import { BarChart2Icon, ClockIcon, CheckCircleIcon, XCircleIcon, BrainIcon, ChevronDownIcon, EyeIcon, ArrowRightLeftIcon } from 'lucide-vue-next'
import { getCandidatures, getCandidatureStats, updateCandidateStatus, recalculateMatchScore, rejectCandidate } from '../../services/candidatureService.js'
import api from '../../services/api.js'
import { getEntreprises } from '../../services/offreService.js'
import { useNotificationStore } from '../../stores/notification'
import { applicationStatusLabel, formatRecruiterDate } from '../../utils/recruiterI18n.js'

export default {
  name: 'JobApplications',
  components: { AppSidebar, GlobalHeader, CandidatePipelineBoard, CandidateActionsDropdown, BarChart2Icon, ClockIcon, CheckCircleIcon, XCircleIcon, BrainIcon, ChevronDownIcon, EyeIcon, ArrowRightLeftIcon },
  setup() {
    const notificationStore = useNotificationStore()
    const toast = {
      success: (msg) => notificationStore.addToast({ type: 'success', message: msg }),
      error:   (msg) => notificationStore.addToast({ type: 'error',   message: msg }),
      info:    (msg) => notificationStore.addToast({ type: 'info',    message: msg })
    }
    return { toast }
  },
  data() {
    return {
      candidatures: [], entreprises: [],
      stats: { total:0, enAttente:0, acceptees:0, refusees:0, scoreMoyenIA:null },
      loading: false, error: null,
      filters: { entrepriseId:'', nomOffre:'', statut:'', scoreRange:'' },
      showPipelineModal: false, selectedCandidature: null, stageUpdating: false,
      showProfileModal: false, selectedProfileId: null
    }
  },
  computed: {
    selectedCandidatureForBoard() {
      if (!this.selectedCandidature) return []
      return [{ id:this.selectedCandidature.id, statut:this.selectedCandidature.statut, candidatNomComplet:this.selectedCandidature.nomCandidat, offreTitre:this.selectedCandidature.titreOffre, creeLe:this.selectedCandidature.creeLe, offreId:this.selectedCandidature.offreId??this.selectedCandidature.id, avisExpert:this.selectedCandidature.scoreIA!=null?{score:this.selectedCandidature.scoreIA/20}:null, tousLesAvis:[] }]
    }
  },
  async created() { await Promise.all([this.fetchStats(), this.fetchEntreprises()]); await this.fetchCandidatures() },
  methods: {
    openPipelineModal(c) {
      const found = this.candidatures.find(x => x.id === c.id)
      this.selectedCandidature = found ?? { id:c.id, nomCandidat:c.candidatNomComplet??c.nomCandidat, titreOffre:c.offreTitre??c.titreOffre, statut:c.statut, creeLe:c.creeLe, scoreIA:null }
      this.showPipelineModal = true
    },
    closePipelineModal() { this.showPipelineModal = false; this.selectedCandidature = null },
    handleCardClick(c) { this.goToDetails(c.id) },
    async handlePipelineStatusChange({ candidateId, toStatus }) {
      if (!candidateId || !toStatus || this.stageUpdating) return
      this.stageUpdating = true
      try {
        await updateCandidateStatus(candidateId, toStatus)
        const row = this.candidatures.find(c => c.id === candidateId)
        if (row) row.statut = toStatus
        if (this.selectedCandidature?.id === candidateId) this.selectedCandidature.statut = toStatus
        await this.fetchStats(); this.toast.success(`Status updated to "${applicationStatusLabel(toStatus)}"`)
      } catch { this.toast.error('Failed to update candidate status') }
      finally { this.stageUpdating = false }
    },
    async fetchCandidatures() {
      this.loading = true; this.error = null
      try {
        const params = { entrepriseId:this.filters.entrepriseId||undefined, nomOffre:this.filters.nomOffre||undefined, statut:this.filters.statut||undefined }
        if (this.filters.scoreRange === 'high')        { params.scoreMin = 80 }
        else if (this.filters.scoreRange === 'medium') { params.scoreMin = 50; params.scoreMax = 80 }
        else if (this.filters.scoreRange === 'low')    { params.scoreMax = 50 }
        const res = await getCandidatures(params); this.candidatures = res.data
      } catch { this.error = 'Unable to load applications.' }
      finally { this.loading = false }
    },
    async fetchStats()      { try { const res = await getCandidatureStats(); this.stats = res.data } catch {} },
    async fetchEntreprises(){ try { const res = await getEntreprises(); this.entreprises = res.data } catch {} },
    applyFilters() { this.fetchCandidatures() },
    apiOrigin() {
      const base = api.defaults.baseURL || ''
      return base.replace(/\/?api\/?$/i, '') || 'http://localhost:5202'
    },
    candidateAvatarFallback(c) {
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(c.nomCandidat || '?')}&background=random&size=128`
    },
    candidateAvatarSrc(c) {
      const raw = (c.avatarUrl ?? c.AvatarUrl ?? '').trim()
      if (!raw) return this.candidateAvatarFallback(c)
      if (/^https?:\/\//i.test(raw)) return raw
      if (raw.startsWith('/')) return `${this.apiOrigin()}${raw}`
      return raw
    },
    onCandidateAvatarError(ev, c) {
      const el = ev?.target
      if (!el || el.dataset.fallbackApplied === '1') return
      el.dataset.fallbackApplied = '1'
      el.src = this.candidateAvatarFallback(c)
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return formatRecruiterDate(dateStr)
    },
    statusLabel(statut) {
      return applicationStatusLabel(statut)
    },
    getStatusClass(statut) { return { 'Nouvelle':'primary','En cours':'tertiary','Acceptée':'success','Refusée':'error' }[statut] || 'primary' },
    getScoreClass(score)   { return score == null ? 'primary' : score >= 50 ? 'tertiary' : 'error' },
    formatScore(score)     { return score == null ? 'N/A' : Math.round(score) + '%' },
    getScoreValue(score)   { return score != null ? Math.round(score) : 0 },
    goToDetails(id)        { this.$router.push(`/recruiter/candidates/${id}`) },
    openProfileModal(id)   { this.selectedProfileId = id; this.showProfileModal = true },
    closeProfileModal()    { this.showProfileModal = false; this.selectedProfileId = null },
    async handleDropdownAction({ action, candidate }) {
      const candidateId = candidate.id
      if (action === 'view')                              { this.goToDetails(candidateId) }
      else if (action === 'view-profile')                 { this.openProfileModal(candidateId) }
      else if (action === 'view-cv')                      { this.handleViewCV(candidate) }
      else if (action === 'calculate' || action === 'recalculate') { await this.handleRecalculateScore(candidateId) }
      else if (action === 'reject') {
        await rejectCandidate(candidateId)
        this.toast.success('Candidate rejected.')
        this.fetchCandidatures()
      } else { this.toast.info(`Action ${action} triggered.`) }
    },
    async handleRecalculateScore(candidateId) {
      this.toast.info('Calculating score...')
      try {
        const res = await recalculateMatchScore(candidateId)
        const candidate = this.candidatures.find(c => c.id === candidateId)
        if (candidate) {
          candidate.scoreIA = res.data.score
          if (res.data.statut) candidate.statut = res.data.statut
        }
        if (res.data.autoDeclined) this.toast.info(`Score ${res.data.score}% — application auto-declined`)
        else this.toast.success(`New score: ${res.data.score}%`)
        await this.fetchStats()
      } catch { this.toast.error('Failed to calculate score') }
    },
    handleViewCV(candidate) {
      if (candidate?.cvUrl) {
        const url = candidate.cvUrl.startsWith('http') ? candidate.cvUrl : `http://localhost:5202/${candidate.cvUrl}`
        window.open(url, '_blank')
      } else { this.toast.error('No CV URL found.') }
    }
  }
}
</script>

<style scoped>
.page-layout  { display:flex; height:100vh; overflow:hidden; background:#f5f7f8; font-family:'Inter',sans-serif; }
.main-content { flex:1; display:flex; flex-direction:column; min-width:0; overflow:hidden; }
.content      { flex:1; padding:32px; overflow-y:auto; max-width:1920px; margin:0 auto; width:100%; box-sizing:border-box; }
.page-heading { margin-bottom:32px; }
.page-title   { font-size:24px; font-weight:700; color:#0F172A; margin:0 0 8px; }
.page-sub     { font-size:14px; color:#64748B; margin:0; }
.stats-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:24px; margin-bottom:40px; }
.stat-card { background:#454a83; padding:24px; border-radius:8px; }
.stat-label { font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; color:#94A3B8; margin:0 0 8px; }
.stat-value-row { display:flex; align-items:flex-end; justify-content:space-between; }
.stat-value { font-size:24px; font-weight:700; line-height:1; margin:0; }
.text-white { color:#fff; } .text-tertiary { color:#0D9488; } .text-primary { color:#454a83; } .text-secondary { color:#64748B; }
.filters-card { background:#fff; padding:24px; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:32px; }
.filters-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.filter-group { display:flex; flex-direction:column; }
.filter-label { font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; color:#64748B; margin-bottom:8px; }
.filter-select, .filter-input { color:#0F172A; height:44px; background:#F5F7FA; border:1px solid #E2E8F0; border-radius:8px; padding:0 12px; font-size:14px; outline:none; font-family:inherit; width:100%; box-sizing:border-box; }
.input-with-icon { position:relative; } .input-with-icon .filter-input { padding-right:40px; }
.select-caret { position:absolute; right:12px; top:50%; transform:translateY(-50%); color:#94A3B8; pointer-events:none; }
.error-banner { background:#FFE4E6; color:#E11D48; border:1px solid #E11D48; border-radius:8px; padding:12px 16px; font-size:14px; margin-bottom:24px; }
.table-card { background:#fff; border-radius:8px; border:1px solid #E2E8F0; overflow:visible; }
.table-responsive { overflow:visible !important; }
.applications-table { width:100%; border-collapse:collapse; text-align:left; }
.applications-table th { padding:16px 24px; background:#F5F7FA; border-bottom:1px solid #E2E8F0; font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; color:#64748B; }
.applications-table td { padding:16px 24px; border-bottom:1px solid #E2E8F0; vertical-align:middle; }
.loading-cell { text-align:center; color:#94A3B8; font-size:14px; padding:40px !important; }
.table-row-hover:hover { background-color:#F5F7FA; }
.col-right { text-align:right; }
.candidate-info { display:flex; align-items:center; gap:12px; }
.candidate-avatar { width:40px; height:40px; border-radius:8px; overflow:hidden; border:1px solid #E2E8F0; }
.candidate-avatar img { width:100%; height:100%; object-fit:cover; }
.candidate-name  { font-size:14px; font-weight:700; color:#0F172A; margin:0 0 2px; }
.candidate-email { font-size:12px; color:#64748B; margin:0; }
.cell-text-bold  { font-size:14px; font-weight:500; color:#0F172A; margin:0; }
.cell-text       { font-size:14px; color:#64748B; margin:0; }
.status-badge { display:inline-flex; align-items:center; gap:4px; padding:4px 10px; border-radius:9999px; font-size:11px; font-weight:700; width:max-content; }
.status-dot   { width:6px; height:6px; border-radius:50%; }
.badge-tertiary { background:rgba(13,148,136,0.1); color:#0D9488; } .bg-tertiary { background:#0D9488; }
.badge-primary  { background:rgba(69,74,131,0.1); color:#454a83; } .bg-primary  { background:#454a83; }
.badge-error    { background:#FFE4E6; color:#E11D48; }             .bg-error    { background:#E11D48; }
.badge-success  { background:#CCFBF1; color:#134E4A; }
.score-wrapper { display:flex; align-items:center; gap:12px; }
.progress-bar-bg { flex:1; height:6px; background:#E2E8F0; border-radius:9999px; overflow:hidden; max-width:80px; }
.progress-bar-fill { height:100%; border-radius:9999px; }
.score-text { font-size:12px; font-weight:700; }
.actions { display:flex; align-items:center; justify-content:flex-end; gap:4px; }
.action-btn { padding:6px 8px; border:none; background:none; border-radius:6px; cursor:pointer; display:flex; align-items:center; gap:6px; color:#64748B; }
.action-btn:hover { background-color:rgba(69,74,131,0.08); color:#0F172A; }
.btn-bg-hover { background:white; border:1px solid #E2E8F0; }
.btn-bg-hover:hover { background:#F8FAFC; border-color:#CBD5E1; }
.action-text { font-size:12px; font-weight:600; }
.pagination-bar  { padding:16px 24px; background:#F5F7FA; border-top:1px solid #E2E8F0; display:flex; align-items:center; justify-content:space-between; }
.pagination-info { font-size:12px; color:#64748B; font-weight:500; margin:0; }
.font-bold { font-weight:700; color:#0F172A; }
.pipeline-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.5); backdrop-filter:blur(3px); display:flex; align-items:center; justify-content:center; z-index:300; }
.pipeline-modal { background:#fff; border-radius:16px; width:960px; max-width:96vw; max-height:90vh; overflow-y:auto; }
.pipeline-modal-header { display:flex; justify-content:space-between; align-items:flex-start; padding:22px 28px; border-bottom:1px solid #e2e8f0; position:sticky; top:0; background:#fff; z-index:1; }
.pipeline-modal-title { font-size:1.05rem; font-weight:800; color:#0f172a; margin:0 0 4px; }
.pipeline-modal-sub   { font-size:0.82rem; color:#94a3b8; margin:0; }
.sep { margin:0 6px; color:#cbd5e1; }
.modal-close-btn { background:none; border:none; cursor:pointer; color:#94a3b8; padding:4px; border-radius:6px; display:flex; }
.modal-close-btn:hover { background:#f1f5f9; color:#475569; }
.pipeline-modal-body { padding:24px 28px 28px; }
</style>