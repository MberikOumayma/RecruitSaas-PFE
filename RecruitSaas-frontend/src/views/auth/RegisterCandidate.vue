<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">
        <img src="/appli-logo.png" alt="TalentFlow" class="auth-brand-logo" />
      </div>
      <h1 class="auth-title">Join the Talent Pool</h1>
      <p class="auth-subtitle">Join 10,000+ candidates finding their next big opportunity.</p>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label class="form-label">Full Name</label>
          <div class="input-wrapper">
            <span class="input-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </span>
            <input v-model="form.fullName" type="text" class="form-input" placeholder="e.g. John Doe" required />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Professional Email</label>
          <div class="input-wrapper">
            <span class="input-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
              </svg>
            </span>
            <input v-model="form.email" type="email" class="form-input" placeholder="email@example.com" required />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Password</label>
            <div class="input-wrapper">
              <span class="input-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </span>
              <input v-model="form.password" :type="showPassword ? 'text' : 'password'" class="form-input" placeholder="••••••••" required />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Confirm Password</label>
            <div class="input-wrapper">
              <span class="input-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </span>
              <input v-model="form.confirmPassword" :type="showPassword ? 'text' : 'password'" class="form-input" placeholder="••••••••" required />
            </div>
          </div>
        </div>

        <p class="hint-text">Use at least 8 characters with a mix of letters and numbers.</p>


        <p class="divider-label">OR CONNECT WITH</p>
        <div class="social-connect-grid">
          <button
            v-for="p in ['linkedin', 'google', 'facebook']"
            :key="p"
            type="button"
            class="social-connect-btn"
            :class="{ 'social-connect-btn--disabled': !isProviderReady(p) }"
            :title="providerHint(p)"
            @click="socialLogin(p)"
          >
            <span v-if="p === 'linkedin'" class="social-connect-icon linkedin-bg">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="white"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>
            </span>
            <span v-else-if="p === 'google'" class="social-connect-icon">
              <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            </span>
            <span v-else class="social-connect-icon facebook-bg">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="white"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
            </span>
            <span>{{ p === 'google' ? 'Google' : p === 'facebook' ? 'Facebook' : 'LinkedIn' }}</span>
          </button>
        </div>

        <p v-if="error" class="msg-error">{{ error }}</p>
        <p v-if="successMessage" class="msg-success">{{ successMessage }}</p>

        <button type="submit" :disabled="loading" class="btn-primary btn-full">
          {{ loading ? 'Creating...' : 'Create Candidate Profile →' }}
        </button>

        <p class="terms-text">
          By signing up, you agree to our <a href="#" class="link">Terms of Service</a> and <a href="#" class="link">Privacy Policy</a>.
        </p>
      </form>

      <div class="trust-bar">
        <span class="trust-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4A6CF7" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>Secure & Encrypted
        </span>
        <span class="trust-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
          </svg>10k+ Active Candidates
        </span>
        <span class="trust-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>Top Recruiters
        </span>
      </div>
    </div>

    <div v-if="showSuccess" class="modal-overlay" @click="goToLogin">
      <div class="modal" @click.stop>
        <div class="modal-icon success-icon">✓</div>
        <h2>Account Created!</h2>
        <p>Your candidate profile has been created successfully.</p>
        <button class="btn-primary" @click="goToLogin">Go to Login</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../../services/api"
import { loginWithProvider, fetchConfiguredProviders, getProviderLabel } from "../../services/socialAuth"

export default {
  name: "RegisterCandidate",
  data() {
    return {
      form: {
        fullName: "",
        email: "",
        password: "",
        confirmPassword: ""
      },
      error: null,
      successMessage: null,
      loading: false,
      showSuccess: false,
      showPassword: false,
      configuredProviders: [],
      providersLoaded: false
    }
  },
  async mounted() {
    this.configuredProviders = await fetchConfiguredProviders()
    this.providersLoaded = true
  },
  methods: {
    isProviderReady(provider) {
      if (!this.providersLoaded) return true
      return this.configuredProviders.includes(provider)
    },
    providerHint(provider) {
      if (this.isProviderReady(provider)) return `S'inscrire avec ${getProviderLabel(provider)}`
      return `${getProviderLabel(provider)} : configurez appsettings.SocialAuth.json`
    },
    socialLogin(provider) {
      if (!this.isProviderReady(provider)) {
        this.error = `Connexion ${getProviderLabel(provider)} non configurée sur le serveur.`
        return
      }
      loginWithProvider(provider, "/dashboard")
    },
    async handleSubmit() {
      try {
        this.error = null
        this.successMessage = null
        this.loading = true

        // ✅ Validations frontend
        if (!this.form.fullName || !this.form.email || !this.form.password || !this.form.confirmPassword) {
          this.error = "All fields are required"
          return
        }
        if (this.form.password !== this.form.confirmPassword) {
          this.error = "Passwords do not match"
          return
        }
        if (this.form.password.length < 8) {
          this.error = "Password must be at least 8 characters"
          return
        }

        // ✅ Découpage du nom complet : "John Doe" → Nom="Doe", mais on envoie le nom complet dans "Nom"
        // Le backend attend : Nom (string), Email, MotDePasse, ConfirmMotDePasse
        const payload = {
          Nom: this.form.fullName.trim(),           // ✅ Correspond à DTO.Nom
          Email: this.form.email.trim(),            // ✅ Correspond à DTO.Email
          MotDePasse: this.form.password,           // ✅ Correspond à DTO.MotDePasse (PascalCase)
          ConfirmMotDePasse: this.form.confirmPassword  // ✅ OBLIGATOIRE pour la validation [Compare]
          // ❌ On retire "prenom", "role" : non attendus par RegisterDto
          // Le backend gérera le rôle par défaut ou via une autre logique
        }

        // ✅ Envoi avec l'instance api configurée (baseURL déjà définie)
        await api.post("/auth/register", payload)

        this.successMessage = "Registration done successfully 🎉"
        this.showSuccess = true
      } catch (err) {
        console.error("❌ Registration error:", err.response?.data)
        this.error = err.response?.data?.errors 
          ? Object.values(err.response.data.errors).flat().join(", ")
          : err.response?.data?.title 
          ? err.response.data.title 
          : "Registration failed. Please try again."
      } finally {
        this.loading = false
      }
    },
    goToLogin() {
      this.$router.push("/login")
    }
  }
}
</script>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

