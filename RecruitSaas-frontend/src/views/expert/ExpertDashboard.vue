<template>
  <div style="display:flex; min-height:100vh; background:#f8fafc;">
    <AppSidebar />
    <main class="dashboard-page">

      <!-- Header global avec user + logout -->
      <GlobalHeader title="Dashboard" />

      <!-- Toast -->
      <transition name="toast-slide">
        <div v-if="toastNotif" class="toast-notif" @click="handleToastClick">
          <div class="toast-icon" :class="'icon-' + toastNotif.type">
            <svg v-if="toastNotif.type === 'new_application'" width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/></svg>
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </div>
          <div class="toast-body">
            <p class="toast-title">{{ toastNotif.title }}</p>
            <p class="toast-text">{{ toastNotif.body }}</p>
          </div>
          <button class="toast-close" @click.stop="toastNotif = null">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
          </button>
        </div>
      </transition>

      <div class="content">

        <!-- Subtitle + Stats -->
        <div class="dashboard-top">
          <p class="page-subtitle">Real-time matching and candidate pipeline overview.</p>
          <div class="stats-row">
            <div class="stat-pill">
              <div class="stat-icon-wrap" style="background:#eff6ff;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2" stroke="#2563eb" stroke-width="1.8" stroke-linecap="round"/></svg>
              </div>
              <div><p class="stat-label">Assigned Jobs</p><p class="stat-val">{{ offres.length }}</p></div>
            </div>
            <div class="stat-pill">
              <div class="stat-icon-wrap" style="background:#f0fdf4;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="#16a34a" stroke-width="1.8" stroke-linecap="round"/><circle cx="9" cy="7" r="4" stroke="#16a34a" stroke-width="1.8"/></svg>
              </div>
              <div><p class="stat-label">Total Candidates</p><p class="stat-val">{{ totalCandidatures }}</p></div>
            </div>
            <div class="stat-pill">
              <div class="stat-icon-wrap" style="background:#fefce8;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="#ca8a04" stroke-width="1.8" stroke-linejoin="round"/></svg>
              </div>
              <div><p class="stat-label">Avg AI Score</p><p class="stat-val" :class="avgScoreClass">{{ avgAIScore }}</p></div>
            </div>
            <div class="stat-pill">
              <div class="stat-icon-wrap" style="background:#fef2f2;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#f97316" stroke-width="1.8"/><path d="M12 6v6l4 2" stroke="#f97316" stroke-width="1.8" stroke-linecap="round"/></svg>
              </div>
              <div><p class="stat-label">Pending Eval.</p><p class="stat-val qs-orange">{{ pendingEvalCount }}</p></div>
            </div>
            
          </div>
        </div>

        <div v-if="loading" class="center-state">
          <div class="spinner"></div><p>Loading data…</p>
        </div>

        <template v-else>
          <!-- Active Job Offers -->
          <div class="section-header">
            <span class="section-title">Active Job Offers</span>
            <button class="btn-report" @click="exportReport">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              Export Report
            </button>
          </div>

          <div class="offers-grid">
            <div v-for="offre in offres" :key="offre.offreId" class="offer-card" :class="{ active: filtreOffreId === offre.offreId }" @click="toggleOffreFilter(offre.offreId)">
              <div class="offer-top">
                <div class="offer-logo">{{ offre.titre?.charAt(0)?.toUpperCase() }}</div>
                <div class="offer-info">
                  <h3>{{ offre.titre }}</h3>
                  <p class="offer-date">{{ offre.datePublication ? formatDateShort(offre.datePublication) : 'Active' }}</p>
                </div>
                <button class="offer-more" @click.stop="goToOffer(offre)">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </button>
              </div>
              <div class="offer-meta">
                <span class="offer-tag">AI MATCH QUALITY</span>
                <span class="offer-score">
                  {{ offreAvgScore(offre.offreId) !== '—' ? offreAvgScore(offre.offreId) + '% avg' : '' }}
                  <span class="offer-cands">{{ offre.nombreCandidatures }} candidates</span>
                </span>
              </div>
              <div class="offer-progress-wrap">
                <div class="offer-progress-bar">
                  <div class="offer-progress-fill" :style="{ width: offreEvalPct(offre.offreId) + '%' }" :class="offreEvalPct(offre.offreId) === 100 ? 'fill-complete' : 'fill-partial'"></div>
                </div>
                <span class="offer-progress-label">{{ offreEvalPct(offre.offreId) }}% evaluated</span>
              </div>
            </div>
            <div class="offer-card offer-empty" @click="goToAllCandidates">
              <div class="offer-plus">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round"/><circle cx="9" cy="7" r="4" stroke="#94a3b8" stroke-width="1.5"/></svg>
              </div>
              <p class="offer-empty-title">View All Candidates</p>
              <p class="offer-empty-sub">Browse and evaluate all assigned candidates</p>
            </div>
          </div>

          <div v-if="filtreOffreId" class="active-filter-bar">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/></svg>
            Filtered by: <strong>{{ offres.find(o=>o.offreId===filtreOffreId)?.titre }}</strong>
            <button class="clear-filter" @click="filtreOffreId = null">✕ Clear</button>
          </div>

          <CandidatePipelineBoard
            :candidatures="candidatures"
            :filtreOffreId="filtreOffreId"
            :showHeader="true"
            title="Active Candidate Pipeline"
            mode="summary"
            @select="goToCandidate"
            :enableDrag="true"
            @status-change="handlePipelineStatusChange"
          />
        </template>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'

