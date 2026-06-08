<template>
  <div class="auth-page">
    <div class="auth-card login-card">
      <div v-if="error" class="status-block">
        <div class="modal-icon error-icon">✕</div>
        <h1 class="auth-title">Connexion échouée</h1>
        <p class="auth-subtitle">{{ error }}</p>
        <router-link to="/login" class="btn-primary btn-full">Retour à la connexion</router-link>
      </div>
      <div v-else class="status-block">
        <div class="spinner" />
        <h1 class="auth-title">Connexion en cours…</h1>
        <p class="auth-subtitle">Redirection vers votre espace</p>
      </div>
    </div>
  </div>
</template>

<script>
import { authStore } from "../../stores/auth"

export default {
  name: "AuthCallback",
  data() {
    return { error: null }
  },
  mounted() {
    const params = new URLSearchParams(window.location.search)
    const err = params.get("error")
    if (err) {
      this.error = decodeURIComponent(err)
      return
    }

    const token = params.get("token")
    if (!token) {
      this.error = "Jeton d'authentification manquant."
      return
    }

    const userName = params.get("userName") || "User"
    const returnUrl = params.get("returnUrl") || "/dashboard"

    authStore.setToken(decodeURIComponent(token), { userName: decodeURIComponent(userName) })
    authStore.fetchCurrentUser().then(() => {
      this.redirectAfterAuth(decodeURIComponent(returnUrl))
    })
  },
  methods: {
    redirectAfterAuth(returnUrl) {
      const role = authStore.user?.role
      let target = returnUrl

      if (target === "/dashboard" || target === "/") {
        if (role === "Tenant") target = "/recruiter/dashboard"
        else if (role === "Expert") target = "/expert/dashboard"
        else if (role === "Admin") target = "/admin/dashboard"
        else if (role === "Candidat") target = "/dashboard"
      }

      this.$router.replace(target)
    },
  },
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
.auth-page { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; background:#f0f2f8; font-family:'DM Sans',sans-serif; padding:24px; }
.auth-card { background:#fff; border-radius:12px; padding:40px 36px; width:100%; max-width:400px; box-shadow:0 4px 20px rgba(74,108,247,0.08); text-align:center; }
.auth-title { font-size:22px; font-weight:700; margin:16px 0 8px; color:#1a1d2e; }
.auth-subtitle { font-size:14px; color:#4a4f6a; margin:0 0 24px; line-height:1.5; }
.status-block { display:flex; flex-direction:column; align-items:center; }
.spinner { width:40px; height:40px; border:3px solid #e5e7f0; border-top-color:#4A6CF7; border-radius:50%; animation:spin 0.8s linear infinite; margin-bottom:8px; }
@keyframes spin { to { transform:rotate(360deg); } }
.modal-icon { width:56px; height:56px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:700; }
.error-icon { background:#fee2e2; color:#dc2626; }
.btn-primary { display:inline-flex; align-items:center; justify-content:center; background:#4A6CF7; color:#fff; padding:12px 24px; border-radius:8px; font-weight:600; text-decoration:none; margin-top:8px; }
.btn-full { width:100%; box-sizing:border-box; }
</style>
