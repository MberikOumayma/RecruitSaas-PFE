<template>
  <div class="page-layout">
    <AppSidebar />

    <main class="main-content">
      <!-- Header -->
      <GlobalHeader title="Create Job Offer" />

      <!-- Stepper -->
      <div class="stepper-bar">
        <AppStepper :current-step="3" />
      </div>

      <!-- Scrollable Content -->
      <div class="content-scroll">
        <div class="content-inner">

          <!-- Preview Card -->
          <div class="preview-card">
            <!-- Preview banner -->
            <div class="preview-banner">
              <span class="preview-banner-label">Candidate Preview Mode</span>
              <div class="browser-dots">
                <span class="dot red" />
                <span class="dot yellow" />
                <span class="dot green" />
              </div>
            </div>

            <!-- Hero -->
            <div class="hero-section">
              <div class="hero-content">
                <h1 class="hero-title">{{ offer.title || 'Senior Full-Stack Engineer' }}</h1>
                <div class="hero-meta">
                  <span class="meta-item">
                    <MapPinIcon :size="13" />
                    {{ offer.location }}
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

                <!-- Application Form preview -->
                <section class="app-form-preview">
                  <h3 class="section-heading-sm">Application Form</h3>
                  <form class="preview-form" @submit.prevent>
                    <div class="form-row-2">
                      <div class="form-group">
                        <label class="form-label">Full Name</label>
                        <input type="text" class="form-input" placeholder="Jane Doe" disabled />
                      </div>
                      <div class="form-group">
                        <label class="form-label">Email Address</label>
                        <input type="email" class="form-input" placeholder="jane@example.com" disabled />
                      </div>
                    </div>
                    <div class="form-group">
                      <label class="form-label">Portfolio / LinkedIn URL</label>
                      <input type="text" class="form-input" placeholder="https://" disabled />
                    </div>
                    <div class="form-group">
                      <label class="form-label">CV / Resume Upload</label>
                      <div class="upload-zone">
                        <CloudUploadIcon :size="36" />
                        <p>Click or drag to upload (PDF, DOCX)</p>
                      </div>
                    </div>
                    <div class="form-group">
                      <label class="form-label">Why do you want to join us?</label>
                      <textarea class="form-textarea" placeholder="Tell us about your motivation..."
                        disabled></textarea>
                    </div>

                    <!-- Dynamic Custom Fields -->
                    <div v-for="field in formFields" :key="field.id" class="form-group">
                      <label class="form-label" style="text-transform: none; letter-spacing: normal;">
                        {{ field.nom }}
                        <span v-if="field.estObligatoire" style="color: #ef4444; margin-left: 2px;">*</span>
                      </label>

                      <template v-if="field.type === 'Texte' || field.type === 0">
                        <input type="text" class="form-input" :placeholder="field.question" disabled />
                      </template>
                      <template v-else-if="field.type === 'Nombre' || field.type === 1">
                        <input type="number" class="form-input" disabled />
                      </template>
                      <template v-else-if="field.type === 'Date' || field.type === 2">
                        <input type="date" class="form-input" disabled />
                      </template>
                      <template v-else-if="field.type === 'ChoixMultiple' || field.type === 3">
                        <select class="form-input" disabled>
                          <option>Select an option...</option>
                        </select>
                      </template>
                      <template v-else-if="field.type === 'Fichier' || field.type === 4">
                        <div class="upload-zone" style="padding: 16px;">
                          <CloudUploadIcon :size="24" />
                          <p>Upload a file</p>
                        </div>
                      </template>
                    </div>
                  </form>
                </section>
              </div>

              <!-- Right: Sidebar info -->
              <div class="preview-sidebar">
                <!-- Internal Experts -->
                <div class="info-card primary-border">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                    <h4 class="info-title" style="margin-bottom: 0;">
                      <ShieldCheckIcon :size="15" />
                      Assigned Members
                    </h4>
                    <button @click="isAssignExpertsModalOpen = true" style="  font-size: 12px; font-weight: 700; color: #454a83; cursor: pointer; ">
                      Assign
                    </button>
                  </div>
                  <div class="experts-list">
                    <div v-for="expert in experts" :key="expert.id || expert.nom" class="expert-row">
                      <div class="avatar-placeholder">
                        <img v-if="expert.nom"
                          :src="'https://ui-avatars.com/api/?name=' + encodeURIComponent(expert.nom)"
                          style="border-radius: 50%; width: 100%; height: 100%; object-fit: cover;" />
                      </div>
                      <div>
                        <p class="expert-name">{{ expert.nom }}</p>
                        <p class="expert-role">{{ expert.poste }}</p>
                      </div>
                    </div>
                    <div v-if="experts.length === 0" style="font-size: 11px; color: #94a3b8; font-style: italic;">No
                      experts assigned.
                    </div>
                  </div>
                </div>

                <!-- Job Settings -->
                <div class="info-card">
                  <h4 class="info-title-plain">Job Settings</h4>
                  <ul class="settings-list">
                    <li><span>Status</span><span :class="offer.estPublie ? 'status-published' : 'status-draft'">{{
                      offer.estPublie ?
                        'Published' : 'Draft' }}</span></li>
                    <li>
                      <span>Visibility</span>
                      <div style="display: flex; align-items: center; gap: 8px;">
                        <span :style="{ color: offer.isPublicLinkEnabled ? '#16a34a' : '#64748b' }">{{ offer.isPublicLinkEnabled ? 'Link Enabled' : 'Link Disabled' }}</span>
                        <button v-if="offer.isPublicLinkEnabled" class="icon-btn" title="Copy link" @click="copyLinkToClipboard" style="padding: 2px; border: none; background: transparent; cursor: pointer; color: #454a83;">
                          <CopyIcon :size="14" />
                        </button>
                      </div>
                    </li>
                    <li><span>Applications</span><span>0</span></li>
                    <li><span>Created</span><span>Oct 24, 2023</span></li>
                  </ul>
                </div>
              </div>

            </div>
          </div>

          <!-- Actions -->
          <div class="bottom-actions">
            <button class="btn btn-ghost" @click="$router.push(`/recruiter/jobs/create/${$route.params.id}/step2`)">
              <ChevronLeftIcon :size="18" />
              Back to configuration
            </button>
            <div class="actions-right">
              <button class="btn btn-outline" @click="saveAsDraft">
                <FileClock :size="16" />
                Save as Draft
              </button>
              <button class="btn btn-primary" @click="publishOffer" :disabled="isSubmitting">
                <SendIcon v-if="!isSubmitting" :size="16" />
                <span v-if="isSubmitting">Publishing...</span>
                <span v-else>Publish Offer</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Modals -->
    <AssignExpertsModal 
      :isOpen="isAssignExpertsModalOpen" 
      :offreId="$route.params.id" 
      @close="isAssignExpertsModalOpen = false"
      @saved="loadOfferDetails" 
    />
  </div>
