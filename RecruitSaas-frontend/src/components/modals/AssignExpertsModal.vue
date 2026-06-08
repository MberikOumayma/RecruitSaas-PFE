<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <div class="header-info">
          <h3 class="modal-title">Assign Experts to Job</h3>
          <p class="modal-subtitle">Select team members to participate in the recruitment process</p>
        </div>
        <button @click="$emit('close')" class="close-btn">
          <XIcon :size="20" />
        </button>
      </div>

      <div class="modal-body">
        <!-- Search -->
        <div class="search-wrapper">
          <SearchIcon :size="16" class="search-icon" />
          <input v-model="searchQuery" type="text" class="search-input"
            placeholder="Search experts by name or position..." />
        </div>

        <div class="experts-split">
          <!-- Available -->
          <div class="expert-section">
            <h4 class="section-title">Available Experts</h4>
            <div v-if="loading" class="loading-state">
              <div class="spinner-sm"></div>
            </div>
            <div v-else-if="filteredAvailable.length === 0" class="empty-state">
              No matching experts found
            </div>
            <div v-else class="expert-list scrollable">
              <div v-for="expert in filteredAvailable" :key="expert.id" class="expert-card">
                <div class="expert-info">
                  <img :src="getAvatar(expert.name)" class="expert-avatar" />
                  <div class="expert-details">
                    <p class="name">{{ expert.name }}</p>
                    <p class="role">{{ expert.role }}</p>
                  </div>
                </div>
                <button class="assign-btn" @click="assignExpert(expert)">
                  Assign
                </button>
              </div>
            </div>
          </div>

          <!-- Assigned -->
          <div class="expert-section assigned">
            <h4 class="section-title">Assigned ({{ assignedExperts.length }})</h4>
            <div v-if="assignedExperts.length === 0" class="empty-state">
              No experts assigned yet
            </div>
            <div v-else class="expert-list scrollable">
              <div v-for="expert in assignedExperts" :key="expert.id" class="expert-card assigned-item">
                <div class="expert-info">
                  <img :src="getAvatar(expert.name)" class="expert-avatar sm" />
                  <p class="name">{{ expert.name }}</p>
                </div>
                <button class="remove-btn" @click="removeExpert(expert)" title="Remove">
                  <XIcon :size="14" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" @click="$emit('close')" class="btn-ghost">Cancel</button>
        <button @click="saveAssignments" :disabled="saving" class="btn-primary">
          <span v-if="saving" class="spinner-sm"></span>
          {{ saving ? 'Saving...' : 'Save Assignments' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { XIcon, SearchIcon, UsersIcon } from 'lucide-vue-next';
import { searchExperts, assignExperts } from '../../services/offreService';

export default {
  name: 'AssignExpertsModal',
  components: {
    XIcon, SearchIcon, UsersIcon
  },
  props: {
    isOpen: { type: Boolean, required: true },
    offreId: { type: [String, Number], required: null }
  },
  data() {
    return {
      searchQuery: '',
      availableExperts: [],
      assignedExperts: [],
      loading: false,
      saving: false,
      error: null
    }
  },
  computed: {
    filteredAvailable() {
      const q = this.searchQuery.toLowerCase();
      return this.availableExperts.filter(e =>
        e.name.toLowerCase().includes(q) || e.role.toLowerCase().includes(q)
      );
    }
  },
  watch: {
    isOpen(newVal) {
      if (newVal && this.offreId) {
        this.loadInitialData();
      }
    }
  },
  methods: {
    async loadInitialData() {
      this.loading = true;
      this.error = null;
      try {
        const res = await searchExperts(this.offreId, '');
        if (res.data) {
          const all = res.data.map(e => ({
            id: e.id,
            name: e.nom,
            role: e.poste,
            isAssigned: e.estAssigne
          }));
          
          this.assignedExperts = all.filter(e => e.isAssigned);
          this.availableExperts = all.filter(e => !e.isAssigned);
        }
      } catch (err) {
        console.error("Failed to load experts", err);
        this.error = "Could not load expert list.";
      } finally {
        this.loading = false;
      }
    },
    getAvatar(name) {
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`;
    },
    assignExpert(expert) {
      if (!this.assignedExperts.find(e => e.id === expert.id)) {
        this.assignedExperts.push(expert);
        this.availableExperts = this.availableExperts.filter(e => e.id !== expert.id);
      }
    },
    removeExpert(expert) {
      this.assignedExperts = this.assignedExperts.filter(e => e.id !== expert.id);
      this.availableExperts.push(expert);
    },
    async saveAssignments() {
      this.saving = true;
      try {
        const expertIds = this.assignedExperts.map(e => e.id);
        await assignExperts(this.offreId, { expertIds });
        this.$emit('saved');
        this.$emit('close');
      } catch (err) {
        console.error("Failed to save assignments", err);
      } finally {
        this.saving = false;
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
  z-index: 2000;
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
  max-width: 680px;
  margin: auto;
  position: relative;
  animation: modal-in 0.3s ease-out;
  display: flex;
  flex-direction: column;
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
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: 70vh;
}

.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-input {
  width: 100%;
  height: 48px;
  padding: 0 16px 0 40px;
  background: #F8FAFf;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #1e293b;
  outline: none;
  transition: all 0.2s;
}

.search-input:focus {
  background: #FFFFFF;
  border-color: #454a83;
  box-shadow: 0 0 0 4px rgba(69, 74, 131, 0.1);
}

.experts-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  overflow: hidden;
}

.expert-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: hidden;
}

.section-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #94a3b8;
  letter-spacing: 0.05em;
  margin: 0;
}

.expert-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.scrollable {
  overflow-y: auto;
  max-height: 400px;
  padding-right: 8px;
}

.scrollable::-webkit-scrollbar {
  width: 4px;
}

.scrollable::-webkit-scrollbar-thumb {
  background: #E2E8F0;
  border-radius: 4px;
}

.expert-card {
  padding: 12px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s;
}

.expert-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.expert-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #E2E8F0;
}

.expert-avatar.sm {
  width: 32px;
  height: 32px;
}

.expert-details .name {
  font-size: 13px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.expert-details .role {
  font-size: 11px;
  color: #64748b;
  margin: 0;
}

.assign-btn {
  padding: 6px 12px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #454a83;
  cursor: pointer;
  transition: all 0.2s;
}

.assign-btn:hover {
  background: #F1F5F9;
  border-color: #454a83;
}

.assigned-item {
  background: #F0F2FF;
  border-color: #C7D2FE;
}

.assigned-item .name {
  font-size: 12px;
}

.remove-btn {
  padding: 6px;
  background: transparent;
  border: none;
  color: #94A3B8;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #FEE2E2;
  color: #EF4444;
}

.empty-state {
  padding: 32px;
  text-align: center;
  color: #94A3B8;
  font-size: 13px;
  font-style: italic;
  background: #F8FAFC;
  border-radius: 10px;
  border: 1px dashed #E2E8F0;
}

.modal-footer {
  padding: 24px 32px;
  border-top: 1px solid #F1F5F9;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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
</style>
