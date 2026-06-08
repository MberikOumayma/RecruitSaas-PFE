<template>
  <div class="page-layout">
    <AppSidebar />
    <main class="main-content">
      <GlobalHeader title="Job Applications" />
      <div class="content">

        <!-- Back + Heading -->
        <div class="page-heading">
          <div class="back-row">
            <button class="back-btn" @click="$router.back()">
              <ArrowLeftIcon :size="16" />
              Back to Job Offers
            </button>
          </div>
          <div class="heading-row">
            <div>
              <h2 class="page-title">Candidates for this offer</h2>
              <p class="page-sub" v-if="offerTitle">
                <BriefcaseIcon :size="14" class="inline-icon" />
                {{ offerTitle }}
              </p>
            </div>
            <div class="heading-actions">
              <button class="rank-btn" @click="rankByFaiss" :disabled="ranking || loading">
                <component :is="ranking ? 'Loader2Icon' : 'ListOrderedIcon'" :size="15" :class="{ 'spin-icon': ranking }" />
                {{ ranking ? 'Ranking…' : 'Rank by AI' }}
              </button>
              <button class="export-btn" @click="exportExcel" :disabled="exporting">
                <component :is="exporting ? 'Loader2Icon' : 'TableIcon'" :size="15" :class="{ 'spin-icon': exporting }" />
                {{ exporting ? 'Generating…' : 'Export Excel' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="filters-card">
          <div class="filters-grid">
            <div class="filter-group">
              <label class="filter-label">Status</label>
              <select class="filter-select" v-model="filters.statut" @change="fetchCandidatures">
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
              <select class="filter-select" v-model="filters.scoreRange" @change="fetchCandidatures">
                <option value="">Any Score</option>
                <option value="high">High (&gt;80%)</option>
                <option value="medium">Medium (50-80%)</option>
                <option value="low">Low (&lt;50%)</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="error" class="error-banner">{{ error }}</div>
        <div v-if="isRanked" class="rank-banner">
          <ListOrderedIcon :size="16" />
          Candidates ranked by FAISS similarity + AI scoring (best match first).
          <button class="rank-reset-btn" @click="resetRank">Reset order</button>
        </div>

        <!-- Table -->
        <div class="table-card">
          <div class="table-responsive">
            <table class="applications-table">
              <thead>
                <tr>
                  <th v-if="isRanked" class="col-rank">Rank</th>
                  <th>Candidate Name</th>
                  <th>Date Applied</th>
                  <th>Status</th>
                  <th>AI Score</th>
                  <th class="col-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td :colspan="tableColspan" class="loading-cell">Loading...</td>
                </tr>
                <tr v-else-if="candidatures.length === 0">
                  <td :colspan="tableColspan" class="loading-cell">No applications found for this offer.</td>
                </tr>
                <tr v-for="c in candidatures" :key="c.id" class="table-row-hover">
                  <td v-if="isRanked">
                    <span class="rank-badge" :class="'rank-' + Math.min(c.rank || 99, 3)">#{{ c.rank }}</span>
                  </td>
                  <td>
                    <div class="candidate-info">
                      <div class="candidate-avatar">
                        <img
                          :src="candidateAvatarSrc(c)"
                          :alt="c.nomCandidat"
                          @error="onCandidateAvatarError($event, c)"
                        />
                      </div>
                      <div>
                        <p class="candidate-name">{{ c.nomCandidat }}</p>
                        <p class="candidate-email">{{ c.emailCandidat }}</p>
                      </div>
                    </div>
                  </td>
                  <td>
                    <p class="cell-text">{{ formatDate(c.creeLe) }}</p>
                  </td>
                  <td>
                    <span class="status-badge" :class="'badge-' + getStatusClass(c.statut)">
                      <span class="status-dot" :class="'bg-' + getStatusClass(c.statut)"></span>
                      {{ statusLabel(c.statut) }}
                    </span>
                  </td>
                  <td>
                    <div class="score-wrapper" v-if="displayScore(c) != null">
                      <div class="progress-bar-bg">
                        <div class="progress-bar-fill" :class="'bg-' + getScoreClass(displayScore(c))"
                          :style="{ width: getScoreValue(displayScore(c)) + '%' }">
                        </div>
                      </div>
                      <span class="score-text" :class="'text-' + getScoreClass(displayScore(c))">
                        {{ formatScore(displayScore(c)) }}
                      </span>
                      <span v-if="isRanked && c.vectorSimilarity != null" class="sim-text" title="FAISS vector similarity">
                        sim {{ Math.round(c.vectorSimilarity * 100) }}%
                      </span>
                    </div>
                    <button v-else class="action-btn text-primary btn-bg-hover" title="Calculate"
                      @click="handleRecalculateScore(c.id)"
                      style="font-size: 11px; padding: 4px 8px; border-radius: 4px; border: 1px solid #E2E8F0; background: #fff;">
                      <BrainIcon :size="14" style="margin-right:4px;" /> Calculate
                    </button>
                  </td>
                  <td class="col-right">
                    <div class="actions">
                      <button class="action-btn text-primary btn-bg-hover" title="View Details"
                        @click="goToDetails(c.id)">
                        <EyeIcon :size="16" />
                        <span class="action-text">View</span>
                      </button>
                      <button class="action-btn text-secondary btn-bg-hover" title="Move Stage"
                        @click="openPipelineModal(c)">
                        <ArrowRightLeftIcon :size="16" />
                      </button>
                      <CandidateActionsDropdown :candidate="c" @action="handleDropdownAction" />
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination-bar">
            <p class="pagination-info">
              Showing <span class="font-bold">{{ candidatures.length }}</span> candidate(s)
            </p>
          </div>
        </div>

      </div>

      <!-- Pipeline Modal -->
      <div v-if="showPipelineModal" class="pipeline-overlay" @click.self="closePipelineModal">
        <div class="pipeline-modal">
          <div class="pipeline-modal-header">
            <div>
              <h3 class="pipeline-modal-title">Move to Stage</h3>
              <p class="pipeline-modal-sub" v-if="selectedCandidature">
                {{ selectedCandidature.nomCandidat }}
                <span class="sep">·</span>
                {{ selectedCandidature.titreOffre }}
              </p>
            </div>
            <button class="modal-close-btn" @click="closePipelineModal">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <div class="pipeline-modal-body">
            <CandidatePipelineBoard :candidatures="selectedCandidatureForBoard" :show-header="false" mode="full"
              :enableDrag="true" @select="handleCardClick" @status-change="handlePipelineStatusChange" />
          </div>
        </div>
      </div>

      <!-- Profile Modal -->
      <CandidatDetailProfile v-if="showProfileModal" :candidature-id="selectedProfileId" @close="closeProfileModal" />
    </main>
  </div>
</template>

<script>
import CandidatePipelineBoard from '../../components/CandidatePipelineBoard.vue'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import CandidateActionsDropdown from '../../components/common/CandidateActionsDropdown.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import CandidatDetailProfile from './CandidatDetailProfile.vue'
import {
  BrainIcon, EyeIcon, ArrowRightLeftIcon, ArrowLeftIcon, BriefcaseIcon, TableIcon, Loader2Icon, ListOrderedIcon
} from 'lucide-vue-next'
import {
  getCandidatures, updateCandidateStatus, recalculateMatchScore, rejectCandidate, rankCandidatesForOffer
} from '../../services/candidatureService.js'
import api from '../../services/api.js'
import { downloadOfferCandidatesExcel } from '../../services/reportService.js'
import { useNotificationStore } from '../../stores/notification'
import { applicationStatusLabel, formatRecruiterDate } from '../../utils/recruiterI18n.js'

export default {
  name: 'OfferCandidates',
  components: {
    AppSidebar, GlobalHeader, CandidatePipelineBoard, CandidateActionsDropdown, CandidatDetailProfile,
    BrainIcon, EyeIcon, ArrowRightLeftIcon, ArrowLeftIcon, BriefcaseIcon, TableIcon, Loader2Icon, ListOrderedIcon
  },
  setup() {
    const notificationStore = useNotificationStore()
    const toast = {
      success: (msg) => notificationStore.addToast({ type: 'success', message: msg }),
      error: (msg) => notificationStore.addToast({ type: 'error', message: msg }),
      info: (msg) => notificationStore.addToast({ type: 'info', message: msg })
    }
    return { toast }
  },
  data() {
    return {
      candidatures: [],
      offerTitle: '',
      loading: false,
      error: null,
      filters: { statut: '', scoreRange: '' },
      showPipelineModal: false,
      selectedCandidature: null,
      stageUpdating: false,
      showProfileModal: false,
      selectedProfileId: null,
      exporting: false,
      ranking: false,
      isRanked: false
    }
  },
  computed: {
    offreId() {
      return this.$route.params.id
    },
    tableColspan() {
      return this.isRanked ? 6 : 5
    },
    selectedCandidatureForBoard() {
      if (!this.selectedCandidature) return []
      return [{
        id: this.selectedCandidature.id,
        statut: this.selectedCandidature.statut,
        candidatNomComplet: this.selectedCandidature.nomCandidat,
        offreTitre: this.selectedCandidature.titreOffre,
        creeLe: this.selectedCandidature.creeLe,
        offreId: this.selectedCandidature.offreId ?? this.selectedCandidature.id,
        avisExpert: this.selectedCandidature.scoreIA != null
          ? { score: this.selectedCandidature.scoreIA / 20 }
          : null,
        tousLesAvis: []
      }]
    }
  },
  async created() {
    await this.fetchCandidatures()
  },
  methods: {
    async fetchCandidatures() {
      this.loading = true
      this.error = null
      this.isRanked = false
      try {
        const params = {
          offreId: this.offreId,
          statut: this.filters.statut || undefined
        }
        if (this.filters.scoreRange === 'high') { params.scoreMin = 80 }
        else if (this.filters.scoreRange === 'medium') { params.scoreMin = 50; params.scoreMax = 80 }
        else if (this.filters.scoreRange === 'low') { params.scoreMax = 50 }

        const res = await getCandidatures(params)
        this.candidatures = res.data

        // Grab offer title from first candidate if available
        if (this.candidatures.length > 0 && this.candidatures[0].titreOffre) {
          this.offerTitle = this.candidatures[0].titreOffre
        }
      } catch {
        this.error = 'Unable to load applications.'
      } finally {
        this.loading = false
      }
    },

    goToDetails(id) {
      this.$router.push(`/recruiter/candidates/${id}`)
    },

    formatDate(dateStr) {
      if (!dateStr) return '-'
      return formatRecruiterDate(dateStr)
    },
    statusLabel(statut) {
      return applicationStatusLabel(statut)
    },

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

    getStatusClass(statut) {
      return { 'Nouvelle': 'primary', 'En cours': 'tertiary', 'Acceptée': 'success', 'Refusée': 'error' }[statut] || 'primary'
    },

    getScoreClass(score) { return score == null ? 'primary' : score >= 50 ? 'tertiary' : 'error' },
    formatScore(score) { return score == null ? 'N/A' : Math.round(score) + '%' },
    getScoreValue(score) { return score != null ? Math.round(score) : 0 },

    displayScore(c) {
      if (this.isRanked && c.faissScore != null) return c.faissScore
      return c.scoreIA
    },

    async rankByFaiss() {
      if (!this.offreId || this.ranking) return
      this.ranking = true
      this.error = null
      this.toast.info('FAISS ranking in progress…')
      try {
        const res = await rankCandidatesForOffer(this.offreId)
        const ranked = res.data?.ranked ?? res.data?.Ranked ?? []
        if (!ranked.length) {
          this.toast.error('No candidates to rank for this offer.')
          return
        }
        this.candidatures = ranked.map(r => ({
          ...r,
          rank: r.rank ?? r.Rank,
          faissScore: r.faissScore ?? r.FaissScore,
          vectorSimilarity: r.vectorSimilarity ?? r.VectorSimilarity,
          scoreIA: r.scoreIA ?? r.ScoreIA ?? r.faissScore ?? r.FaissScore
        }))
        this.isRanked = true
        if (this.candidatures[0]?.titreOffre) {
          this.offerTitle = this.candidatures[0].titreOffre
        }
        this.toast.success('Candidates ranked by AI relevance.')
      } catch {
        this.error = 'Unable to rank candidates. Check that the AI service is running.'
        this.toast.error('FAISS ranking failed.')
      } finally {
        this.ranking = false
      }
    },

    resetRank() {
      this.isRanked = false
      this.fetchCandidatures()
    },

    openProfileModal(id) {
      this.selectedProfileId = id
      this.showProfileModal = true
    },
    closeProfileModal() {
      this.showProfileModal = false
      this.selectedProfileId = null
    },

    openPipelineModal(c) {
      const found = this.candidatures.find(x => x.id === c.id)
      this.selectedCandidature = found ?? {
        id: c.id,
        nomCandidat: c.candidatNomComplet ?? c.nomCandidat,
        titreOffre: c.offreTitre ?? c.titreOffre,
        statut: c.statut,
        creeLe: c.creeLe,
        scoreIA: null
      }
      this.showPipelineModal = true
    },

    closePipelineModal() {
      this.showPipelineModal = false
      this.selectedCandidature = null
    },

    handleCardClick(c) {
      this.goToDetails(c.id)
    },

    async handlePipelineStatusChange({ candidateId, toStatus }) {
      if (!candidateId || !toStatus || this.stageUpdating) return
      this.stageUpdating = true
      try {
        await updateCandidateStatus(candidateId, toStatus)
        const row = this.candidatures.find(c => c.id === candidateId)
        if (row) row.statut = toStatus
        if (this.selectedCandidature?.id === candidateId) {
          this.selectedCandidature.statut = toStatus
        }
        this.toast.success(`Status updated to "${toStatus}"`)
      } catch {
        this.toast.error('Failed to update candidate status')
      } finally {
        this.stageUpdating = false
      }
    },

    async handleDropdownAction({ action, candidate }) {
      const candidateId = candidate.id
      if (action === 'view') {
        this.goToDetails(candidateId)
      } else if (action === 'view-profile') {
        this.openProfileModal(candidateId)
      } else if (action === 'view-cv') {
        this.handleViewCV(candidate)
      } else if (action === 'calculate' || action === 'recalculate') {
        await this.handleRecalculateScore(candidateId)
      } else if (action === 'reject') {
        await rejectCandidate(candidateId)
        this.toast.success('Candidate rejected.')
        this.fetchCandidatures()
      } else {
        this.toast.info(`Action ${action} triggered.`)
      }
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
        if (this.selectedCandidature?.id === candidateId) {
          this.selectedCandidature.scoreIA = res.data.score
          if (res.data.statut) this.selectedCandidature.statut = res.data.statut
        }
        if (res.data.autoDeclined) this.toast.info(`Score ${res.data.score}% — application auto-declined`)
        else this.toast.success(`New score: ${res.data.score}%`)
      } catch {
        this.toast.error('Failed to calculate score')
      }
    },

    handleViewCV(candidate) {
      if (candidate?.cvUrl) {
        const url = candidate.cvUrl.startsWith('http')
          ? candidate.cvUrl
          : `http://localhost:5202/${candidate.cvUrl}`
        window.open(url, '_blank')
      } else {
        this.toast.error('No CV URL found.')
      }
    },

    async exportExcel() {
      this.exporting = true
      this.toast.info('Generating Excel report…')
      try {
        await downloadOfferCandidatesExcel(this.offreId, this.offerTitle || 'offer')
        this.toast.success('Excel downloaded!')
      } catch {
        this.toast.error('Failed to generate Excel report.')
      } finally {
        this.exporting = false
      }
    }
  }
}
</script>

<style scoped>
.page-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f5f7f8;
  font-family: 'Inter', sans-serif;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* Heading */
.page-heading {
  margin-bottom: 28px;
}

.back-row {
  margin-bottom: 16px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px 6px 10px;
  background: #fff;
  border: 1px solid rgba(69, 74, 131, 0.18);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #454a83;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s, box-shadow 0.15s;
}

.back-btn:hover {
  background: rgba(69, 74, 131, 0.06);
  box-shadow: 0 1px 4px rgba(69, 74, 131, 0.1);
}

.heading-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.heading-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.rank-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 18px;
  background: #454a83;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.15s, transform 0.1s;
}

