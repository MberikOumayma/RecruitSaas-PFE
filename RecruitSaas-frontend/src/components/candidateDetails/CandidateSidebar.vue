<template>
  <div class="right-col">
    <div class="sticky-wrap">
      <div class="card stats-card">
        <div class="stats-grid">
          <div class="stat-box"><span class="stat-num" :style="{ color: gaugeColor }">{{ candidate.scoreIA != null ? Math.round(candidate.scoreIA) : '—' }}</span><span class="stat-lbl">AI Score</span></div>
        </div>
      </div>

      <div class="card">
        <p class="sb-section-title">Pipeline Actions</p>
        <div class="sb-btn-stack">
          <button class="sb-btn sb-stage" @click="$emit('move-stage')"><ArrowRightLeftIcon :size="14" /><span>Move to Stage</span></button>
        </div>
        <div class="card" style="border:none; border-radius:0;">
          <p class="sb-section-title">Export Profile</p>
          <div class="sb-btn-stack">
            <button class="sb-btn sb-export" @click="$emit('export-pdf')" :disabled="exporting.pdf">
              <component :is="exporting.pdf ? 'Loader2Icon' : 'DownloadIcon'" :size="14"
                :class="{ 'spin-icon': exporting.pdf }" />
              <span>{{ exporting.pdf ? 'Generating…' : 'Download PDF' }}</span>
            </button>
            <button class="sb-btn sb-export" @click="$emit('export-word')" :disabled="exporting.word">
              <component :is="exporting.word ? 'Loader2Icon' : 'FileTextIcon'" :size="14"
                :class="{ 'spin-icon': exporting.word }" />
              <span>{{ exporting.word ? 'Generating…' : 'Download Word' }}</span>
            </button>
          </div>
        </div>
      </div>
        
      <div class="card">
        <p class="sb-section-title">Resume (CV)</p>
        <button class="sb-btn sb-cv" @click="$emit('view-cv')"><FileTextIcon :size="14" /><span>View Original CV</span><ExternalLinkIcon :size="11" class="trail" /></button>
      </div>

    
      <div class="card">
        <p class="sb-section-title">Application Info</p>
        <div class="info-list">
          <div class="info-row"><span class="info-lbl"><CalendarIcon :size="11" /> Applied</span><span class="info-val">{{ formatDate(candidate.creeLe) }}</span></div>
          <div class="info-row"><span class="info-lbl"><GlobeIcon :size="11" /> Source</span><span class="info-pill">Direct</span></div>
          <div class="info-row">
            <span class="info-lbl"><UserIcon :size="11" /> Expert(s)</span>
            <span v-if="assignedExperts.length" class="info-val">{{ assignedExpertsLabel }}</span>
            <span v-else class="info-na">Unassigned</span>
          </div>
          <div class="info-row" v-if="candidate.statut">
            <span class="info-lbl"><ActivityIcon :size="11" /> Status</span>
            <span class="status-pill" :class="statusPillClass(candidate.statut)"><span class="s-dot"></span>{{ candidate.statut }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  ArrowRightLeftIcon, DownloadIcon, Loader2Icon, FileTextIcon, ExternalLinkIcon, CalendarIcon, GlobeIcon, UserIcon, ActivityIcon
} from 'lucide-vue-next'

export default {
  name: 'CandidateSidebar',
  components: {
    ArrowRightLeftIcon, DownloadIcon, Loader2Icon, FileTextIcon, ExternalLinkIcon, CalendarIcon, GlobeIcon, UserIcon, ActivityIcon
  },
  props: {
    candidate: { type: Object, required: true },
    gaugeColor: { type: String, default: '#CBD5E1' },
   
    assignedExperts: { type: Array, default: () => [] },
    exporting: { type: Object, required: true },
    assignedExpertsLabel: { type: String, default: '' }
  },
  methods: {
    gradeColorClass(grade) {
      return { A:'grade-a', B:'grade-b', C:'grade-c', D:'grade-d', F:'grade-f' }[grade] || ''
    },
    formatDateTime(d) {
      if (!d) return '—'
      return new Date(d).toLocaleString('en-US', { month:'short', day:'numeric', year:'numeric', hour:'2-digit', minute:'2-digit' })
    },
    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' })
    },
    statusPillClass(s) {
      return { 'Nouvelle':'sp-blue','En cours':'sp-amber','Acceptée':'sp-green','Refusée':'sp-red','Présélectionné':'sp-purple','Entretien':'sp-teal' }[s] || 'sp-blue'
    }
  }
}
</script>