</template>

<script>
import { getOffreById, changePublicationStatus } from '../../services/offreService'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import AppStepper from '../../components/common/AppStepper.vue'
import AssignExpertsModal from '../../components/modals/AssignExpertsModal.vue'
import {
  ArrowLeftIcon, BellIcon, CheckCircleIcon, MapPinIcon, BanknoteIcon,
  FileTextIcon, CloudUploadIcon, ShieldCheckIcon, ChevronLeftIcon, SendIcon, FileClock, CopyIcon
} from 'lucide-vue-next'

import { useNotification } from '../../composables/useNotification'

export default {
  name: 'CreateJobStep3',
  components: {
    AppSidebar, GlobalHeader, AppStepper, AssignExpertsModal,
    ArrowLeftIcon, BellIcon, CheckCircleIcon, MapPinIcon, BanknoteIcon,
    FileTextIcon, CloudUploadIcon, ShieldCheckIcon, ChevronLeftIcon, SendIcon, FileClock, CopyIcon
  },
  setup() {
    const { toast } = useNotification()
    return { toast }
  },
  data() {
    return {
      isSubmitting: false,
      offer: {},
      experts: [],
      formFields: [],
      isAssignExpertsModalOpen: false
    }
  },
  mounted() {
    this.loadOfferDetails()
  },
  methods: {
    async loadOfferDetails() {
      const offreId = this.$route.params.id
      if (!offreId || offreId === 'new') return
      try {
        const res = await getOffreById(offreId)
        const data = res.data
        this.offer = {
          title: data.titre,
          location: data.localisation,
          description: data.description,
          estPublie: data.estPublie,
          isPublicLinkEnabled: data.isPublicLinkEnabled,
          lienPublic: data.lienPublic
        }
        this.experts = data.experts || []
        this.formFields = data.formulaire?.champs || []
      } catch (err) {
        console.error("Failed to load offer details", err)
      }
    },
    async publishOffer() {
      const offreId = this.$route.params.id
      if (!offreId || offreId === 'new') {
        this.toast.error("No offer found to publish.")
        return
      }
      this.isSubmitting = true
      try {
        await changePublicationStatus(offreId, true)
        this.toast.success("Offer published successfully!")
        this.$router.push('/recruiter/jobs')
      } catch (err) {
        console.error("Failed to publish", err)
        this.toast.error("Failed to publish offer.")
      } finally {
        this.isSubmitting = false
      }
    },
    async saveAsDraft() {
      const offreId = this.$route.params.id
      try {
        await changePublicationStatus(offreId, false)
        this.toast.info("Offer saved as draft.")
        this.$router.push('/recruiter/jobs')
      } catch (err) {
        console.error("Failed to save", err)
        this.toast.error("Failed to save draft.")
      } 
    },
    copyLinkToClipboard() {
      if (!this.offer.lienPublic) return;
      navigator.clipboard.writeText(this.offer.lienPublic)
        .then(() => {
          this.toast.info("Link copied to clipboard!");
        })
        .catch(err => console.error("Failed to copy link:", err));
    }
  }
}
</script>

