import api from "./api"

/* --------------------------------
   OFFRES
-------------------------------- */

export const getOffres = (entrepriseId, search, filter) => {
  const params = {}
  if (entrepriseId) params.entrepriseId = entrepriseId
  if (search) params.search = search
  if (filter) params.filter = filter

  return api.get("/offres", { params })
}

export const getOffreById = (id) => {
  return api.get(`/offres/${id}`)
}

export const createOffre = (data) => {
  return api.post("/offres", data)
}

export const updateOffre = (id, data) => {
  return api.put(`/offres/${id}`, data)
}

export const deleteOffre = (id) => {
  return api.delete(`/offres/${id}`)
}

export const changePublicationStatus = (id, publier) => {
  return api.patch(`/offres/${id}/publication`, null, {
    params: { publier }
  })
}

export const togglePublicLink = (id, enabled, expiresAt = null) => {
  return api.patch(`/offres/${id}/public-link`, null, {
    params: { enabled, expiresAt }
  })
}

export const regeneratePublicToken = (id) => {
  return api.post(`/offres/${id}/regenerate-token`)
}

export const getPublicOffre = (token) => {
  return api.get(`/offres/public/${token}`)
}


/* --------------------------------
   EXPERT ASSIGNMENT
-------------------------------- */

export const assignExperts = (offreId, data) => {
  return api.post(`/offres/${offreId}/experts`, data)
}

export const searchExperts = (offreId, search) => {
  return api.get(`/offres/${offreId}/experts/search`, {
    params: { search }
  })
}

export const removeExpertAssignment = (offreId, expertId) => {
  return api.delete(`/offres/${offreId}/experts/${expertId}`)
}


/* --------------------------------
   FORMULAIRE
-------------------------------- */

export const initializeForm = (offreId) => {
  return api.post(`/offres/${offreId}/formulaire`)
}

export const addFields = (offreId, data) => {
  return api.post(`/offres/${offreId}/champs`, { champs: data })
}

export const updateField = (champId, data) => {
  return api.put(`/offres/champs/${champId}`, data)
}

export const deleteField = (champId) => {
  return api.delete(`/offres/champs/${champId}`)
}

export const reorderFields = (formId, data) => {
  return api.put(`/offres/formulaires/${formId}/ordre`, data)
}

export const getEntreprises = () => {
  return api.get("/offres/entreprises")
}