import {
  formatRecruiterDate,
  applicationStatusLabel,
  isRejectedApplicationStatus,
} from '../../utils/recruiterI18n'
import CandidatePipelineBoard from '@/components/CandidatePipelineBoard.vue'
import api from '../../services/api'
import { updateCandidateStatus } from '../../services/candidatureService'
import { useNotifications } from '@/composables/useNotifications'

const router = useRouter()

function getExpertId() {
  const token = localStorage.getItem('token')
  if (!token) return null
  try { return JSON.parse(atob(token.split('.')[1])).expertId ?? null } catch { return null }
}

const expertId      = getExpertId()
const offres        = ref([])
const candidatures  = ref([])
const loading       = ref(false)
const filtreOffreId = ref(null)

const { notifications, unreadCount } = useNotifications()
const toastNotif = ref(null)
let   toastTimer = null

watch(unreadCount, (newVal, oldVal) => {
  if (newVal > oldVal) {
    const latest = notifications.value.find(n => !n.read)
    if (latest) {
      toastNotif.value = latest
      clearTimeout(toastTimer)
      toastTimer = setTimeout(() => { toastNotif.value = null }, 5000)
    }
  }
})

function handleToastClick() {
  if (!toastNotif.value) return
  const n = toastNotif.value; toastNotif.value = null
  if (n.candidatId) router.push({ path: '/expert/candidates', query: { candidatId: n.candidatId } })
  else if (n.offreId) router.push({ path: '/expert/candidates', query: { offreId: n.offreId } })
}

