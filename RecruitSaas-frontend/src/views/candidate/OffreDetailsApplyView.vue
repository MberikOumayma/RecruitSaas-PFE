<template>
  <div class="page-layout">
    <AppSidebar />

    <main class="main-content">
      <GlobalHeader title="Offre Details & Apply" />

      <!-- Scrollable Content -->
      <div class="content-scroll">
        <div class="content-inner">

          <!-- Toasts -->
          <teleport to="body">
            <transition name="hs-slide-down">
              <div v-if="alreadyAppliedError" class="hs-alert-top hs-alert-warn">
                <div class="hs-alert-icon"><span style="font-size: 16px;">⚠️</span></div>
                <div class="hs-alert-body">
                  <span class="hs-alert-title">Already Applied</span>
                  <span class="hs-alert-desc">You have already applied for this offer.</span>
                </div>
                <button class="hs-alert-close" @click="alreadyAppliedError = false">✕</button>
              </div>
            </transition>
            
            <transition name="hs-slide-down">
              <div v-if="applySuccess" class="hs-alert-top hs-alert-ok">
                <div class="hs-alert-icon"><span style="font-size: 16px;">✔️</span></div>
                <div class="hs-alert-body">
                  <span class="hs-alert-title">Application Sent!</span>
                  <span class="hs-alert-desc">Your candidature was submitted successfully.</span>
                </div>
                <button class="hs-alert-close" @click="applySuccess = false">✕</button>
              </div>
            </transition>

            <transition name="hs-slide-down">
              <div v-if="cancelSuccess" class="hs-alert-top hs-alert-ok">
                <div class="hs-alert-icon"><span style="font-size: 16px;">✔️</span></div>
                <div class="hs-alert-body">
                  <span class="hs-alert-title">Application Cancelled</span>
                  <span class="hs-alert-desc">Your application has been successfully withdrawn.</span>
                </div>
                <button class="hs-alert-close" @click="cancelSuccess = false">✕</button>
              </div>
            </transition>
          </teleport>

          <button class="hs-back" @click="goBack">
            <ChevronLeftIcon :size="16" />
            Back to Search
          </button>

          <div v-if="loading" class="hs-state"><div class="hs-spinner"></div></div>
          
          <div v-else-if="offer" class="preview-card">
            <!-- Hero -->
            <div class="hero-section">
              <div class="hero-content">
                <h1 class="hero-title">{{ offer.titre }}</h1>
                <div class="hero-meta">
                  <span class="meta-item">
                    <MapPinIcon :size="13" />
                    {{ offer.localisation || 'Remote' }}
                  </span>
                  <span class="meta-item">
                    <BriefcaseIcon :size="13" />
                    {{ companyName }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Body -->
            <div class="preview-body">
              <!-- Left: Content -->
              <div class="preview-main">
                <section>
                  <h3 class="section-heading">
                    <FileTextIcon :size="18" class="section-icon" />
                    Job Description
                  </h3>
                  <div class="section-text rich-content" v-html="offer.description || 'No description provided.'"></div>
                </section>

                <!-- Status Check Loading -->
                <section v-if="checkingApplication" class="app-form-preview app-form-checking">
                  <div class="hs-spinner"></div>
                  <p>Checking your application status...</p>
                </section>

                <!-- Already Applied - Message + Bouton Discard -->
                <section v-else-if="alreadyApplied" class="app-form-preview app-form-applied">
                  <div class="applied-icon">✓</div>
                  <h3 class="section-heading-sm applied-title">Already applied for this offer</h3>
                  <p class="applied-subtitle">
                    Your application was submitted<span v-if="appliedDate"> on <strong>{{ appliedDate }}</strong></span>. 
                    You can withdraw it at any time.
                  </p>
                  
                  <div v-if="cancelErr" class="hs-alert-warn applied-error">{{ cancelErr }}</div>
                  
                  <div class="applied-actions">
                    <button class="btn btn-ghost" @click="goBack">Back to offers</button>
                    <button class="btn btn-danger" :disabled="cancelling" @click="cancelApplication">
                      <span v-if="cancelling" class="hs-btn-spinner"></span>
                      {{ cancelling ? 'Discarding...' : 'Discard Application' }}
                    </button>
                  </div>
                </section>

                <section v-else-if="candidaturesClosed" class="app-form-preview app-form-closed">
                  <div class="applied-icon">📅</div>
                  <h3 class="section-heading-sm applied-title">Candidatures closes</h3>
                  <p class="applied-subtitle">
                    La date limite était le <strong>{{ deadlineDisplay }}</strong>. Il n'est plus possible de postuler pour cette offre.
                  </p>
                  <div class="applied-actions">
                    <button type="button" class="btn btn-ghost" @click="goBack">Retour aux offres</button>
                  </div>
                </section>

                <!-- Form - Affiché seulement si PAS déjà postulé et date limite non dépassée -->
                <section v-else class="app-form-preview">
                  <h3 class="section-heading-sm">Application Form</h3>
                  <p style="font-size: 12px; color: #64748b; margin-bottom: 20px;">Please provide the necessary documents and details to apply.</p>
                  
                  <form class="preview-form" @submit.prevent="submit">
                    <div class="form-row-2">
                      <div class="form-group">
                        <label class="form-label">Full Name <span class="req">*</span></label>
                        <input v-model="fullName" type="text" class="form-input" placeholder="Jane Doe" required />
                      </div>
                      <div class="form-group">
                        <label class="form-label">Email Address <span class="req">*</span></label>
                        <input v-model="email" type="email" class="form-input" placeholder="jane@example.com" required />
                      </div>
                    </div>
                    <div class="form-group">
                      <label class="form-label">Portfolio / LinkedIn URL</label>
                      <input v-model="portfolioUrl" type="url" class="form-input" placeholder="https://" />
                    </div>
                    
                    <div class="form-group">
                      <label class="form-label">CV / Resume Upload <span class="req">*</span></label>
                      <div class="upload-zone" :class="{ 'dz-over': dzOver, 'dz-done': cvFile }" @dragover.prevent="dzOver = true" @dragleave="dzOver = false" @drop.prevent="onDrop" @click="$refs.fileIn.click()">
                        <input ref="fileIn" type="file" accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.gif,.webp,.bmp,.tiff,.tif,.svg,.zip,.rar,.7z" style="display:none" @change="onFile" />
                        <template v-if="!cvFile">
                          <CloudUploadIcon :size="36" />
                          <p>Click or drag to upload your CV</p>
                          <small>PDF, DOCX, DOC, Images • Max 10MB</small>
                        </template>
                        <div v-else style="display: flex; align-items: center; gap: 10px; color: #1a2035; width: 100%; justify-content: center;">
                          <span>📄</span>
                          <strong>{{ cvFile.name }}</strong>
                          <span style="color: #64748b;">({{ formatSize(cvFile.size) }})</span>
                          <button type="button" @click.stop="cvFile = null" style="background:none; border:none; color:#ef4444; cursor:pointer;" title="Remove">✕</button>
                        </div>
                      </div>
                    </div>

                    <div class="form-group">
                      <label class="form-label">Why do you want to join us?</label>
                      <textarea v-model="motivation" class="form-textarea" placeholder="Tell us about your motivation..."></textarea>
                    </div>

                    <!-- Dynamic Requirements -->
                    <template v-if="formFields.length">
                      <div style="height: 1px; background: #e2e8f0; margin: 15px 0;"></div>
                      <h4 style="font-size: 13px; font-weight: 700; margin-bottom: 15px;">Additional Questions</h4>

                      <div v-for="f in formFields" :key="f.id" class="form-group">
                        <label class="form-label" style="text-transform: none; letter-spacing: normal;">
                          {{ f.question }}
                          <span v-if="f.estObligatoire" class="req">*</span>
                        </label>
                        <p v-if="f.optionsJson" style="font-size: 11px; color:#64748b; margin-bottom: 4px;">{{ f.optionsJson }}</p>

                        <template v-if="resolveType(f) === 'fichier'">
                          <div class="upload-zone" :class="{'dz-done': fileMap[String(f.id)], 'dz-error': fieldErrors[String(f.id)]}" @dragover.prevent="$set(customDzOver, f.id, true)" @dragleave="$set(customDzOver, f.id, false)" @drop.prevent="onCustomFileDrop($event, f.id)" @click="onCustomDzClick(f.id)" style="padding: 16px;">
                            <input :ref="'cfi_' + f.id" type="file" accept=".pdf,.doc,.docx,.png,.jpg,.jpeg" style="display:none" @change="onCustomFileChange($event, f.id)" />
                            <template v-if="!fileMap[String(f.id)]">
                              <CloudUploadIcon :size="24" />
                              <p>Upload a file</p>
                            </template>
                            <div v-else style="display: flex; align-items: center; gap: 10px; justify-content: center; width: 100%;">
                              <span>📄</span>
                              <strong>{{ fileMap[String(f.id)].name }}</strong>
                              <button type="button" @click.stop="clearCustomFile(f.id)" style="background:none; border:none; color:#ef4444; cursor:pointer;">✕</button>
                            </div>
                          </div>
                          <p v-if="fieldErrors[String(f.id)]" style="color:#ef4444; font-size: 11px; margin-top:4px;">{{ fieldErrors[String(f.id)] }}</p>
                        </template>

                        <template v-else-if="resolveType(f) === 'number'">
                          <input v-model.number="f.value" type="number" class="form-input" :class="{'input-error': fieldErrors[String(f.id)]}" :required="f.estObligatoire" min="0" @input="clearFieldError(f.id)" />
                          <p v-if="fieldErrors[String(f.id)]" style="color:#ef4444; font-size: 11px; margin-top:4px;">{{ fieldErrors[String(f.id)] }}</p>
                        </template>

                        <template v-else-if="resolveType(f) === 'textarea'">
                          <textarea v-model="f.value" class="form-textarea" :class="{'input-error': fieldErrors[String(f.id)]}" :required="f.estObligatoire" @input="clearFieldError(f.id)"></textarea>
                          <p v-if="fieldErrors[String(f.id)]" style="color:#ef4444; font-size: 11px; margin-top:4px;">{{ fieldErrors[String(f.id)] }}</p>
                        </template>

                        <template v-else>
                          <input v-model="f.value" type="text" class="form-input" :class="{'input-error': fieldErrors[String(f.id)]}" :required="f.estObligatoire" @input="clearFieldError(f.id)" />
                          <p v-if="fieldErrors[String(f.id)]" style="color:#ef4444; font-size: 11px; margin-top:4px;">{{ fieldErrors[String(f.id)] }}</p>
                        </template>
                      </div>
                    </template>
                    
                    <div v-if="applyErr" class="hs-alert-warn" style="padding: 10px; margin-top: 10px; color: #b91c1c;">{{ applyErr }}</div>

                    <!-- Actions -->
                    <div class="bottom-actions" style="margin-top: 20px;">
                      <button type="button" class="btn btn-ghost" @click="goBack">Cancel</button>
                      <button type="submit" class="btn btn-primary" :disabled="submitting || !cvFile">
                        <SendIcon v-if="!submitting" :size="16" />
                        <span v-if="submitting">Sending...</span>
                        <span v-else>Submit Application</span>
                      </button>
                    </div>

                  </form>
                </section>
              </div>

              <!-- Right: Sidebar info (cachée) -->
              <div class="preview-sidebar">
                <div class="info-card">
                  <h4 class="info-title-plain">Job Information</h4>
                  <ul class="settings-list">
                    <li><span>Posted</span><span>{{ daysAgo(offer.creeLe) }}</span></li>
                    <li v-if="deadlineDisplay">
                      <span>Date limite</span>
                      <span>{{ deadlineDisplay }}</span>
                    </li>
                    <li>
                      <span>Company</span>
                      <span>{{ companyName }}</span>
                    </li>
                  </ul>
                </div>
              </div>

            </div>
          </div>
          
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import {
  MapPinIcon, FileTextIcon, CloudUploadIcon, ChevronLeftIcon, SendIcon, BriefcaseIcon
} from 'lucide-vue-next'
import { getCandidatOffreById, getCandidatFormulaire, postuler, getCandidatProfile } from '../../services/candidatService'
import api from '../../services/api'

export default {
  name: 'OffreDetailsApplyView',
  components: {
    AppSidebar, GlobalHeader,
    MapPinIcon, FileTextIcon, CloudUploadIcon, ChevronLeftIcon, SendIcon, BriefcaseIcon
  },
  data() {
    return {
      loading: true,
      offer: null,
      score: 85,
      err: null,

      checkingApplication: true,
      alreadyApplied: false,
      appliedDate: '',
      cancelling: false,
      cancelErr: null,
      cancelSuccess: false,

      formFields: [],
      fileMap: {},
      customDzOver: {},
      fieldErrors: {},
      cvFile: null,
      cvPreviewUrl: null,
      fullName: '',
      email: '',
      portfolioUrl: '',
      motivation: '',
      dzOver: false,
      submitting: false,
      applyErr: null,
      applySuccess: false,
      alreadyAppliedError: false,
      _objectUrls: [],
    }
  },
  computed: {
    companyName() {
      const d = this.offer || {}
      return (
        d.entrepriseNom || d.nomEntreprise || d.entreprise?.nom || d.entreprise?.name || d.tenant?.nom || '—'
      )
    },
    candidaturesClosed() {
      const raw = this.offer?.dateLimiteCandidatures ?? this.offer?.DateLimiteCandidatures
      if (!raw) return false
      const lim = new Date(raw)
      const now = new Date()
      const limUtc = Date.UTC(lim.getUTCFullYear(), lim.getUTCMonth(), lim.getUTCDate())
      const nowUtc = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())
      return nowUtc > limUtc
    },
    deadlineDisplay() {
      const raw = this.offer?.dateLimiteCandidatures ?? this.offer?.DateLimiteCandidatures
      if (!raw) return ''
      return new Date(raw).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
    },
  },
  async mounted() {
    const id = this.$route.params.id
    if (!id) return this.goBack()

    this.score = Math.floor(Math.random() * 25) + 70

    try {
      this.loading = true
      const { data } = await getCandidatOffreById(id)
      this.offer = data
    } catch(e) {
      this.err = 'Failed to load offer details.'
    } finally {
      this.loading = false
    }

    if(this.offer) {
      await this.loadUserInfo()
      await this.checkAlreadyApplied(id)
      if (!this.alreadyApplied && !this.candidaturesClosed) {
        await this.fetchFormFields(id)
      }
    }
  },
  methods: {
    goBack() {
      this.$router.push('/offres')
    },
    daysAgo(d) {
      if (!d) return 'Recently'
      const diff = Math.floor((Date.now() - new Date(d)) / 86400000)
      if (diff === 0) return 'Today'
      return diff === 1 ? '1 day ago' : `${diff} days ago`
    },
    
    // Vérifie si l'utilisateur a déjà postulé à cette offre
    async checkAlreadyApplied(id) {
      this.checkingApplication = true
      try {
        const { data } = await api.get(`/candidat/postuler/check/${id}`)
        if (data?.hasApplied) {
          this.alreadyApplied = true
          // Optionnel : récupérer la date de candidature pour l'afficher
          try {
            const { data: cands } = await api.get('/candidat/mes-candidatures')
            const list = Array.isArray(cands) ? cands : (cands?.data || [])
            const found = list.find(c => String(c.offreId || c.OffreId) === String(id))
            if (found && (found.creeLe || found.CreeLe || found.datePostulation)) {
              this.appliedDate = new Date(found.creeLe || found.CreeLe || found.datePostulation).toLocaleDateString()
            }
          } catch { /* ignore si erreur */ }
        }
      } catch { /* ignore si erreur */ } 
      finally {
        this.checkingApplication = false
      }
    },

    // Annule la candidature (appel à l'API DELETE)
    async cancelApplication() {
      this.cancelErr = null
      this.cancelling = true
      try {
        await api.delete(`/candidat/postuler/${this.offer.id}`)
        this.alreadyApplied = false
        this.appliedDate = ''
        this.cancelSuccess = true
        // Afficher un toast de succès puis recharger le formulaire
        setTimeout(() => { 
          this.cancelSuccess = false
          if (!this.candidaturesClosed) {
            this.fetchFormFields(this.offer.id)
          }
        }, 3000)
      } catch (e) {
        this.cancelErr = e.response?.data?.message || 'Failed to discard application.'
      } finally {
        this.cancelling = false
      }
    },

    getJwtFromStorage() {
      const tokens = [localStorage.getItem('token'), localStorage.getItem('authToken')]
      return tokens.find(t => t) || ''
    },
    decodeToken(token) {
      try {
        const payload = token.split('.')[1]
        let base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
        const pad = base64.length % 4
        if (pad) base64 += '='.repeat(4 - pad)
        return JSON.parse(atob(base64))
      } catch { return {} }
    },
    async loadUserInfo() {
      const token = this.getJwtFromStorage()
      const d = this.decodeToken(token)
      let em = localStorage.getItem('email') || d.email || d['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'] || ''
      let nm = localStorage.getItem('fullName') || d.name || d.username || ''
      this.fullName = nm
      this.email = em

      try {
        const res = await api.get('/candidat/profile')
        const p = res?.data?.data || res?.data || {}
        if(p.fullName) this.fullName = p.fullName
        if(p.email) this.email = p.email
      } catch { /* ignore */ }
    },
    async fetchFormFields(id) {
      try {
        const { data } = await getCandidatFormulaire(id)
        if (data && data.champsPersonnalises) {
          this.formFields = data.champsPersonnalises.map(f => ({
            ...f,
            question: f.question || f.nom,
            type: f.type || 'Texte',
            value: ''
          })).sort((a,b) => (a.ordre || 0) - (b.ordre || 0))
        }
      } catch { this.formFields = [] }
    },
    resolveType(f) {
      const t = String(f.type).toLowerCase()
      if (t === 'fichier' || t === '4') return 'fichier'
      if (t === 'nombre' || t === '1') return 'number'
      if (t === 'texte_long' || t === 'textarea') return 'textarea'
      return 'text'
    },
    formatSize(bytes) {
      if(!bytes) return ''
      if(bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB'
      return (bytes/(1024*1024)).toFixed(1) + ' MB'
    },
    onFile(e) {
      this.cvFile = e.target.files[0] || null
    },
    onDrop(e) {
      this.dzOver = false
      this.cvFile = e.dataTransfer.files[0] || null
    },
    onCustomDzClick(fid) {
      const ref = this.$refs['cfi_'+fid]
      if(ref) (Array.isArray(ref) ? ref[0] : ref).click()
    },
    onCustomFileChange(e, fid) {
      this.fileMap = { ...this.fileMap, [fid]: e.target.files[0] }
      this.clearFieldError(fid)
    },
    onCustomFileDrop(e, fid) {
      this.fileMap = { ...this.fileMap, [fid]: e.dataTransfer.files[0] }
      this.clearFieldError(fid)
    },
    clearCustomFile(fid) {
      this.fileMap = { ...this.fileMap, [fid]: null }
    },
    clearFieldError(fid) {
      this.fieldErrors = { ...this.fieldErrors, [fid]: null }
    },
    validateCustomFields() {
      let valid = true
      const errs = {}
      for(const f of this.formFields) {
        if(!f.estObligatoire) continue
        const fid = String(f.id)
        const type = this.resolveType(f)
        if(type === 'fichier') {
          if(!this.fileMap[fid]) { errs[fid] = 'Required'; valid = false }
        } else {
          if(!f.value && f.value !== 0) { errs[fid] = 'Required'; valid = false }
        }
      }
      this.fieldErrors = errs
      return valid
    },
    async submit() {
      this.applyErr = null
      if (this.candidaturesClosed) {
        this.applyErr = 'Les candidatures sont closes pour cette offre.'
        return
      }
      if(!this.cvFile) { this.applyErr = 'Please upload your CV.'; return; }
      if(!this.validateCustomFields()) return;

      this.submitting = true
      try {
        const formData = new FormData()
        formData.append('offreId', this.offer.id)
        formData.append('fullName', this.fullName)
        formData.append('email', this.email)
        formData.append('portfolioUrl', this.portfolioUrl)
        formData.append('motivation', this.motivation)
        formData.append('cv', this.cvFile)

        const customObj = {}
        this.formFields.forEach((f, idx) => {
          if(this.resolveType(f) === 'fichier') {
            const file = this.fileMap[String(f.id)]
            if(file) {
              formData.append('customFile_'+idx, file)
              formData.append('customFile_'+idx+'_question', f.question)
            }
          } else {
            if(f.value !== '' && f.value !== null) customObj[f.question] = f.value
          }
        })
        if(Object.keys(customObj).length) {
          formData.append('champsPersonnalises', JSON.stringify(customObj))
        }

        await postuler(formData)
        this.applySuccess = true
        window.scrollTo({ top: 0, behavior: 'smooth' })
        setTimeout(() => {
          this.$router.push('/applications')
        }, 1500)
      } catch (e) {
        if(e.response?.status === 409) {
          this.alreadyAppliedError = true
          this.alreadyApplied = true
        } else {
          this.applyErr = e.response?.data?.message || 'Server error.'
        }
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
/* ── Global Layout ── */
.page-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f5f7f8;
  font-family: 'Inter', sans-serif;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
}

.content-inner {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-sizing: border-box;
}

.hs-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: #3b5bdb;
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  font-family: inherit;
  margin-bottom: 8px;
}
.hs-back:hover { opacity: .7; }

/* ── Carte Principale ── */
.preview-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  width: 100%;
  margin-bottom: 20px;
}

/* ── Hero Section ── */
.hero-section {
  background: linear-gradient(135deg, #454a83 0%, #30345d 100%);
  min-height: 180px;
  display: flex;
  align-items: flex-end;
  padding: 40px 48px;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hero-title {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.hero-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #cbd5e1;
}

/* ── Preview Body ── */
.preview-body {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
}

.preview-main {
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
  padding: 40px 48px;
  box-sizing: border-box;
}

/* ── Sections Texte ── */
.section-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px;
  color: #0f172a;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.section-icon { color: #454a83; }

.section-text {
  font-size: 14px;
  color: #0c0d0f;
  line-height: 1.7;
  margin: 0;
  text-align: left;
}
.rich-content :deep(p) { margin-bottom: 1em; }
.rich-content :deep(h2) { font-size: 1.1rem; font-weight: 700; margin: 1.25rem 0 0.5rem; color: #0f172a; }

/* ── FORMULAIRE ── */
.app-form-preview {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 48px;
  width: 100%;
  margin-top: 32px;
  box-sizing: border-box;
}

/* État "Checking" */
.app-form-checking {
  text-align: center;
  padding: 60px 48px;
}

/* État "Already Applied" */
.app-form-applied {
  background: #f0fdf4;
  border: 2px solid #86efac;
  border-radius: 16px;
  padding: 48px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.app-form-closed {
  background: #fffbeb;
  border: 2px solid #fcd34d;
  border-radius: 16px;
  padding: 48px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.app-form-closed .applied-title {
  color: #92400e;
}

.app-form-closed .applied-subtitle {
  color: #a16207;
}

.applied-icon {
  width: 64px;
  height: 64px;
  background: #16a34a;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.applied-title {
  font-size: 20px;
  color: #166534;
  margin: 0;
}

.applied-subtitle {
  font-size: 14px;
  color: #166534;
  margin: 0;
  max-width: 400px;
  line-height: 1.5;
}

.applied-error {
  margin: 0;
  width: 100%;
  max-width: 400px;
}

.applied-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

.section-heading-sm {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px;
  color: #0f172a;
}

/* Formulaire principal en colonne unique */
.preview-form { 
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

/* Row 2 colonnes pour Full Name et Email */
.form-row-2 { 
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  width: 100%;
}

.form-group { 
  display: flex; 
  flex-direction: column; 
  gap: 8px;
  width: 100%;
}

.form-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: #475569;
}
.req { color: #ef4444; margin-left: 2px; }

.form-input {
  width: 100%;
  background: #fff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  color: #1e293b;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-input:focus { 
  border-color: #454a83; 
  outline: none;
  box-shadow: 0 0 0 3px rgba(69, 74, 131, 0.1);
}
.input-error { border-color: #ef4444; }

.form-textarea {
  width: 100%;
  background: #fff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  color: #1e293b;
  height: 120px;
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
}
.form-textarea:focus { 
  border-color: #454a83; 
  outline: none;
  box-shadow: 0 0 0 3px rgba(69, 74, 131, 0.1);
}

.upload-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #64748b;
  font-size: 13px;
  cursor: pointer;
  background: #fff;
  transition: all 0.2s;
  width: 100%;
  box-sizing: border-box;
  text-align: center;
}
.upload-zone:hover, .dz-over { 
  border-color: #454a83; 
  background: #f0f4ff; 
  color: #454a83; 
}
.dz-done { 
  border-color: #10b981; 
  background: #f0fdf4; 
  color: #047857; 
  border-style: solid;
}
.dz-error { 
  border-color: #ef4444; 
  background: #fef2f2; 
}

.hs-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 20px 0;
  width: 100%;
}

/* ── Sidebar ── */
.preview-sidebar { 
  display: none;
}

/* ── Alertes ── */
.hs-alert-warn { 
  background: #fff7ed; 
  border: 1px solid #fed7aa; 
  border-radius: 8px; 
  padding: 12px;
  font-size: 13px; 
  color: #9a3412;
  margin-top: 10px;
}

/* ── Boutons ── */
.bottom-actions { 
  display: flex; 
  justify-content: flex-end; 
  gap: 16px; 
  align-items: center;
  padding-top: 32px;
  border-top: 1px solid #e2e8f0;
  margin-top: 20px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-primary { 
  background: #454a83; 
  color: #fff; 
}
.btn-primary:hover:not(:disabled) { 
  background: #383c6a;
}
.btn-primary:disabled { 
  opacity: 0.5; 
  cursor: not-allowed; 
}

.btn-ghost { 
  background: transparent; 
  color: #64748b; 
}
.btn-ghost:hover { 
  color: #0f172a;
  background: #f1f5f9;
}

.btn-outline { 
  background: transparent; 
  border: 1px solid #e2e8f0; 
  color: #334155; 
}
.btn-outline:hover { 
  background: #f8fafc; 
}

/* Bouton Danger (Discard) */
.btn-danger {
  background: #ef4444;
  color: white;
  border: none;
}
.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}
.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Spinner pour bouton */
.hs-btn-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: hs-spin 0.6s linear infinite;
  vertical-align: middle;
  margin-right: 6px;
}

/* ── Toasts ── */
.hs-alert-top {
  position: fixed; 
  top: 24px; 
  left: 50%; 
  transform: translateX(-50%); 
  z-index: 99999;
  min-width: 380px; 
  max-width: 580px; 
  border-radius: 12px; 
  padding: 16px;
  display: flex; 
  align-items: center; 
  gap: 12px; 
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  font-family: 'Inter', sans-serif; 
  background: #fff;
  border: 1px solid #e2e8f0;
}
.hs-alert-ok { 
  border-left: 4px solid #10b981;
}
.hs-alert-warn { 
  border-left: 4px solid #f59e0b;
}
.hs-alert-title { 
  display: block; 
  font-size: 14px; 
  font-weight: 700; 
  color: #1a2035; 
}
.hs-alert-desc { 
  display: block; 
  font-size: 13px; 
  color: #64748b; 
  margin-top: 2px; 
}
.hs-alert-close { 
  margin-left: auto; 
  background: none; 
  border: none; 
  cursor: pointer; 
  color: #94a3b8; 
  font-size: 18px; 
  padding: 0 4px;
}
.hs-slide-down-enter-active, 
.hs-slide-down-leave-active { 
  transition: all 0.3s ease; 
}
.hs-slide-down-enter-from, 
.hs-slide-down-leave-to { 
  opacity: 0; 
  transform: translate(-50%, -20px); 
}

/* ── Loading ── */
.hs-state { text-align: center; padding: 80px 20px; color: #94a3b8; }
.hs-spinner {
  width: 40px; height: 40px; border: 3px solid #e2e8f0; border-top-color: #454a83; border-radius: 50%;
  animation: hs-spin .8s linear infinite; margin: 0 auto 16px;
}
@keyframes hs-spin { to { transform: rotate(360deg); } }

/* ── Responsive ── */
@media (max-width: 1024px) {
  .content-inner { padding: 0 24px; }
  .hero-section { padding: 32px; }
  .preview-main { padding: 32px; }
  .app-form-preview { padding: 32px; }
  .app-form-applied { padding: 32px; }
}

@media (max-width: 768px) {
  .content-inner { padding: 0 16px; }
  .hero-section { padding: 24px; }
  .hero-title { font-size: 22px; }
  .preview-main { padding: 24px; }
  .app-form-preview { padding: 24px; }
  .app-form-applied { padding: 24px; }
  
  .form-row-2 { 
    grid-template-columns: 1fr; 
  }
  
  .bottom-actions,
  .applied-actions {
    flex-direction: column-reverse;
    width: 100%;
  }
  .btn { width: 100%; }
}
</style>