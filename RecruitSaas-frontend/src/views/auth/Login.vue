<template>
  <div class="auth-page">
    <div class="auth-card login-card">
      <div class="auth-brand">
        <img src="/appli-logo.png" alt="TalentFlow" class="auth-brand-logo" />
      </div>
      <h1 class="auth-title">Welcome Back</h1>
      <p class="auth-subtitle">Find your next career move</p>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label class="form-label">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2" style="margin-right:6px;vertical-align:middle"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            Email Address
          </label>
          <input v-model="form.email" type="email" class="form-input" placeholder="name@gmail.com" required />
        </div>

        <div class="form-group">
          <div class="label-row">
            <label class="form-label">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2" style="margin-right:6px;vertical-align:middle"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              Password
            </label>
            <a href="#" class="link forgot-link">Forgot password?</a>
          </div>
          <div class="input-wrapper">
            <input v-model="form.password" :type="showPassword ? 'text' : 'password'" class="form-input" placeholder="Enter your password" required />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
        </div>

        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.keepLogged" />
            <span>Keep me logged in</span>
          </label>
        </div>

        <button type="submit" class="btn-primary btn-full">Log In &nbsp;→</button>

        <div class="divider"><span>Or continue with</span></div>

        <div class="social-buttons">
          <button
            v-for="p in socialProviders"
            :key="p.id"
            type="button"
            class="btn-social"
            :class="[`btn-social-${p.id}`, { 'btn-social--disabled': !isProviderReady(p.id) }]"
            :title="providerHint(p.id)"
            @click="socialLogin(p.id)"
          >
            <span class="social-icon" v-html="p.icon" />
            <span class="social-label">{{ p.label }}</span>
          </button>
        </div>
        <p v-if="providersLoaded && configuredProviders.length === 0" class="social-hint">
          Configurez vos clés OAuth dans <code>appsettings.SocialAuth.json</code> (voir le fichier .example).
        </p>

        <p class="login-link">
          Don't have an account?
          <router-link to="/register-candidate" class="link">Register as a Candidate</router-link>
        </p>
      </form>
    </div>

    <div v-if="error" class="modal-overlay" @click="error = null">
      <div class="modal" @click.stop>
        <div class="modal-icon error-icon">✕</div>
        <h2>Login Failed</h2>
        <p>{{ error }}</p>
        <button class="btn-primary" @click="error = null">Try Again</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../../services/api"
import { authStore } from "../../stores/auth"
import { loginWithProvider, fetchConfiguredProviders, getProviderLabel } from "../../services/socialAuth"

const SOCIAL_ICONS = {
  google: '<svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>',
  facebook: '<svg width="18" height="18" viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
  linkedin: '<svg width="18" height="18" viewBox="0 0 24 24" fill="#0077b5"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>'
}

