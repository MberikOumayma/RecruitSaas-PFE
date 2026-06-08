<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <div class="header-info">
          <h3 class="modal-title">{{ mode === 'create' ? 'Add New Expert' : 'Edit Expert Role' }}</h3>
          <p class="modal-subtitle">Configure professional details and permissions</p>
        </div>
        <button @click="$emit('close')" class="close-btn">
          <XIcon :size="20" />
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <template v-if="mode === 'create'">
          <div class="form-row">
            <div class="form-group flex-1">
              <label class="form-label">First Name</label>
              <input v-model="form.prenom" type="text" class="form-input" placeholder="e.g. John" required />
            </div>
            <div class="form-group flex-1">
              <label class="form-label">Last Name</label>
              <input v-model="form.nom" type="text" class="form-input" placeholder="e.g. Doe" required />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Email Address</label>
            <input v-model="form.email" type="email" class="form-input" placeholder="john.doe@company.com" required />
          </div>

         

          <div class="form-group">
            <label class="form-label">Assign to Company</label>
            <select v-model="form.entrepriseId" class="form-select" required>
              <option value="" disabled>Select a company...</option>
              <option v-for="ent in entreprises" :key="ent.id" :value="ent.id">{{ ent.nom }}</option>
            </select>
          </div>
        </template>

        <div class="form-group">
          <label class="form-label">Professional Role / Position</label>
          <input v-model="form.poste" type="text" class="form-input" required
            placeholder="e.g. Senior Cloud Architect" />
        </div>

        <div v-if="error" class="error-alert">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
          {{ error }}
        </div>

        <div class="modal-footer">
          <button type="button" @click="$emit('close')" class="btn-ghost">Cancel</button>
          <button type="submit" :disabled="saving" class="btn-primary">
            <span v-if="saving" class="spinner-sm"></span>
            {{ saving ? 'Saving...' : (mode === 'create' ? 'Create Expert Profile' : 'Save Changes') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { XIcon } from 'lucide-vue-next';
import teamService from '../../services/teamService';

export default {
  name: 'ExpertModal',
  components: {
    XIcon
  },
  props: {
    isOpen: {
      type: Boolean,
      required: true
    },
    mode: {
      type: String,
      default: 'create' // 'create' or 'edit'
    },
    expertData: {
      type: Object,
      default: () => null
    },
    entreprises: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      saving: false,
      error: null,
      form: {
        nom: '',
        prenom: '',
        email: '',
        motDePasse: '',
        entrepriseId: '',
        poste: ''
      }
    }
  },
  watch: {
    isOpen(newVal) {
      if (newVal) {
        this.error = null;
        if (this.mode === 'create') {
          this.form = { nom: '', prenom: '', email: '', motDePasse: '', entrepriseId: '', poste: '' };
        } else if (this.mode === 'edit' && this.expertData) {
          this.form = { poste: this.expertData.poste };
        }
      }
    }
  },
  methods: {
    async handleSubmit() {
      this.saving = true
      this.error = null

      try {
        if (this.mode === 'create') {
          const res = await teamService.createExpert({
            firstName: this.form.prenom,
            lastName:  this.form.nom,
            email:     this.form.email,
            companyId: this.form.entrepriseId,
            poste:     this.form.poste
          })
          this.$emit('saved', res.data)
        } else if (this.mode === 'edit' && this.expertData) {
          await teamService.updateExpert(this.expertData.id, { poste: this.form.poste })
          this.$emit('saved', null)
        }
        this.$emit('close')
      } catch (err) {
        this.error = err.response?.data?.message || `Failed to ${this.mode} expert.`
        console.error('Modal submit error:', err)
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  overflow-y: auto;
}

.modal-content {
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 520px;
  margin: auto;
  position: relative;
  animation: modal-in 0.3s ease-out;
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.98);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid #F1F5F9;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 4px;
}

.modal-subtitle {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

.close-btn {
  background: #F8FAFc;
  border: 1px solid #E2E8F0;
  color: #94A3B8;
  cursor: pointer;
  padding: 8px;
  border-radius: 10px;
  display: flex;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #F1F5F9;
  color: #454a83;
}

.modal-body {
  padding: 32px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 700;
  color: #475569;
  margin-bottom: 8px;
}

.form-input,
.form-select {
  width: 100%;
  height: 48px;
  padding: 0 16px;
  background: #F8FAFf;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #1e293b;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;
}

.form-input::placeholder {
  color: #94A3B8;
}

.form-input:focus,
.form-select:focus {
  background: #FFFFFF;
  border-color: #454a83;
  box-shadow: 0 0 0 4px rgba(69, 74, 131, 0.1);
}

.error-alert {
  background: #FEF2F2;
  border: 1px solid #FEE2E2;
  color: #B91C1C;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #F1F5F9;
}

.btn-ghost {
  padding: 12px 24px;
  background: transparent;
  border: 1px solid #E2E8F0;
  font-size: 0.9rem;
  font-weight: 700;
  color: #64748B;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.2s;
}

.btn-ghost:hover {
  background: #F8FAFC;
  color: #475569;
}

.btn-primary {
  padding: 12px 24px;
  background: #454a83;
  border: none;
  font-size: 0.9rem;
  font-weight: 700;
  color: #FFFFFF;
  cursor: pointer;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #363a6a;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(69, 74, 131, 0.2);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.flex-1 {
  flex: 1;
}
</style>
