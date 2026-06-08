import axios from "axios"

const API = "https://localhost:5001/api/tenant"

export default {

  async getExperts(companyId) {
    return axios.get(`${API}/companies/${companyId}/experts`)
  },

  async inviteExpert(data) {
    return axios.post(`${API}/experts/invite`, data)
  },

  async deactivateExpert(id) {
    return axios.put(`${API}/experts/${id}/deactivate`)
  },

  async updateExpert(id, data) {
    return axios.put(`${API}/experts/${id}`, data)
  }

}