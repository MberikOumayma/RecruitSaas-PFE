<template>
  <div style="display:flex; min-height:100vh; background:#f0f2f8;">
    <AppSidebar />

    <div class="main-wrap">
      <GlobalHeader title="Candidates" />

      <!-- ─── TOP BAR ─── -->
      <div class="topbar">
        <div class="topbar-left">
          <span class="badge-count">{{ candidaturesFiltrees.length }} candidates</span>
        </div>
        <div class="topbar-right">
          <div class="search-wrap">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
              <circle cx="11" cy="11" r="8" stroke="#94a3b8" stroke-width="2"/>
              <path d="M21 21l-4.35-4.35" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <input v-model="searchQuery" placeholder="Search candidates..." class="search-input" />
          </div>
          <div class="select-wrapper">
            <select v-model="filtreOffreId" @change="chargerCandidatures" class="select-filter">
              <option :value="null">All offers</option>
              <option v-for="o in offres" :key="o.offreId" :value="o.offreId">{{ o.titre }}</option>
            </select>
          </div>
          <div class="select-wrapper">
            <select v-model="filtreStatut" @change="chargerCandidatures" class="select-filter">
              <option value="">All statuses</option>
              <option value="Nouvelle">New</option>
              <option value="En cours">In Progress</option>
              <option value="Présélectionné">Shortlisted</option>
              <option value="Entretien">Interview</option>
              <option value="Acceptée">Accepted</option>
            </select>
          </div>
          <div class="export-group">
            <button class="btn-export-csv" @click="exportCSV">CSV</button>
            <button class="btn-export-pdf" @click="exportPDF">PDF</button>
          </div>
        </div>
      </div>

      <!-- ─── BODY ─── -->
      <div class="body-wrap">

        <!-- Stats bar -->
        <div class="quick-stats">
          <div class="qs-item"><span class="qs-num">{{ candidaturesFiltrees.length }}</span><span class="qs-label">Applications</span></div>
          <div class="qs-sep"></div>
          <div class="qs-item"><span class="qs-num qs-green">{{ evaluatedCount }}</span><span class="qs-label">Evaluated</span></div>
          <div class="qs-sep"></div>
          <div class="qs-item"><span class="qs-num qs-orange">{{ pendingCount }}</span><span class="qs-label">Pending</span></div>
          <div class="qs-sep"></div>
          <div class="qs-item"><span class="qs-num qs-blue">{{ avgScore }}</span><span class="qs-label">Avg score</span></div>
        </div>

        <!-- Table header -->
        <div class="list-header">
          <span class="col-name">Candidate</span>
          <span class="col-email">Email</span>
          <span class="col-offer">Offer</span>
          <span class="col-score">Score</span>
          <span class="col-status">Status</span>
          <span class="col-action"></span>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="list-state">
          <div class="spinner"></div><p>Loading candidates...</p>
        </div>
        <div v-else-if="candidaturesFiltrees.length === 0" class="list-state">
          <p class="empty-title">No candidates found</p>
        </div>

        <!-- Scrollable list -->
        <div class="list-scroll">
          <div
            v-for="c in candidaturesFiltrees" :key="c.id"
            class="cand-row"
            :class="{ evaluated: c.avisExpert }"
            @click="selectCandidate(c)"
          >
            <div class="col-name row-candidate">
              <div class="avatar" :style="{ background: avatarColor(c.candidatNomComplet) }">{{ initiales(c.candidatNomComplet) }}</div>
              <div>
                <p class="row-name">{{ c.candidatNomComplet }}</p>
                <p class="row-sub">Applied {{ formatDate(c.creeLe) }}</p>
              </div>
            </div>
            <div class="col-email row-muted">{{ truncate(c.candidatEmail, 28) }}</div>
            <div class="col-offer row-muted">{{ truncate(c.offreTitre, 22) }}</div>
            <div class="col-score">
              <span v-if="c.avisExpert" class="score-pill" :class="scorePillClass(c.avisExpert.score)">{{ c.avisExpert.score.toFixed(1) }}</span>
              <span v-else class="score-pill score-pend">—</span>
            </div>
            <div class="col-status"><span class="statut-badge" :class="statutClass(c.statut)">{{ statutLabel(c.statut) }}</span></div>
            <div class="col-action"><button class="btn-view" @click.stop="selectCandidate(c)">View</button></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── MODAL CENTRÉ ─── -->
    <transition name="modal-fade">
      <div v-if="selectedCandidate" class="modal-overlay" @click.self="selectedCandidate = null">
        <div class="modal-box">

          <!-- Close -->
          <button class="modal-close" @click="selectedCandidate = null">✕</button>

          <!-- Header -->
          <div class="modal-header">
            <div class="modal-avatar-wrap">
              <div class="avatar avatar-xl" :style="{ background: avatarColor(selectedCandidate.candidatNomComplet) }">
                {{ initiales(selectedCandidate.candidatNomComplet) }}
              </div>
              <span v-if="selectedCandidate.avisExpert" class="evaluated-badge">✓ Evaluated</span>
            </div>
            <div class="modal-identity">
              <h2 class="modal-name">{{ selectedCandidate.candidatNomComplet }}</h2>
              <p class="modal-offer">{{ selectedCandidate.offreTitre }}</p>
              <div class="modal-chips">
                <a :href="'mailto:' + selectedCandidate.candidatEmail" class="chip">{{ selectedCandidate.candidatEmail }}</a>
                <span v-if="selectedCandidate.candidatTelephone" class="chip">{{ selectedCandidate.candidatTelephone }}</span>
                <span class="statut-badge" :class="statutClass(selectedCandidate.statut)">{{ statutLabel(selectedCandidate.statut) }}</span>
              </div>
            </div>

          </div>

          <!-- Pipeline -->
          <div class="pipeline-wrap">
            <div class="pipeline">
              <div
                v-for="(s, i) in PIPELINE_STEPS" :key="s.key"
                class="p-step"
                :class="{
                  'p-done':    isPipelineDone(selectedCandidate.statut, s.key),
                  'p-active':  selectedCandidate.statut === s.key,
                  'p-danger':  s.key === 'Refusée' && selectedCandidate.statut === 'Refusée',
                  'p-success': s.key === 'Acceptée' && selectedCandidate.statut === 'Acceptée'
                }"
              >
                <div class="p-line" v-if="i > 0" :class="{ 'p-line-done': isPipelineDone(selectedCandidate.statut, s.key) || selectedCandidate.statut === s.key }"></div>
                <div class="p-dot">
                  <svg v-if="isPipelineDone(selectedCandidate.statut, s.key)" width="10" height="10" viewBox="0 0 24 24" fill="none">
                    <path d="M20 6L9 17l-5-5" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <div v-else-if="selectedCandidate.statut === s.key" class="p-inner"></div>
                </div>
                <span class="p-label">{{ s.label }}</span>
              </div>
            </div>
          </div>

          <!-- Modal body scrollable -->
          <div class="modal-body-scroll">

            <!-- 2 colonnes -->
            <div class="modal-cols">

              <!-- Colonne gauche: AI + Eval -->
              <div class="modal-col">

                <!-- AI Analysis -->
                <div class="section">
                  <p class="section-title">AI Analysis</p>
                  <div class="ai-box">
                    <div class="ai-header">
                      <span class="ai-tag">AI</span>
                      <div class="ai-bar-wrap">
                        <div class="ai-bar-fill" :class="scorePillClass(selectedCandidate.avisExpert?.score ?? 0)" :style="{ width: Math.round((selectedCandidate.avisExpert?.score ?? 0) * 20) + '%' }"></div>
                      </div>
                      <span class="ai-score">{{ selectedCandidate.avisExpert ? selectedCandidate.avisExpert.score.toFixed(1) : '—' }}<span class="ai-score-of">/5</span></span>
                      <span v-if="selectedCandidate.avisExpert" class="ai-match" :class="scorePillClass(selectedCandidate.avisExpert.score)">{{ Math.round(selectedCandidate.avisExpert.score * 20) }}%</span>
                    </div>
                    <p class="ai-summary">{{ selectedCandidate.resumeIA || 'No AI summary available yet.' }}</p>
                  </div>
                </div>

                <!-- My Evaluation -->
                <div class="section">
                  <p class="section-title">{{ selectedCandidate.avisExpert ? 'Update my evaluation' : 'Evaluate this candidate' }}</p>
                  <div class="eval-block">
                    <div class="eval-score-row">
                      <span class="eval-label">Score</span>
                      <span class="eval-score-display" :class="scoreColorClass(avisForm.score)">
                        {{ formatScore(avisForm.score) }}<span class="eval-score-of">/5</span>
                      </span>
                      <span class="eval-pct" :class="scorePillClass(avisForm.score)">{{ Math.round(avisForm.score * 20) }}% match</span>
                    </div>
                    <input
                      type="range" min="0" max="5" step="0.1"
                      v-model.number="avisForm.score"
                      class="score-slider"
                      :style="{ '--pct': (avisForm.score / 5 * 100) + '%' }"
                    />
                    <div class="slider-labels">
                      <span v-for="n in [0,1,2,3,4,5]" :key="n">{{ n }}</span>
                    </div>
                    <label class="comment-label">Expert assessment</label>
                    <textarea
                      v-model="avisForm.commentaire"
                      class="comment-area"
                      rows="3"
                      placeholder="Describe strengths, weaknesses..."
                    ></textarea>
                    <div class="eval-footer">
                      <button class="btn-submit" :disabled="submitting" @click="soumettreAvis">
                        <div v-if="submitting" class="spinner-btn"></div>
                        <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none">
                          <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        {{ submitting ? 'Saving...' : (selectedCandidate.avisExpert ? 'Update evaluation' : 'Submit evaluation') }}
                      </button>
                      <transition name="fade">
                        <span v-if="successMsg" class="saved-pill">✓ Saved!</span>
                      </transition>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Colonne droite: Team reviews + CV -->
              <div class="modal-col">

                <!-- Team Reviews -->
                <div class="section" v-if="selectedCandidate.tousLesAvis?.length">
                  <p class="section-title">Team reviews <span class="reviews-count">{{ selectedCandidate.tousLesAvis.length }}</span></p>
                  <div class="avg-bar">
                    <span class="avg-label">Team avg</span>
                    <div class="avg-track"><div class="avg-fill" :class="scorePillClass(avgTousLesAvis(selectedCandidate))" :style="{ width: Math.round(avgTousLesAvis(selectedCandidate)*20)+'%' }"></div></div>
                    <span class="avg-val" :class="scoreColorClass(avgTousLesAvis(selectedCandidate))">{{ avgTousLesAvis(selectedCandidate).toFixed(1) }}/5</span>
                  </div>
                  <div v-for="(av, i) in selectedCandidate.tousLesAvis" :key="av.id ?? i" class="review-item">
                    <div class="avatar avatar-sm" :style="{ background: avatarColor(av.expertNom) }">{{ (av.expertNom || 'E').charAt(0).toUpperCase() }}</div>
                    <div class="review-body">
                      <div class="review-top">
                        <span class="review-name">{{ av.expertNom || 'Expert' }}</span>
                        <span class="score-pill score-pill-xs" :class="scorePillClass(av.score)">{{ av.score.toFixed(1) }}/5</span>
                      </div>
                      <p v-if="av.commentaire" class="review-comment">"{{ av.commentaire }}"</p>
                    </div>
                  </div>
                </div>

                <!-- No team reviews placeholder -->
                <div class="section" v-else>
                  <p class="section-title">Team reviews</p>
                  <div class="no-reviews">No team reviews yet</div>
                </div>

                <!-- CV -->
                <div class="section" v-if="getCvUrl(selectedCandidate)">
                  <p class="section-title">Resume / CV</p>
                  <div class="cv-row">
                    <button class="btn-cv" @click="openCv(selectedCandidate)">View CV</button>
                  </div>
                </div>

                <!-- AI interview report (same EntretiensIA data as tenant / recruiter) -->
                <div class="section">
                  <p class="section-title">AI interview report</p>
                  <div v-if="entretienRapportDisponible(selectedCandidate)" class="entretien-box">
                    <div class="entretien-teaser">
                      <span class="entretien-score-chip">{{ entretienScoreAffiche(selectedCandidate) }}</span>
                      <span class="entretien-teaser-hint">/100</span>
                    </div>
                    <button type="button" class="btn-rapport" @click="openRapportEntretien">View full report</button>
                  </div>
                  <div v-else class="no-reviews">No completed AI interview report yet.</div>
                </div>

                <p class="card-date">Applied {{ formatDateFull(selectedCandidate.creeLe) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <RapportEntretien
      v-if="showRapportEntretien && rapportEntretienData"
      :rapport="rapportEntretienData"
      :questions="rapportEntretienQuestions"
      @close="showRapportEntretien = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, reactive } from 'vue'
import api from '@/services/api'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import GlobalHeader from '@/components/layout/GlobalHeader.vue'
import RapportEntretien from '@/components/RapportEntretien.vue'
import {
  applicationStatusLabel,
  formatRecruiterDate,
  interviewMentionLabel,
  isRejectedApplicationStatus,
} from '@/utils/recruiterI18n'

const PIPELINE_STEPS = [
  { key: 'Nouvelle',      label: 'Applied'     },
  { key: 'En cours',      label: 'In Review'   },
  { key: 'Présélectionné',label: 'Shortlisted' },
  { key: 'Entretien',     label: 'Interview'   },
  { key: 'Acceptée',      label: 'Accepted'    },
  { key: 'Refusée',       label: 'Declined'    },
]
const PIPELINE_ORDER = ['Nouvelle','En cours','Présélectionné','Entretien','Acceptée','Refusée']

function getExpertId() {
  const t = localStorage.getItem('token')
  if (!t) return null
  try { return JSON.parse(atob(t.split('.')[1])).expertId ?? null } catch { return null }
}

const expertId          = getExpertId()
const offres            = ref([])
const candidatures      = ref([])
const loading           = ref(false)
const filtreOffreId     = ref(null)
const filtreStatut      = ref('')
const searchQuery       = ref('')
const selectedCandidate = ref(null)
const submitting        = ref(false)
const successMsg        = ref(false)
const avisForm          = reactive({ score: 0, commentaire: '' })

const showRapportEntretien     = ref(false)
const rapportEntretienData     = ref(null)
const rapportEntretienQuestions = ref([])

// ── Computed ──────────────────────────────────────────────────────────────────
const candidaturesFiltrees = computed(() => {
  if (!Array.isArray(candidatures.value)) return []
  let list = candidatures.value.filter(c => !isRejectedApplicationStatus(c.statut))
  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    list = list.filter(c =>
      c.candidatNomComplet?.toLowerCase().includes(q) ||
      c.candidatEmail?.toLowerCase().includes(q) ||
      c.offreTitre?.toLowerCase().includes(q)
    )
  }
  return list
})
const evaluatedCount = computed(() => candidaturesFiltrees.value.filter(c => c.avisExpert).length)
const pendingCount   = computed(() => candidaturesFiltrees.value.length - evaluatedCount.value)
const avgScore       = computed(() => {
  const ev = candidaturesFiltrees.value.filter(c => c.avisExpert)
  if (!ev.length) return '—'
  return (ev.reduce((a, c) => a + c.avisExpert.score, 0) / ev.length).toFixed(1)
})

// ── Lifecycle ──────────────────────────────────────────────────────────────────
onMounted(async () => {
  if (!expertId) return
  await chargerOffres()
  await chargerCandidatures()
})

watch(selectedCandidate, (c) => {
  if (!c) {
    showRapportEntretien.value = false
    rapportEntretienData.value = null
    rapportEntretienQuestions.value = []
    return
  }
  avisForm.score       = c.avisExpert?.score       ?? 0
  avisForm.commentaire = c.avisExpert?.commentaire ?? ''
  successMsg.value     = false
})

// ── API ────────────────────────────────────────────────────────────────────────
async function chargerOffres() {
  try {
    const { data } = await api.get(`/expert/${expertId}/offres`)
    offres.value = Array.isArray(data) ? data : []
  } catch { offres.value = [] }
}

async function chargerCandidatures() {
  loading.value = true
  try {
    const params = {}
    if (filtreOffreId.value) params.offreId = filtreOffreId.value
    if (filtreStatut.value)  params.statut  = filtreStatut.value
    const { data } = await api.get(`/expert/${expertId}/candidatures`, { params })
    candidatures.value = Array.isArray(data) ? data : []
    if (selectedCandidate.value && isRejectedApplicationStatus(selectedCandidate.value.statut)) {
      selectedCandidate.value = null
    } else if (selectedCandidate.value) {
      const fresh = candidatures.value.find(c => c.id === selectedCandidate.value.id)
      if (fresh) selectedCandidate.value = fresh
    }
  } catch { candidatures.value = [] }
  finally { loading.value = false }
}

async function soumettreAvis() {
  if (!selectedCandidate.value) return
  submitting.value = true
  successMsg.value = false
  try {
    await api.post(`/expert/${expertId}/avis`, {
      candidatureId: selectedCandidate.value.id,
      score:         avisForm.score,
      commentaire:   avisForm.commentaire,
    })
    successMsg.value = true
    await chargerCandidatures()
    setTimeout(() => { successMsg.value = false }, 3000)
  } catch {}
  finally { submitting.value = false }
}

// ── Actions ───────────────────────────────────────────────────────────────────
function selectCandidate(c) { selectedCandidate.value = c }
function openCv(c)          { const u = getCvUrl(c); if (u) window.open(u, '_blank', 'noopener,noreferrer') }
function getCvUrl(c)        { return c?.cvUrl || c?.cvURL || c?.CvUrl || '' }

/** Champs API expert (camelCase) ou PascalCase */
function rawEntretienRapportJson(c) {
  return c?.entretienRapportIA ?? c?.EntretienRapportIA ?? null
}
function rawEntretienQuestionsJson(c) {
  return c?.entretienQuestionsIA ?? c?.EntretienQuestionsIA ?? null
}

function entretienRapportDisponible(c) {
  const raw = rawEntretienRapportJson(c)
  return typeof raw === 'string' ? raw.trim().length > 0 : raw != null
}

function scoreMentionInterview(score) {
  if (score == null || score === '') return ''
  const s = Number(score)
  if (Number.isNaN(s)) return ''
  if (s >= 85) return 'Excellent'
  if (s >= 70) return 'Good'
  if (s >= 50) return 'Satisfactory'
  return 'Insufficient'
}

function entretienScoreAffiche(c) {
  if (!c) return '—'
  const sc = c.entretienScore ?? c.EntretienScore
  if (sc != null && sc !== '') {
    const n = Number(sc)
    return Number.isNaN(n) ? '—' : String(Math.round(n))
  }
  const raw = rawEntretienRapportJson(c)
  if (!raw) return '—'
  try {
    const rapport = typeof raw === 'string' ? JSON.parse(raw) : raw
    return String(Math.round(rapport?.scoreGlobal ?? 0))
  } catch {
    return '—'
  }
}

/** Même structure que CandidateDetails.vue / InterviewsCalendar (openDetail + rapport). */
function buildRapportEntretienPayload(c) {
  const rawRapport = rawEntretienRapportJson(c)
  if (!rawRapport) return null
  let rapport = null
  try {
    rapport = typeof rawRapport === 'string' ? JSON.parse(rawRapport) : rawRapport
  } catch {
    rapport = null
  }
  const scoreInterview = c.entretienScore ?? c.EntretienScore
  const duree = c.entretienDureeMinutes ?? c.EntretienDureeMinutes
  const verifOk = c.entretienVerificationFacialeOk ?? c.EntretienVerificationFacialeOk ?? false
  const tabChanges = c.entretienNbChangementsOnglet ?? c.EntretienNbChangementsOnglet ?? 0

  let questions = []
  const rawQ = rawEntretienQuestionsJson(c)
  if (rawQ) {
    try {
      questions = typeof rawQ === 'string' ? JSON.parse(rawQ) : rawQ
      if (!Array.isArray(questions)) questions = []
    } catch {
      questions = []
    }
  }

  const rapportData = {
    nomCandidat: c.candidatNomComplet || '',
    titreOffre: c.offreTitre || '',
    scoreGlobal: rapport?.scoreGlobal ?? (scoreInterview != null && scoreInterview !== '' ? Number(scoreInterview) : 0),
    mention: rapport?.mention ?? interviewMentionLabel(scoreMentionInterview(scoreInterview ?? rapport?.scoreGlobal)),
    recommandation: rapport?.recommandation ?? '',
    resume_executif: rapport?.resume_executif ?? '',
    points_forts: rapport?.points_forts ?? [],
    points_amelioration: rapport?.points_amelioration ?? [],
    competences_evaluees: rapport?.competences_evaluees ?? [],
    commentaire_recruteur: rapport?.commentaire_recruteur ?? '',
    dureeMinutes: rapport?.dureeMinutes ?? duree,
    nbQuestionsRepondues: rapport?.nbQuestionsRepondues ?? 0,
    verificationFacialeOk: verifOk,
    nbChangementsOnglet: tabChanges,
    fraudDetection: rapport?.fraudDetection ?? null,
  }

  return { rapport: rapportData, questions }
}

function openRapportEntretien() {
  const c = selectedCandidate.value
  const built = buildRapportEntretienPayload(c)
  if (!built) return
  rapportEntretienData.value = built.rapport
  rapportEntretienQuestions.value = built.questions
  showRapportEntretien.value = true
}

// ── Export ────────────────────────────────────────────────────────────────────
function exportCSV() {
  const data = candidaturesFiltrees.value
  if (!data.length) return
  const headers = ['Candidate','Email','Offer','Status','Score','Comment']
  const rows = data.map(c => [
    c.candidatNomComplet ?? '', c.candidatEmail ?? '', c.offreTitre ?? '',
    applicationStatusLabel(c.statut), c.avisExpert?.score?.toFixed(1) ?? '',
    (c.avisExpert?.commentaire ?? '').replace(/"/g, '""'),
  ])
  const csv = [headers, ...rows].map(r => r.map(v => `"${v}"`).join(',')).join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href = url; a.download = `candidates-${new Date().toISOString().slice(0,10)}.csv`; a.click()
  URL.revokeObjectURL(url)
}

function exportPDF() {
  const data = candidaturesFiltrees.value
  if (!data.length) return
  const now  = new Date().toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' })
  const rows = data.map(c =>
    `<tr><td>${c.candidatNomComplet??''}</td><td>${c.offreTitre??''}</td><td>${applicationStatusLabel(c.statut)}</td><td>${c.avisExpert?c.avisExpert.score.toFixed(1)+'/5':'—'}</td></tr>`
  ).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:Arial;padding:36px}table{width:100%;border-collapse:collapse}thead{background:#1A2B4C;color:#fff}th,td{padding:8px 12px;text-align:left;border-bottom:1px solid #f1f5f9}</style></head><body><h1 style="color:#1A2B4C">Candidates Report</h1><p>${now}</p><table><thead><tr><th>Candidate</th><th>Offer</th><th>Status</th><th>Score</th></tr></thead><tbody>${rows}</tbody></table></body></html>`
  const w = window.open('','_blank','width=1000,height=700')
  if (!w) return
  w.document.write(html); w.document.close(); w.focus()
  setTimeout(() => w.print(), 600)
}

// ── Helpers ────────────────────────────────────────────────────────────────────
function isPipelineDone(cur, key) {
  if (key === 'Refusée' || key === 'Acceptée') return false
  const ci = PIPELINE_ORDER.indexOf(cur), si = PIPELINE_ORDER.indexOf(key)
  return si < ci && ci !== -1
}
function avgTousLesAvis(c) {
  if (!c.tousLesAvis?.length) return 0
  return c.tousLesAvis.reduce((a, v) => a + v.score, 0) / c.tousLesAvis.length
}
function initiales(nom)      { if (!nom) return '?'; return nom.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2) }
function truncate(str, n)    { return str && str.length > n ? str.slice(0, n) + '…' : str || '—' }
function formatScore(val)    { return (typeof val === 'number' ? val : 0).toFixed(1) }
function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr), diff = Date.now() - d.getTime(), h = Math.floor(diff / 3600000)
  if (h < 24) return `${h}h ago`
  const days = Math.floor(h / 24)
  if (days < 7) return `${days}d ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
function formatDateFull(dateStr) {
  if (!dateStr) return '—'
  return formatRecruiterDate(dateStr, { year: 'numeric', month: 'long', day: 'numeric' })
}
function avatarColor(name) {
  if (!name) return '#1A2B4C'
  const c = ['#1A2B4C','#0d4f8c','#1a3c2e','#3b1f4e','#7c3238','#1e4a6e','#2d4a1e']
  let h = 0; for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h)
  return c[Math.abs(h) % c.length]
}
function statutLabel(s) { return applicationStatusLabel(s) }
function statutClass(s) {
  return { 'st-new': s==='Nouvelle','st-inprogress': s==='En cours','st-shortlisted': s==='Présélectionné','st-interview': s==='Entretien','st-accepted': s==='Acceptée','st-declined': s==='Refusée' }
}
function scorePillClass(score) {
  if (score == null) return 'score-none'
  if (score >= 4)    return 'score-high'
  if (score >= 2.5)  return 'score-mid'
  return 'score-low'
}
function scoreColorClass(val) { return val >= 4 ? 'score-high' : val >= 2.5 ? 'score-mid' : 'score-low' }
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
* { box-sizing: border-box; }

/* ─── Layout ─── */
.main-wrap {
  flex: 1; min-width: 0; display: flex; flex-direction: column;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  color: #1e293b; height: 100vh; overflow: hidden; background: #f0f2f8;
}

/* ─── Topbar ─── */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 28px; background: #fff; border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0; gap: 12px; flex-wrap: wrap;
}
.topbar-left { display: flex; align-items: center; gap: 10px; }
.topbar-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.badge-count {
  background: #f1f5f9; color: #64748b; font-size: 0.72rem;
  font-weight: 700; padding: 3px 10px; border-radius: 99px;
}
.search-wrap { position: relative; display: flex; align-items: center; }
.search-wrap svg { position: absolute; left: 10px; pointer-events: none; }
.search-input {
  padding: 8px 12px 8px 32px; border: 1px solid #e2e8f0;
  border-radius: 9px; font-size: 0.82rem; font-family: inherit;
  outline: none; background: #f8fafc; width: 200px; color: #0f172a;
}
.search-input:focus { border-color: #1A2B4C; background: #fff; }
.search-input::placeholder { color: #94a3b8; }
.select-wrapper { display: inline-flex; }
.select-filter {
  appearance: none; background: #f8fafc; border: 1px solid #e2e8f0;
  color: #334155; padding: 8px 14px; border-radius: 9px;
  font-size: 0.81rem; font-weight: 500; cursor: pointer; font-family: inherit; outline: none;
}
.export-group { display: flex; gap: 4px; }
.btn-export-csv {
  background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0;
  border-radius: 8px; padding: 7px 13px; font-size: 0.79rem;
  font-weight: 700; cursor: pointer; font-family: inherit;
}
.btn-export-pdf {
  background: #1A2B4C; color: #fff; border: none;
  border-radius: 8px; padding: 7px 13px; font-size: 0.79rem;
  font-weight: 700; cursor: pointer; font-family: inherit;
}

/* ─── Body (list area) ─── */
.body-wrap {
  flex: 1; display: flex; flex-direction: column;
  overflow: hidden; min-height: 0; background: #fff;
}

/* Stats */
.quick-stats {
  display: flex; align-items: center; padding: 12px 28px;
  background: #fafafa; border-bottom: 1px solid #f1f5f9; flex-shrink: 0;
}
.qs-item { display: flex; flex-direction: column; align-items: center; gap: 1px; padding: 0 20px; }
.qs-num { font-size: 1.3rem; font-weight: 800; color: #0f172a; line-height: 1; }
.qs-label { font-size: 0.62rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; }
.qs-green { color: #16a34a; } .qs-orange { color: #f97316; } .qs-blue { color: #2563eb; }
.qs-sep { width: 1px; height: 28px; background: #e2e8f0; flex-shrink: 0; }

/* List header */
.list-header {
  display: flex; align-items: center; padding: 9px 28px;
  background: #f8fafc; border-bottom: 1px solid #e2e8f0;
  font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: #94a3b8; flex-shrink: 0;
}
.col-name   { flex: 1.4; min-width: 0; }
.col-email  { flex: 1.1; min-width: 0; }
.col-offer  { flex: 0.9; min-width: 0; }
.col-score  { width: 80px; flex-shrink: 0; text-align: center; }
.col-status { width: 120px; flex-shrink: 0; }
.col-action { width: 70px; flex-shrink: 0; }

.list-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 60px 20px; gap: 10px; color: #94a3b8;
}
.empty-title { font-size: 0.95rem; font-weight: 700; color: #475569; margin: 0; }

/* Scrollable list */
.list-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Rows */
.cand-row {
  display: flex; align-items: center; padding: 13px 28px;
  border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.12s;
  position: relative;
}
.cand-row:hover { background: #fafafa; }
.cand-row.evaluated { border-left: 3px solid #22c55e; padding-left: 25px; }
.row-candidate { display: flex; align-items: center; gap: 12px; }
.row-name { font-size: 0.87rem; font-weight: 700; color: #0f172a; margin: 0 0 1px; }
.row-sub  { font-size: 0.7rem; color: #94a3b8; margin: 0; }
.row-muted { font-size: 0.76rem; color: #64748b; font-weight: 500; }
.btn-view {
  font-size: 0.72rem; font-weight: 600; color: #1A2B4C;
  background: #eff6ff; border: 1px solid #bfdbfe;
  border-radius: 7px; padding: 4px 10px; cursor: pointer; font-family: inherit;
}
.btn-view:hover { background: #dbeafe; }

/* Avatars */
.avatar    { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.75rem; color: #fff; flex-shrink: 0; }
.avatar-sm { width: 30px; height: 30px; font-size: 0.65rem; }
.avatar-xl { width: 64px; height: 64px; font-size: 1.2rem; }

/* Score pills */
.score-pill { display: inline-flex; align-items: center; font-size: 0.72rem; font-weight: 700; padding: 3px 9px; border-radius: 99px; }
.score-pill-xs { font-size: 0.62rem; padding: 2px 6px; }
.score-high { background: #dcfce7; color: #15803d; }
.score-mid  { background: #fef9c3; color: #a16207; }
.score-low  { background: #fee2e2; color: #dc2626; }
.score-none, .score-pend { background: #f1f5f9; color: #94a3b8; border: 1px solid #e2e8f0; }

/* Status badges */
.statut-badge { display: inline-block; font-size: 0.62rem; font-weight: 700; padding: 3px 8px; border-radius: 99px; text-transform: uppercase; letter-spacing: 0.05em; }
.st-new        { background: #eff6ff; color: #2563eb; }
.st-inprogress { background: #fff7ed; color: #f97316; }
.st-shortlisted{ background: #f0fdf4; color: #16a34a; }
.st-interview  { background: #fdf4ff; color: #a855f7; }
.st-accepted   { background: #f0fdf4; color: #16a34a; }
.st-declined   { background: #fef2f2; color: #ef4444; }

/* ─── MODAL CENTRÉ ─── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 20px;
}

.modal-box {
  background: #fff;
  border-radius: 20px;
  width: 100%;
  max-width: 860px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  position: relative;
  box-shadow: 0 24px 80px rgba(15,23,42,0.25);
  overflow: hidden;
}

.modal-close {
  position: absolute; top: 14px; right: 14px;
  background: #f1f5f9; border: none; width: 30px; height: 30px;
  border-radius: 8px; cursor: pointer; font-size: 14px; color: #475569;
  z-index: 10; display: flex; align-items: center; justify-content: center;
}
.modal-close:hover { background: #e2e8f0; }

/* Modal header */
.modal-header {
  display: flex; align-items: flex-start; gap: 16px;
  padding: 24px 28px 16px;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}
.modal-avatar-wrap { position: relative; flex-shrink: 0; }
.evaluated-badge {
  position: absolute; bottom: -4px; left: 50%; transform: translateX(-50%);
  white-space: nowrap;
  background: #f0fdf4; color: #16a34a; font-size: 0.58rem;
  font-weight: 700; padding: 2px 7px; border-radius: 99px; border: 1px solid #bbf7d0;
}
.modal-identity { flex: 1; min-width: 0; }
.modal-name  { font-size: 1.2rem; font-weight: 800; color: #0f172a; margin: 0 0 4px; }
.modal-offer { font-size: 0.82rem; color: #64748b; margin: 0 0 10px; }
.modal-chips { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.chip {
  display: inline-flex; align-items: center;
  font-size: 0.72rem; color: #475569; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 6px; padding: 3px 8px; text-decoration: none;
}
.btn-sm {
  font-size: 0.76rem; font-weight: 600; padding: 7px 14px;
  border-radius: 8px; cursor: pointer; font-family: inherit;
  border: 1px solid #e2e8f0; background: #f8fafc; color: #475569;
}
.btn-primary { background: #1A2B4C; color: #fff; border-color: #1A2B4C; }

/* Pipeline */
.pipeline-wrap {
  padding: 16px 28px;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
  background: #fafafa;
}
.pipeline { display: flex; align-items: center; }
.p-step { display: flex; flex-direction: column; align-items: center; gap: 5px; flex: 1; position: relative; }
.p-line {
  position: absolute; top: 10px; right: 50%; width: 100%; height: 2px;
  background: #e2e8f0; z-index: 0; transition: background 0.3s;
}
.p-line-done { background: #1A2B4C; }
.p-dot {
  width: 20px; height: 20px; border-radius: 50%;
  background: #f1f5f9; border: 1.5px solid #e2e8f0;
  z-index: 1; display: flex; align-items: center; justify-content: center;
  position: relative; transition: all 0.2s;
}
.p-done .p-dot    { background: #1A2B4C; border-color: #1A2B4C; }
.p-active .p-dot  { background: #1A2B4C; border-color: #1A2B4C; box-shadow: 0 0 0 4px rgba(26,43,76,0.12); }
.p-danger .p-dot  { background: #ef4444; border-color: #ef4444; }
.p-success .p-dot { background: #22c55e; border-color: #22c55e; }
.p-inner { width: 8px; height: 8px; border-radius: 50%; background: #fff; }
.p-label { font-size: 0.58rem; font-weight: 600; color: #94a3b8; text-align: center; }
.p-done .p-label, .p-active .p-label { color: #1A2B4C; font-weight: 700; }
.p-danger .p-label  { color: #ef4444; font-weight: 700; }
.p-success .p-label { color: #22c55e; font-weight: 700; }

/* Modal scrollable body */
.modal-body-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 20px 28px 24px;
}

/* 2-col layout inside modal */
.modal-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 640px) {
  .modal-cols { grid-template-columns: 1fr; }
  .modal-header { flex-wrap: wrap; }
}

.modal-col { display: flex; flex-direction: column; gap: 16px; }

/* Section */
.section {}
.section-title {
  font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: #64748b; margin: 0 0 8px;
}

/* AI box */
.ai-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; }
.ai-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.ai-tag { font-size: 0.65rem; font-weight: 700; background: #1A2B4C; color: #fff; padding: 3px 8px; border-radius: 99px; }
.ai-bar-wrap { flex: 1; height: 5px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }
.ai-bar-fill { height: 100%; border-radius: 99px; }
.ai-bar-fill.score-high { background: #22c55e; }
.ai-bar-fill.score-mid  { background: #f59e0b; }
.ai-bar-fill.score-low  { background: #ef4444; }
.ai-score { font-size: 1.1rem; font-weight: 800; color: #0f172a; line-height: 1; }
.ai-score-of { font-size: 0.65rem; color: #94a3b8; font-weight: 500; margin-left: 1px; }
.ai-match { font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 99px; }
.ai-match.score-high { background: #dcfce7; color: #15803d; }
.ai-match.score-mid  { background: #fef9c3; color: #a16207; }
.ai-match.score-low  { background: #fee2e2; color: #dc2626; }
.ai-summary {
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 400;
  font-style: normal;
  color: #334155;
  line-height: 1.65;
  border-left: 2px solid #e2e8f0;
  padding-left: 10px;
  margin: 0;
}

/* Eval */
.eval-block { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; }
.eval-score-row { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; }
.eval-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; }
.eval-score-display { font-size: 1.4rem; font-weight: 800; line-height: 1; }
.eval-score-display.score-high { color: #22c55e; } .eval-score-display.score-mid { color: #f59e0b; } .eval-score-display.score-low { color: #ef4444; }
.eval-score-of { font-size: 0.74rem; font-weight: 500; color: #94a3b8; }
.eval-pct { font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 99px; margin-left: auto; }
.eval-pct.score-high { background: #dcfce7; color: #15803d; }
.eval-pct.score-mid  { background: #fef9c3; color: #a16207; }
.eval-pct.score-low  { background: #fee2e2; color: #dc2626; }
.score-slider {
  -webkit-appearance: none; appearance: none; width: 100%; height: 6px;
  border-radius: 99px; outline: none; cursor: pointer;
  background: linear-gradient(to right, #1A2B4C 0%, #1A2B4C var(--pct, 0%), #e2e8f0 var(--pct, 0%), #e2e8f0 100%);
  margin-bottom: 4px;
}
.score-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 20px; height: 20px; border-radius: 50%;
  background: #fff; border: 2.5px solid #1A2B4C; cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
.slider-labels { display: flex; justify-content: space-between; padding: 2px 1px 10px; }
.slider-labels span { font-size: 0.6rem; color: #cbd5e1; font-weight: 600; }
.comment-label { display: block; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 6px; }
.comment-area {
  width: 100%; background: #fff; border: 1px solid #e2e8f0;
  border-radius: 10px; color: #334155; padding: 10px 13px;
  font-size: 0.83rem; resize: vertical; font-family: inherit; line-height: 1.6; outline: none;
}
.comment-area:focus { border-color: #1A2B4C; }
.eval-footer { display: flex; align-items: center; gap: 12px; margin-top: 12px; }
.btn-submit {
  display: inline-flex; align-items: center; gap: 7px;
  background: #1A2B4C; color: #fff; border: none; border-radius: 10px;
  padding: 10px 20px; font-size: 0.83rem; font-weight: 700;
  cursor: pointer; font-family: inherit; transition: opacity 0.15s;
}
.btn-submit:hover:not(:disabled) { opacity: 0.88; }
.btn-submit:disabled { opacity: 0.4; cursor: not-allowed; }
.saved-pill {
  display: inline-flex; align-items: center; gap: 5px;
  background: #f0fdf4; color: #16a34a; font-size: 0.78rem;
  font-weight: 700; padding: 6px 12px; border-radius: 99px; border: 1px solid #bbf7d0;
}

/* No reviews */
.no-reviews {
  background: #f8fafc; border: 1px dashed #e2e8f0; border-radius: 10px;
  padding: 20px; text-align: center; font-size: 0.78rem; color: #94a3b8;
}

/* Team reviews */
.reviews-count {
  display: inline-flex; align-items: center; justify-content: center;
  background: #1A2B4C; color: #fff; font-size: 0.62rem;
  font-weight: 700; width: 18px; height: 18px; border-radius: 50%; margin-left: 6px;
}
.avg-bar { display: flex; align-items: center; gap: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; margin-bottom: 10px; }
.avg-label { font-size: 0.68rem; font-weight: 700; color: #94a3b8; white-space: nowrap; }
.avg-track { flex: 1; height: 6px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }
.avg-fill  { height: 100%; border-radius: 99px; transition: width 0.5s ease; }
.avg-fill.score-high { background: #22c55e; } .avg-fill.score-mid { background: #f59e0b; } .avg-fill.score-low { background: #ef4444; }
.avg-val { font-size: 0.76rem; font-weight: 800; white-space: nowrap; }
.avg-val.score-high { color: #16a34a; } .avg-val.score-mid { color: #a16207; } .avg-val.score-low { color: #dc2626; }
.review-item { display: flex; align-items: flex-start; gap: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 11px 13px; margin-bottom: 8px; }
.review-body { flex: 1; min-width: 0; }
.review-top  { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.review-name { font-size: 0.82rem; font-weight: 700; color: #0f172a; }
.review-comment { font-size: 0.78rem; color: #475569; font-style: italic; margin: 0; line-height: 1.5; }

/* CV */
.cv-row { display: flex; gap: 8px; }
.btn-cv {
  display: inline-flex; align-items: center; gap: 6px;
  background: #f8fafc; color: #475569; border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 6px 12px; font-size: 0.74rem;
  font-weight: 700; cursor: pointer; text-decoration: none; font-family: inherit;
}
.card-date { font-size: 0.68rem; color: #cbd5e1; text-align: right; font-weight: 500; margin-top: 4px; }

/* AI interview report (under CV) */
.entretien-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.entretien-teaser { display: flex; align-items: baseline; gap: 6px; }
.entretien-score-chip {
  font-size: 1.25rem;
  font-weight: 800;
  color: #1A2B4C;
  line-height: 1;
}
.entretien-teaser-hint { font-size: 0.72rem; font-weight: 600; color: #94a3b8; }
.btn-rapport {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #eef2ff;
  color: #3730a3;
  border: 1px solid #c7d2fe;
  border-radius: 8px;
  padding: 7px 14px;
  font-size: 0.74rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
}
.btn-rapport:hover { background: #e0e7ff; }

/* Rapport modal above candidate modal */
:deep(.rapport-overlay) {
  z-index: 1100;
}

/* Spinners */
.spinner { width: 22px; height: 22px; border: 2.5px solid #e2e8f0; border-top-color: #1A2B4C; border-radius: 50%; animation: spin 0.65s linear infinite; }
.spinner-btn { width: 13px; height: 13px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.65s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Modal transition */
.modal-fade-enter-active { transition: all 0.25s cubic-bezier(.4,0,.2,1); }
.modal-fade-leave-active { transition: all 0.18s cubic-bezier(.4,0,.2,1); }
.modal-fade-enter-from   { opacity: 0; transform: scale(0.96); }
.modal-fade-leave-to     { opacity: 0; transform: scale(0.96); }

/* Fade */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Responsive table */
@media (max-width: 900px) {
  .col-email, .col-offer { display: none; }
}
</style>