<template>
  <div class="card quiz-status-card" v-if="quizInfo.exists">
    <div class="qs-header">
      <div class="qs-icon">📝</div>
      <div class="qs-title-block">
        <p class="qs-title">Technical Assessment</p>
        <p class="qs-sub">{{ candidate.titreOffre }}</p>
      </div>
      <span class="qs-badge" :class="quizInfo.completed ? 'qs-badge-done' : 'qs-badge-pending'">
        {{ quizInfo.completed ? '✓ Completed' : '⏳ Pending' }}
      </span>
    </div>

    <div class="qs-body">
      <div class="qs-row">
        <span class="qs-lbl">📅 Scheduled</span>
        <span class="qs-val">{{ formatDateTime(quizInfo.scheduledDate) }}</span>
      </div>

      <!-- ✅ SECTION QUI S'AFFICHE SEULEMENT SI completed === true -->
      <template v-if="quizInfo.completed">
        <div class="qs-row">
          <span class="qs-lbl">✅ Completed</span>
          <span class="qs-val">{{ formatDateTime(quizInfo.completedAt) }}</span>
        </div>
        
        <!-- Score & Grade -->
        <div class="qs-score-block">
          <div class="qs-score-circle" :class="gradeColorClass(quizInfo.grade)">
            <span class="qs-score-num">{{ quizInfo.grade }}</span>
          </div>
          <div class="qs-score-details">
            <p class="qs-score-pct">{{ Math.round(quizInfo.percentage) }}% success rate</p>
            <p class="qs-score-raw">{{ quizInfo.score }} / {{ quizInfo.total }} correct answers</p>
          </div>
        </div>

        <!-- Évaluation détaillée -->
        <div class="qs-evaluation">
          <h4 class="qs-eval-title">📊 Performance Summary</h4>
          
          <div class="eval-bars">
            <div class="eval-bar-row">
              <span class="eval-bar-label">Technical Knowledge</span>
              <div class="eval-bar-bg">
                <div class="eval-bar-fill" :style="{ width: evalPct('technical') + '%' }"></div>
              </div>
              <span class="eval-bar-pct">{{ evalPct('technical') }}%</span>
            </div>
            <div class="eval-bar-row">
              <span class="eval-bar-label">Problem Solving</span>
              <div class="eval-bar-bg">
                <div class="eval-bar-fill" :style="{ width: evalPct('problem') + '%' }"></div>
              </div>
              <span class="eval-bar-pct">{{ evalPct('problem') }}%</span>
            </div>
            <div class="eval-bar-row">
              <span class="eval-bar-label">Time Management</span>
              <div class="eval-bar-bg">
                <div class="eval-bar-fill" :style="{ width: evalPct('time') + '%' }"></div>
              </div>
              <span class="eval-bar-pct">{{ evalPct('time') }}%</span>
            </div>
          </div>

          <div class="eval-insights" v-if="quizEvaluation.insights.length">
            <p class="eval-insights-title">💡 Key Insights</p>
            <ul class="eval-insights-list">
              <li v-for="(insight, i) in quizEvaluation.insights" :key="i" class="eval-insight-item">
                <span class="eval-insight-icon">✓</span>
                <span>{{ insight }}</span>
              </li>
            </ul>
          </div>

          
        </div>

       
      </template>

      <template v-else>
        <div class="qs-pending-msg">
          <span>⏰ Candidate has not yet confirmed quiz completion.</span>
        </div>
        <div class="qs-actions">
          <button class="btn-pdf-report btn-pdf-disabled" disabled>
            🔒 PDF — Awaiting Candidate Confirmation
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { getQuizByCandidature } from '../../services/quizService'

export default {
  name: 'CandidateQuizStatus',
  props: {
    candidateId: { type: [String, Number], required: true },
    candidate: { type: Object, required: true },
    generatingPdf: { type: Boolean, default: false }
  },
  data() {
    return {
      quizInfo: {
        exists:        false,
        quizToken:     null,
        scheduledDate: null,
        completed:     false,
        completedAt:   null,
        score:         null,
        total:         null,
        percentage:    null,
        grade:         null,
        totalTimeSec:  null,
      },
      quizEvaluation: {
        technical: 0,
        problem: 0,
        time: 0,
        insights: [],
        recommendation: ''
      }
    }
  },
  computed: {
    
  },
  created() {
    this.fetchQuizInfo()
  },
  methods: {
    async fetchQuizInfo() {
      try {
        const res = await getQuizByCandidature(this.candidateId)
        const data = res.data
        this.quizInfo = {
          exists:        data.exists       ?? false,
          quizToken:     data.quizToken    ?? null,
          scheduledDate: data.scheduledDate ?? null,
          completed:     data.completed    ?? false,
          completedAt:   data.completedAt  ?? null,
          score:         data.score        ?? null,
          total:         data.total        ?? null,
          percentage:    data.percentage   ?? null,
          grade:         data.grade        ?? null,
          totalTimeSec:  data.totalTimeSec ?? null,
        }
      } catch (e) {
        console.error('Failed to fetch quiz info', e)
      }
    },
    formatDateTime(d) {
      if (!d) return '—'
      return new Date(d).toLocaleString('en-US', { month:'short', day:'numeric', year:'numeric', hour:'2-digit', minute:'2-digit' })
    },
    gradeColorClass(grade) {
      return { A:'grade-a', B:'grade-b', C:'grade-c', D:'grade-d', F:'grade-f' }[grade] || ''
    },
    evalPct(category) {
      if (!this.quizInfo.completed) return 0
      const base = this.quizInfo.percentage || 0
      const adjustments = {
        technical: 0,
        problem: -5,
        time: this.quizInfo.totalTimeSec < 300 ? 10 : 0
      }
      return Math.min(100, Math.max(0, base + (adjustments[category] || 0)))
    }
  }
}
</script>

