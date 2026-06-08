<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <AppSidebar />

    <!-- Main content -->
    <main class="main-content">
      <GlobalHeader title="My Profile" />
      <div class="profile-page">

        <!-- ── PAGE HEADER ── -->
        <div class="page-header">
          <div class="header-left">
            <div class="header-icon">
              <UserCircleIcon :size="22" />
            </div>
            <div>
              <h1 class="page-title">My Profile</h1>
              <p class="page-subtitle">Manage your personal information and preferences</p>
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

            <!-- Avatar card -->
            <div class="card avatar-card">
              <div class="avatar-wrapper">
                <img 
                  :src="displayAvatarUrl" 
                  class="avatar-img" 
                  alt="Avatar"
                  @error="onImageError"
                />
                
                <input
                  ref="avatarInput"
                  type="file"
                  accept="image/png,image/jpeg,image/webp,image/svg+xml"
                  style="display:none"
                  @change="onAvatarChange"
                />
                
                <button 
                  class="avatar-edit-btn" 
                  title="Change photo" 
                  @click="$refs.avatarInput.click()"
                  type="button"
                >
                  <CameraIcon :size="13" />
                </button>
              </div>
              <p class="avatar-name">{{ form.fullName || '—' }}</p>
              <span class="role-badge">{{ roleLabel }}</span>

              <!-- Profile strength -->
              <div class="strength-wrap">
                <div class="strength-header">
                  <span>Profile Strength</span>
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
              <p class="section-label">CONTACT</p>
              <div class="info-item">
                <MailIcon :size="13" class="info-icon" />
                <span>{{ form.email || 'Not set' }}</span>
              </div>
              <div class="info-item">
                <PhoneIcon :size="13" class="info-icon" />
                <span>{{ form.phone || 'Not set' }}</span>
              </div>
              <div class="info-item">
                <MapPinIcon :size="13" class="info-icon" />
                <span>{{ form.location || 'Not set' }}</span>
              </div>
              <div class="info-item">
                <BriefcaseIcon :size="13" class="info-icon" />
                <span>{{ seekingLabel || 'Status not set' }}</span>
              </div>
            </div>

          </div>

          <!-- ═══ RIGHT COLUMN ═══ -->
          <div class="right-col">

            <!-- PERSONAL INFORMATION -->
            <div class="card">
              <div class="card-header-row">
                <UserIcon :size="15" class="card-header-icon" />
                <p class="section-label">PERSONAL INFORMATION</p>
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
                    <input v-model="form.email" type="email" placeholder="you@example.com" />
                  </div>
                </div>
                <div class="field">
                  <label>Phone</label>
                  <div class="input-wrap">
                    <PhoneIcon :size="14" class="input-icon" />
                    <input v-model="form.phone" placeholder="+216 00 000 000" />
                  </div>
                </div>
                <div class="field">
                  <label>Location</label>
                  <div class="input-wrap">
                    <MapPinIcon :size="14" class="input-icon" />
                    <input v-model="form.location" placeholder="City, Country" />
                  </div>
                </div>
                <div class="field span-2">
                  <label>Bio / Summary</label>
                  <textarea v-model="form.bio" rows="3" placeholder="Write a short intro about yourself…"></textarea>
                </div>
              </div>
            </div>

            <!-- CAREER STATUS -->
            <div class="card">
              <div class="card-header-row">
                <BriefcaseIcon :size="15" class="card-header-icon" />
                <p class="section-label">CAREER STATUS</p>
              </div>
              <div class="form-grid">
                <div class="field span-2">
                  <label>Current Status <span class="req">*</span></label>
                  <div class="status-grid">
                    <button
                      v-for="opt in seekingOptions"
                      :key="opt.value"
                      class="status-btn"
                      :class="{ active: form.seeking === opt.value }"
                      @click="form.seeking = opt.value"
                      type="button"
                    >
                      <span class="status-dot" :class="opt.color"></span>
                      {{ opt.label }}
                    </button>
                  </div>
                </div>
                <div class="field">
                  <label>Education Level</label>
                  <select v-model="form.education">
                    <option value="">Select…</option>
                    <option value="bac">Baccalaureate</option>
                    <option value="licence">Licence / Bachelor</option>
                    <option value="master">Master</option>
                    <option value="ingenieur">Engineering Degree</option>
                    <option value="doctorat">Doctorat / PhD</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="field">
                  <label>Field of Study</label>
                  <div class="input-wrap">
                    <BookOpenIcon :size="14" class="input-icon" />
                    <input v-model="form.fieldOfStudy" placeholder="e.g. Computer Science" />
                  </div>
                </div>
                <div class="field">
                  <label>Years of Experience</label>
                  <select v-model="form.experience">
                    <option value="">Select…</option>
                    <option value="0">No experience</option>
                    <option value="1">Less than 1 year</option>
                    <option value="1-3">1–3 years</option>
                    <option value="3-5">3–5 years</option>
                    <option value="5+">5+ years</option>
                  </select>
                </div>
                <div class="field">
                  <label>Availability</label>
                  <select v-model="form.availability">
                    <option value="">Select…</option>
                    <option value="immediate">Immediately</option>
                    <option value="1month">Within 1 month</option>
                    <option value="3months">Within 3 months</option>
                    <option value="not_available">Not available</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- SKILLS -->
            <div class="card">
              <div class="card-header-row">
                <ZapIcon :size="15" class="card-header-icon" />
                <p class="section-label">SKILLS</p>
              </div>
              <div class="field">
                <label>Type a skill and press Enter</label>
                <div class="input-wrap">
                  <ZapIcon :size="14" class="input-icon" />
                  <input
                    v-model="skillInput"
                    @keydown.enter.prevent="addSkill"
                    placeholder="e.g. React, Python, Figma…"
                  />
                </div>
              </div>
              <div class="tags-wrap">
                <span v-for="(sk, i) in form.skills" :key="i" class="tag">
                  {{ sk }}
                  <button @click="removeSkill(i)" type="button" class="tag-del">×</button>
                </span>
                <span v-if="!form.skills.length" class="tags-empty">No skills added yet.</span>
              </div>
            </div>

            <!-- LINKS -->
            <div class="card">
              <div class="card-header-row">
                <GlobeIcon :size="15" class="card-header-icon" />
                <p class="section-label">LINKS & PORTFOLIO</p>
              </div>
              <div class="form-grid">
                <div class="field">
                  <label>LinkedIn</label>
                  <div class="input-wrap">
                    <LinkedinIcon :size="14" class="input-icon" />
                    <input v-model="form.linkedin" placeholder="https://linkedin.com/in/…" />
                  </div>
                </div>
                <div class="field">
                  <label>GitHub</label>
                  <div class="input-wrap">
                    <GithubIcon :size="14" class="input-icon" />
                    <input v-model="form.github" placeholder="https://github.com/…" />
                  </div>
                </div>
                <div class="field span-2">
                  <label>Portfolio / Website</label>
                  <div class="input-wrap">
                    <GlobeIcon :size="14" class="input-icon" />
                    <input v-model="form.portfolioUrl" placeholder="https://myportfolio.com" />
                  </div>
                </div>
              </div>
            </div>

           
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
          <h3>Delete your account?</h3>
          <p>All your data will be permanently erased. This action cannot be undone.</p>
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
import GlobalHeader from '@/components/layout/GlobalHeader.vue'
import {
  SaveIcon, CameraIcon, MailIcon, PhoneIcon, MapPinIcon,
  BriefcaseIcon, GlobeIcon, LinkedinIcon, GithubIcon,
  CheckCircleIcon, AlertCircleIcon, AlertTriangleIcon,
  UserIcon, UserCircleIcon, LockIcon, ZapIcon,
  BookOpenIcon
} from 'lucide-vue-next'

