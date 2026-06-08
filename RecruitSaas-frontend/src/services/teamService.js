import api from "./api";

const teamService = {
  // Récupérer la liste des experts d'une entreprise
  getExperts(entrepriseId, search) {
    if (entrepriseId) {
      const params = {};
      if (search) params.search = search;
      return api.get(`/tenant/companies/${entrepriseId}/experts`, { params });
    }
    // Si pas d'entrepriseId, retourne une liste vide
    return Promise.resolve({ data: [] });
  },

  // Récupérer un expert par ID
  getExpertById(id) {
    return api.get(`/tenant/experts/${id}`);
  },

  createExpert(expertData) {
  return api.post("/tenant/experts/invite", {
    firstName: expertData.firstName || expertData.prenom,
    lastName:  expertData.lastName  || expertData.nom,
    email:     expertData.email,
    companyId: expertData.companyId || expertData.entrepriseId,
    poste:     expertData.poste     
  })
},

  // Modifier un expert
  updateExpert(id, expertData) {
    return api.put(`/tenant/experts/${id}`, expertData);
  },

  // Désactiver un expert
  deactivateExpert(id) {
    return api.put(`/tenant/experts/${id}/deactivate`);
  },

  // Réactiver un expert
  reactivateExpert(id) {
    return api.put(`/tenant/experts/${id}/reactivate`);
  },

  // Supprimer un expert
  deleteExpert(id) {
    return api.delete(`/tenant/experts/${id}`);
  },

  resendInvitation(id) {
    return api.post(`/tenant/experts/${id}/resend-invitation`);
  },

  // Récupérer la liste des entreprises du tenant connecté
  getEntreprises() {
    return api.get("/tenant/companies");
  },
  // Récupérer les offres disponibles
getOffresDisponibles() {
  return api.get('/tenant/offres-disponibles')
},

// Assigner un expert à une offre
assignOffre(expertId, data) {
  return api.put(`/tenant/experts/${expertId}/assign-offre`, data)
}
};

export default teamService;