export default {
  data() {
    return {
      form: { email: '', password: '', keepLogged: false },
      showPassword: false,
      error: null,
      configuredProviders: [],
      providersLoaded: false,
      socialProviders: [
        { id: 'google', label: 'Google', icon: SOCIAL_ICONS.google },
        { id: 'facebook', label: 'Facebook', icon: SOCIAL_ICONS.facebook },
        { id: 'linkedin', label: 'LinkedIn', icon: SOCIAL_ICONS.linkedin }
      ]
    }
  },
  async mounted() {
    const oauthError = this.$route.query.error
    if (oauthError) {
      this.error = typeof oauthError === "string" ? decodeURIComponent(oauthError) : "Connexion sociale échouée."
    }
    this.configuredProviders = await fetchConfiguredProviders()
    this.providersLoaded = true
  },
  methods: {
    isProviderReady(provider) {
      if (!this.providersLoaded) return true
      return this.configuredProviders.includes(provider)
    },
    providerHint(provider) {
      if (this.isProviderReady(provider)) return `Se connecter avec ${getProviderLabel(provider)}`
      return `${getProviderLabel(provider)} : ajoutez vos clés dans appsettings.SocialAuth.json`
    },
    socialLogin(provider) {
      if (!this.isProviderReady(provider)) {
        this.error = `Connexion ${getProviderLabel(provider)} non configurée. Copiez appsettings.SocialAuth.json.example vers appsettings.SocialAuth.json et redémarrez l'API.`
        return
      }
      const redirect = this.$route.query.redirect
        ? decodeURIComponent(this.$route.query.redirect)
        : "/dashboard"
      loginWithProvider(provider, redirect)
    },
    decodeToken(token) {
      try {
        const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
        return JSON.parse(
          decodeURIComponent(
            atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')
          )
        )
      } catch (e) { return {} }
    },
    async handleSubmit() {
      try {
        const res = await api.post("/auth/login", {
          email: this.form.email,
          motDePasse: this.form.password
        })

        const token = res.data.token
        authStore.setToken(token, res.data)
        await authStore.fetchCurrentUser()
        localStorage.setItem("token", token)
        localStorage.setItem("username", res.data.fullName || res.data.userName || "")
        localStorage.setItem("userEmail", res.data.email || this.form.email)

        const decoded = this.decodeToken(token)
        const role = decoded.role ||
          decoded["http://schemas.microsoft.com/ws/2008/06/identity/claims/role"]

        // ── Redirect vers la page demandée avant le login ──
        const redirect = this.$route.query.redirect
        if (redirect) {
          this.$router.push(decodeURIComponent(redirect))
          return
        }

        // ── Redirect par défaut selon le rôle ──
        if      (role === "Tenant")   this.$router.push("/recruiter/dashboard")
        else if (role === "Expert")   this.$router.push("/expert/dashboard")
        else if (role === "Candidat") this.$router.push("/dashboard")
        else if (role === "Admin")    this.$router.push("/admin/dashboard")
        else                          this.$router.push("/")

      } catch (err) {
        this.error = err.response?.data || "Login failed"
      }
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
.auth-page { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; overflow-y:auto; background-color:#f0f2f8; color:#1a1d2e; font-family:'DM Sans',-apple-system,BlinkMacSystemFont,sans-serif; font-size:16px; line-height:1.5; padding:24px; -webkit-font-smoothing:antialiased; }
.auth-page *, .auth-page *::before, .auth-page *::after { box-sizing:border-box; }
.auth-card { background:#ffffff; border-radius:12px; padding:40px 36px; width:100%; max-width:400px; box-shadow:0 4px 20px rgba(74,108,247,0.08); }
.login-card { max-width:360px; width:360px; flex-shrink:0; }
.auth-brand { display: flex; justify-content: center; margin-bottom: clamp(14px, 3vw, 22px); }
.auth-brand-logo {
  height: clamp(42px, 11vw, 68px);
  width: auto;
  max-width: min(300px, 90vw);
  object-fit: contain;
  display: block;
}
.auth-title { font-size:24px; font-weight:700; color:#1a1d2e; text-align:center; margin:0 0 8px; line-height:1.3; }
.auth-subtitle { font-size:13px; color:#4a4f6a; text-align:center; margin:0 0 28px; line-height:1.5; }
.auth-form { display:flex; flex-direction:column; gap:16px; }
.form-group { display:flex; flex-direction:column; gap:6px; }
.form-label { font-size:13px; font-weight:600; color:#1a1d2e; display:flex; align-items:center; }
.label-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:2px; }
.forgot-link { font-size:12px; color:#4A6CF7; font-weight:500; text-decoration:none; }
.forgot-link:hover { text-decoration:underline; }
.input-wrapper { position:relative; display:flex; align-items:center; }
.form-input { width:100%; padding:11px 14px; border:1.5px solid #e5e7f0; border-radius:8px; font-size:14px; font-family:inherit; color:#1a1d2e; background:#ffffff; outline:none; transition:border-color 0.2s,box-shadow 0.2s; }
.form-input:focus { border-color:#4A6CF7; box-shadow:0 0 0 3px rgba(74,108,247,0.1); }
.form-input::placeholder { color:#9095b0; }
.toggle-password { all:unset; position:absolute; right:12px; cursor:pointer; display:flex; align-items:center; }
.checkbox-group { flex-direction:row; align-items:center; }
.checkbox-label { display:flex; align-items:center; gap:8px; font-size:13px; color:#4a4f6a; cursor:pointer; }
.checkbox-label input[type="checkbox"] { accent-color:#4A6CF7; cursor:pointer; flex-shrink:0; }
.btn-primary { all:unset; display:inline-flex; align-items:center; justify-content:center; background:#4A6CF7; color:#ffffff; padding:13px 0; border-radius:8px; font-size:15px; font-weight:600; cursor:pointer; font-family:inherit; transition:background 0.2s,transform 0.1s; }
.btn-primary:hover { background:#3b5de0; }
.btn-primary:active { transform:scale(0.99); }
.btn-full { width:100%; }
.divider { display:flex; align-items:center; gap:12px; color:#9095b0; font-size:13px; }
.divider::before, .divider::after { content:''; flex:1; height:1px; background:#e5e7f0; }
.social-buttons { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.btn-social { all:unset; box-sizing:border-box; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; padding:10px 6px; min-height:72px; border:1.5px solid #e5e7f0; border-radius:8px; font-size:11px; font-weight:600; color:#1a1d2e; background:#ffffff; cursor:pointer; font-family:inherit; transition:border-color 0.2s,background 0.2s,opacity 0.2s; }
.btn-social:hover:not(.btn-social--disabled) { border-color:#4A6CF7; background:#eef0fe; }
.btn-social-linkedin:hover:not(.btn-social--disabled) { border-color:#0077b5; background:#e8f4fc; }
.btn-social--disabled { opacity:0.45; cursor:not-allowed; }
.social-icon { display:flex; align-items:center; justify-content:center; line-height:0; }
.social-label { line-height:1.2; text-align:center; }
.social-hint { font-size:11px; color:#9095b0; text-align:center; margin:0; line-height:1.4; }
.social-hint code { font-size:10px; background:#f0f2f8; padding:2px 4px; border-radius:4px; }
.login-link { font-size:14px; color:#4a4f6a; text-align:center; margin:0; }
.link { color:#4A6CF7; font-weight:600; text-decoration:none; }
.link:hover { text-decoration:underline; }
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.45); display:flex; align-items:center; justify-content:center; z-index:100; padding:24px; }
.modal { background:#ffffff; border-radius:12px; padding:40px 36px; max-width:380px; width:100%; text-align:center; box-shadow:0 20px 60px rgba(0,0,0,0.2); color:#1a1d2e; }
.modal h2 { font-size:20px; font-weight:700; margin:0 0 8px; color:#1a1d2e; }
.modal p  { font-size:14px; color:#4a4f6a; margin:0 0 24px; line-height:1.6; }
.modal-icon { width:56px; height:56px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:700; margin:0 auto 16px; }
.error-icon { background:#fee2e2; color:#dc2626; }
@media (max-width:600px) { .auth-card { padding:28px 20px; } .social-buttons { grid-template-columns:1fr; } .login-card { max-width:100%; width:100%; } }
</style>