const API_BASE = 'http://localhost:5202'

export default {
  name: 'CandidateProfileView',
  components: {
    AppSidebar,
    GlobalHeader,
    SaveIcon, CameraIcon, MailIcon, PhoneIcon, MapPinIcon,
    BriefcaseIcon, GlobeIcon, LinkedinIcon, GithubIcon,
    CheckCircleIcon, AlertCircleIcon, AlertTriangleIcon,
    UserIcon, UserCircleIcon, LockIcon, ZapIcon,
    BookOpenIcon
  },
  data() {
    return {
      saving: false,
      successMsg: '',
      errorMsg: '',
      confirmDelete: false,
      skillInput: '',
      role: null,
      defaultAvatar: 'https://t3.ftcdn.net/jpg/16/93/30/10/360_F_1693301062_WIKjLfV17a39eqipWY1SYTG2fiNTaqwa.jpg',
      form: {
        fullName: '', email: '', phone: '', location: '', bio: '', avatarUrl: '',
        seeking: '', education: '', fieldOfStudy: '', experience: '', availability: '',
        skills: [], linkedin: '', github: '', portfolioUrl: '',
        currentPassword: '', newPassword: '', confirmPassword: ''
      },
      localAvatarPreview: null,
      seekingOptions: [
        { value: 'student',     label: 'Student',               color: 'dot-blue'   },
        { value: 'internship',  label: 'Looking for Internship', color: 'dot-purple' },
        { value: 'job',         label: 'Looking for Job',        color: 'dot-green'  },
        { value: 'freelance',   label: 'Freelance',              color: 'dot-orange' },
        { value: 'not_looking', label: 'Not Looking',            color: 'dot-gray'   }
      ]
    }
  },
  computed: {
    displayAvatarUrl() {
  if (this.localAvatarPreview) {
    return this.localAvatarPreview
  }

  if (this.form.avatarUrl) {
    // Si c'est un chemin relatif du serveur, préfixer avec l'URL de l'API
    if (this.form.avatarUrl.startsWith('/')) {
      return `${API_BASE}${this.form.avatarUrl}`
    }
    return this.form.avatarUrl
  }

  return this.defaultAvatar
},
    roleLabel() {
      const map = { Admin: 'Administrator', Tenant: 'Recruiter', Expert: 'Expert', Candidat: 'Candidate' }
      return map[this.role] || 'Candidate'
    },

    seekingLabel() {
      return this.seekingOptions.find(o => o.value === this.form.seeking)?.label || ''
    },

    profileStrength() {
      const fields = ['fullName', 'email', 'phone', 'location', 'bio', 'seeking', 'education', 'portfolioUrl']
      const filled = fields.filter(f => this.form[f]?.trim()).length
      const hasSkills = this.form.skills?.length > 0 ? 1 : 0
      return Math.round(((filled + hasSkills) / (fields.length + 1)) * 100)
    },

    strengthColor() {
      if (this.profileStrength >= 80) return '#10b981'
      if (this.profileStrength >= 50) return '#f59e0b'
      return '#ef4444'
    },

    strengthHint() {
      if (this.profileStrength >= 80) return "Great profile! You're highly visible."
      if (this.profileStrength >= 50) return 'Add more info to increase visibility.'
      return 'Complete your profile to get noticed.'
    }
  },

  async mounted() {
    console.log('🚀 CandidateProfile component mounted')
    await this.loadProfile()
    
    console.log('📸 État avatar après loadProfile:', {
      avatarUrl: this.form.avatarUrl,
      localPreview: !!this.localAvatarPreview,
      displayUrl: this.displayAvatarUrl
    })
    
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        this.role = payload.role
          || payload['http://schemas.microsoft.com/ws/2008/06/identity/claims/role']
          || null
      } catch { this.role = null }
    }
  },

  methods: {
    async loadProfile() {
      const token = localStorage.getItem('token')
      if (!token) {
        this.errorMsg = 'Session expirée. Veuillez vous reconnecter.'
        setTimeout(() => this.$router?.push('/login'), 2000)
        return
      }

      try {
        console.log('📥 Chargement du profil depuis le serveur...')
        const res = await fetch(`${API_BASE}/api/candidat/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        })

        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err.message || `Erreur HTTP ${res.status}`)
        }

        const result = await res.json()
        
        if (result.success && result.data) {
          // ✅ IMPORTANT: Fusionner complètement et garder avatarUrl
          this.form = {
            ...this.form,
            ...result.data,
            skills: Array.isArray(result.data.skills) ? result.data.skills : [],
            seeking: result.data.seeking || 'student',
            avatarUrl: result.data.avatarUrl || null  // 👈 EXPLICITE
          }
          
          console.log('✅ Profil chargé avec succès:', {
            fullName: this.form.fullName,
            avatarUrl: this.form.avatarUrl,
            seeking: this.form.seeking
          })
        }
      } catch (err) {
        console.error('❌ Load profile error:', err)
        this.errorMsg = 'Impossible de charger le profil: ' + err.message
        setTimeout(() => this.errorMsg = '', 4000)
      }
    },

    onImageError(e) {
      console.error('❌ Erreur chargement image:', e.target.src)
      e.target.src = this.defaultAvatar
    },

    onAvatarChange(e) {
      const file = e.target.files[0]
      if (!file) return
      
      if (file.size > 5 * 1024 * 1024) {
        this.errorMsg = 'Avatar must be under 5 MB.'
        setTimeout(() => this.errorMsg = '', 3000)
        e.target.value = ''
        return
      }
      
      const ext = file.name.split('.').pop().toLowerCase()
      const allowed = ['jpg', 'jpeg', 'png', 'webp', 'svg']
      if (!allowed.includes(ext)) {
        this.errorMsg = 'Format non supporté (jpg, png, webp, svg)'
        setTimeout(() => this.errorMsg = '', 3000)
        e.target.value = ''
        return
      }
      
      const reader = new FileReader()
      reader.onload = (ev) => {
        this.localAvatarPreview = ev.target.result
        console.log('✅ Preview local créé')
      }
      reader.onerror = () => {
        this.errorMsg = 'Erreur de lecture du fichier'
        setTimeout(() => this.errorMsg = '', 3000)
      }
      reader.readAsDataURL(file)
    },

    addSkill() {
      const sk = this.skillInput.trim()
      if (sk && !this.form.skills.includes(sk)) {
        this.form.skills.push(sk)
      }
      this.skillInput = ''
    },

    removeSkill(i) { 
      this.form.skills.splice(i, 1) 
    },

    async saveProfile() {
      this.saving = true
      this.successMsg = ''
      this.errorMsg = ''

      const token = localStorage.getItem('token')
      if (!token) {
        this.errorMsg = 'Session expirée. Veuillez vous reconnecter.'
        setTimeout(() => this.$router?.push('/login'), 2000)
        this.saving = false
        return
      }

      if (this.form.newPassword) {
        if (this.form.newPassword !== this.form.confirmPassword) {
          this.errorMsg = 'New passwords do not match.'
          setTimeout(() => this.errorMsg = '', 3000)
          this.saving = false
          return
        }
        if (this.form.newPassword.length < 6) {
          this.errorMsg = 'New password must be at least 6 characters.'
          setTimeout(() => this.errorMsg = '', 3000)
          this.saving = false
          return
        }
      }

      try {
        const formData = new FormData()

        const simpleFields = [
          'fullName','email','phone','location','bio',
          'seeking','education','fieldOfStudy','experience','availability',
          'linkedin','github','portfolioUrl',
          'currentPassword','newPassword','confirmPassword'
        ]
        simpleFields.forEach(key => {
          const val = this.form[key]
          if (val != null && val !== '') {
            formData.append(key, String(val))
          }
        })

        if (Array.isArray(this.form.skills)) {
          this.form.skills.forEach(sk => {
            if (sk) formData.append('skills', sk)
          })
        }

        const avatarFile = this.$refs?.avatarInput?.files?.[0]
        if (avatarFile) {
          formData.append('avatar', avatarFile)
        }

        console.log('📤 Envoi du profil...')
        const res = await fetch(`${API_BASE}/api/candidat/profile`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${token}` },
          body: formData
        })

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}))
          throw new Error(errData.message || `Erreur ${res.status}`)
        }

        const data = await res.json()
        
        if (!data.success) {
          throw new Error(data.message || 'Échec de la sauvegarde')
        }

        // ✅ IMPORTANT: Mise à jour avec les données serveur (inclut avatarUrl)
        if (data.data) {
          this.form = {
            ...this.form,
            ...data.data,  // 👈 Inclut avatarUrl sauvegardé
            skills: Array.isArray(data.data.skills) ? data.data.skills : [],
            seeking: data.data.seeking || 'student'
          }
          
          console.log('✅ Profil mis à jour avec:', {
            avatarUrl: data.data.avatarUrl,
            fullName: data.data.fullName
          })
        }

        // ✅ CRUCIAL: Effacer la preview locale maintenant qu'on a la version serveur
        this.localAvatarPreview = null
        console.log('🧹 Preview local effacé, affichage de:', this.displayAvatarUrl)

        if (this.$refs?.avatarInput) {
          this.$refs.avatarInput.value = ''
        }

        this.successMsg = 'Profile saved successfully! ✅'
        setTimeout(() => this.successMsg = '', 3000)

      } catch (err) {
        console.error('❌ Save profile error:', err)
        this.errorMsg = 'Error saving: ' + err.message
        setTimeout(() => this.errorMsg = '', 4000)
      } finally {
        this.saving = false
      }
    }
  }
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
.main-content {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
}
.profile-page {
  padding: 36px 40px;
  max-width: 1900px;
}

