<template>
  <div class="page-layout">
    <AppSidebar />

    <main class="main-content">
      <!-- Header -->
      <GlobalHeader title="Create New Job Posting" />

      <!-- Stepper -->
      <div class="stepper-bar">
        <AppStepper :current-step="2" />
      </div>

      <!-- Content -->
      <div class="content-scroll">
        <div class="content-grid">

          <!-- Left: Form Builder -->
          <section class="form-builder-col">
            <div class="card">
              <div class="card-header">
                <h2 class="card-title">Form Builder</h2>
                <p class="card-subtitle">Define application fields</p>
              </div>

              <div class="fields-list">
                <div v-for="(field, index) in fields" :key="field.id" class="field-item">
                  <div class="field-top">
                    <div class="field-left">
                      <GripVerticalIcon :size="16" class="drag-icon" />
                      <input v-model="field.label" class="field-name-input" type="text" />
                    </div>
                    <div class="field-right">
                      <span class="required-label">Required</span>
                      <button class="toggle-switch" :class="{ active: field.required }"
                        @click="field.required = !field.required" type="button"
                        :aria-label="`Toggle required for ${field.label}`">
                        <span class="toggle-thumb" />
                      </button>
                      <button class="delete-btn" @click="removeField(index)" type="button" title="Remove field">
                        <Trash2Icon :size="16" />
                      </button>
                    </div>
                  </div>
                  <div class="field-meta-editable">
                    <select v-model="field.type" class="type-select">
                      <option value="Texte">Texte</option>
                      <option value="Nombre">Nombre</option>
                      <option value="Fichier">Fichier</option>
                    </select>
                    <input v-model="field.hint" class="hint-input" type="text"
                      placeholder="Description/Hint (optional)" />
                  </div>
                </div>

                <button class="add-field-btn" type="button" @click="addField">
                  <PlusCircleIcon :size="18" />
                  Add new custom field
                </button>
              </div>
            </div>
          </section>

          <!-- Right: Expert Assignment -->
          <aside class="expert-col">
            <div class="card" style="margin-bottom: 24px;">
              <h2 class="card-title" style="margin-bottom: 16px;">Job Visibility</h2>
              <div class="form-group">
                <div class="toggle-card">
                  <div class="toggle-icon-wrap">
                    <Link2Icon :size="16" />
                  </div>
                  <div class="toggle-text">
                    <p class="toggle-title">Public application link</p>
                  </div>
                  <button class="toggle-switch" :class="{ active: showPublicLink }" @click="handlePublicLinkToggle"
                    type="button" aria-label="Toggle public link">
                    <span class="toggle-thumb" />
                  </button>
                </div>
                <div v-if="showPublicLink" class="public-link-display">
                  <div class="link-actions">
                    <a :href="lienPublic" target="_blank" class="link-url">{{ lienPublic }}</a>
                    <button class="icon-btn" title="Copy link" @click="copyLinkToClipboard">
                      <Copy :size="14" />
                    </button>
                    <button class="icon-btn" title="Regenerate link" @click="handleRegenerateToken">
                      <RefreshCwIcon :size="14" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

          </aside>

        </div>
      </div>

      <!-- Footer -->
      <footer class="page-footer">
        <button class="btn btn-outline" @click="$router.push(`/recruiter/jobs/create/${offreId}/step1`)">
          <ArrowLeftIcon :size="16" />
          Back
        </button>
        <div class="footer-right">
          <button class="btn btn-primary" @click="handleNext" :disabled="isSubmitting">
            <span v-if="isSubmitting">Saving...</span>
            <span v-else>Next: Preview</span>
            <ArrowRightIcon v-if="!isSubmitting" :size="16" />
          </button>
        </div>
      </footer>
    </main>

  </div>
</template>

<script>
import {
  addFields, updateField, deleteField, reorderFields, getOffreById,
  initializeForm, assignExperts, searchExperts, togglePublicLink, regeneratePublicToken
} from '../../services/offreService'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import AppStepper from '../../components/common/AppStepper.vue'
import {
  BellIcon, HelpCircleIcon, GripVerticalIcon, Trash2Icon,
  PlusCircleIcon, SearchIcon, XIcon, ArrowLeftIcon, ArrowRightIcon, Link2Icon, RefreshCwIcon, Copy
} from 'lucide-vue-next'

import { useNotification } from '../../composables/useNotification'

