import api from './api';

export const getCandidatOffres = () => {
  return api.get('/candidat/offres');
};

export const getCandidatOffreById = (id) => {
  return api.get(`/candidat/offres/${id}`);
};

export const getCandidatFormulaire = (offreId) => {
  return api.get(`/candidat/formulaire/${offreId}`);
};
export const getCandidatProfile = (candidatId) =>
  api.get(`/candidat/${candidatId}/profile`)

export const postuler = (formData) => {
  return api.post('/candidat/postuler', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