<style scoped>
.quiz-status-card { background:#fff; border-radius:14px; border:0.5px solid #E8EDF4; overflow:hidden; }
.qs-header { display:flex; align-items:center; gap:12px; padding:16px 18px; border-bottom:0.5px solid #F1F5F9; }
.qs-icon   { font-size:1.4rem; }
.qs-title-block { flex:1; }
.qs-title { font-size:14px; font-weight:700; color:#0F172A; margin:0 0 2px; }
.qs-sub   { font-size:11px; color:#94A3B8; margin:0; }
.qs-badge { font-size:11px; font-weight:700; padding:4px 10px; border-radius:99px; }
.qs-badge-done    { background:#EAF3DE; color:#27500A; }
.qs-badge-pending { background:#FAEEDA; color:#633806; }

.qs-body { padding:12px 18px; }
.qs-row  { display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:0.5px solid #F8FAFC; font-size:13px; }
.qs-row:last-child { border-bottom:none; }
.qs-lbl { color:#94A3B8; }
.qs-val { font-weight:600; color:#0F172A; display:flex; align-items:center; gap:6px; }

/* Score Block */
.qs-score-block { display:flex; align-items:center; gap:14px; padding:12px 0; margin:8px 0; border-top:0.5px solid #F1F5F9; border-bottom:0.5px solid #F1F5F9; }
.qs-score-circle { width:52px; height:52px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.5rem; font-weight:800; border:3px solid currentColor; flex-shrink:0; }
.qs-score-circle.grade-a { color:#22c55e; background:#f0fdf4; }
.qs-score-circle.grade-b { color:#6366f1; background:#eef2ff; }
.qs-score-circle.grade-c { color:#f59e0b; background:#fffbeb; }
.qs-score-circle.grade-d { color:#f97316; background:#fff7ed; }
.qs-score-circle.grade-f { color:#ef4444; background:#fef2f2; }
.qs-score-num { color:inherit; }
.qs-score-details { flex:1; }
.qs-score-pct { font-size:14px; font-weight:700; color:#0F172A; margin:0 0 2px; }
.qs-score-raw { font-size:12px; color:#94A3B8; margin:0; }

/* Evaluation Section */
.qs-evaluation { margin:14px 0; padding:14px; background:#F8FAFC; border-radius:10px; border:0.5px solid #E2E8F0; }
.qs-eval-title { font-size:13px; font-weight:700; color:#0F172A; margin:0 0 12px; }

/* Bars */
.eval-bars { display:flex; flex-direction:column; gap:10px; margin-bottom:14px; }
.eval-bar-row { display:flex; align-items:center; gap:10px; }
.eval-bar-label { font-size:11px; color:#64748B; width:110px; flex-shrink:0; }
.eval-bar-bg { flex:1; height:6px; background:#E2E8F0; border-radius:99px; overflow:hidden; }
.eval-bar-fill { height:100%; background:linear-gradient(90deg, #1A2B4C, #4c51bf); border-radius:99px; transition:width 0.4s ease; }
.eval-bar-pct { font-size:11px; font-weight:700; color:#1A2B4C; width:36px; text-align:right; }

/* Insights */
.eval-insights { margin-bottom:14px; }
.eval-insights-title { font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 8px; }
.eval-insights-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:6px; }
.eval-insight-item { display:flex; align-items:flex-start; gap:8px; font-size:12px; color:#475569; line-height:1.5; }
.eval-insight-icon { color:#1D9E75; font-weight:700; flex-shrink:0; margin-top:2px; }

/* Recommendation Box */
.eval-recommendation { display:flex; align-items:flex-start; gap:10px; padding:12px; border-radius:10px; border-left:4px solid currentColor; }
.eval-recommendation.rec-strong { background:#f0fdf4; color:#22c55e; border-left-color:#22c55e; }
.eval-recommendation.rec-hire { background:#eef2ff; color:#6366f1; border-left-color:#6366f1; }
.eval-recommendation.rec-consider { background:#fffbeb; color:#f59e0b; border-left-color:#f59e0b; }
.eval-recommendation.rec-reject { background:#fef2f2; color:#ef4444; border-left-color:#ef4444; }
.eval-rec-icon { font-size:1.2rem; flex-shrink:0; margin-top:2px; }
.eval-rec-title { font-size:13px; font-weight:700; color:#0F172A; margin:0 0 4px; }
.eval-rec-text { font-size:12px; color:#64748B; margin:0; line-height:1.5; }

/* Button PDF */
.qs-actions { padding:12px 18px 16px; }
.btn-pdf-report { width:100%; padding:12px 16px; background:#1A2B4C; color:#fff; border:none; border-radius:10px; font-size:13px; font-weight:700; cursor:pointer; font-family:'DM Sans', sans-serif; display:flex; align-items:center; justify-content:center; gap:8px; transition:background .2s, opacity .2s; }
.btn-pdf-report:hover:not(:disabled) { background:#243d6a; }
.btn-pdf-report:disabled { opacity:0.6; cursor:not-allowed; }
.btn-pdf-disabled { background:#F1F5F9 !important; color:#94A3B8 !important; cursor:not-allowed !important; border:0.5px solid #E2E8F0; }
.qs-pdf-hint { font-size:11px; color:#94A3B8; text-align:center; margin:8px 0 0; line-height:1.5; }
.qs-pending-msg { font-size:12px; color:#94A3B8; padding:8px 0; display:flex; align-items:center; gap:6px; }
</style>
