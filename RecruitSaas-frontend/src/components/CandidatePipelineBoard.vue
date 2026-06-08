<template>
  <div class="pipeline-board">

    <!-- Header optionnel -->
    <div v-if="showHeader" class="board-header">
      <span class="board-title">{{ title }}</span>
      <div class="board-actions">
        <span class="board-total">{{ totalVisible }} total</span>
        <button class="btn-sort" @click="toggleSort">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18M7 12h10M11 18h2"/>
          </svg>
          {{ sortByScore ? 'Sort: Score ↓' : 'Sort: Date ↓' }}
        </button>
      </div>
    </div>

    <!-- Colonnes pipeline -->
    <div class="pipeline-grid" :style="{ gridTemplateColumns: `repeat(${columns.length}, 1fr)` }">
      <div
        v-for="col in columns"
        :key="col.statut"
        class="pipeline-col"
        :class="{ 'drop-active': enableDrag && dragOverStatus === col.statut }"
        @dragover.prevent="onDragOver(col.statut)"
        @dragleave="onDragLeave(col.statut)"
        @drop.prevent="onDrop(col.statut)"
      >
        <!-- Header colonne -->
        <div class="col-header">
          <span class="col-dot" :style="{ background: col.color }"></span>
          <span class="col-title">{{ col.label }}</span>
          <span class="col-count">{{ candidatesForCol(col.statut).length }}</span>
        </div>

        <!-- Cards -->
        <div
          v-for="c in sortedCandidates(candidatesForCol(col.statut))"
          :key="c.id"
          class="cand-card"
          :class="{ 'card-reviewed': c.avisExpert }"
          :draggable="enableDrag"
          @dragstart="onDragStart(c)"
          @dragend="onDragEnd"
          @click="$emit('select', c)"
        >
          <div class="card-top">
            <div class="card-avatar" :style="{ background: avatarColor(c.candidatNomComplet) }">
              {{ initiales(c.candidatNomComplet) }}
            </div>
            <div class="card-info">
              <p class="card-name">{{ c.candidatNomComplet }}</p>
              <p class="card-time">{{ formatDate(c.creeLe) }}</p>
            </div>
            <div class="card-right">
              <div v-if="c.avisExpert" class="score-badge" :class="scoreBadgeClass(c.avisExpert.score)">
                {{ Math.round(c.avisExpert.score * 20) }}%
              </div>
              <!-- Badge statut -->
              <span v-if="col.statut === 'Acceptée'" class="badge badge-green">Accepted</span>
              <span v-else-if="col.statut === 'Refusée'" class="badge badge-red">Declined</span>
              <span v-else-if="c.avisExpert" class="badge badge-green">✓ Rated</span>
              <span v-else class="badge badge-pending">Pending</span>
            </div>
          </div>

          <!-- Tags -->
          <div class="card-tags">
            <span class="card-tag">{{ truncate(c.offreTitre, 22) }}</span>
            <!-- Score team si plusieurs avis -->
            <span v-if="c.tousLesAvis?.length > 1" class="card-tag tag-team">
              {{ c.tousLesAvis.length }} reviews · {{ avgAvis(c).toFixed(1) }}/5
            </span>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="candidatesForCol(col.statut).length === 0" class="col-empty">
          {{ col.emptyText }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  candidatures: {
    type: Array,
    default: () => []
  },
  filtreOffreId: {
    type: String,
    default: null
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  title: {
    type: String,
    default: 'Candidate Pipeline'
  },
  // 'expert' = 3 colonnes, 'full' = 5 colonnes (tenant)
  mode: {
    type: String,
    default: 'expert'
  },
  enableDrag: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'status-change'])

const sortByScore = ref(false)
const dragCandidate = ref(null)
const dragOverStatus = ref(null)

// ── Définition des colonnes selon le mode ──
const COLUMNS_EXPERT = [
  { statut: 'Nouvelle',       label: 'Applied',      color: '#3b82f6', emptyText: 'No new applications' },
  { statut: 'En cours',       label: 'In Review',    color: '#a855f7', emptyText: 'No applications in review' },
  { statut: 'Présélectionné', label: 'Shortlisted',  color: '#f59e0b', emptyText: 'No shortlisted candidates' },
  { statut: 'Entretien',      label: 'Interview',    color: '#06b6d4', emptyText: 'No interviews scheduled' },
  { statut: 'Acceptée',       label: 'Accepted',     color: '#22c55e', emptyText: 'No accepted candidates' },
  { statut: 'Refusée',        label: 'Declined',     color: '#ef4444', emptyText: 'No declined candidates' }
]

const COLUMNS_FULL = COLUMNS_EXPERT

const columns = computed(() => props.mode === 'full' ? COLUMNS_FULL : COLUMNS_EXPERT)

// ── Candidatures filtrées ──
const candidaturesFiltrees = computed(() => {
  if (!props.filtreOffreId) return props.candidatures
  return props.candidatures.filter(c => c.offreId === props.filtreOffreId)
})

const totalVisible = computed(() => candidaturesFiltrees.value.length)

function candidatesForCol(statut) {
  return candidaturesFiltrees.value.filter(c => c.statut === statut)
}

function sortedCandidates(list) {
  if (!sortByScore.value) return list
  return [...list].sort((a, b) => (b.avisExpert?.score ?? -1) - (a.avisExpert?.score ?? -1))
}

function toggleSort() { sortByScore.value = !sortByScore.value }