export default {
  name: 'CreateJobStep2',
  components: {
    AppSidebar, GlobalHeader, AppStepper,
    BellIcon, HelpCircleIcon, GripVerticalIcon, Trash2Icon,
    PlusCircleIcon, SearchIcon, XIcon, ArrowLeftIcon, ArrowRightIcon, Link2Icon, RefreshCwIcon, Copy
  },
  setup() {
    const { toast, confirm } = useNotification()
    return { toast, confirm }
  },
  data() {
    return {
      offreId: null,
      formId: null,
      isSubmitting: false,
      expertSearch: '',
      fields: [],
      availableExperts: [],
      deletedFieldIds: [],
      showPublicLink: false,
      lienPublic: '',
      initialFieldsStr: ''
    }
  },
  computed: {
    filteredExperts() {
      const q = this.expertSearch.toLowerCase()
      return this.availableExperts.filter(
        e => e.name.toLowerCase().includes(q) || e.role.toLowerCase().includes(q)
      )
    }
  },
  async mounted() {
    this.offreId = this.$route.params.id;
    if (!this.offreId || this.offreId === 'new') {
      this.toast.error("No valid offer found. Please go back to Step 1.");
      this.$router.push('/recruiter/jobs/create/new/step1');
      return;
    }

    try {
      const res = await getOffreById(this.offreId);
      const offre = res.data;

      let formulaire = offre.formulaire;
      this.lienPublic = offre.lienPublic || '';
      this.showPublicLink = offre.isPublicLinkEnabled;
      if (!formulaire) {
        const formRes = await initializeForm(this.offreId);
        formulaire = formRes.data;
      }
      this.formId = formulaire.id;

      if (formulaire.champs) {
        this.fields = formulaire.champs.map(c => ({
          id: c.id,
          label: c.nom,
          required: c.estObligatoire,
          type: c.type,
          hint: c.question || ''
        }));
      }
      this.initialFieldsStr = JSON.stringify(this.fields);

      const expRes = await searchExperts(this.offreId, '');
      if (expRes.data) {
        this.availableExperts = expRes.data.map(e => ({
          id: e.id,
          name: e.nom,
          role: e.poste,
          avatar: 'https://ui-avatars.com/api/?name=' + encodeURIComponent(e.nom)
        }));
      }
      } catch (e) {
        console.error("Error reading offer data:", e);
      }
    },
  methods: {
    addField() {
      this.fields.push({
        id: null,
        label: 'New Field',
        required: false,
        type: 'Texte',
        hint: ''
      })
    },
    removeField(index) {
      const field = this.fields[index];
      if (field.id) {
        this.deletedFieldIds.push(field.id);
      }
      this.fields.splice(index, 1);
    },
    getAvatar(name) {
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`;
    },
    async handlePublicLinkToggle() {
      const newState = !this.showPublicLink;
      try {
        const res = await togglePublicLink(this.offreId, newState);
        this.showPublicLink = res.data.isPublicLinkEnabled;
        this.lienPublic = res.data.lienPublic;
        this.toast.success(`Public link ${this.showPublicLink ? 'enabled' : 'disabled'}`);
      } catch (err) {
        console.error("Failed to toggle public link", err);
        this.toast.error("Failed to toggle public link");
      }
    },
    async handleRegenerateToken() {
      const confirmed = await this.confirm({
        title: "Regenerate Link?",
        message: "Are you sure you want to regenerate the public link? The old link will stop working immediately.",
        confirmText: "Regenerate",
        cancelText: "Cancel"
      });
      
      if (!confirmed) return;

      try {
        const res = await regeneratePublicToken(this.offreId);
        this.lienPublic = res.data.lienPublic;
        this.toast.success("New link generated!");
      } catch (err) {
        console.error("Failed to regenerate token", err);
        this.toast.error("Failed to regenerate token");
      }
    },
    copyLinkToClipboard() {
      if (!this.lienPublic) return;
      navigator.clipboard.writeText(this.lienPublic)
        .then(() => {
          this.toast.info("Link copied to clipboard!");
        })
        .catch(err => console.error("Failed to copy link:", err));
    },
    async handleNext() {
      if (!this.offreId) {
        this.toast.error("No valid offer found. Please go back to Step 1.")
        return
      }

      const isDirty = this.initialFieldsStr !== JSON.stringify(this.fields) || this.deletedFieldIds.length > 0;
      if (!isDirty) {
        this.$router.push(`/recruiter/jobs/create/${this.offreId}/step3`)
        return
      }

      this.isSubmitting = true
      try {
        for (const fieldId of this.deletedFieldIds) {
          await deleteField(fieldId);
        }

        const newFields = [];
        for (let i = 0; i < this.fields.length; i++) {
          const f = this.fields[i];
          const dto = {
            nom: f.label,
            question: f.hint,
            type: f.type,
            estObligatoire: f.required,
            ordre: i + 1,
            optionsJson: null
          };

          if (f.id) {
            await updateField(f.id, Object.assign({}, dto, { id: f.id }));
          } else {
            newFields.push(dto);
          }
        }

        if (newFields.length > 0) {
          await addFields(this.offreId, newFields);
        }

        const orderDtoss = this.fields.filter(f => f.id).map((f, i) => ({
          champId: f.id,
          ordre: i + 1
        }));
        if (orderDtoss.length > 0 && this.formId) {
          await reorderFields(this.formId, orderDtoss);
        }

        this.toast.success("Configuration saved successfully.");
        this.$router.push(`/recruiter/jobs/create/${this.offreId}/step3`)
      } catch (err) {
        console.error("Failed to save step 2", err)
        this.toast.error("Failed to save configuration: " + (err.response?.data?.message || err.message))
      } finally {
        this.isSubmitting = false
      }
    }
  }
}
</script>

<style scoped>
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
  padding: 24px 32px 100px;
}

.content-scroll::-webkit-scrollbar {
  width: 4px;
}

.content-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.content-grid {
  display: flex;
  gap: 24px;
  max-width: 1100px;
  margin: 0 auto;
  align-items: flex-start;
}

.form-builder-col {
  flex: 1;
}

.expert-col {
  width: 340px;
  flex-shrink: 0;
}

/* ── Card ── */
.card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-title {
  font-size: 17px;
  font-weight: 700;
  margin: 0;
  color: #0f172a;
}

.card-subtitle {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

/* ── Fields ── */
.fields-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-item {
  padding: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.drag-icon {
  color: #94a3b8;
  cursor: grab;
}

.field-name-input {
  background: #fff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  outline: none;
  padding: 6px 10px;
  width: 180px;
  transition: all 0.2s ease;
}

.field-name-input:hover {
  border-color: #94a3b8;
}

.field-name-input:focus {
  border-color: #454a83;
  box-shadow: 0 0 0 3px rgba(69, 74, 131, 0.12);
}

.field-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.required-label {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
}

/* Toggle */
.toggle-switch {
  width: 40px;
  height: 22px;
  border-radius: 999px;
  background: #cbd5e1;
  border: none;
  position: relative;
  cursor: pointer;
  transition: background 0.2s;
  padding: 0;
}

.toggle-switch.active {
  background: #454a83;
}

.toggle-thumb {
  display: block;
  width: 16px;
  height: 16px;
  background: #fff;
  border-radius: 50%;
  position: absolute;
  top: 3px;
  left: 3px;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-switch.active .toggle-thumb {
  transform: translateX(18px);
}

.delete-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.15s;
}

.delete-btn:hover {
  color: #ef4444;
}

.field-meta-editable {
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
}

.type-select,
.hint-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
  color: #334155;
  outline: none;
  transition: border-color 0.15s;
}

.type-select:focus,
.hint-input:focus {
  border-color: #454a83;
}

.type-select {
  flex: 0 0 160px;
}

.add-field-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  background: none;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
  margin-top: 4px;
}

.add-field-btn:hover {
  color: #454a83;
  border-color: #454a83;
}

/* Toggle card & Link display */
.toggle-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.toggle-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(69, 74, 131, 0.12);
  color: #454a83;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toggle-text {
  flex: 1;
}

.toggle-title {
  color: #0f172a;
  font-size: 13px;
  font-weight: 700;
  margin: 0;
}

.public-link-display {
  margin-top: 12px;
  padding: 12px;
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 12px;
  color: #454a83;
  border: 1px solid #cbd5e1;
}

.link-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.link-url {
  flex: 1;
  word-break: break-all;
  color: inherit;
  text-decoration: none;
  font-weight: 600;
}

.link-url:hover {
  text-decoration: underline;
}

.icon-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: rgba(69, 74, 131, 0.1);
  color: #454a83;
}


/* ── Footer ── */
.page-footer {
  position: absolute;
  bottom: 0;
  left: clamp(220px, 24vw, 300px);
  right: 0;
  height: 72px;
  background: #fff;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.06);
  z-index: 10;
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
  font-family: inherit;
}

.btn-primary {
  background: #1A2B4C;
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
  border: none;
  color: #64748b;
}

.btn-ghost:hover {
  color: #0f172a;
}
</style>
