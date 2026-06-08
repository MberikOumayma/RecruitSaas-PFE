<template>
  <div class="app-layout">
    <AppSidebar />

    <main class="main-content">
      <div class="profile-page">

        <!-- ── PAGE HEADER ── -->
        <div class="page-header">
          <div class="header-left">
            <div class="header-icon">
              <BuildingIcon :size="22" />
            </div>
            <div>
              <h1 class="page-title">Company Owner's Profile</h1>
              <p class="page-subtitle">Manage your company information and recruiter account</p>
            </div>
          </div>
          <button class="btn-save" @click="saveProfile" :disabled="saving">
            <SaveIcon :size="15" />
            <span>{{ saving ? 'Saving…' : 'Save Changes' }}</span>
          </button>
        </div>

        <!-- ── ALERTS ── -->
        <transition name="slide-down">
          <div v-if="successMsg" class="alert alert-success">
            <CheckCircleIcon :size="15" />
            <span>{{ successMsg }}</span>
          </div>
        </transition>
        <transition name="slide-down">
          <div v-if="errorMsg" class="alert alert-error">
            <AlertCircleIcon :size="15" />
            <span>{{ errorMsg }}</span>
          </div>
        </transition>

        <!-- ── BODY GRID ── -->
        <div class="profile-grid">

          <!-- ═══ LEFT COLUMN ═══ -->
          <div class="left-col">

            <!-- Company logo card -->
            <div class="card avatar-card">
              <div class="logo-wrapper">
                <img :src="displayLogoUrl" class="company-logo" alt="Company Logo" />
                <input
                  ref="logoInput"
                  type="file"
                  accept="image/png,image/jpeg,image/webp,image/svg+xml"
                  style="display:none"
                  @change="onLogoChange"
                />
                <button class="logo-edit-btn" title="Change logo" @click="$refs.logoInput.click()">
                  <CameraIcon :size="13" />
                </button>
              </div>
              <p class="company-name">{{ form.fullName || '—' }}</p>
              <span class="role-badge">
                <BuildingIcon :size="10" />
                Recruiter
              </span>

              <div class="strength-wrap">
                <div class="strength-header">
                  <span>Profile Completeness</span>
                  <span class="strength-pct" :style="{ color: strengthColor }">{{ profileStrength }}%</span>
                </div>
                <div class="strength-track">
                  <div
                    class="strength-bar"
                    :style="{ width: profileStrength + '%', background: strengthColor }"
                  ></div>
                </div>
                <p class="strength-hint">{{ strengthHint }}</p>
              </div>
            </div>

            <!-- Quick info -->
            <div class="card info-card">
              <p class="section-label">COMPANY INFO</p>
              <div class="info-item">
                <MailIcon :size="13" class="info-icon" />
                <span>{{ form.email || 'Not set' }}</span>
              </div>
              <div class="info-item">
                <PhoneIcon :size="13" class="info-icon" />
                <span>{{ form.phone || 'Not set' }}</span>
              </div>
              <div class="info-item">
                <GlobeIcon :size="13" class="info-icon" />
                <span>{{ form.website || 'Website not set' }}</span>
              </div>
            </div>

          </div>

          <!-- ═══ RIGHT COLUMN ═══ -->
          <div class="right-col">

            <!-- RECRUITER ACCOUNT -->
            <div class="card">
              <div class="card-header-row">
                <UserCircleIcon :size="15" class="card-header-icon" />
                <p class="section-label">RECRUITER ACCOUNT</p>
              </div>
              <div class="form-grid">
                <div class="field">
                  <label>Full Name <span class="req">*</span></label>
                  <div class="input-wrap">
                    <UserIcon :size="14" class="input-icon" />
                    <input v-model="form.fullName" placeholder="Your full name" />
                  </div>
                </div>
                <div class="field">
                  <label>Email <span class="req">*</span></label>
                  <div class="input-wrap">
                    <MailIcon :size="14" class="input-icon" />
                    <input v-model="form.email" type="email" placeholder="you@company.com" />
                  </div>
                </div>
                <div class="field">
                  <label>Job Title</label>
                  <div class="input-wrap">
                    <BriefcaseIcon :size="14" class="input-icon" />
                    <input v-model="form.jobTitle" placeholder="e.g. HR Manager, Talent Lead" />
                  </div>
                </div>
                <div class="field">
                  <label>Phone</label>
                  <div class="input-wrap">
                    <PhoneIcon :size="14" class="input-icon" />
                    <input v-model="form.phone" placeholder="+216 00 000 000" />
                  </div>
                </div>
              </div>
            </div>

            <!-- ONLINE PRESENCE -->
            <div class="card">
              <div class="card-header-row">
                <GlobeIcon :size="15" class="card-header-icon" />
                <p class="section-label">ONLINE PRESENCE</p>
              </div>
              <div class="form-grid">
                <div class="field span-2">
                  <label>Company Website</label>
                  <div class="input-wrap">
                    <GlobeIcon :size="14" class="input-icon" />
                    <input v-model="form.website" placeholder="https://yourcompany.com" />
                  </div>
                </div>
                <div class="field">
                  <label>LinkedIn Company Page</label>
                  <div class="input-wrap">
                    <LinkedinIcon :size="14" class="input-icon" />
                    <input v-model="form.linkedin" placeholder="https://linkedin.com/company/…" />
                  </div>
                </div>
                <div class="field">
                  <label>Twitter / X</label>
                  <div class="input-wrap">
                    <AtSignIcon :size="14" class="input-icon" />
                    <input v-model="form.twitter" placeholder="https://twitter.com/…" />
                  </div>
                </div>
              </div>
            </div>

            
            <!-- ══════════════════════════════════════════════════════ -->
            <!-- CHANGE PASSWORD — section ajoutée                     -->
            <!-- ══════════════════════════════════════════════════════ -->
            <div class="card pwd-card">
              <div class="card-header-row">
                <LockIcon :size="15" class="card-header-icon" />
                <p class="section-label">CHANGE PASSWORD</p>
              </div>

              <!-- Alert succès / erreur propre à la section mot de passe -->
              <transition name="slide-down">
                <div v-if="pwdSuccess" class="alert alert-success pwd-alert">
                  <CheckCircleIcon :size="15" />
                  <span>{{ pwdSuccess }}</span>
                </div>
              </transition>
              <transition name="slide-down">
                <div v-if="pwdError" class="alert alert-error pwd-alert">
                  <AlertCircleIcon :size="15" />
                  <span>{{ pwdError }}</span>
                </div>
              </transition>

              <div class="form-grid">
                <!-- Mot de passe actuel -->
                <div class="field span-2">
                  <label>Current Password <span class="req">*</span></label>
                  <div class="input-wrap">
                    <LockIcon :size="14" class="input-icon" />
                    <input
                      v-model="pwd.current"
                      :type="showPwd.current ? 'text' : 'password'"
                      placeholder="Enter your current password"
                      autocomplete="current-password"
                    />
                    <button
                      type="button"
                      class="eye-btn"
                      @click="showPwd.current = !showPwd.current"
                      :title="showPwd.current ? 'Hide' : 'Show'"
                    >
                      <EyeOffIcon v-if="showPwd.current" :size="15" />
                      <EyeIcon v-else :size="15" />
                    </button>
                  </div>
                </div>

                <!-- Nouveau mot de passe -->
                <div class="field">
                  <label>New Password <span class="req">*</span></label>
                  <div class="input-wrap">
                    <LockIcon :size="14" class="input-icon" />
                    <input
                      v-model="pwd.new"
                      :type="showPwd.new ? 'text' : 'password'"
                      placeholder="Min. 8 characters"
                      autocomplete="new-password"
                    />
                    <button
                      type="button"
                      class="eye-btn"
                      @click="showPwd.new = !showPwd.new"
                    >
                      <EyeOffIcon v-if="showPwd.new" :size="15" />
                      <EyeIcon v-else :size="15" />
                    </button>
                  </div>
                  <!-- Indicateur de force -->
                  <div v-if="pwd.new" class="pwd-strength-wrap">
                    <div class="pwd-strength-track">
                      <div
                        class="pwd-strength-bar"
                        :style="{ width: pwdStrength.pct + '%', background: pwdStrength.color }"
                      ></div>
                    </div>
                    <span class="pwd-strength-label" :style="{ color: pwdStrength.color }">
                      {{ pwdStrength.label }}
                    </span>
                  </div>
                </div>

                <!-- Confirmer nouveau mot de passe -->
                <div class="field">
                  <label>Confirm New Password <span class="req">*</span></label>
                  <div class="input-wrap" :class="{ 'input-mismatch': pwd.confirm && pwd.new !== pwd.confirm }">
                    <LockIcon :size="14" class="input-icon" />
                    <input
                      v-model="pwd.confirm"
                      :type="showPwd.confirm ? 'text' : 'password'"
                      placeholder="Repeat new password"
                      autocomplete="new-password"
                    />
                    <button
                      type="button"
                      class="eye-btn"
                      @click="showPwd.confirm = !showPwd.confirm"
                    >
                      <EyeOffIcon v-if="showPwd.confirm" :size="15" />
                      <EyeIcon v-else :size="15" />
                    </button>
                  </div>
                  <p v-if="pwd.confirm && pwd.new !== pwd.confirm" class="field-error">
                    Passwords do not match.
                  </p>
                </div>
              </div>

              <!-- Bouton changer mot de passe -->
              <div class="pwd-footer">
                <button
                  class="btn-change-pwd"
                  @click="changePassword"
                  :disabled="pwdSaving || !canSubmitPwd"
                >
                  <LockIcon :size="14" />
                  {{ pwdSaving ? 'Updating…' : 'Update Password' }}
                </button>
              </div>
            </div>
            <!-- ══════════════════════════════════════════════════════ -->

          </div>
        </div>
      </div>
    </main>

    <!-- DELETE MODAL -->
    <transition name="modal-fade">
      <div v-if="confirmDelete" class="modal-backdrop" @click.self="confirmDelete = false">
        <div class="modal">
          <div class="modal-icon-wrap">
            <AlertTriangleIcon :size="28" />
          </div>
          <h3>Delete company account?</h3>
          <p>All job postings, applications, and company data will be permanently erased. This cannot be undone.</p>
          <div class="modal-btns">
            <button class="btn-ghost" @click="confirmDelete = false">Cancel</button>
            <button class="btn-delete">Yes, Delete</button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script>