function avgAvis(c) {
  if (!c.tousLesAvis?.length) return 0
  return c.tousLesAvis.reduce((a, v) => a + v.score, 0) / c.tousLesAvis.length
}

// ── Helpers ──
function initiales(nom) {
  if (!nom) return '?'
  return nom.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2)
}
function truncate(str, n) {
  return str && str.length > n ? str.slice(0, n) + '…' : str || '—'
}
function formatDate(d) {
  if (!d) return ''
  const h = Math.floor((Date.now() - new Date(d).getTime()) / 3600000)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}
function avatarColor(name) {
  if (!name) return '#1A2B4C'
  const c = ['#1A2B4C', '#0d4f8c', '#1a3c2e', '#3b1f4e', '#7c3238', '#1e4a6e', '#2d4a1e']
  let h = 0
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h)
  return c[Math.abs(h) % c.length]
}
function scoreBadgeClass(score) {
  if (score == null) return 'score-none'
  if (score >= 4) return 'score-high'
  if (score >= 2.5) return 'score-mid'
  return 'score-low'
}

function onDragStart(candidate) {
  if (!props.enableDrag) return
  dragCandidate.value = candidate
}

function onDragEnd() {
  dragCandidate.value = null
  dragOverStatus.value = null
}

function onDragOver(statut) {
  if (!props.enableDrag) return
  dragOverStatus.value = statut
}

function onDragLeave(statut) {
  if (dragOverStatus.value === statut) dragOverStatus.value = null
}

function onDrop(targetStatut) {
  if (!props.enableDrag || !dragCandidate.value) return
  const candidate = dragCandidate.value
  dragOverStatus.value = null
  dragCandidate.value = null

  if (!candidate?.id || candidate.statut === targetStatut) return
  emit('status-change', {
    candidateId: candidate.id,
    fromStatus: candidate.statut,
    toStatus: targetStatut,
    candidate
  })
}
</script>

<style scoped>
.pipeline-board { width: 100%; }

/* Header */
.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.board-title   { font-size: 1rem; font-weight: 800; color: #0f172a; }
.board-actions { display: flex; align-items: center; gap: 8px; }
.board-total   { font-size: 0.75rem; color: #94a3b8; font-weight: 600; }
.btn-sort {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 6px 12px; background: #fff; border: 1px solid #e2e8f0;
  border-radius: 8px; font-size: 0.76rem; font-weight: 600;
  cursor: pointer; color: #475569; font-family: inherit;
}
.btn-sort:hover { background: #f1f5f9; }

/* Grid colonnes */
.pipeline-grid {
  display: grid;
  gap: 12px;
  align-items: start;
}

/* Colonne */
.pipeline-col { background: #f1f5f9; border-radius: 13px; padding: 14px; min-height: 200px; }
.pipeline-col.drop-active { outline: 2px dashed #1A2B4C; outline-offset: -6px; }

.col-header {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.63rem; font-weight: 800; letter-spacing: 0.1em;
  color: #475569; margin-bottom: 10px; text-transform: uppercase;
}
.col-dot   { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.col-title { flex: 1; }
.col-count {
  background: #e2e8f0; color: #475569;
  font-size: 0.63rem; padding: 2px 6px;
  border-radius: 99px; font-weight: 700;
}

/* Card */
.cand-card {
  background: #fff; border: 1px solid #e2e8f0;
  border-radius: 10px; padding: 11px 12px; margin-bottom: 7px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  transition: box-shadow 0.15s, transform 0.12s;
  cursor: pointer;
}
.cand-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); transform: translateY(-1px); }
.cand-card.card-reviewed { border-left: 3px solid #22c55e; }

.card-top  { display: flex; align-items: center; gap: 9px; }
.card-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  color: #fff; display: flex; align-items: center;
  justify-content: center; font-weight: 800; font-size: 0.68rem; flex-shrink: 0;
}
.card-info  { flex: 1; min-width: 0; }
.card-name  { font-size: 0.8rem; font-weight: 700; color: #0f172a; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-time  { font-size: 0.66rem; color: #94a3b8; margin: 0; }
.card-right { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; flex-shrink: 0; }

.score-badge { font-size: 0.63rem; font-weight: 800; padding: 2px 6px; border-radius: 6px; }
.score-high { background: #dcfce7; color: #16a34a; }
.score-mid  { background: #fef9c3; color: #a16207; }
.score-low  { background: #fee2e2; color: #dc2626; }
.score-none { background: #f1f5f9; color: #94a3b8; }

.badge         { font-size: 0.6rem; font-weight: 700; padding: 2px 6px; border-radius: 99px; white-space: nowrap; }
.badge-green   { background: #f0fdf4; color: #16a34a; }
.badge-red     { background: #fef2f2; color: #dc2626; }
.badge-pending { background: #f1f5f9; color: #94a3b8; }

.card-tags  { display: flex; gap: 4px; margin-top: 7px; flex-wrap: wrap; }
.card-tag   { background: #f1f5f9; color: #475569; font-size: 0.63rem; padding: 2px 7px; border-radius: 99px; font-weight: 500; }
.tag-team   { background: #eff6ff; color: #2563eb; }

.col-empty  { text-align: center; color: #94a3b8; font-size: 0.74rem; padding: 20px 0; }

/* Responsive */
@media (max-width: 1200px) {
  .pipeline-grid { grid-template-columns: repeat(3, 1fr) !important; }
}
@media (max-width: 800px) {
  .pipeline-grid { grid-template-columns: 1fr !important; }
}
</style>