<style scoped>
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




.project-check {
  color: #454a83;
}

/* ── Stepper ── */
.stepper-bar {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

/* ── Content ── */
.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.content-scroll::-webkit-scrollbar {
  width: 4px;
}

.content-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.content-inner {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── Preview card ── */
.preview-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.preview-banner {
  background: #0f2120;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.preview-banner-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.5);
}

.browser-dots {
  display: flex;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.red {
  background: #f87171;
}

.dot.yellow {
  background: #fbbf24;
}

.dot.green {
  background: #4ade80;
}

/* ── Hero ── */
.hero-section {
  background: linear-gradient(135deg, #454a83 0%, #30345d 100%);
  min-height: 200px;
  display: flex;
  align-items: flex-end;
  padding: 32px;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hero-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 4px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: fit-content;
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

/* ── Preview body ── */
.preview-body {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 28px;
  padding: 28px;
}

.preview-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Sections */
.section-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 10px;
  color: #0f172a;
}

.section-icon {
  color: #454a83;
}

.section-text {
  font-size: 13px;
  color: #0c0d0f;
  line-height: 1.7;
  margin: 0;
  text-align: left;
}

.rich-content :deep(p) {
  margin-bottom: 1em;
}

.rich-content :deep(h2) {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 1.25rem 0 0.5rem;
  color: #0f172a;
}

.rich-content :deep(h3) {
  font-size: 1rem;
  font-weight: 700;
  margin: 1rem 0 0.5rem;
  color: #0f172a;
}

.rich-content :deep(ul),
.rich-content :deep(ol) {
  padding-left: 1.25rem;
  margin-bottom: 1rem;
}

.rich-content :deep(li) {
  margin-bottom: 0.25rem;
}

.rich-content :deep(a) {
  color: #454a83;
  text-decoration: underline;
}

/* Application form preview */
.app-form-preview {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.section-heading-sm {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 16px;
  color: #0f172a;
}

.preview-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(15, 33, 32, 0.6);
}

.form-input {
  width: 100%;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  color: #475569;
  box-sizing: border-box;
}

.upload-zone {
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
  font-size: 13px;
}

.form-textarea {
  width: 100%;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  color: #475569;
  height: 80px;
  resize: none;
  box-sizing: border-box;
  font-family: inherit;
}

/* ── Right sidebar ── */
.preview-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 18px;
}

.info-card.primary-border {
  border-color: rgba(69, 74, 131, 0.2);
  background: #f8fafc;
}

.info-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  color: #454a83;
  margin: 0 0 14px;
}

.info-title-plain {
  font-size: 13px;
  font-weight: 700;
  margin: 0 0 12px;
  color: #0f172a;
}

.experts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 14px;
}

.expert-row {
  color: #454a83;
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar-placeholder {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #e2e8f0;
  flex-shrink: 0;
}

.expert-name {
  font-size: 12px;
  font-weight: 700;
  margin: 0;
}

.expert-role {
  font-size: 10px;
  color: #64748b;
  margin: 0;
}

.manage-btn {
  width: 100%;
  padding: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #454a83;
  background: none;
  border: 1px solid rgba(69, 74, 131, 0.25);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.manage-btn:hover {
  background: #e5e9e9;
}

.settings-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 12px;
  color: #475569;
}

.settings-list li {
  display: flex;
  justify-content: space-between;
}

.status-published {
  color: #16a34a;
  font-weight: 700;
}

.status-draft {
  color: #f59e0b;
  font-weight: 700;
}

/* ── Bottom actions ── */
.bottom-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0 12px;
}

.actions-right {
  display: flex;
  gap: 12px;
}

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s, background 0.15s;
  font-family: inherit;
}

.btn-primary {
  background: #454a83;
  color: #fff;
}

.btn-primary:hover {
  opacity: 0.85;
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
  border: none;
  color: #475569;
}

.btn-ghost:hover {
  color: #0f172a;
}
</style>
