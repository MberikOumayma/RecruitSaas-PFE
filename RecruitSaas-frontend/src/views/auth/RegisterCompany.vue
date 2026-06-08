<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">
        <img src="/appli-logo.png" alt="TalentFlow" class="auth-brand-logo" />
      </div>
      <h1 class="auth-title">Register your company</h1>
      <p class="auth-subtitle">Scale your business with our professional suite of enterprise tools.</p>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label class="form-label">Company Name</label>
          <input v-model="form.companyName" type="text" class="form-input" placeholder="Enter your company name" required />
        </div>
        <div class="form-group">
          <label class="form-label">CEO Name</label>
          <input v-model="form.tenantName" type="text" class="form-input" placeholder="Enter CEO name" required />
        </div>
        <div class="form-group">
          <label class="form-label">RNE</label>
          <input v-model="form.rne" type="text" class="form-input" placeholder="Enter National Registry number" required />
        </div>
        <div class="form-group">
          <label class="form-label">Work Email</label>
          <input v-model="form.email" type="email" class="form-input" placeholder="name@company.com" required />
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <div class="input-wrapper">
            <input v-model="form.password" :type="showPassword ? 'text' : 'password'" class="form-input pw-input" placeholder="Min. 8 characters" required />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
          <p class="hint-text">Include at least one number and a symbol.</p>
        </div>
        <div class="form-group">
          <label class="form-label">Industry</label>
          <select v-model="form.industry" class="form-select" required>
            <option value="">Select industry</option>
            <option value="tech">Technology</option>
            <option value="finance">Finance</option>
            <option value="health">Healthcare</option>
            <option value="education">Education</option>
            <option value="retail">Retail</option>
            <option value="manufacturing">Manufacturing</option>
            <option value="consulting">Consulting</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.agreed" required />
            <span>I agree to the Terms of Service and Privacy Policy.</span>
          </label>
        </div>

        <p v-if="error" class="msg-error">{{ error }}</p>
        <button type="submit" class="btn-primary btn-full">Create Account</button>
      </form>
    </div>

    <div v-if="showPending" class="modal-overlay">
      <div class="modal">
        <div class="modal-icon pending-icon">⏳</div>
        <h2>Registration Submitted!</h2>
        <p>Your company registration is under review.</p>
        <button class="btn-primary" @click="$router.push('/')">Back to Home</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../../services/api"

export default {
  data() {
    return {
      form: {
        companyName: '',
        tenantName: '',
        rne: '',
        email: '',
        password: '',
        industry: '',
        agreed: false
      },
      showPassword: false,
      showPending: false,
      error: null
    }
  },
  methods: {
    async handleSubmit() {
      try {
        // ✅ Payload adapté EXACTEMENT au CompanyRegisterDto du backend
        await api.post("/auth/company/register", {
          TenantName: this.form.tenantName,      // ✅ Correspond à DTO.TenantName
          CompanyName: this.form.companyName,     // ✅ Correspond à DTO.CompanyName
          RNE: this.form.rne,                     // ✅ Correspond à DTO.RNE
          WorkEmail: this.form.email,             // ✅ Correspond à DTO.WorkEmail
          Password: this.form.password,           // ✅ Correspond à DTO.Password
          Industry: this.form.industry            // ✅ "Industry" et NON "Secteur"
          // ❌ On retire Prenom, Description, LogoUrl : non attendus par le DTO
          // Le backend gérera les valeurs par défaut pour Description/LogoUrl si besoin
        })
        this.showPending = true
      } catch (err) {
        console.error("Registration error:", err)
        this.error = err.response?.data?.message || err.response?.data || "Erreur lors de l'envoi"
      }
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
  align-items: flex-start;
  justify-content: center;
  overflow-y: auto;
  background-color: #f0f2f8;
  color: #1a1d2e;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  padding: 24px;
  -webkit-font-smoothing: antialiased;
  padding: 60px 24px 24px 24px;
}

.auth-page *,
.auth-page *::before,
.auth-page *::after { box-sizing: border-box; }

.auth-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 40px 36px;
  width: 100%;
  max-width: 450px;
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
.form-label { font-size: 13px; font-weight: 600; color: #1a1d2e; text-align: left;}

.input-wrapper { position: relative; display: flex; align-items: center; }

.form-input {
  width: 100%;
  padding: 11px 14px;
  border: 1.5px solid #e5e7f0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  color: #1a1d2e;
  background: #ffffff;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.pw-input { padding-right: 40px; }
.form-input:focus { border-color: #4A6CF7; box-shadow: 0 0 0 3px rgba(74,108,247,0.1); }
.form-input::placeholder { color: #9095b0; }

.toggle-password { all: unset; position: absolute; right: 12px; cursor: pointer; display: flex; align-items: center; }

.form-select {
  width: 100%; padding: 11px 14px;
  border: 1.5px solid #e5e7f0; border-radius: 8px;
  font-size: 14px; font-family: inherit; color: #1a1d2e;
  background: #ffffff; appearance: none; cursor: pointer; outline: none;
  transition: border-color 0.2s;
}
.form-select:focus { border-color: #4A6CF7; box-shadow: 0 0 0 3px rgba(74,108,247,0.1); }

.hint-text { font-size: 11px; color: #9095b0; margin-top: 2px; }

.checkbox-group { flex-direction: row; align-items: flex-start; }
.checkbox-label { display: flex; align-items: flex-start; gap: 8px; font-size: 13px; color: #4a4f6a; cursor: pointer; }
.checkbox-label input[type="checkbox"] { margin-top: 2px; accent-color: #4A6CF7; cursor: pointer; flex-shrink: 0; }

.msg-error { color: #dc2626; font-size: 13px; margin: 0; }

.btn-primary {
  all: unset;
  display: inline-flex; align-items: center; justify-content: center;
  background: #4A6CF7; color: #ffffff;
  padding: 13px 24px; border-radius: 8px;
  font-size: 15px; font-weight: 600; cursor: pointer; font-family: inherit;
  transition: background 0.2s, transform 0.1s;
}
.btn-primary:hover { background: #3b5de0; }
.btn-full { width: 87%; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 24px; }
.modal { background: #ffffff; border-radius: 12px; padding: 40px 36px; max-width: 380px; width: 100%; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.2); color: #1a1d2e; }
.modal h2 { font-size: 20px; font-weight: 700; margin: 0 0 8px 0; color: #1a1d2e; }
.modal p  { font-size: 14px; color: #4a4f6a; margin: 0 0 24px 0; line-height: 1.6; }
.modal-icon { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 700; margin: 0 auto 16px; }
.pending-icon { background: #fef3c7; color: #d97706; }

@media (max-width: 600px) {
  .auth-card { padding: 28px 20px; }
}
</style>