.rank-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.rank-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.rank-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  background: #EEF2FF;
  color: #3730A3;
  border: 1px solid #C7D2FE;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  margin-bottom: 24px;
}

.rank-reset-btn {
  margin-left: auto;
  padding: 4px 10px;
  border: 1px solid #C7D2FE;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #3730A3;
  cursor: pointer;
  font-family: inherit;
}

.rank-reset-btn:hover {
  background: #E0E7FF;
}

.col-rank {
  width: 72px;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  padding: 4px 8px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 800;
  background: #F1F5F9;
  color: #475569;
}

.rank-badge.rank-1 {
  background: #FEF3C7;
  color: #B45309;
}

.rank-badge.rank-2 {
  background: #F1F5F9;
  color: #334155;
}

.rank-badge.rank-3 {
  background: #FFEDD5;
  color: #C2410C;
}

.sim-text {
  font-size: 10px;
  font-weight: 600;
  color: #64748B;
  white-space: nowrap;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 6px;
}

.page-sub {
  font-size: 14px;
  color: #64748B;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.inline-icon {
  color: #454a83;
  flex-shrink: 0;
}

/* Filters */
.filters-card {
  background: #fff;
  padding: 20px 24px;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 16px;
}

@media(min-width:640px) {
  .filters-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-label {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748B;
  margin-bottom: 8px;
}

.filter-select {
  color: #0F172A;
  height: 44px;
  background: #F5F7FA;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
  cursor: pointer;
}

/* Error */
.error-banner {
  background: #FFE4E6;
  color: #E11D48;
  border: 1px solid #E11D48;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  margin-bottom: 24px;
}

/* Table */
.table-card {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  overflow: visible;
}

.table-responsive {
  overflow: visible !important;
}

.applications-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.applications-table th {
  padding: 16px 24px;
  background: #F5F7FA;
  border-bottom: 1px solid #E2E8F0;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748B;
}

.applications-table td {
  padding: 16px 24px;
  border-bottom: 1px solid #E2E8F0;
  vertical-align: middle;
}

.loading-cell {
  text-align: center;
  color: #94A3B8;
  font-size: 14px;
  padding: 48px !important;
}

.table-row-hover {
  transition: background-color 0.2s;
}

.table-row-hover:hover {
  background-color: #F5F7FA;
}

.col-right {
  text-align: right;
}

/* Candidate cell */
.candidate-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.candidate-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #E2E8F0;
  flex-shrink: 0;
}