import AppSidebar from '@/components/layout/AppSidebar.vue'
import {
  SaveIcon, CameraIcon, MailIcon, PhoneIcon, MapPinIcon,
  BriefcaseIcon, GlobeIcon, LinkedinIcon,
  CheckCircleIcon, AlertCircleIcon, AlertTriangleIcon,
  UserIcon, UserCircleIcon, LockIcon, ZapIcon,
  BuildingIcon, UsersIcon, CalendarIcon,
  AtSignIcon, TargetIcon,
  EyeIcon, EyeOffIcon          // ← AJOUTÉ
} from 'lucide-vue-next'

const API_BASE = 'http://localhost:5202'

export default {
  name: 'TenantProfileView',
  components: {
    AppSidebar,
    SaveIcon, CameraIcon, MailIcon, PhoneIcon, MapPinIcon,
    BriefcaseIcon, GlobeIcon, LinkedinIcon,
    CheckCircleIcon, AlertCircleIcon, AlertTriangleIcon,
    UserIcon, UserCircleIcon, LockIcon, ZapIcon,
    BuildingIcon, UsersIcon, CalendarIcon,
    AtSignIcon, TargetIcon,
    EyeIcon, EyeOffIcon          // ← AJOUTÉ
  },

  data() {
    return {
      saving: false,
      successMsg: '',
      errorMsg: '',
      confirmDelete: false,
      techInput: '',
      defaultLogo: 'https://via.placeholder.com/88x88?text=Logo',
      workTypes: ['Full-time', 'Part-time', 'Remote', 'Hybrid', 'Internship', 'Freelance'],
      hiringOptions: [
        { value: 'actively',  label: 'Actively Hiring', color: 'dot-green'  },
        { value: 'sometimes', label: 'Occasionally',    color: 'dot-orange' },
        { value: 'paused',    label: 'Paused',          color: 'dot-gray'   },
      ],
      form: {
        tenantName: '', companyName: '', industry: '', companySize: '',
        foundedYear: '', location: '', description: '', logoUrl: '',
        fullName: '', email: '', jobTitle: '', phone: '',
        website: '', linkedin: '', twitter: '',
        hiringStatus: 'actively', workTypes: [], techStack: [],
        activeJobs: 0, totalHires: 0,
      },
      localLogoPreview: null,

      // ── Mot de passe ────────────────────────────────────────────
      pwd: { current: '', new: '', confirm: '' },
      showPwd: { current: false, new: false, confirm: false },
      pwdSaving: false,
      pwdSuccess: '',
      pwdError: '',
    }
  },

  computed: {
    displayLogoUrl() {
      if (this.localLogoPreview) return this.localLogoPreview
      if (this.form.logoUrl) {
        if (this.form.logoUrl.startsWith('/')) return `${API_BASE}${this.form.logoUrl}`
        return this.form.logoUrl
      }
      return this.defaultLogo
    },

    profileStrength() {
      const fields = ['companyName', 'industry', 'companySize', 'location', 'description', 'website', 'fullName', 'email', 'jobTitle']
      const filled = fields.filter(f => this.form[f]?.trim()).length
      const hasStack = this.form.techStack?.length > 0 ? 1 : 0
      return Math.round(((filled + hasStack) / (fields.length + 1)) * 100)
    },

    strengthColor() {
      if (this.profileStrength >= 80) return '#10b981'
      if (this.profileStrength >= 50) return '#f59e0b'
      return '#ef4444'
    },

    strengthHint() {
      if (this.profileStrength >= 80) return 'Great profile! Candidates will find you easily.'
      if (this.profileStrength >= 50) return 'Add more details to attract better candidates.'
      return 'Complete your company profile to start hiring.'
    },

    // ── Force du mot de passe ──────────────────────────────────────
    pwdStrength() {
      const p = this.pwd.new
      if (!p) return { pct: 0, color: '#e2e8f0', label: '' }
      let score = 0
      if (p.length >= 8)              score++
      if (p.length >= 12)             score++
      if (/[A-Z]/.test(p))           score++
      if (/[0-9]/.test(p))           score++
      if (/[^A-Za-z0-9]/.test(p))   score++

      if (score <= 1) return { pct: 20,  color: '#ef4444', label: 'Very weak'  }
      if (score === 2) return { pct: 40,  color: '#f97316', label: 'Weak'       }
      if (score === 3) return { pct: 60,  color: '#f59e0b', label: 'Fair'       }
      if (score === 4) return { pct: 80,  color: '#10b981', label: 'Strong'     }
      return                 { pct: 100, color: '#0d9488', label: 'Very strong' }
    },

    // Le bouton "Update Password" est actif uniquement si tous les champs sont remplis
    // et que les deux nouveaux mots de passe correspondent
    canSubmitPwd() {
      return (
        this.pwd.current.length > 0 &&
        this.pwd.new.length >= 8 &&
        this.pwd.new === this.pwd.confirm
      )
    },
  },

  async mounted() {
    await this.loadProfile()
  },

  methods: {
    // ── Chargement du profil ───────────────────────────────────────
    async loadProfile() {
      const token = localStorage.getItem('token')
      if (!token) {
        this.errorMsg = 'Session expired. Please sign in again.'
        setTimeout(() => this.$router?.push('/login'), 2000)
        return
      }

      try {
        const res = await fetch(`${API_BASE}/api/tenant/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err.message || `HTTP error ${res.status}`)
        }
        const result = await res.json()
        if (result.success && result.data) {
          this.form = {
            ...this.form,
            tenantName: result.data.tenantName || '',
            ...result.data,
            workTypes:    Array.isArray(result.data.workTypes)  ? result.data.workTypes  : [],
            techStack:    Array.isArray(result.data.techStack)  ? result.data.techStack  : [],
            hiringStatus: result.data.hiringStatus || 'actively',
          }
        }
      } catch (err) {
        console.error('Load profile error:', err)
        this.errorMsg = 'Unable to load profile: ' + err.message
        setTimeout(() => this.errorMsg = '', 4000)
      }
    },

    // ── Logo ───────────────────────────────────────────────────────
    onLogoChange(e) {
      const file = e.target.files[0]
      if (!file) return
      if (file.size > 5 * 1024 * 1024) {
        this.errorMsg = 'Logo must be under 5 MB.'
        setTimeout(() => this.errorMsg = '', 3000)
        e.target.value = ''
        return
      }
      const ext = file.name.split('.').pop().toLowerCase()
      if (!['jpg', 'jpeg', 'png', 'webp', 'svg'].includes(ext)) {
        this.errorMsg = 'Unsupported format (jpg, png, webp, svg)'
        setTimeout(() => this.errorMsg = '', 3000)
        e.target.value = ''
        return
      }
      const reader = new FileReader()
      reader.onload = (ev) => { this.localLogoPreview = ev.target.result }
      reader.readAsDataURL(file)
    },

    // ── Tech stack ─────────────────────────────────────────────────
    addTech() {
      const t = this.techInput.trim()
      if (t && !this.form.techStack.includes(t)) this.form.techStack.push(t)
      this.techInput = ''
    },
    removeTech(i) { this.form.techStack.splice(i, 1) },
    toggleWorkType(wt) {
      const idx = this.form.workTypes.indexOf(wt)
      if (idx === -1) this.form.workTypes.push(wt)
      else this.form.workTypes.splice(idx, 1)
    },

    // ── Sauvegarde profil ──────────────────────────────────────────
    async saveProfile() {
      this.saving = true
      this.successMsg = ''
      this.errorMsg   = ''

      const token = localStorage.getItem('token')
      if (!token) {
        this.errorMsg = 'Session expired.'
        setTimeout(() => this.$router?.push('/login'), 2000)
        this.saving = false
        return
      }

      try {
        const formData = new FormData()
        const simpleFields = [
          'tenantName','companyName','industry','companySize','location','description',
          'website','linkedin','twitter','hiringStatus','fullName','email','jobTitle','phone'
        ]
        simpleFields.forEach(key => {
          const val = this.form[key]
          if (val != null && val !== '') formData.append(key, String(val))
        })
        if (Array.isArray(this.form.workTypes))
          this.form.workTypes.forEach(wt => { if (wt) formData.append('workTypes', wt) })
        if (Array.isArray(this.form.techStack))
          this.form.techStack.forEach(t => { if (t) formData.append('techStack', t) })

        const logoFile = this.$refs?.logoInput?.files?.[0]
        if (logoFile) formData.append('logo', logoFile)

        const res = await fetch(`${API_BASE}/api/tenant/profile`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        })
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}))
          throw new Error(errData.message || `Error ${res.status}`)
        }
        const data = await res.json()
        if (!data.success) throw new Error(data.message || 'Échec de la sauvegarde')

        if (data.data) {
          this.form = {
            ...this.form,
            ...data.data,
            workTypes:    Array.isArray(data.data.workTypes) ? data.data.workTypes : [],
            techStack:    Array.isArray(data.data.techStack) ? data.data.techStack : [],
            hiringStatus: data.data.hiringStatus || 'actively',
          }
          this.localLogoPreview = null
        }
        if (this.$refs?.logoInput) this.$refs.logoInput.value = ''

        this.successMsg = 'Saved successfully ✅'
        setTimeout(() => this.successMsg = '', 3000)
      } catch (err) {
        console.error('Save profile error:', err)
        this.errorMsg = 'Error saving: ' + err.message
        setTimeout(() => this.errorMsg = '', 4000)
      } finally {
        this.saving = false
      }
    },

    // ── Changement de mot de passe ─────────────────────────────────
    async changePassword() {
      if (!this.canSubmitPwd) return

      this.pwdSaving  = true
      this.pwdSuccess = ''
      this.pwdError   = ''

      const token = localStorage.getItem('token')
      if (!token) {
        this.pwdError = 'Session expired. Please sign in again.'
        this.pwdSaving = false
        return
      }

      try {
        const res = await fetch(`${API_BASE}/api/tenant/change-password`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            currentPassword: this.pwd.current,
            newPassword:     this.pwd.new,
            confirmPassword: this.pwd.confirm,
          }),
        })

        const data = await res.json().catch(() => ({}))

        if (!res.ok || !data.success) {
          throw new Error(data.message || `Error ${res.status}`)
        }

        // Succès : vider les champs
        this.pwd = { current: '', new: '', confirm: '' }
        this.showPwd = { current: false, new: false, confirm: false }
        this.pwdSuccess = 'Password updated successfully ✅'
        setTimeout(() => this.pwdSuccess = '', 4000)
      } catch (err) {
        console.error('Change password error:', err)
        this.pwdError = err.message || 'An error occurred.'
        setTimeout(() => this.pwdError = '', 5000)
      } finally {
        this.pwdSaving = false
      }
    },
  },
}
</script>

<style scoped>
/* ═══ LAYOUT ═══ */
.app-layout {
  display: flex;
  min-height: 100vh;
  background: #f1f5f9;
  font-family: 'Inter', -apple-system, sans-serif;
}
.main-content { flex: 1; overflow-y: auto; min-width: 0; }
.profile-page { padding: 36px 40px; max-width: 1500px; }

/* ═══ HEADER ═══ */
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 28px;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon {
  width: 46px; height: 46px; border-radius: 12px;
  background: #1A2B4C; color: #fff;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.page-title   { font-size: 22px; font-weight: 800; color: #0f172a; margin: 0 0 3px; letter-spacing: -0.4px; }
.page-subtitle { font-size: 14px; color: #64748b; margin: 0; }

.btn-save {
  display: flex; align-items: center; gap: 7px;
  background: #454a83; color: #fff; border: none; border-radius: 10px;
  padding: 12px 24px; font-size: 14px; font-weight: 600;
  cursor: pointer; font-family: inherit;
  box-shadow: 0 2px 8px rgba(26,43,76,0.25);
  transition: background 0.15s, transform 0.1s, opacity 0.15s;
}
.btn-save:hover   { background: #243760; transform: translateY(-1px); }
.btn-save:active  { transform: translateY(0); }
.btn-save:disabled { opacity: 0.55; cursor: not-allowed; transform: none; }

/* ═══ ALERTS ═══ */
.alert {
  display: flex; align-items: center; gap: 9px;
  padding: 13px 18px; border-radius: 10px;
  font-size: 14px; font-weight: 500;
  margin-bottom: 20px; border: 1px solid transparent;
}
.alert-success { background: #f0fdf4; color: #15803d; border-color: #bbf7d0; }
.alert-error   { background: #fff1f2; color: #be123c; border-color: #fecdd3; }
.pwd-alert     { margin-bottom: 16px; }

.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; }
.slide-down-enter-from { opacity: 0; transform: translateY(-10px); }
.slide-down-leave-to   { opacity: 0; transform: translateY(-6px); }

/* ═══ GRID ═══ */
.profile-grid { display: grid; grid-template-columns: 250px 1fr; gap: 22px; align-items: start; }
.left-col, .right-col { display: flex; flex-direction: column; gap: 18px; }

/* ═══ CARDS ═══ */
.card {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px;
  padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); transition: box-shadow 0.2s;
}
.card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.07); }

.card-header-row { display: flex; align-items: center; gap: 8px; margin-bottom: 18px; }
.card-header-icon { color: #1A2B4C; flex-shrink: 0; }
.card-header-row .section-label { margin-bottom: 0; }

.section-label {
  font-size: 11px; font-weight: 800; letter-spacing: 0.1em;
  text-transform: uppercase; color: #94a3b8; margin: 0 0 18px;
}

/* ═══ LOGO CARD ═══ */
.avatar-card { text-align: center; padding: 30px 24px 24px; }
.logo-wrapper {
  position: relative; display: inline-flex;
  align-items: center; justify-content: center;
  width: 96px; height: 96px; margin-bottom: 16px;
}
.company-logo {
  width: 96px; height: 96px; border-radius: 18px;
  object-fit: contain; border: 2px solid #e2e8f0;
  background: #f8fafc; padding: 4px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
.logo-edit-btn {
  position: absolute; bottom: -4px; right: -4px;
  width: 30px; height: 30px; border-radius: 50%;
  background: #1A2B4C; color: #fff; border: 2.5px solid #fff;
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  transition: background 0.15s, transform 0.15s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.logo-edit-btn:hover { background: #2d4a7a; transform: scale(1.1); }

.company-name { font-size: 16px; font-weight: 800; color: #0f172a; margin: 0 0 8px; letter-spacing: -0.3px; }
.role-badge {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(26,43,76,0.08); color: #1A2B4C;
  font-size: 11px; font-weight: 700;
  border-radius: 9999px; padding: 4px 14px; margin-bottom: 22px;
}
.strength-wrap { text-align: left; }
.strength-header { display: flex; justify-content: space-between; font-size: 12px; color: #64748b; margin-bottom: 8px; }
.strength-pct { font-weight: 800; transition: color 0.3s; }
.strength-track { height: 7px; background: #f1f5f9; border-radius: 9999px; overflow: hidden; margin-bottom: 8px; }
.strength-bar  { height: 100%; border-radius: 9999px; transition: width 0.5s ease, background 0.3s; }
.strength-hint { font-size: 12px; color: #94a3b8; margin: 0; line-height: 1.4; }

/* ═══ INFO CARD ═══ */
.info-card { padding: 20px 24px; }
.info-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 0; font-size: 13px; color: #475569;
  border-bottom: 1px solid #f8fafc;
  overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
}
.info-item:last-child { border-bottom: none; }
.info-icon { color: #cbd5e1; flex-shrink: 0; }

/* ═══ FORM ═══ */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 7px; }
.field.span-2 { grid-column: span 2; }
.field label { font-size: 13px; font-weight: 600; color: #374151; display: flex; align-items: center; gap: 5px; }
.req { color: #ef4444; }

.input-wrap { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 12px; color: #cbd5e1; pointer-events: none; flex-shrink: 0; }
.input-wrap input { padding-left: 36px !important; }

/* Bordure rouge si mismatch */
.input-mismatch input { border-color: #fca5a5 !important; }

.field input,
.field select,
.field textarea {
  width: 100%; box-sizing: border-box;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  padding: 11px 14px; font-size: 14px; color: #0f172a;
  background: #fafbfc; outline: none;
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  resize: vertical; font-family: inherit;
}
.field input:focus,
.field select:focus,
.field textarea:focus {
  border-color: #1A2B4C; background: #fff;
  box-shadow: 0 0 0 3px rgba(26,43,76,0.08);
}
.field input::placeholder,
.field textarea::placeholder { color: #cbd5e1; }

/* Bouton œil (show/hide password) */
.eye-btn {
  position: absolute; right: 12px;
  background: none; border: none; padding: 0;
  color: #94a3b8; cursor: pointer;
  display: flex; align-items: center;
  transition: color 0.15s;
}
.eye-btn:hover { color: #1A2B4C; }

/* Champ password : espace à droite pour l'icône œil */
.input-wrap input[type="password"],
.input-wrap input[type="text"] {
  padding-right: 38px !important;
}

/* Erreur de champ */
.field-error { font-size: 12px; color: #ef4444; margin: 0; }

/* ═══ FORCE DU MOT DE PASSE ═══ */
.pwd-strength-wrap {
  display: flex; align-items: center; gap: 10px; margin-top: 8px;
}
.pwd-strength-track {
  flex: 1; height: 5px; background: #e2e8f0;
  border-radius: 9999px; overflow: hidden;
}
.pwd-strength-bar { height: 100%; border-radius: 9999px; transition: width 0.4s ease, background 0.3s; }
.pwd-strength-label { font-size: 12px; font-weight: 700; white-space: nowrap; }

/* ═══ PASSWORD CARD FOOTER ═══ */
.pwd-card { border-color: #e0e7ff; }
.pwd-footer { display: flex; justify-content: flex-end; margin-top: 20px; }

.btn-change-pwd {
  display: inline-flex; align-items: center; gap: 8px;
  background: #1A2B4C; color: #fff;
  border: none; border-radius: 10px;
  padding: 12px 24px; font-size: 14px; font-weight: 600;
  cursor: pointer; font-family: inherit;
  box-shadow: 0 2px 8px rgba(26,43,76,0.2);
  transition: background 0.15s, transform 0.1s, opacity 0.15s;
}
.btn-change-pwd:hover:not(:disabled)   { background: #243760; transform: translateY(-1px); }
.btn-change-pwd:active:not(:disabled)  { transform: translateY(0); }
.btn-change-pwd:disabled { opacity: 0.45; cursor: not-allowed; }

/* ═══ STATUS / HIRING ═══ */
.status-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px; }
.status-btn {
  display: flex; align-items: center; gap: 7px;
  padding: 9px 16px; border: 1.5px solid #e2e8f0; border-radius: 9px;
  background: #fafbfc; font-size: 13px; font-weight: 600; color: #64748b;
  cursor: pointer; transition: all 0.15s; font-family: inherit;
}
.status-btn:hover  { border-color: #1A2B4C; color: #1A2B4C; background: rgba(26,43,76,0.04); }
.status-btn.active { border-color: #1A2B4C; background: rgba(26,43,76,0.08); color: #1A2B4C; }
.status-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-green   { background: #10b981; }
.dot-orange  { background: #f59e0b; }
.dot-gray    { background: #94a3b8; }

/* ═══ TAGS ═══ */
.tags-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; min-height: 34px; }
.tag {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(26,43,76,0.07); color: #1A2B4C;
  border-radius: 9999px; padding: 6px 14px;
  font-size: 13px; font-weight: 600; transition: background 0.12s;
}
.tag:hover { background: rgba(26,43,76,0.13); }
.tag-del { background: none; border: none; color: #94a3b8; font-size: 15px; line-height: 1; cursor: pointer; padding: 0; transition: color 0.1s; }
.tag-del:hover { color: #ef4444; }
.tags-empty { font-size: 13px; color: #cbd5e1; align-self: center; }

/* ═══ MODAL ═══ */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(15,23,42,0.35);
  backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal { background: #fff; border-radius: 20px; padding: 40px 36px; max-width: 380px; width: 90%; text-align: center; box-shadow: 0 24px 48px rgba(0,0,0,0.18); }
.modal-icon-wrap { width: 58px; height: 58px; border-radius: 50%; background: #fef2f2; color: #ef4444; display: flex; align-items: center; justify-content: center; margin: 0 auto 18px; }
.modal h3  { font-size: 18px; font-weight: 800; color: #0f172a; margin: 0 0 10px; }
.modal p   { font-size: 14px; color: #64748b; margin: 0 0 26px; line-height: 1.6; }
.modal-btns { display: flex; gap: 12px; justify-content: center; }
.modal-fade-enter-active, .modal-fade-leave-active { transition: all 0.25s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

.btn-ghost { background: #f8fafc; color: #475569; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 11px 22px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.15s; font-family: inherit; }
.btn-ghost:hover { background: #f1f5f9; }
.btn-delete { flex-shrink: 0; background: #fff; color: #dc2626; border: 1.5px solid #fca5a5; border-radius: 10px; padding: 10px 20px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.15s, border-color 0.15s; font-family: inherit; white-space: nowrap; }
.btn-delete:hover { background: #fef2f2; border-color: #f87171; }

/* ═══ RESPONSIVE ═══ */
@media (max-width: 900px) {
  .profile-grid { grid-template-columns: 1fr; }
  .left-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
}
@media (max-width: 600px) {
  .profile-page { padding: 20px 16px; }
  .form-grid { grid-template-columns: 1fr; }
  .field.span-2 { grid-column: span 1; }
  .left-col { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 14px; }
  .btn-save { width: 100%; justify-content: center; }
}
</style>