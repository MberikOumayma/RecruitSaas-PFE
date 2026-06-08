import api from './api'

const AI = import.meta.env.VITE_AI_URL || 'http://localhost:8000'

// ── Tenant/Expert ─────────────────────────────────────────────────────────────

export const planifierEntretien = (candidatureId, creneaux, message = '') =>
  api.post(`/entretiens/${candidatureId}/planifier`, { creneaux, message })

export const getEntretiens = (offreId = null, statut = null) =>
  api.get('/entretiens', { params: { offreId, statut } })

export const getEntretienById = (id) =>
  api.get(`/entretiens/${id}`)

export const annulerEntretien = (id) =>
  api.post(`/entretiens/${id}/annuler`)

// ── PUBLIC (candidat) ─────────────────────────────────────────────────────────

export const getCreneauxPublic = (token) =>
  api.get(`/entretiens/public/${token}/creneaux`)

export const confirmerCreneau = (token, dateChoisie) =>
  api.post(`/entretiens/public/${token}/confirmer`, { dateChoisie })

export const rejoindreEntretien = (token) =>
  api.get(`/entretiens/public/${token}/rejoindre`)

// ── CANDIDAT : ses entretiens ─────────────────────────────────────────────────

export const getMesEntretiens = () =>
  api.get('/entretiens/mes-entretiens')

// ── NOUVEAUX : cycle entretien IA ─────────────────────────────────────────────

export const startEntretien = (token, questions) =>
  api.post(`/entretiens/public/${token}/start`, { questions })

export const saveAnswer = (token, dto) =>
  api.post(`/entretiens/public/${token}/save-answer`, dto)

export const completeEntretien = (token, dto) =>
  api.post(`/entretiens/public/${encodeURIComponent(token)}/complete`, dto, { timeout: 20000 })

export function buildCompleteEntretienPayload (questions, { rapport, duree, fraudMetrics, verifOk, alertes }) {
  const scoredQuestions = questions.filter(q => q.type !== 'salutation' && q.score != null)
  const avg = scoredQuestions.length
    ? Math.round(scoredQuestions.reduce((a, b) => a + (b.score || 0), 0) / scoredQuestions.length)
    : 0
  return {
    questions,
    rapportIA: rapport != null ? JSON.stringify(rapport) : 'null',
    scoreGlobal: avg,
    dureeMinutes: duree,
    nbChangementsOnglet: fraudMetrics?.tab_changes ?? 0,
    verificationFacialeOk: !!verifOk,
    alertesSecurite: alertes ?? [],
  }
}

// ── IA : génération questions ─────────────────────────────────────────────────

export async function generateInterviewQuestions(titreOffre, descriptionOffre, competences) {
  const res = await fetch(`${AI}/ai/interview-questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      titreOffre,
      descriptionOffre: descriptionOffre || '',
      competences:      competences || [],
      nombreQuestions:  8
    })
  })
  const data = await res.json()
  return data.questions || []
}

// ── IA : évaluation réponse ───────────────────────────────────────────────────

export async function evaluateAnswer(question, reponse, titreOffre) {
  const res = await fetch(`${AI}/ai/evaluate-answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, reponse, titreOffre })
  })
  return res.json()
}

// ── IA : rapport final ────────────────────────────────────────────────────────

export async function generateReport(titreOffre, nomCandidat, questions, dureeMinutes, options = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), options.timeoutMs ?? 45000)
  try {
    const res = await fetch(`${AI}/ai/generate-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
      body: JSON.stringify({
        titreOffre,
        nomCandidat,
        questions,
        dureeMinutes,
        fraudMetrics: options.fraudMetrics || null,
        verificationFacialeOk: options.verificationFacialeOk ?? null,
      })
    })
    if (!res.ok) throw new Error(`generate-report failed: ${res.status}`)
    return res.json()
  } finally {
    clearTimeout(timer)
  }
}