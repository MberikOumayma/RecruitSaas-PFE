<template>
  <div class="page-layout">
    <AppSidebar />

    <main class="main-content">
      <!-- Header -->
      <GlobalHeader :title="isEditing ? 'Edit Job Offer' : 'Create New Job'" />

      <!-- Stepper -->
      <div class="stepper-bar">
        <AppStepper :current-step="1" />
      </div>

      <!-- Scrollable form area -->
      <div class="content-scroll">
        <div class="content-inner">
          <div class="section-header">
            <h3 class="section-title">Job Offer Details</h3>
            <p class="section-sub">Define the core aspects of your job listing. This information will be visible to
              potential candidates.</p>
          </div>

          <form class="job-form" @submit.prevent>
            <div class="form-grid">

              <!-- Company -->
              <div class="form-group">
                <label class="form-label">Company</label>
                <div class="select-wrapper">
                  <select v-model="form.company" class="form-select">
                    <option value="">Select a company</option>
                    <option v-for="e in entreprises" :key="e.id" :value="e.id">
                      {{ e.nom }}
                    </option>
                  </select>
                  <ChevronDownIcon :size="16" class="select-icon" />
                </div>
              </div>

              <!-- Job Title -->
              <div class="form-group">
                <label class="form-label">Job Title</label>
                <input v-model="form.title" type="text" class="form-input" placeholder="e.g. Senior Product Designer" />
              </div>

              <!-- Job Description -->
              <div class="form-group form-group-full">
                <label class="form-label">Job Description</label>
                <Editor 
                  v-model="form.description" 
                  placeholder="Describe the role, responsibilities, and requirements..." 
                />
              </div>

              <!-- Location -->
              <div class="form-group">
                <label class="form-label">Location</label>
                <div class="input-icon-wrapper">
                  <MapPinIcon :size="16" class="input-icon" />
                  <input v-model="form.location" type="text" class="form-input with-icon"
                    placeholder="City, Country or Remote" />
                </div>
              </div>

              <!-- Contract Type -->
              <div class="form-group">
                <label class="form-label">Contract Type</label>
                <div class="select-wrapper">
                  <select v-model="form.contractType" class="form-select">
                    <option disabled value="">Select a type</option>
                    <option value="CDI">Permanent (CDI)</option>
                    <option value="CDD">Fixed-term (CDD)</option>
                    <option value="Freelance">Freelance</option>
                    <option value="Stage">Internship</option>
                    <option value="Alternance">Apprenticeship</option>
                    <option value="Interim">Temporary</option>
                  </select>
                  <ChevronDownIcon :size="16" class="select-icon" />
                </div>
              </div>

              <!-- Date limite de candidature (dernier jour inclus) -->
              <div class="form-group">
                <label class="form-label">Application deadline</label>
                <div class="input-icon-wrapper">
                  <CalendarIcon :size="16" class="input-icon" />
                  <input
                    v-model="form.dateLimite"
                    type="date"
                    class="form-input with-icon"
                    :min="minDateLimite"
                  />
                </div>
                <p class="field-hint">After this date (inclusive), candidates can no longer apply. Leave empty for no deadline.</p>
              </div>

              <!-- Public Link Toggle Removed -->

            </div>

            <!-- Footer Actions -->
            <div class="form-footer">
              <button type="button" class="btn btn-ghost" @click="$router.back()">
                <XIcon :size="16" />
                Cancel
              </button>
              <div class="footer-right">
                <button class="btn btn-primary" @click="handlesave">
                  <EyeIcon :size="16" /> jump to preview
                </button>
                <button class="btn btn-primary" @click="handleNext" :disabled="isSubmitting">
                  <span v-if="isSubmitting">Saving...</span>
                  <span v-else>Next: Configuration</span>
                  <ArrowRightIcon v-if="!isSubmitting" :size="16" />
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { createOffre, updateOffre, getOffreById, getEntreprises, initializeForm } from '../../services/offreService'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import AppStepper from '../../components/common/AppStepper.vue'
import Editor from '../../components/common/Editor.vue'
import {
  EyeIcon, ChevronDownIcon,
  MapPinIcon, XIcon, ArrowRightIcon, CalendarIcon
} from 'lucide-vue-next'

import { useNotification } from '../../composables/useNotification'

