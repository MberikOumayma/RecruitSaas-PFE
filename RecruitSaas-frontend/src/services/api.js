import axios from "axios"

const API_ORIGIN = import.meta.env.VITE_API_ORIGIN || "http://localhost:5202"

const api = axios.create({
  baseURL: `${API_ORIGIN}/api`,
})
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token")

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)
export default api