.candidate-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.candidate-name {
  font-size: 14px;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 2px;
}

.candidate-email {
  font-size: 12px;
  color: #64748B;
  margin: 0;
}

.cell-text {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

/* Status badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 700;
  width: max-content;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.badge-primary { background: rgba(69, 74, 131, 0.1); color: #454a83; }
.bg-primary { background: #454a83; }
.badge-tertiary { background: rgba(13, 148, 136, 0.1); color: #0D9488; }
.bg-tertiary { background: #0D9488; }
.badge-success { background: #CCFBF1; color: #134E4A; }
.bg-success { background: #0D9488; }
.badge-error { background: #FFE4E6; color: #E11D48; }
.bg-error { background: #E11D48; }

/* Score */
.score-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.progress-bar-bg {
  flex: 1;
  height: 6px;
  background: #E2E8F0;
  border-radius: 9999px;
  overflow: hidden;
  max-width: 80px;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.score-text {
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.text-primary { color: #454a83; }
.text-tertiary { color: #0D9488; }
.text-error { color: #E11D48; }
.text-secondary { color: #64748B; }

/* Actions */
.actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  font-family: inherit;
  transition: background 0.15s, color 0.15s;
  color: #64748B;
}

.btn-bg-hover:hover {
  background: rgba(69, 74, 131, 0.08);
}

.action-text {
  font-size: 12px;
}

/* Pagination */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  border-top: 1px solid #E2E8F0;
  background: #F5F7FA;
}

.pagination-info {
  font-size: 13px;
  color: #64748B;
  font-weight: 500;
  margin: 0;
}

.font-bold { font-weight: 700; }

/* Pipeline Modal */
.pipeline-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.pipeline-modal {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 900px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pipeline-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid #E2E8F0;
}

.pipeline-modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 4px;
}

.pipeline-modal-sub {
  font-size: 13px;
  color: #64748B;
  margin: 0;
}

.sep {
  margin: 0 4px;
  color: #CBD5E1;
}

.modal-close-btn {
  padding: 6px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 6px;
  color: #94A3B8;
  transition: color 0.15s, background 0.15s;
}

.modal-close-btn:hover {
  color: #0F172A;
  background: #F1F5F9;
}

.pipeline-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* Export button */
.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 18px;
  background: #16a34a;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.15s, transform 0.1s;
  flex-shrink: 0;
}

.export-btn:hover:not(:disabled) {
  opacity: 0.88;
  transform: translateY(-1px);
}

.export-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

@keyframes spin-anim { to { transform: rotate(360deg); } }
.spin-icon { animation: spin-anim 0.7s linear infinite; }
</style>
