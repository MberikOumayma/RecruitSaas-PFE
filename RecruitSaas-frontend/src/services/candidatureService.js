import api from "./api"

/* --------------------------------
   CANDIDATURES
-------------------------------- */

export const getCandidatures = (filters = {}) => {
  const params = {}
  if (filters.entrepriseId) params.entrepriseId = filters.entrepriseId
  if (filters.nomOffre)     params.nomOffre     = filters.nomOffre
  if (filters.statut)       params.statut       = filters.statut
  if (filters.scoreMin != null) params.scoreMin = filters.scoreMin
  if (filters.scoreMax != null) params.scoreMax = filters.scoreMax
  if (filters.dateDebut)    params.dateDebut    = filters.dateDebut
  if (filters.dateFin)      params.dateFin      = filters.dateFin
  if (filters.offreId)      params.offreId      = filters.offreId

  return api.get("/candidatures", { params })
}

export const getCandidatureStats = () => api.get("/candidatures/stats")

export const getCandidatureById = (id) => api.get(`/candidatures/${id}`)

// ── AI ────────────────────────────────────────────────────────────────────
export const classifyCandidate      = (id) => api.post(`/candidatures/${id}/ai/classify`)
export const recalculateMatchScore  = (id) => api.post(`/candidatures/${id}/ai/score`)
export const summarizeCv            = (id) => api.post(`/candidatures/${id}/ai/summarize`)
export const extractSkills          = (id) => api.post(`/candidatures/${id}/ai/extract-skills`)
export const extractExperience      = (id) => api.post(`/candidatures/${id}/ai/extract-experience`)

// ── Pipeline ──────────────────────────────────────────────────────────────
export const updateCandidateStatus = (id, newStatus) =>
  api.patch(`/candidatures/${id}/statut`, { statut: newStatus })

export const rejectCandidate = (id) => updateCandidateStatus(id, 'Refusée')

export const addCandidateFeedback = (id, comment) =>
  new Promise((resolve) => {
    setTimeout(() => resolve({
      data: {
        id: Date.now(),
        comment,
        author: 'Current User',
        timestamp: new Date().toISOString()
      }
    }), 800)
  })

// ── Expert reviews ────────────────────────────────────────────────────────
export const getAvisExperts = (candidatureId) =>
  api.get(`/candidatures/${candidatureId}/avis-experts`)

export const getExpertsAssignes = (candidatureId) =>
  api.get(`/candidatures/${candidatureId}/experts-assignes`)

// ── Interview ─────────────────────────────────────────────────────────────
export const getInterviewContext = (candidatureId) =>
  api.get(`/candidatures/${candidatureId}/interview/context`)

// ── Profil candidat ───────────────────────────────────────────────────────
export const getCandidateProfile = (userId) =>
  api.get(`/candidat/${userId}/profile`)

export const getCandidateProfileForCandidature = async (candidatureId) => {
  try {
    const profileRes = await api.get(`/candidatures/${candidatureId}/candidate-profile`)
    if (profileRes.data && profileRes.data.success && profileRes.data.data) {
      return profileRes
    }
  } catch (error) {
    console.warn("Could not load candidate profile natively. Falling back to form responses.", error)
  }

  // Fallback sur les réponses formulaire
  const candidatureRes = await api.get(`/candidatures/${candidatureId}`)
  const candidature = candidatureRes.data

  let parsedResponses = {}
  if (candidature && candidature.formulaireResponses) {
    parsedResponses = typeof candidature.formulaireResponses === 'string'
      ? (() => { try { return JSON.parse(candidature.formulaireResponses) } catch { return {} } })()
      : candidature.formulaireResponses
  }

  return {
    data: {
      success: true,
      data: {
        fullName:   parsedResponses.fullName  || "Candidate",
        email:      parsedResponses.email     || "—",
        phone:      parsedResponses.phone     || "",
        bio:        "Profile not yet completed. Information gathered from the application form.",
        seeking:    "",
        education:  "",
        experience: "",
        skills:     []
      }
    }
  }
}
export const rankCandidatesForOffer = (offreId) =>
  api.post(`/candidatures/offre/${offreId}/rank`)

export const extractCertifications = (id) =>
  api.post(`/candidatures/${id}/ai/extract-certifications`)