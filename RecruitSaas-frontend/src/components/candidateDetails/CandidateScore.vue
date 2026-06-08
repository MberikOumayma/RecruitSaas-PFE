<template>
  <div class="card">
    <div class="score-strip">
      <div class="gauge-wrap">
        <svg viewBox="0 0 72 44" width="72" height="44">
          <path d="M6,42 A32,32 0 0,1 66,42" fill="none" stroke="#E1F5EE" stroke-width="6" stroke-linecap="round"/>
          <path d="M6,42 A32,32 0 0,1 66,42" fill="none" :stroke="gaugeColor" stroke-width="6" stroke-linecap="round" :stroke-dasharray="`${gaugeLength} 101`"/>
          <text x="36" y="40" text-anchor="middle" font-size="15" font-weight="600" :fill="gaugeColor" font-family="DM Sans, sans-serif">{{ candidate.scoreIA != null ? Math.round(candidate.scoreIA) : '—' }}</text>
        </svg>
      </div>
      <div class="score-detail">
        <p class="score-title">Match score — {{ candidate.titreOffre }}</p>
        <div class="score-bars">
          <div class="bar-row"><span class="bar-lbl">Technical</span><div class="bar-bg"><div class="bar-fill bar-green" :style="{ width: matchDimBarWidth('technical') }"></div></div><span class="bar-pct">{{ matchDimBarLabel('technical') }}</span></div>
          <div class="bar-row"><span class="bar-lbl">Experience</span><div class="bar-bg"><div class="bar-fill bar-amber" :style="{ width: matchDimBarWidth('experience') }"></div></div><span class="bar-pct">{{ matchDimBarLabel('experience') }}</span></div>
          <div class="bar-row"><span class="bar-lbl">Domain fit</span><div class="bar-bg"><div class="bar-fill bar-green" :style="{ width: matchDimBarWidth('domainFit') }"></div></div><span class="bar-pct">{{ matchDimBarLabel('domainFit') }}</span></div>
        </div>
        <p v-if="!scoreBreakdown && candidate.scoreIA != null" class="score-breakdown-hint">Run <strong>Recalculate</strong> for Technical / Experience / Domain breakdown (not stored after reload).</p>
      </div>
    </div>
    <div class="score-actions">
      <button class="action-pill" @click="$emit('recalculate')"><RefreshCwIcon :size="18" />Recalculate</button>
    </div>
  </div>
</template>

<script>
import { RefreshCwIcon } from 'lucide-vue-next'

export default {
  name: 'CandidateScore',
  components: { RefreshCwIcon },
  props: {
    candidate: { type: Object, required: true },
    gaugeColor: { type: String, required: true },
    gaugeLength: { type: Number, required: true },
    scoreBreakdown: { type: Object, default: null },
  },
  methods: {
    matchDimBarWidth(dim) {
      const v = this.scoreBreakdown?.[dim]
      if (v == null || Number.isNaN(Number(v))) return '0%'
      return Math.min(100, Math.max(0, Math.round(Number(v)))) + '%'
    },
    matchDimBarLabel(dim) {
      const v = this.scoreBreakdown?.[dim]
      if (v == null || Number.isNaN(Number(v))) return '—'
      return Math.min(100, Math.max(0, Math.round(Number(v)))) + '%'
    },
  }
}
</script>

<style scoped>
.card { background:#fff; border-radius:14px; border:0.5px solid #E8EDF4; overflow:hidden; }
.score-strip { display:grid; grid-template-columns:auto 1fr; gap:18px; align-items:center; padding:16px 20px; border-bottom:0.5px solid #F1F5F9; }
.score-title { font-size:14px; font-weight:600; color:#0F172A; margin:0 0 8px; }
.score-breakdown-hint { font-size:11px; color:#64748B; margin:8px 0 0; line-height:1.35; }
.score-bars  { display:flex; flex-direction:column; gap:5px; }
.bar-row { display:flex; align-items:center; gap:8px; }
.bar-lbl { font-size:13px; color:#94A3B8; width:68px; flex-shrink:0; }
.bar-bg  { flex:1; height:3px; background:#F1F5F9; border-radius:99px; overflow:hidden; }
.bar-fill { height:100%; border-radius:99px; }
.bar-green { background:#1D9E75; } .bar-amber { background:#EF9F27; }
.bar-pct { font-size:11px; color:#94A3B8; width:30px; text-align:right; }
.score-actions { display:flex; gap:8px; padding:10px 20px; background:#F8FAFC; }
.action-pill { display:inline-flex; align-items:center; gap:6px; padding:6px 12px; border-radius:8px; font-size:12px; font-weight:600; background:#fff; border:0.5px solid #E2E8F0; color:#475569; cursor:pointer; font-family:inherit; }
.action-pill:hover:not(:disabled) { background:#F1F5F9; color:#0F172A; }
.action-pill:disabled { opacity:0.5; cursor:not-allowed; }
</style>