const totalCandidatures    = computed(() => offres.value.reduce((acc, o) => acc + (o.nombreCandidatures ?? 0), 0))
const candidaturesActives  = computed(() => candidatures.value.filter(c => !isRejectedApplicationStatus(c.statut)))
const candidaturesFiltrees = computed(() => filtreOffreId.value ? candidaturesActives.value.filter(c => c.offreId === filtreOffreId.value) : candidaturesActives.value)
const pendingEvalCount     = computed(() => candidaturesFiltrees.value.filter(c => !c.avisExpert).length)
const avgAIScore = computed(() => {
  const ev = candidaturesFiltrees.value.filter(c => c.avisExpert)
  if (!ev.length) return '—'
  return Math.round(ev.reduce((a, c) => a + c.avisExpert.score, 0) / ev.length * 20) + '%'
})
const avgScoreClass = computed(() => {
  const ev = candidaturesFiltrees.value.filter(c => c.avisExpert)
  if (!ev.length) return ''
  const avg = ev.reduce((a, c) => a + c.avisExpert.score, 0) / ev.length
  return avg >= 4 ? 'score-green' : avg >= 2.5 ? 'score-amber' : 'score-red'
})
function offreAvgScore(offreId) {
  const ev = candidaturesActives.value.filter(c => c.offreId === offreId && c.avisExpert)
  if (!ev.length) return '—'
  return Math.round(ev.reduce((a, c) => a + c.avisExpert.score, 0) / ev.length * 20)
}
function offreEvalPct(offreId) {
  const all = candidaturesActives.value.filter(c => c.offreId === offreId)
  if (!all.length) return 0
  return Math.round(all.filter(c => c.avisExpert).length / all.length * 100)
}
function toggleOffreFilter(offreId) { filtreOffreId.value = filtreOffreId.value === offreId ? null : offreId }
function goToAllCandidates() { router.push('/expert/candidates') }
function goToOffer(offre)    { router.push({ path: '/expert/candidates', query: { offreId: offre.offreId } }) }
function goToCandidate(c)    { router.push({ path: '/expert/candidates', query: { candidatId: c.id } }) }
async function handlePipelineStatusChange({ candidateId, toStatus }) {
  if (!candidateId || !toStatus) return
  try {
    await updateCandidateStatus(candidateId, toStatus)
    const row = candidatures.value.find(c => c.id === candidateId)
    if (row) row.statut = toStatus
  } catch (e) {
    console.error('Failed to update candidate status', e)
  }
}
function exportReport() { exportCSV(); exportPDF() }
function exportCSV() {
  const data = candidaturesFiltrees.value; if (!data.length) return
  const headers = ['Candidate','Email','Phone','Offer','Status','Score','Match%','Comment','Applied']
  const rows = data.map(c => [
    c.candidatNomComplet??'',c.candidatEmail??'',c.candidatTelephone??'',c.offreTitre??'',
    applicationStatusLabel(c.statut),c.avisExpert?.score?.toFixed(1)??'',c.avisExpert?Math.round(c.avisExpert.score*20)+'%':'',(c.avisExpert?.commentaire??'').replace(/"/g,'""'),c.creeLe?formatRecruiterDate(c.creeLe):''])
  const csv = [headers,...rows].map(r=>r.map(v=>`"${v}"`).join(',')).join('\n')
  const blob = new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8;'})
  const url = URL.createObjectURL(blob); const a = document.createElement('a')
  a.href=url; a.download=`report-${new Date().toISOString().slice(0,10)}.csv`; a.click(); URL.revokeObjectURL(url)
}
function exportPDF() {
  const data = candidaturesFiltrees.value; if (!data.length) return
  const now = new Date().toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'})
  const offreTitle = filtreOffreId.value ? offres.value.find(o=>o.offreId===filtreOffreId.value)?.titre??'All Offers' : 'All Offers'
  const rows = data.map(c=>`<tr><td>${c.candidatNomComplet??''}</td><td>${c.offreTitre??''}</td><td>${applicationStatusLabel(c.statut)}</td><td>${c.avisExpert?c.avisExpert.score.toFixed(1)+'/5':'—'}</td><td>${c.avisExpert?.commentaire??'—'}</td></tr>`).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:Arial;padding:36px;font-size:13px}h1{color:#1A2B4C}table{width:100%;border-collapse:collapse}thead{background:#1A2B4C;color:#fff}th,td{padding:8px 12px;text-align:left;font-size:12px;border-bottom:1px solid #f1f5f9}</style></head><body><h1>Pipeline Report</h1><p>${offreTitle} · ${now}</p><table><thead><tr><th>Candidate</th><th>Offer</th><th>Status</th><th>Score</th><th>Comment</th></tr></thead><tbody>${rows}</tbody></table></body></html>`
  const w = window.open('','_blank','width=1000,height=700'); if (!w) return
  w.document.write(html); w.document.close(); w.focus(); setTimeout(()=>w.print(),500)
}
function formatDateShort(d) {
  return formatRecruiterDate(d, { month: 'short', day: 'numeric', year: 'numeric' })
}

onMounted(async () => {
  if (!expertId) return
  loading.value = true
  try {
    const [offresRes, candidaturesRes] = await Promise.all([
      api.get(`/expert/${expertId}/offres`),
      api.get(`/expert/${expertId}/candidatures`)
    ])
    offres.value       = Array.isArray(offresRes.data)       ? offresRes.data       : []
    candidatures.value = Array.isArray(candidaturesRes.data) ? candidaturesRes.data : []
  } catch (e) { console.error('Error loading dashboard', e) }
  finally { loading.value = false }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
* { box-sizing: border-box; }

.dashboard-page { flex:1; min-width:0; display:flex; flex-direction:column; overflow:hidden; font-family:'Plus Jakarta Sans',system-ui,sans-serif; color:#1e293b; background:#f8fafc; }

.content { flex:1; overflow-y:auto; padding:24px 32px; }

/* Dashboard top */
.dashboard-top { display:flex; flex-direction:column; gap:16px; margin-bottom:24px; width:100%; }
.page-subtitle  { font-size:0.83rem; color:#94a3b8; margin:0; }
.stats-row      { display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:14px; width:100%; }

.stat-pill { display:flex; align-items:center; gap:10px; background:#fff; border:1px solid #e2e8f0; border-radius:13px; padding:14px 16px; box-shadow:0 1px 3px rgba(0,0,0,0.05); min-width:0; }
.stat-icon-wrap { width:36px; height:36px; border-radius:9px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.stat-label { font-size:0.6rem; color:#94a3b8; margin:0; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; }
.stat-val   { font-size:1.2rem; font-weight:800; color:#0f172a; margin:0; line-height:1.1; }
.stat-val.score-green { color:#16a34a; } .stat-val.score-amber { color:#d97706; } .stat-val.score-red { color:#dc2626; }
.qs-orange { color:#f97316; }

/* Toast */
.toast-notif { position:fixed; top:20px; right:24px; z-index:1100; display:flex; align-items:flex-start; gap:11px; background:#fff; border:1px solid #e2e8f0; border-left:4px solid #1A2B4C; border-radius:12px; padding:14px 16px; max-width:340px; box-shadow:0 8px 28px rgba(0,0,0,0.12); cursor:pointer; }
.toast-icon  { width:30px; height:30px; border-radius:8px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.icon-new_application { background:#eff6ff; color:#2563eb; } .icon-eval_reminder { background:#fefce8; color:#ca8a04; } .icon-status_updates { background:#f0fdf4; color:#16a34a; }
.toast-body  { flex:1; min-width:0; } .toast-title { font-size:0.82rem; font-weight:700; color:#0f172a; margin:0 0 2px; } .toast-text { font-size:0.74rem; color:#475569; margin:0; }
.toast-close { background:none; border:none; cursor:pointer; color:#94a3b8; padding:2px; display:flex; align-items:center; }
.toast-slide-enter-active { animation:toast-in 0.3s cubic-bezier(0.34,1.4,0.64,1); } .toast-slide-leave-active { animation:toast-in 0.2s ease reverse; }
@keyframes toast-in { from { opacity:0; transform:translateX(20px) scale(0.95); } to { opacity:1; transform:translateX(0) scale(1); } }

/* Section */
.section-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
.section-title  { font-size:1rem; font-weight:800; color:#0f172a; }
.btn-report { display:inline-flex; align-items:center; gap:6px; background:#1A2B4C; color:#fff; border:none; border-radius:9px; padding:8px 16px; font-size:0.8rem; font-weight:700; cursor:pointer; font-family:inherit; }
.btn-report:hover { opacity:0.88; }

/* Offers */
.offers-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:14px; }
.offer-card  { background:#fff; border:1px solid #e2e8f0; border-radius:13px; padding:18px; cursor:pointer; transition:box-shadow 0.2s,transform 0.15s; box-shadow:0 1px 3px rgba(0,0,0,0.05); }
.offer-card:hover  { box-shadow:0 6px 20px rgba(0,0,0,0.08); transform:translateY(-2px); }
.offer-card.active { border-color:#1A2B4C; box-shadow:0 0 0 2px rgba(26,43,76,0.15); }
.offer-top   { display:flex; align-items:flex-start; gap:11px; margin-bottom:14px; }
.offer-logo  { width:42px; height:42px; background:#1A2B4C; color:#fff; border-radius:10px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1rem; flex-shrink:0; }
.offer-info  { flex:1; } .offer-info h3 { font-size:0.88rem; font-weight:700; color:#0f172a; margin:0 0 2px; } .offer-date { font-size:0.7rem; color:#94a3b8; margin:0; }
.offer-more  { background:#f1f5f9; border:1px solid #e2e8f0; border-radius:7px; cursor:pointer; color:#475569; padding:5px 8px; display:flex; align-items:center; flex-shrink:0; }
.offer-meta  { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.offer-tag   { font-size:0.58rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:0.09em; }
.offer-score { font-size:0.8rem; font-weight:700; color:#1A2B4C; display:flex; flex-direction:column; align-items:flex-end; }
.offer-cands { font-size:0.7rem; color:#64748b; font-weight:500; }
.offer-progress-wrap  { display:flex; align-items:center; gap:8px; }
.offer-progress-bar   { flex:1; height:5px; background:#e2e8f0; border-radius:99px; overflow:hidden; }
.offer-progress-fill  { height:100%; border-radius:99px; transition:width 0.5s ease; }
.fill-complete { background:#22c55e; } .fill-partial { background:#3b82f6; }
.offer-progress-label { font-size:0.62rem; color:#94a3b8; font-weight:600; white-space:nowrap; }
.offer-empty  { border:2px dashed #e2e8f0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; background:#fafafa; min-height:140px; }
.offer-plus   { width:44px; height:44px; background:#f1f5f9; border-radius:50%; display:flex; align-items:center; justify-content:center; }
.offer-empty-title { font-size:0.84rem; font-weight:700; color:#475569; margin:0; }
.offer-empty-sub   { font-size:0.73rem; color:#94a3b8; margin:0; text-align:center; }

.active-filter-bar { display:flex; align-items:center; gap:8px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:9px; padding:8px 14px; font-size:0.8rem; color:#1A2B4C; margin-bottom:14px; }
.active-filter-bar strong { font-weight:700; }
.clear-filter { margin-left:auto; background:none; border:none; cursor:pointer; color:#3b82f6; font-size:0.78rem; font-weight:700; padding:2px 6px; border-radius:5px; font-family:inherit; }

.center-state { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:72px 20px; gap:10px; color:#94a3b8; }
.spinner { width:26px; height:26px; border:2.5px solid #e2e8f0; border-top-color:#1A2B4C; border-radius:50%; animation:spin 0.65s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }

@media (max-width:1100px) { .offers-grid { grid-template-columns:repeat(2,1fr); } .stats-row { grid-template-columns:repeat(2, minmax(0, 1fr)); } }
@media (max-width:600px)  { .stats-row { grid-template-columns:1fr; } }
@media (max-width:800px)  { .content { padding:16px; } .offers-grid { grid-template-columns:1fr; } }
</style>