/* ═══ HEADER ═══ */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon {
  width: 46px; height: 46px;
  border-radius: 12px;
  background: #1A2B4C;
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.page-title {
  font-size: 22px; font-weight: 800; color: #0f172a;
  margin: 0 0 3px; letter-spacing: -0.4px;
}
.page-subtitle { font-size: 14px; color: #64748b; margin: 0; }

.btn-save {
  display: flex; align-items: center; gap: 7px;
  background: #1A2B4C; color: #fff;
  border: none; border-radius: 10px;
  padding: 12px 24px;
  font-size: 14px; font-weight: 600;
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
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; }
.slide-down-enter-from { opacity: 0; transform: translateY(-10px); }
.slide-down-leave-to   { opacity: 0; transform: translateY(-6px); }

/* ═══ GRID ═══ */
.profile-grid {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 22px;
  align-items: start;
}
.left-col, .right-col { display: flex; flex-direction: column; gap: 18px; }

/* ═══ CARDS ═══ */
.card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s;
}
.card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.07); }

.card-header-row {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 18px;
}
.card-header-icon { color: #1A2B4C; flex-shrink: 0; }
.card-header-row .section-label { margin-bottom: 0; }

.section-label {
  font-size: 11px; font-weight: 800;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: #94a3b8; margin: 0 0 18px;
}

/* ═══ AVATAR CARD ═══ */
.avatar-card { text-align: center; padding: 30px 24px 24px; }
.avatar-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}
.avatar-img {
  width: 96px; height: 96px; border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e2e8f0;
  background: #f8fafc;
  box-shadow: 0 4px 14px rgba(0,0,0,0.08);
  transition: opacity 0.2s;
}
.avatar-img:hover { opacity: 0.95; }
.avatar-edit-btn {
  position: absolute; bottom: -4px; right: -4px;
  width: 30px; height: 30px; border-radius: 50%;
  background: #1A2B4C; color: #fff;
  border: 2.5px solid #fff;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.avatar-edit-btn:hover { background: #2d4a7a; transform: scale(1.1); }

.avatar-name {
  font-size: 16px; font-weight: 800; color: #0f172a;
  margin: 0 0 8px; letter-spacing: -0.3px;
}
.role-badge {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(26,43,76,0.08); color: #1A2B4C;
  font-size: 11px; font-weight: 700;
  border-radius: 9999px; padding: 4px 14px;
  margin-bottom: 22px;
}

/* ─ Strength ─ */
.strength-wrap { text-align: left; }
.strength-header {
  display: flex; justify-content: space-between;
  font-size: 12px; color: #64748b; margin-bottom: 8px;
}
.strength-pct { font-weight: 800; transition: color 0.3s; }
.strength-track {
  height: 7px; background: #f1f5f9;
  border-radius: 9999px; overflow: hidden; margin-bottom: 8px;
}
.strength-bar {
  height: 100%; border-radius: 9999px;
  transition: width 0.5s ease, background 0.3s;
}
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
.form-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
}
.field { display: flex; flex-direction: column; gap: 7px; }
.field.span-2 { grid-column: span 2; }
.field label {
  font-size: 13px; font-weight: 600; color: #374151;
  display: flex; align-items: center; gap: 5px;
}
.req { color: #ef4444; }

.input-wrap { position: relative; display: flex; align-items: center; }
.input-icon {
  position: absolute; left: 12px;
  color: #cbd5e1; pointer-events: none; flex-shrink: 0;
}
.input-wrap input { padding-left: 36px !important; }

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
.field select { appearance: none; cursor: pointer; }
.field input::placeholder,
.field textarea::placeholder { color: #cbd5e1; }

/* ═══ STATUS BUTTONS ═══ */
.status-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px; }
.status-btn {
  display: flex; align-items: center; gap: 7px;
  padding: 9px 16px;
  border: 1.5px solid #e2e8f0; border-radius: 9px;
  background: #fafbfc; font-size: 13px; font-weight: 600;
  color: #64748b; cursor: pointer;
  transition: all 0.15s; font-family: inherit;
}
.status-btn:hover { border-color: #1A2B4C; color: #1A2B4C; background: rgba(26,43,76,0.04); }
.status-btn.active {
  border-color: #1A2B4C;
  background: rgba(26,43,76,0.08);
  color: #1A2B4C;
  box-shadow: 0 2px 8px rgba(26,43,76,0.1);
}
.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-blue   { background: #3b82f6; }
.dot-purple { background: #8b5cf6; }
.dot-green  { background: #10b981; }
.dot-orange { background: #f59e0b; }
.dot-gray   { background: #94a3b8; }

/* ═══ TAGS ═══ */
.tags-wrap {
  display: flex; flex-wrap: wrap; gap: 8px;
  margin-top: 12px; min-height: 34px;
}
.tag {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(26,43,76,0.07); color: #1A2B4C;
  border-radius: 9999px; padding: 6px 14px;
  font-size: 13px; font-weight: 600;
  transition: background 0.12s;
}
.tag:hover { background: rgba(26,43,76,0.13); }
.tag-del {
  background: none; border: none; color: #94a3b8;
  font-size: 15px; line-height: 1;
  cursor: pointer; padding: 0; transition: color 0.1s;
  display: flex; align-items: center;
}
.tag-del:hover { color: #ef4444; transform: scale(1.1); }
.tags-empty { font-size: 13px; color: #cbd5e1; align-self: center; }

/* ═══ DANGER ═══ */
.danger-card { border-color: #fed7d7; background: #fffafa; }
.danger-lbl { color: #f87171; }
.danger-row { display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
.danger-title { font-size: 14px; font-weight: 700; color: #dc2626; margin: 0 0 5px; }
.danger-desc  { font-size: 13px; color: #94a3b8; margin: 0; line-height: 1.5; max-width: 480px; }
.btn-delete {
  flex-shrink: 0; background: #fff; color: #dc2626;
  border: 1.5px solid #fca5a5; border-radius: 10px;
  padding: 10px 20px; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: background 0.15s, border-color 0.15s;
  font-family: inherit; white-space: nowrap;
}
.btn-delete:hover { background: #fef2f2; border-color: #f87171; }

/* ═══ GHOST BUTTON ═══ */
.btn-ghost {
  background: #f8fafc; color: #475569;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  padding: 11px 22px; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: background 0.15s; font-family: inherit;
}
.btn-ghost:hover { background: #f1f5f9; }

/* ═══ MODAL ═══ */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(15,23,42,0.35);
  backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.modal {
  background: #fff; border-radius: 20px;
  padding: 40px 36px; max-width: 380px; width: 90%;
  text-align: center;
  box-shadow: 0 24px 48px rgba(0,0,0,0.18);
  animation: slideUp 0.25s ease;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.modal-icon-wrap {
  width: 58px; height: 58px; border-radius: 50%;
  background: #fef2f2; color: #ef4444;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 18px;
}
.modal h3 { font-size: 18px; font-weight: 800; color: #0f172a; margin: 0 0 10px; }
.modal p  { font-size: 14px; color: #64748b; margin: 0 0 26px; line-height: 1.6; }
.modal-btns { display: flex; gap: 12px; justify-content: center; }

/* ═══ RESPONSIVE ═══ */
@media (max-width: 900px) {
  .main-content { margin-left: 60px; }
  .profile-grid { grid-template-columns: 1fr; }
  .left-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
}
@media (max-width: 600px) {
  .profile-page { padding: 20px 16px; }
  .main-content { margin-left: 0; }
  .form-grid { grid-template-columns: 1fr; }
  .field.span-2 { grid-column: span 1; }
  .left-col { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 14px; }
  .btn-save { width: 100%; justify-content: center; }
}
</style>