/* ═══════════════════════════════════════════════
   position fixed + inset:0 = plein écran garanti
   ═══════════════════════════════════════════════ */
.auth-page {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
  background-color: #f0f2f8;
  color: #1a1d2e;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  padding: 24px;
  -webkit-font-smoothing: antialiased;
  padding: 200px 24px 24px 24px;
}

.auth-page *,
.auth-page *::before,
.auth-page *::after { box-sizing: border-box; }

.auth-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 40px 36px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 4px 20px rgba(74,108,247,0.08);
}

.auth-brand { display: flex; justify-content: center; margin-bottom: clamp(14px, 3vw, 22px); }
.auth-brand-logo {
  height: clamp(42px, 11vw, 68px);
  width: auto;
  max-width: min(300px, 90vw);
  object-fit: contain;
  display: block;
}
.auth-title { font-size: 24px; font-weight: 700; color: #1a1d2e; text-align: center; margin: 0 0 8px 0; line-height: 1.3; }
.auth-subtitle { font-size: 13px; color: #4a4f6a; text-align: center; margin: 0 0 28px 0; line-height: 1.5; }

.auth-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-label { font-size: 13px; font-weight: 600; color: #1a1d2e; display: flex; align-items: center; }

.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 12px; display: flex; align-items: center; pointer-events: none; }

.form-input {
  width: 100%;
  padding: 11px 14px 11px 38px;
  border: 1.5px solid #e5e7f0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  color: #1a1d2e;
  background: #ffffff;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-input:focus { border-color: #4A6CF7; box-shadow: 0 0 0 3px rgba(74,108,247,0.1); }
.form-input::placeholder { color: #9095b0; }

.hint-text { font-size: 11px; color: #9095b0; margin-top: 2px; }

.divider-label { text-align: center; font-size: 11px; font-weight: 700; letter-spacing: 1px; color: #9095b0; position: relative; }
.divider-label::before, .divider-label::after { content: ''; position: absolute; top: 50%; width: 35%; height: 1px; background: #e5e7f0; }
.divider-label::before { left: 0; } .divider-label::after { right: 0; }

.social-connect-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
.social-connect-btn {
  all: unset; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 14px 8px; border: 1.5px solid #e5e7f0; border-radius: 10px; cursor: pointer; font-size: 12px; font-weight: 600; color: #1a1d2e;
  transition: border-color 0.2s, background 0.2s;
}
.social-connect-btn:hover:not(.social-connect-btn--disabled) { border-color: #4A6CF7; background: #eef0fe; }
.social-connect-btn--disabled { opacity: 0.45; cursor: not-allowed; }
.social-connect-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: #f5f6fa; }
.social-connect-icon.linkedin-bg { background: #0077b5; }
.social-connect-icon.facebook-bg { background: #1877F2; }

.msg-error   { color: #dc2626; font-size: 13px; margin: 0; }
.msg-success { color: #059669; font-size: 13px; margin: 0; }

.btn-primary {
  all: unset;
  display: inline-flex; align-items: center; justify-content: center;
  background: #4A6CF7; color: #ffffff;
  padding: 13px 24px; border-radius: 8px;
  font-size: 15px; font-weight: 600; cursor: pointer; font-family: inherit;
  transition: background 0.2s, transform 0.1s;
}
.btn-primary:hover { background: #3b5de0; }
.btn-full { width: 86%; }

.terms-text { font-size: 12px; color: #9095b0; text-align: center; line-height: 1.5; margin: 0; }
.link { color: #4A6CF7; font-weight: 600; text-decoration: none; }
.link:hover { text-decoration: underline; }

.trust-bar { display: flex; justify-content: center; gap: 20px; margin-top: 16px; flex-wrap: wrap; }
.trust-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #4a4f6a; font-weight: 500; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 24px; }
.modal { background: #ffffff; border-radius: 12px; padding: 40px 36px; max-width: 380px; width: 100%; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.2); color: #1a1d2e; }
.modal h2 { font-size: 20px; font-weight: 700; margin: 0 0 8px 0; color: #1a1d2e; }
.modal p  { font-size: 14px; color: #4a4f6a; margin: 0 0 24px 0; line-height: 1.6; }
.modal-icon { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 700; margin: 0 auto 16px; }
.success-icon { background: #d1fae5; color: #059669; }

@media (max-width: 600px) {
  .auth-card { padding: 28px 20px; }
  .form-row  { grid-template-columns: 1fr; }
  .trust-bar { gap: 12px; }
  .social-connect-grid { grid-template-columns: 1fr; }
}
</style>