export default {
  name: 'CreateJobStep1',
  components: {
    AppSidebar, GlobalHeader, AppStepper, Editor,
    EyeIcon, ChevronDownIcon,
    MapPinIcon, XIcon, ArrowRightIcon, CalendarIcon
  },
  setup() {
    const { toast } = useNotification()
    return { toast }
  },
  data() {
    return {
      entreprises: [],
      isSubmitting: false,
      isEditing: false,
      offreId: null,
      form: {
        company: '',
        title: '',
        description: '',
        location: '',
        contractType: '',
        dateLimite: '',
      },
      initialFormStr: ''
    }
  },
  computed: {
    minDateLimite() {
      const t = new Date()
      const y = t.getFullYear()
      const m = String(t.getMonth() + 1).padStart(2, '0')
      const d = String(t.getDate()).padStart(2, '0')
      return `${y}-${m}-${d}`
    },
  },
  async mounted() {
    this.fetchEntreprises()
    const id = this.$route.params.id
    if (id && id !== 'new') {
      this.isEditing = true
      this.offreId = id
      await this.loadOfferData(id)
    }
  },
  methods: {
    async loadOfferData(id) {
      try {
        const res = await getOffreById(id)
        const o = res.data
        if (o) {
          this.form.company = o.entrepriseId || ''
          this.form.title = o.titre || ''
          this.form.description = o.description || ''
          this.form.location = o.localisation || ''
          this.form.contractType = o.typeContrat || ''
          const dl = o.dateLimiteCandidatures ?? o.DateLimiteCandidatures
          this.form.dateLimite = dl ? String(dl).slice(0, 10) : ''
          
          this.initialFormStr = JSON.stringify(this.form)
        }
      } catch (err) {
        console.error("Failed to load offer data", err)
      }
    },
    async handleNext() {
      if (!this.form.title || !this.form.company || this.form.contractType === '') {
        this.toast.warning("Please fill required fields (Title, Company, Contract Type).")
        return
      }
      if (!this.validateDateLimite()) return
      
      const isDirty = this.initialFormStr !== JSON.stringify(this.form)
      if (this.isEditing && !isDirty) {
        this.$router.push(`/recruiter/jobs/create/${this.offreId}/step2`)
        return
      }

      this.isSubmitting = true
      try {
        const payload = {
          entrepriseId: this.form.company,
          titre: this.form.title,
          description: this.form.description,
          localisation: this.form.location,
          typeContrat: this.form.contractType,
          dateLimiteCandidatures: this.dateLimitePayload(),
        }

        let currentId = this.offreId

        if (this.isEditing) {
          await updateOffre(this.offreId, payload)
          this.toast.success("Job offer updated successfully.")
        } else {
          const res = await createOffre(payload)
          currentId = res?.data?.id || res?.data
          await initializeForm(currentId)
          this.toast.success("offer created successfully.")
        }

        this.$router.push(`/recruiter/jobs/create/${currentId}/step2`)
      } catch (err) {
        console.error("Operation failed", err)
        const validationErrors = err?.response?.data?.errors
          ? Object.values(err.response.data.errors).flat().join(' | ')
          : null
        const apiMsg = err?.response?.data?.message
          || err?.response?.data?.title
          || validationErrors
          || "Failed to save job offer."
        this.toast.error(apiMsg)
      } finally {
        this.isSubmitting = false
      }
    },
    async handlesave() {
      if (!this.form.title || !this.form.company || this.form.contractType === '') {
        this.toast.warning("Please fill required fields (Title, Company, Contract Type).")
        return
      }
      if (!this.validateDateLimite()) return
      
      const isDirty = this.initialFormStr !== JSON.stringify(this.form)
      let currentId = this.offreId

      if (this.isEditing && !isDirty) {
        this.$router.push(`/recruiter/jobs/create/${currentId}/step3`)
        return
      }

      this.isSubmitting = true
      try {
        const payload = {
          entrepriseId: this.form.company,
          titre: this.form.title,
          description: this.form.description,
          localisation: this.form.location,
          typeContrat: this.form.contractType,
          dateLimiteCandidatures: this.dateLimitePayload(),
        }

        let currentId = this.offreId

        if (this.isEditing) {
          await updateOffre(this.offreId, payload)
          this.toast.success("Job offer updated successfully.")
        } else {
          const res = await createOffre(payload)
          currentId = res?.data?.id || res?.data
          this.toast.success("Draft saved successfully.")
        }

        this.$router.push(`/recruiter/jobs/create/${currentId}/step3`)
      } catch (err) {
        console.error("Operation failed", err)
        const validationErrors = err?.response?.data?.errors
          ? Object.values(err.response.data.errors).flat().join(' | ')
          : null
        const apiMsg = err?.response?.data?.message
          || err?.response?.data?.title
          || validationErrors
          || "Failed to save job offer."
        this.toast.error(apiMsg)
      } finally {
        this.isSubmitting = false
      }
    },
    dateLimitePayload() {
      if (!this.form.dateLimite || String(this.form.dateLimite).trim() === '') return null
      return `${this.form.dateLimite}T00:00:00.000Z`
    },
    validateDateLimite() {
      if (!this.form.dateLimite) return true
      if (this.form.dateLimite < this.minDateLimite) {
        this.toast.warning('The application deadline cannot be in the past.')
        return false
      }
      return true
    },
    async fetchEntreprises() {
      try {
        const res = await getEntreprises()
        this.entreprises = res.data || []
      } catch (err) {
        console.error("Failed to load entreprises", err)
      }
    }
  }
}
</script>

<style scoped>
/* ── Layout ── */
.page-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #F5F7FA;
  font-family: 'Inter', sans-serif;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}



/* ── Stepper bar ── */
.stepper-bar {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

/* ── Content scroll ── */
.content-scroll {
  flex: 1;
  overflow-y: auto;
}

.content-scroll::-webkit-scrollbar {
  width: 4px;
}

.content-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.content-inner {
  max-width: 860px;
  margin: 0 auto;
  padding: 32px;
}

/* ── Section header ── */
.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 6px;
  color: #0f172a;
}

.section-sub {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

/* ── Form ── */
.job-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group-full {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}

.field-hint {
  font-size: 11px;
  color: #64748b;
  margin: 0;
  line-height: 1.45;
}

.form-input,
.form-select {
  height: 44px;
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0 14px;
  font-size: 13px;
  background: #fff;
  color: #0f172a;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus {
  border-color: #454a83;
  box-shadow: 0 0 0 3px rgba(69, 74, 131, 0.12);
}

/* Select wrapper with icon */
.select-wrapper {
  position: relative;
}

.form-select {
  appearance: none;
  padding-right: 36px;
}

.select-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

/* Input with left icon */
.input-icon-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.form-input.with-icon {
  padding-left: 36px;
}

/* Toggle switch */
.form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.footer-right {
  display: flex;
  gap: 12px;
}

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s, background 0.15s;
}

.btn-primary {
  background: #454a83;
  color: #fff;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-outline {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #334155;
}

.btn-outline:hover {
  background: #f8fafc;
}

.btn-ghost {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #475569;
}

.btn-ghost:hover {
  background: #f1f5f9;
}
</style>
