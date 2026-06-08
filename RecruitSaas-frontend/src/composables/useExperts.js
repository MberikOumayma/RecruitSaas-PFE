import { ref } from 'vue'
import axios from 'axios'

const API = 'https://localhost:5001/api/tenant'

export function useExperts() {
  const experts = ref([])
  const loading = ref(false)

  const fetchExperts = async (companyId) => {
    loading.value = true
    const res = await axios.get(`${API}/companies/${companyId}/experts`)
    experts.value = res.data
    loading.value = false
  }

  const inviteExpert = async (data) => {
    await axios.post(`${API}/experts/invite`, data)
  }

  const updateExpert = async (id, data) => {
    await axios.put(`${API}/experts/${id}`, data)
  }

  const deactivateExpert = async (id) => {
    await axios.put(`${API}/experts/${id}/deactivate`)
  }

  return {
    experts,
    loading,
    fetchExperts,
    inviteExpert,
    updateExpert,
    deactivateExpert
  }
}