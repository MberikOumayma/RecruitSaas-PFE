<template>
  <div class="rapport-overlay" @click.self="$emit('close')">
    <div class="rapport-modal">

      <!-- Header -->
      <div class="rapport-header">
        <div class="rapport-header-left">
          <div class="rapport-avatar">{{ initiales(rapport.nomCandidat) }}</div>
          <div>
            <h2 class="rapport-nom">{{ rapport.nomCandidat }}</h2>
            <p class="rapport-poste">{{ rapport.titreOffre }}</p>
          </div>
        </div>
        <div class="rapport-header-right">
          <button class="btn-pdf" @click="exportPdf">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/></svg>
            Export PDF
          </button>
          <button class="btn-close" @click="$emit('close')">✕</button>
        </div>
      </div>

      <!-- Contenu du rapport -->
      <div class="rapport-body">

        <!-- Score global -->
        <div class="score-section">
          <div class="score-circle">
            <svg viewBox="0 0 120 120" class="score-ring">
              <circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="8"/>
              <circle cx="60" cy="60" r="52" fill="none" :stroke="scoreColor(rapport.scoreGlobal)" stroke-width="8"
                stroke-linecap="round" stroke-dasharray="326.73"
                :stroke-dashoffset="326.73 - (326.73 * rapport.scoreGlobal / 100)"
                transform="rotate(-90 60 60)"/>
            </svg>
            <div class="score-inner">
              <span class="score-num">{{ Math.round(rapport.scoreGlobal) }}</span>
              <span class="score-over">/100</span>
            </div>
          </div>
          <div class="score-meta">
            <div class="mention-badge" :class="mentionClass(rapport.mention)">{{ mentionLabel(rapport.mention) }}</div>
            <div class="reco-badge" :class="recoClass(rapport.recommandation)">
              <span class="reco-icon">{{ recoIcon(rapport.recommandation) }}</span>
              {{ recoLabel(rapport.recommandation) }}
            </div>
            <div class="meta-stats">
              <div class="meta-stat"><span class="meta-label">Duration</span><span class="meta-val">{{ rapport.dureeMinutes || '—' }} min</span></div>
              <div class="meta-stat"><span class="meta-label">Questions</span><span class="meta-val">{{ rapport.nbQuestionsRepondues || questions.length }}</span></div>
              <div class="meta-stat"><span class="meta-label">Face verification</span><span class="meta-val" :class="rapport.verificationFacialeOk ? 'ok' : 'warn'">{{ rapport.verificationFacialeOk ? '✓ OK' : '✗ Not verified' }}</span></div>
              <div v-if="rapport.nbChangementsOnglet > 0" class="meta-stat">
                <span class="meta-label">Tab switches</span>
                <span class="meta-val warn">{{ rapport.nbChangementsOnglet }}x</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Détection anti-fraude (FraudPredictor v5) -->
        <div class="section" v-if="rapport.fraudDetection">
          <h3 class="section-title">Fraud analysis</h3>
          <div class="fraud-card" :class="fraudCardClass(rapport.fraudDetection)">
            <div class="fraud-header">
              <span class="fraud-icon">{{ rapport.fraudDetection.icon }}</span>
              <div>
                <p class="fraud-verdict">{{ rapport.fraudDetection.verdict }}</p>
                <p class="fraud-sub">
                  XGBoost v5 model · Threshold {{ rapport.fraudDetection.threshold ?? 0.31 }}
                  <span v-if="rapport.fraudDetection.rule_score != null">
                    · ML {{ rapport.fraudDetection.ml_score }}% · Rules {{ rapport.fraudDetection.rule_score }}%
                  </span>
                </p>
              </div>
              <div class="fraud-score-badge">{{ rapport.fraudDetection.score }}%</div>
            </div>
            <p class="fraud-level">Suspicion level: <strong>{{ fraudLevelLabel(rapport.fraudDetection.level) }}</strong></p>
            <ul v-if="rapport.fraudDetection.viols?.length" class="fraud-viols">
              <li v-for="(v, i) in rapport.fraudDetection.viols" :key="i">{{ v }}</li>
            </ul>
            <p v-else class="fraud-ok">No major violations detected.</p>
          </div>
        </div>

        <!-- Résumé exécutif -->
        <div class="section">
          <h3 class="section-title">Executive summary</h3>
          <p class="section-text">{{ rapport.resume_executif }}</p>
        </div>

        <!-- Points forts / axes d'amélioration -->
        <div class="two-cols">
          <div class="section">
            <h3 class="section-title green">Strengths</h3>
            <ul class="point-list">
              <li v-for="(p, i) in rapport.points_forts" :key="i" class="point-item point-ok">
                <span class="point-dot"></span>{{ p }}
              </li>
            </ul>
          </div>
          <div class="section">
            <h3 class="section-title orange">Areas for improvement</h3>
            <ul class="point-list">
              <li v-for="(p, i) in rapport.points_amelioration" :key="i" class="point-item point-warn">
                <span class="point-dot"></span>{{ p }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Compétences évaluées -->
        <div class="section" v-if="rapport.competences_evaluees?.length">
          <h3 class="section-title">Skills assessed</h3>
          <div class="competences-grid">
            <div v-for="c in rapport.competences_evaluees" :key="c.competence" class="competence-item">
              <div class="comp-header">
                <span class="comp-name">{{ c.competence }}</span>
                <span class="comp-level" :class="niveauClass(c.niveau)">{{ niveauLabel(c.niveau) }}</span>
              </div>
              <div class="comp-bar-bg">
                <div class="comp-bar-fill" :style="{ width: c.score + '%', background: scoreColor(c.score) }"></div>
              </div>
              <span class="comp-score">{{ c.score }}/100</span>
            </div>
          </div>
        </div>

        <!-- Q&A détail -->
        <div class="section" v-if="questions.length">
          <h3 class="section-title">Answer details</h3>
          <div class="qa-list">
            <div v-for="q in questions" :key="q.id" class="qa-item">
              <div class="qa-header">
                <span class="qa-num">Q{{ q.id }}</span>
                <span class="qa-type">{{ typeLabel(q.type) }}</span>
                <span class="qa-score" :style="{ color: scoreColor(q.score || 0) }">{{ q.score || '—' }}/100</span>
              </div>
              <p class="qa-question">{{ q.texte }}</p>
              <p class="qa-reponse" v-if="q.reponse">{{ q.reponse }}</p>
              <p class="qa-feedback" v-if="q.feedback">💬 {{ q.feedback }}</p>
            </div>
          </div>
        </div>

        <!-- Commentaire recruteur -->
        <div class="section" v-if="rapport.commentaire_recruteur">
          <h3 class="section-title">Recruiter comment</h3>
          <p class="section-text commentaire">{{ rapport.commentaire_recruteur }}</p>
        </div>

        <!-- Footer -->
        <div class="rapport-footer">
          <span>RecruitSaaS · AI-generated report</span>
          <span>{{ new Date().toLocaleDateString('en-US', { day:'numeric', month:'long', year:'numeric' }) }}</span>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { fraudLevelLabel } from '@/utils/recruiterI18n'

export default {
  name: 'RapportEntretien',
  props: {
    rapport:   { type: Object, required: true },
    questions: { type: Array,  default: () => [] }
  },
  emits: ['close'],
  methods: {
    fraudLevelLabel,
    initiales(n) { return n ? n.split(' ').map(p=>p[0]).join('').toUpperCase().slice(0,2) : '?' },
    scoreColor(s) { return s >= 80 ? '#1D9E75' : s >= 50 ? '#EF9F27' : '#E24B4A' },
    mentionClass(m) {
      return { 'Excellent':'mention-green', 'Bien':'mention-blue', 'Satisfaisant':'mention-amber', 'Insuffisant':'mention-red' }[m] || 'mention-gray'
    },
    recoClass(r)  { return { 'Recruter':'reco-green', 'À considérer':'reco-amber', 'Refuser':'reco-red' }[r] || 'reco-gray' },
    recoIcon(r)   { return { 'Recruter':'✓', 'À considérer':'◎', 'Refuser':'✗' }[r] || '?' },
    niveauClass(n){ return { 'Expert':'niv-expert', 'Avancé':'niv-avance', 'Intermédiaire':'niv-inter', 'Débutant':'niv-debutant' }[n] || '' },
    mentionLabel(m) {
      return { Excellent:'Excellent', Bien:'Good', Satisfaisant:'Satisfactory', Insuffisant:'Insufficient' }[m] || m
    },
    recoLabel(r) {
      return { Recruter:'Hire', 'À considérer':'Consider', Refuser:'Reject' }[r] || r
    },
    niveauLabel(n) {
      return { Expert:'Expert', Avancé:'Advanced', Intermédiaire:'Intermediate', Débutant:'Beginner' }[n] || n
    },
    typeLabel(t)  {
      return { introduction:'Introduction', technique:'Technical', comportementale:'Behavioral', situation:'Scenario', perspective:'Outlook' }[t] || t
    },
    fraudCardClass(f) {
      if (!f) return ''
      if (f.level === 'ELEVE') return 'fraud-high'
      if (f.level === 'MOYEN') return 'fraud-medium'
      if (f.level === 'FAIBLE') return 'fraud-low'
      return 'fraud-none'
    },

    exportPdf() {
      const r  = this.rapport
      const qs = this.questions

      const sc = r.scoreGlobal || 0
      const scoreColor = sc >= 80 ? '#1D9E75' : sc >= 50 ? '#EF9F27' : '#E24B4A'
      const dash   = 326.73
      const offset = dash - (dash * sc / 100)
      const date   = new Date().toLocaleDateString('en-US', { day:'numeric', month:'long', year:'numeric' })
      const avatar = (r.nomCandidat||'?').split(' ').map(p=>p[0]).join('').toUpperCase().slice(0,2)

      // ── Questions HTML ──────────────────────────────────────────────────
      const questionsHtml = qs.length ? `
        <div class="section">
          <h3 class="section-title">Answer details</h3>
          ${qs.map(q => {
            const qsc = q.score || 0
            const qc  = qsc >= 80 ? '#1D9E75' : qsc >= 50 ? '#EF9F27' : '#E24B4A'
            return `
              <div class="qa-item">
                <div class="qa-header">
                  <span class="qa-num">Q${q.id}</span>
                  <span class="qa-type">${q.type || ''}</span>
                  <span class="qa-score" style="color:${qc}">${qsc || '—'}/100</span>
                </div>
                <p class="qa-question">${(q.texte||'').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</p>
                ${q.reponse ? `<p class="qa-reponse">${(q.reponse).replace(/</g,'&lt;').replace(/>/g,'&gt;')}</p>` : ''}
                ${q.feedback ? `<p class="qa-feedback">💬 ${(q.feedback).replace(/</g,'&lt;').replace(/>/g,'&gt;')}</p>` : ''}
              </div>`
          }).join('')}
        </div>` : ''

      // ── Compétences HTML ───────────────────────────────────────────────
      const competencesHtml = (r.competences_evaluees||[]).length ? `
        <div class="section">
          <h3 class="section-title">Skills assessed</h3>
          ${r.competences_evaluees.map(c => {
            const cc = c.score >= 80 ? '#1D9E75' : c.score >= 50 ? '#EF9F27' : '#E24B4A'
            return `
              <div class="comp-item">
                <div class="comp-header">
                  <span class="comp-name">${c.competence||''}</span>
                  <span class="comp-level">${this.niveauLabel(c.niveau)||''}</span>
                </div>
                <div class="comp-bar-bg">
                  <div class="comp-bar-fill" style="width:${c.score||0}%;background:${cc}"></div>
                </div>
                <span class="comp-score">${c.score||0}/100</span>
              </div>`
          }).join('')}
        </div>` : ''

      // ── Points forts / axes ────────────────────────────────────────────
      const fortsHtml = (r.points_forts||[]).map(p =>
        `<li class="point-item"><span class="point-dot dot-ok"></span>${p}</li>`).join('')
      const amelioHtml = (r.points_amelioration||[]).map(p =>
        `<li class="point-item"><span class="point-dot dot-warn"></span>${p}</li>`).join('')

      // ── Commentaire recruteur ──────────────────────────────────────────
      const commentaireHtml = r.commentaire_recruteur ? `
        <div class="section">
          <h3 class="section-title">Recruiter comment</h3>
          <p class="section-text commentaire">${r.commentaire_recruteur}</p>
        </div>` : ''

      // ── HTML final ─────────────────────────────────────────────────────
      const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Report - ${r.nomCandidat} - ${r.titreOffre}</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; color: #374151; background: white; padding: 32px; max-width: 860px; margin: 0 auto; }
  .header { display: flex; align-items: center; gap: 14px; padding-bottom: 20px; border-bottom: 2px solid #e5e7eb; margin-bottom: 24px; }
  .avatar { width: 48px; height: 48px; border-radius: 50%; background: #1A2B4C; color: #B5D4F4; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; flex-shrink: 0; }
  .nom { font-size: 20px; font-weight: 700; color: #0f172a; }
  .poste { font-size: 13px; color: #64748b; margin-top: 2px; }
  .score-section { display: flex; align-items: center; gap: 32px; background: #f8fafc; border-radius: 12px; padding: 24px; border: 1px solid #e5e7eb; margin-bottom: 24px; }
  .score-circle { position: relative; width: 110px; height: 110px; flex-shrink: 0; }
  .score-circle svg { width: 110px; height: 110px; }
  .score-inner { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
  .score-num { font-size: 26px; font-weight: 800; color: #0f172a; line-height: 1; }
  .score-over { font-size: 11px; color: #94a3b8; }
  .score-meta { flex: 1; display: flex; flex-direction: column; gap: 8px; }
  .mention { font-size: 13px; font-weight: 700; padding: 4px 14px; border-radius: 99px; display: inline-block; background: #fffbeb; color: #92400e; }
  .reco { font-size: 13px; font-weight: 700; padding: 4px 14px; border-radius: 8px; display: inline-block; background: #fffbeb; color: #92400e; border: 1px solid #fcd34d; }
  .meta-stats { display: flex; gap: 20px; flex-wrap: wrap; margin-top: 6px; }
  .meta-stat { display: flex; flex-direction: column; gap: 2px; }
  .meta-label { font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }
  .meta-val { font-size: 13px; font-weight: 600; color: #0f172a; }
  .section { margin-bottom: 24px; }
  .section-title { font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9; margin-bottom: 12px; }
  .section-title.green { color: #065f46; } .section-title.orange { color: #92400e; }
  .section-text { font-size: 14px; color: #374151; line-height: 1.7; }
  .commentaire { background: #f8fafc; border-left: 3px solid #1A2B4C; padding: 12px 16px; border-radius: 0 8px 8px 0; font-style: italic; }
  .two-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
  .point-list { list-style: none; display: flex; flex-direction: column; gap: 6px; }
  .point-item { display: flex; align-items: flex-start; gap: 8px; font-size: 13px; color: #374151; line-height: 1.5; }
  .point-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
  .dot-ok { background: #1D9E75; } .dot-warn { background: #EF9F27; }
  .comp-item { margin-bottom: 12px; }
  .comp-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  .comp-name { font-size: 13px; font-weight: 600; color: #0f172a; }
  .comp-level { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 99px; background: #fffbeb; color: #92400e; }
  .comp-bar-bg { height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden; margin-bottom: 2px; }
  .comp-bar-fill { height: 100%; border-radius: 3px; }
  .comp-score { font-size: 11px; color: #94a3b8; font-weight: 600; }
  .qa-item { background: #f8fafc; border-radius: 10px; padding: 14px; border: 1px solid #e5e7eb; margin-bottom: 12px; page-break-inside: avoid; break-inside: avoid; }
  .qa-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
  .qa-num { font-size: 11px; font-weight: 700; color: #64748b; background: #e5e7eb; padding: 2px 7px; border-radius: 4px; }
  .qa-type { font-size: 11px; color: #94a3b8; }
  .qa-score { font-size: 13px; font-weight: 700; margin-left: auto; }
  .qa-question { font-size: 13px; font-weight: 600; color: #0f172a; margin-bottom: 6px; }
  .qa-reponse { font-size: 13px; color: #374151; line-height: 1.5; margin-bottom: 6px; }
  .qa-feedback { font-size: 12px; color: #64748b; font-style: italic; }
  .rapport-footer { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; padding-top: 16px; border-top: 1px solid #e5e7eb; margin-top: 8px; }
  @media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    body { padding: 16px; }
    .qa-item { page-break-inside: avoid; break-inside: avoid; }
    .section { break-inside: avoid; }
  }
</style>
</head>
<body>
  <div class="header">
    <div class="avatar">${avatar}</div>
    <div>
      <div class="nom">${r.nomCandidat || ''}</div>
      <div class="poste">${r.titreOffre || ''}</div>
    </div>
  </div>

  <div class="score-section">
    <div class="score-circle">
      <svg viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="8"/>
        <circle cx="60" cy="60" r="52" fill="none" stroke="${scoreColor}" stroke-width="8"
          stroke-linecap="round" stroke-dasharray="${dash}" stroke-dashoffset="${offset}"
          transform="rotate(-90 60 60)"/>
      </svg>
      <div class="score-inner">
        <span class="score-num">${Math.round(sc)}</span>
        <span class="score-over">/100</span>
      </div>
    </div>
    <div class="score-meta">
      <span class="mention">${this.mentionLabel(r.mention) || ''}</span>
      <span class="reco">${this.recoLabel(r.recommandation) || ''}</span>
      <div class="meta-stats">
        <div class="meta-stat"><span class="meta-label">Duration</span><span class="meta-val">${r.dureeMinutes || '—'} min</span></div>
        <div class="meta-stat"><span class="meta-label">Questions</span><span class="meta-val">${qs.length}</span></div>
        <div class="meta-stat"><span class="meta-label">Face verification</span><span class="meta-val">${r.verificationFacialeOk ? '✓ OK' : '✗ Not verified'}</span></div>
        ${r.nbChangementsOnglet > 0 ? `<div class="meta-stat"><span class="meta-label">Tab switches</span><span class="meta-val">${r.nbChangementsOnglet}x</span></div>` : ''}
      </div>
    </div>
  </div>

  ${r.fraudDetection ? `
  <div class="section">
    <h3 class="section-title">Fraud analysis</h3>
    <div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;padding:16px;">
      <p style="font-size:16px;font-weight:700;margin-bottom:6px;">${r.fraudDetection.icon || ''} ${r.fraudDetection.verdict || ''} — ${r.fraudDetection.score || 0}%</p>
      <p style="font-size:13px;color:#64748b;margin-bottom:8px;">Level: ${this.fraudLevelLabel(r.fraudDetection.level) || ''} · XGBoost v5 model</p>
      ${(r.fraudDetection.viols || []).length
        ? `<ul style="margin:0;padding-left:18px;">${r.fraudDetection.viols.map(v => `<li>${v}</li>`).join('')}</ul>`
        : '<p style="margin:0;color:#065f46;">No major violations detected.</p>'}
    </div>
  </div>` : ''}

  <div class="section">
    <p class="section-text">${r.resume_executif || ''}</p>
  </div>

  <div class="two-cols">
    <div>
      <h3 class="section-title green" style="margin-bottom:10px">Strengths</h3>
      <ul class="point-list">${fortsHtml}</ul>
    </div>
    <div>
      <h3 class="section-title orange" style="margin-bottom:10px">Areas for improvement</h3>
      <ul class="point-list">${amelioHtml}</ul>
    </div>
  </div>

  ${competencesHtml}
  ${questionsHtml}
  ${commentaireHtml}

  <div class="rapport-footer">
    <span>RecruitSaaS · AI-generated report</span>
    <span>${date}</span>
  </div>
</body>
</html>`

      const win = window.open('', '_blank', 'width=960,height=800')
      if (!win) { alert('Allow popups for this site to export the PDF'); return }
      win.document.open()
      win.document.write(html)
      win.document.close()
      win.focus()
      setTimeout(() => { win.print() }, 800)
    }
  }
}
</script>

<style scoped>
* { box-sizing: border-box; }
.rapport-overlay { position:fixed; inset:0; background:rgba(15,23,42,0.6); backdrop-filter:blur(4px); z-index:1000; display:flex; align-items:center; justify-content:center; padding:16px; }
.rapport-modal { background:#fff; border-radius:16px; width:100%; max-width:860px; max-height:90vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 24px 80px rgba(0,0,0,0.2); }

.rapport-header { display:flex; align-items:center; justify-content:space-between; padding:20px 24px; border-bottom:1px solid #e5e7eb; flex-shrink:0; }
.rapport-header-left { display:flex; align-items:center; gap:14px; }
.rapport-avatar { width:48px; height:48px; border-radius:50%; background:#1A2B4C; color:#B5D4F4; display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:700; flex-shrink:0; }
.rapport-nom   { font-size:18px; font-weight:700; color:#0f172a; margin:0; }
.rapport-poste { font-size:13px; color:#64748b; margin:2px 0 0; }
.rapport-header-right { display:flex; align-items:center; gap:8px; }
.btn-pdf { display:flex; align-items:center; gap:6px; padding:8px 14px; background:#1A2B4C; color:#fff; border:none; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; font-family:inherit; }
.btn-pdf:hover { background:#243d6a; }
.btn-close { width:32px; height:32px; border-radius:8px; border:1px solid #e5e7eb; background:#f9fafb; cursor:pointer; font-size:16px; color:#64748b; display:flex; align-items:center; justify-content:center; }

.rapport-body { flex:1; overflow-y:auto; padding:24px; display:flex; flex-direction:column; gap:24px; }

.score-section { display:flex; align-items:center; gap:32px; background:#f8fafc; border-radius:12px; padding:24px; border:1px solid #e5e7eb; }
.score-circle  { position:relative; width:120px; height:120px; flex-shrink:0; }
.score-ring    { width:120px; height:120px; }
.score-inner   { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }
.score-num  { font-size:28px; font-weight:800; color:#0f172a; line-height:1; }
.score-over { font-size:12px; color:#94a3b8; }
.score-meta { flex:1; display:flex; flex-direction:column; gap:10px; }
.mention-badge { font-size:13px; font-weight:700; padding:4px 14px; border-radius:99px; display:inline-block; width:fit-content; }
.mention-green { background:#ecfdf5; color:#065f46; } .mention-blue { background:#eff6ff; color:#1e40af; }
.mention-amber { background:#fffbeb; color:#92400e; } .mention-red { background:#fef2f2; color:#991b1b; }
.mention-gray  { background:#f1f5f9; color:#475569; }
.reco-badge { font-size:13px; font-weight:700; padding:4px 14px; border-radius:8px; display:flex; align-items:center; gap:6px; width:fit-content; }
.reco-green { background:#ecfdf5; color:#065f46; border:1px solid #6ee7b7; }
.reco-amber { background:#fffbeb; color:#92400e; border:1px solid #fcd34d; }
.reco-red   { background:#fef2f2; color:#991b1b; border:1px solid #fca5a5; }
.reco-icon  { font-size:14px; }
.meta-stats { display:flex; flex-wrap:wrap; gap:12px; margin-top:4px; }
.meta-stat  { display:flex; flex-direction:column; gap:2px; }
.meta-label { font-size:10px; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.05em; }
.meta-val   { font-size:13px; font-weight:600; color:#0f172a; }
.meta-val.ok   { color:#1D9E75; } .meta-val.warn { color:#EF9F27; }

.section { display:flex; flex-direction:column; gap:10px; }
.section-title { font-size:13px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.06em; margin:0; padding-bottom:8px; border-bottom:1px solid #f1f5f9; }
.section-title.green  { color:#065f46; } .section-title.orange { color:#92400e; }
.section-text { font-size:14px; color:#374151; line-height:1.7; margin:0; }
.commentaire { background:#f8fafc; border-left:3px solid #1A2B4C; padding:12px 16px; border-radius:0 8px 8px 0; font-style:italic; }

.two-cols { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.point-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:6px; }
.point-item { display:flex; align-items:flex-start; gap:8px; font-size:13px; color:#374151; line-height:1.5; }
.point-dot  { width:6px; height:6px; border-radius:50%; flex-shrink:0; margin-top:5px; }
.point-ok .point-dot   { background:#1D9E75; } .point-warn .point-dot { background:#EF9F27; }

.competences-grid { display:flex; flex-direction:column; gap:12px; }
.competence-item  { display:flex; flex-direction:column; gap:4px; }
.comp-header { display:flex; align-items:center; justify-content:space-between; }
.comp-name   { font-size:13px; font-weight:600; color:#0f172a; }
.comp-level  { font-size:11px; font-weight:700; padding:2px 8px; border-radius:99px; }
.niv-expert   { background:#ecfdf5; color:#065f46; } .niv-avance { background:#eff6ff; color:#1e40af; }
.niv-inter    { background:#fffbeb; color:#92400e; } .niv-debutant { background:#fef2f2; color:#991b1b; }
.comp-bar-bg  { height:6px; background:#e5e7eb; border-radius:3px; overflow:hidden; }
.comp-bar-fill { height:100%; border-radius:3px; transition:width 0.5s; }
.comp-score   { font-size:11px; color:#94a3b8; font-weight:600; align-self:flex-end; }

.qa-list { display:flex; flex-direction:column; gap:12px; }
.qa-item  { background:#f8fafc; border-radius:10px; padding:14px; border:1px solid #e5e7eb; }
.qa-header { display:flex; align-items:center; gap:8px; margin-bottom:8px; }
.qa-num   { font-size:11px; font-weight:700; color:#64748b; background:#e5e7eb; padding:2px 7px; border-radius:4px; }
.qa-type  { font-size:11px; color:#94a3b8; }
.qa-score { font-size:13px; font-weight:700; margin-left:auto; }
.qa-question { font-size:13px; font-weight:600; color:#0f172a; margin:0 0 6px; }
.qa-reponse  { font-size:13px; color:#374151; margin:0 0 6px; line-height:1.5; }
.qa-feedback { font-size:12px; color:#64748b; margin:0; font-style:italic; }

.rapport-footer { display:flex; justify-content:space-between; font-size:11px; color:#94a3b8; padding-top:16px; border-top:1px solid #e5e7eb; margin-top:8px; }

.fraud-card { border-radius:12px; padding:18px 20px; border:1px solid #e5e7eb; }
.fraud-high { background:#fef2f2; border-color:#fecaca; }
.fraud-medium { background:#fff7ed; border-color:#fed7aa; }
.fraud-low { background:#fffbeb; border-color:#fde68a; }
.fraud-none { background:#f0fdf4; border-color:#bbf7d0; }
.fraud-header { display:flex; align-items:center; gap:14px; margin-bottom:10px; }
.fraud-icon { font-size:28px; line-height:1; }
.fraud-verdict { font-size:16px; font-weight:700; color:#0f172a; margin:0; }
.fraud-sub { font-size:11px; color:#64748b; margin:2px 0 0; }
.fraud-score-badge { margin-left:auto; font-size:22px; font-weight:800; color:#0f172a; }
.fraud-level { font-size:13px; color:#475569; margin:0 0 10px; }
.fraud-viols { margin:0; padding-left:18px; color:#b91c1c; font-size:13px; }
.fraud-ok { margin:0; font-size:13px; color:#065f46; }
</style>