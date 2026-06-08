import api from './api'

// ── Quiz generation (AI-powered, based on job offer) ─────────────────────────
export const generateQuiz = (offreId, numQuestions = 10, timePerQuestion = 60) =>
  api.post(`/quiz/generate/${offreId}`, null, {
    params: { numQuestions, timePerQuestion }
  })

// ── Schedule a quiz for a candidate ──────────────────────────────────────────
export const scheduleQuiz = (payload) =>
  api.post('/quiz/schedule', payload)

// ── Candidate-facing: fetch quiz by token (public, no auth) ──────────────────
export const getQuizByToken = (token) =>
  api.get(`/quiz/by-token/${token}`)

// ── Submit quiz result (candidate submits answers) ───────────────────────────
export const submitResult = (payload) =>
  api.post('/quiz/submit-result', payload)

// ── Confirm quiz completion and redirect to dashboard ────────────────────────
export const confirmCompletion = (payload) =>
  api.post('/quiz/confirm-complete', payload)

// ── Recruiter: get quiz status/result for a candidature ──────────────────────
export const getQuizByCandidature = (candidatureId) =>
  api.get(`/quiz/candidature/${candidatureId}`)

// ── Recruiter: get detailed result by quiz token ─────────────────────────────
export const getQuizResult = (quizToken) =>
  api.get(`/quiz/result/${quizToken}`)