<style scoped>
.right-col { position:relative; }
.sticky-wrap { position:sticky; top:22px; display:flex; flex-direction:column; gap:14px; }
.card { background:#fff; border-radius:14px; border:0.5px solid #E8EDF4; overflow:hidden; }
.stats-card { overflow:hidden; }
.stats-grid { display:grid; grid-template-columns:1fr; }
.stat-box   { padding:14px; text-align:center; border-right:0.5px solid #F1F5F9; }
.stat-box:last-child { border-right:none; }
.stat-num   { display:block; font-size:22px; font-weight:700; color:#0F172A; line-height:1; }
.stat-lbl   { display:block; font-size:11px; color:#94A3B8; margin-top:4px; text-transform:uppercase; letter-spacing:0.06em; }

.sb-section-title { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8; margin:0 0 12px; padding:16px 16px 0; }
.sb-btn-stack { padding:0 16px 16px; display:flex; flex-direction:column; gap:8px; }
.sb-btn { display:flex; align-items:center; gap:9px; width:100%; padding:9px 12px; border-radius:9px; font-size:13px; font-weight:600; cursor:pointer; font-family:inherit; border:0.5px solid #E2E8F0; background:#F8FAFC; color:#334155; }
.sb-btn span { flex:1; text-align:left; }
.sb-stage:hover { background:#F1F5F9; color:#1A2B4C; }
.sb-cv { margin:0 16px 16px; width:calc(100% - 32px); } .sb-cv:hover { background:#F1F5F9; }
.trail { margin-left:auto; opacity:0.4; }

.sb-export { background:#F8FAFC; color:#454a83; border-color:rgba(69,74,131,0.25); }
.sb-export:hover:not(:disabled) { background:rgba(69,74,131,0.07); border-color:#454a83; }
.sb-export:disabled { opacity:0.5; cursor:not-allowed; }
@keyframes spin-anim { to { transform:rotate(360deg); } }
.spin-icon { animation:spin-anim 0.7s linear infinite; }

.sb-quiz-info { padding:0 16px 14px; }
.sbq-row  { display:flex; align-items:center; gap:10px; }
.sbq-score { font-size:1.4rem; font-weight:800; width:40px; height:40px; border-radius:8px; display:flex; align-items:center; justify-content:center; border:2px solid currentColor; flex-shrink:0; }
.grade-a { color:#22c55e; } .grade-b { color:#6366f1; } .grade-c { color:#f59e0b; } .grade-d { color:#f97316; } .grade-f { color:#ef4444; }
.sbq-pct  { font-size:13px; font-weight:700; color:#0F172A; margin:0 0 2px; }
.sbq-date { font-size:11px; color:#94A3B8; margin:0; }
.sbq-pending { display:flex; align-items:center; gap:6px; font-size:12px; color:#94A3B8; }

.info-list { padding:0 16px 14px; }
.info-row  { display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:0.5px solid #F8FAFC; }
.info-row:last-child { border-bottom:none; }
.info-lbl  { display:flex; align-items:center; gap:5px; font-size:12px; color:#94A3B8; }
.info-val  { font-size:12px; font-weight:600; color:#0F172A; }
.info-pill { font-size:11px; padding:3px 8px; background:#F1F5F9; color:#475569; border-radius:99px; }
.info-na   { font-size:12px; color:#CBD5E1; font-style:italic; }

.status-pill { display:inline-flex; align-items:center; gap:4px; font-size:11px; font-weight:700; padding:3px 8px; border-radius:99px; }
.s-dot { width:5px; height:5px; border-radius:50%; background:currentColor; }
.sp-blue   { background:#E6F1FB; color:#0C447C; }
.sp-green  { background:#EAF3DE; color:#27500A; }
.sp-amber  { background:#FAEEDA; color:#633806; }
.sp-red    { background:#FCEBEB; color:#791F1F; }
.sp-purple { background:#EEEDFE; color:#3C3489; }
.sp-teal   { background:#E1F5EE; color:#085041; }
</style>
