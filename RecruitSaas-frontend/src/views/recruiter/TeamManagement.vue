<template>
  <div class="page-layout">
    <AppSidebar />
    <main class="main-content">
      <GlobalHeader title="Recruitment portal" />

      <div class="content">

        <!-- Page heading -->
        <div class="page-heading">
          <div>
            <h3 class="page-title">Team Management</h3>
            <p class="page-sub">Oversee your organization's expert network and collaboration permissions.</p>
          </div>
          <button @click="openModal('create')" class="btn-add">
            <UserPlusIcon :size="16" />
            Add Expert
          </button>
        </div>

        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon-wrap" style="background:#eff6ff;">
              <UsersIcon :size="20" color="#2563eb" />
            </div>
            <div>
              <p class="stat-label">Total Members</p>
              <p class="stat-val">{{ experts.length }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrap" style="background:#f0fdf4;">
              <BuildingIcon :size="20" color="#16a34a" />
            </div>
            <div>
              <p class="stat-label">Companies</p>
              <p class="stat-val">{{ entreprises.length }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrap" style="background:#fff7ed;">
              <BriefcaseIcon :size="20" color="#f97316" />
            </div>
            <div>
              <p class="stat-label">Assigned</p>
              <p class="stat-val">{{ experts.filter(e => e.offreId).length }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrap" style="background:#fefce8;">
              <ActivityIcon :size="20" color="#ca8a04" />
            </div>
            <div>
              <p class="stat-label">Network Strength</p>
              <div class="progress-wrap">
                <div class="progress-track">
                  <div class="progress-fill" style="width:75%"></div>
                </div>
                <span class="progress-pct">75%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="filters-card">
          <div class="filters-row">
            <div class="filter-group flex-1">
              <label class="filter-label">Search Team Members</label>
              <div class="input-wrap">
                <SearchIcon :size="15" class="input-icon" />
                <input type="text" class="filter-input padded" placeholder="Search by name or email"
                  v-model="filters.search" @input="fetchExperts" />
              </div>
            </div>
            <div class="filter-group" style="min-width:220px;">
              <label class="filter-label">Filter by Company</label>
              <div class="input-wrap">
                <select class="filter-input" v-model="filters.entrepriseId" @change="fetchExperts">
                  <option value="">All Companies</option>
                  <option v-for="ent in entreprises" :key="ent.id" :value="ent.id">{{ ent.nom }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- State -->
        <div v-if="loading" class="state-msg">Loading members...</div>
        <div v-if="error" class="error-banner">{{ error }}</div>

        <!-- Table -->
        <div v-if="!loading && experts.length > 0" class="table-card">
          <table class="data-table">
            <thead>
              <tr>
                <th>Member</th>
                <th>Company</th>
                <th>Job</th>
                <th>Offer</th>
                <th style="text-align:right;">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="expert in experts" :key="expert.id">
                <td>
                  <div class="user-cell">
                    <div class="avatar">{{ getInitials(expert.fullName || expert.nom) }}</div>
                    <div>
                      <p class="cell-name">{{ expert.fullName || expert.nom }}</p>
                      <p class="cell-email">{{ expert.email }}</p>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="company-badge">{{ expert.companyName || expert.nomEntreprise }}</span>
                </td>
                <td>
                  <p class="cell-name">{{ expert.poste || '—' }}</p>
                </td>
                <td>
                  <span v-if="expert.offreTitre" class="offer-chip">
                    <BriefcaseIcon :size="10" style="margin-right:3px;" />
                    {{ expert.offreTitre }}
                  </span>
                  <span v-else class="not-assigned">Not assigned</span>
                </td>
                <td>
                  <div class="actions">
                    <button @click="resendInvitation(expert)" class="action-btn amber" title="Resend invitation email">
                      <MailIcon :size="15" />
                    </button>
                    <button @click="openAssignModal(expert)" class="action-btn teal" title="Assign to offer">
                      <BriefcaseIcon :size="15" />
                    </button>
                    <button @click="openModal('edit', expert)" class="action-btn blue" title="Edit">
                      <EditIcon :size="15" />
                    </button>
                    <button @click="deleteExpert(expert.id)" class="action-btn red" title="Remove">
                      <TrashIcon :size="15" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="table-footer">
            Showing <strong>{{ experts.length }}</strong> expert{{ experts.length !== 1 ? 's' : '' }}
          </div>
        </div>

        <div v-else-if="!loading && experts.length === 0 && !error" class="empty-state">
          <UsersIcon :size="36" color="#cbd5e1" />
          <p>No members found.</p>
        </div>

      </div>
    </main>

    <!-- Modal Edit/Create -->
    <ExpertModal
      :is-open="modal.isOpen"
      :mode="modal.mode"
      :expert-data="modal.expertData"
      :entreprises="entreprises"
      @close="closeModal"
      @saved="onExpertSaved"
    />

    <!-- Modal Assign -->
    <div v-if="assignModal.isOpen" class="modal-overlay" @click.self="closeAssignModal">
      <div class="modal-box">
        <div class="modal-header">
          <h3 class="modal-title">Assign to Job Offer</h3>
          <button class="icon-btn" @click="closeAssignModal"><XIcon :size="18" /></button>
        </div>
        <div class="modal-body">
          <p class="modal-sub">Assigning: <strong>{{ assignModal.expert?.fullName }}</strong></p>
          <div class="field-group">
            <label class="filter-label">Job Title / Poste</label>
            <input v-model="assignModal.poste" type="text" class="filter-input" placeholder="e.g. Senior Evaluator" />
          </div>
          <div class="field-group" style="margin-top:14px;">
            <label class="filter-label">Assign to Offer</label>
            <select v-model="assignModal.offreId" class="filter-input">
              <option :value="null">— No assignment —</option>
              <option v-for="o in offres" :key="o.id" :value="o.id">{{ o.titre }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeAssignModal">Cancel</button>
          <button class="btn-add" @click="saveAssign" :disabled="assignSaving">
            <BriefcaseIcon :size="14" />
            {{ assignSaving ? 'Saving...' : 'Save Assignment' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import ExpertModal from '../../components/modals/ExpertModal.vue'
import {
  SearchIcon, UserPlusIcon, EditIcon, TrashIcon, XIcon, MailIcon,
  UsersIcon, BuildingIcon, ActivityIcon, BriefcaseIcon
} from 'lucide-vue-next'
import teamService from '../../services/teamService'
import { useNotification } from '../../composables/useNotification'

export default {
  name: 'TeamManagement',
  components: {
    AppSidebar, GlobalHeader, ExpertModal,
    SearchIcon, UserPlusIcon, EditIcon, TrashIcon, XIcon, MailIcon,
    UsersIcon, BuildingIcon, ActivityIcon, BriefcaseIcon
  },
  setup() {
    const { toast, confirm } = useNotification()
    return { toast, confirm }
  },
  data() {
    return {
      experts: [], entreprises: [], offres: [],
      loading: false, error: null,
      filters: { search: '', entrepriseId: '' },
      modal: { isOpen: false, mode: 'create', expertData: null },
      assignModal: { isOpen: false, expert: null, offreId: null, poste: '' },
      assignSaving: false
    }
  },
  async created() {
    await this.fetchEntreprises()
    await this.fetchOffres()
  },
  methods: {
    getInitials(name) {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
    },
    async fetchOffres() {
      try { const res = await teamService.getOffresDisponibles(); this.offres = res.data || [] }
      catch (err) { console.error('fetchOffres', err) }
    },
    openAssignModal(expert) {
      this.assignModal = { isOpen: true, expert, offreId: expert.offreId || null, poste: expert.poste || '' }
    },
    closeAssignModal() { this.assignModal.isOpen = false; this.assignModal.expert = null; this.assignSaving = false },
    async saveAssign() {
      this.assignSaving = true; this.error = null
      try {
        await teamService.assignOffre(this.assignModal.expert.id, { offreId: this.assignModal.offreId || null, poste: this.assignModal.poste })
        await this.fetchExperts(); this.closeAssignModal()
      } catch (err) { console.error('Assign error:', err); this.error = 'Failed to assign the offer.'; this.assignSaving = false }
    },
    async fetchEntreprises() {
      try {
        const response = await teamService.getEntreprises()
        this.entreprises = response.data.data || response.data || []
        if (this.entreprises.length > 0) { this.filters.entrepriseId = this.entreprises[0].id; await this.fetchExperts() }
      } catch (err) { console.error('fetchEntreprises', err); this.error = 'Unable to load companies.' }
    },
    async fetchExperts() {
      if (!this.filters.entrepriseId) { this.experts = []; this.loading = false; return }
      this.loading = true; this.error = null
      try {
        const response = await teamService.getExperts(this.filters.entrepriseId, this.filters.search)
        const data = response.data
        this.experts = data.items || data.data || (Array.isArray(data) ? data : [])
      } catch (err) { console.error('fetchExperts', err); this.error = 'Failed to load team members.' }
      finally { this.loading = false }
    },
    openModal(mode, expert = null) { this.modal.mode = mode; this.modal.isOpen = true; this.modal.expertData = expert },
    closeModal() { this.modal.isOpen = false; this.modal.expertData = null },
    onExpertSaved(result) {
      this.fetchExperts()
      if (this.modal.mode !== 'create' || !result) return
      const email = result.email || result.Email
      const invitationSent = result.invitationEmailSent ?? result.InvitationEmailSent
      if (invitationSent) {
        this.toast.success(`Invitation email sent to ${email}.`)
      } else {
        this.toast.error(`Expert created but the invitation email could not be sent${email ? ` to ${email}` : ''}. Check server logs.`)
      }
    },
    async resendInvitation(expert) {
      try {
        const res = await teamService.resendInvitation(expert.id)
        const email = res.data?.email || expert.email
        const invitationSent = res.data?.invitationEmailSent ?? res.data?.InvitationEmailSent
        if (invitationSent) {
          this.toast.success(`Invitation email resent to ${email}.`)
        } else {
          this.toast.error(`Could not send invitation email to ${email}. Check server logs.`)
        }
      } catch (err) {
        this.toast.error(err.response?.data?.message || 'Failed to resend invitation.')
      }
    },
    async deleteExpert(id) {
      const confirmed = await this.confirm({ title: 'Remove Expert?', message: 'This action cannot be undone.', confirmText: 'Remove', cancelText: 'Cancel' })
      if (!confirmed) return
      try {
        await teamService.deleteExpert(id)
        this.experts = this.experts.filter(e => e.id !== id)
        this.toast.success("Expert removed successfully.")
        // Re-synchronise depuis le serveur pour confirmer la suppression réelle en BD
        await this.fetchExperts()
      } catch (err) {
        console.error("Delete error:", err)
        const apiMessage = err?.response?.data?.message
                        || err?.response?.data?.title
                        || err?.message
                        || "Failed to remove expert."
        this.toast.error(apiMessage)
      }
    }
  }
}
</script>

<style scoped>
* { box-sizing: border-box; }

.page-layout { display:flex; height:100vh; overflow:hidden; background:#f0f2f8; font-family:'Inter',sans-serif; }
.main-content { flex:1; display:flex; flex-direction:column; min-width:0; overflow:hidden; }
.content { flex:1; padding:28px 32px; overflow-y:auto; }

/* Heading */
.page-heading { display:flex; align-items:center; justify-content:space-between; margin-bottom:24px; }
.page-title { font-size:1.25rem; font-weight:800; color:#0f172a; margin:0 0 3px; }
.page-sub { font-size:0.8rem; color:#94a3b8; margin:0; }

/* Add button */
.btn-add {
  display:inline-flex; align-items:center; gap:7px;
    background: #454a83;
 color:#fff; border:none;
  border-radius:9px; padding:10px 18px;
  font-size:0.82rem; font-weight:700; cursor:pointer;
  transition:opacity 0.15s;
}
.btn-add:hover { opacity:0.88; }
.btn-add:disabled { opacity:0.5; cursor:not-allowed; }

/* Stats */
.stats-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:20px; }
.stat-card {
  display:flex; align-items:center; gap:14px;
  background:#fff; border:1px solid #e2e8f0; border-radius:13px;
  padding:16px 20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);
}
.stat-icon-wrap { width:42px; height:42px; border-radius:11px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.stat-label { font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:#94a3b8; margin:0 0 3px; }
.stat-val { font-size:1.5rem; font-weight:800; color:#0f172a; margin:0; line-height:1; }
.progress-wrap { display:flex; align-items:center; gap:8px; margin-top:4px; }
.progress-track { flex:1; height:6px; background:#e2e8f0; border-radius:99px; overflow:hidden; }
.progress-fill { height:100%; background:#1A2B4C; border-radius:99px; }
.progress-pct { font-size:0.75rem; font-weight:700; color:#1A2B4C; }

/* Filters */
.filters-card { background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:18px 20px; margin-bottom:18px; }
.filters-row { display:flex; gap:14px; flex-wrap:wrap; }
.filter-group { display:flex; flex-direction:column; gap:6px; }
.flex-1 { flex:1; }
.filter-label { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#64748b; }
.input-wrap { position:relative; display:flex; align-items:center; }
.input-icon { position:absolute; left:10px; color:#94a3b8; pointer-events:none; }
.filter-input {
  height:40px; width:100%; border:1px solid #e2e8f0; border-radius:8px;
  padding:0 12px; font-size:0.82rem; color:#0f172a;
  background:#fff; outline:none; appearance:none;
}
.filter-input.padded { padding-left:32px; }
.filter-input:focus { border-color:#1A2B4C; }

/* States */
.state-msg { text-align:center; color:#94a3b8; padding:32px; font-size:0.85rem; }
.error-banner { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; border-radius:8px; padding:10px 14px; margin-bottom:14px; font-size:0.82rem; }

/* Table */
.table-card { background:#fff; border:1px solid #e2e8f0; border-radius:13px; overflow:hidden; }
.data-table { width:100%; border-collapse:collapse; }
.data-table thead tr { background:#f8fafc; }
.data-table th {
  padding:11px 16px; text-align:left;
  font-size:0.63rem; font-weight:700;
  text-transform:uppercase; letter-spacing:0.08em;
  color:#94a3b8; border-bottom:1px solid #e2e8f0;
}
.data-table tbody tr { border-bottom:1px solid #f1f5f9; transition:background 0.1s; }
.data-table tbody tr:hover { background:#fafafa; }
.data-table tbody tr:last-child { border-bottom:none; }
.data-table td { padding:12px 16px; vertical-align:middle; }

.user-cell { display:flex; align-items:center; gap:11px; }
.avatar {
  width:36px; height:36px; border-radius:8px;
  background:#1A2B4C; color:#fff;
  display:flex; align-items:center; justify-content:center;
  font-size:0.7rem; font-weight:800; flex-shrink:0;
}
.cell-name { font-size:0.83rem; font-weight:700; color:#0f172a; margin:0 0 1px; }
.cell-email { font-size:0.7rem; color:#94a3b8; margin:0; }

.company-badge {
  display:inline-block; background:#f1f5f9; color:#475569;
  font-size:0.71rem; font-weight:600;
  padding:3px 9px; border-radius:99px;
}
.offer-chip {
  display:inline-flex; align-items:center;
  background:#eff6ff; color:#2563eb;
  font-size:0.65rem; font-weight:600;
  padding:2px 7px; border-radius:99px; margin-top:3px;
}
.not-assigned { font-size:0.76rem; color:#cbd5e1; font-style:italic; }

.actions { display:flex; justify-content:flex-end; gap:5px; }
.action-btn {
  width:32px; height:32px; border:none; border-radius:8px;
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:background 0.12s;
}
.action-btn.teal  { background:#f0fdfa; color:#0d9488; }
.action-btn.teal:hover  { background:#ccfbf1; }
.action-btn.blue  { background:#eff6ff; color:#1A2B4C; }
.action-btn.blue:hover  { background:#dbeafe; }
.action-btn.amber  { background:#fffbeb; color:#d97706; }
.action-btn.amber:hover  { background:#fef3c7; }
.action-btn.red   { background:#fef2f2; color:#dc2626; }
.action-btn.red:hover   { background:#fee2e2; }

.table-footer { padding:12px 16px; font-size:0.75rem; color:#94a3b8; border-top:1px solid #f1f5f9; }

/* Empty */
.empty-state { display:flex; flex-direction:column; align-items:center; gap:10px; padding:60px 20px; color:#94a3b8; font-size:0.84rem; }

/* Modal */
.modal-overlay { position:fixed; inset:0; background:rgba(15,23,42,0.4); backdrop-filter:blur(3px); display:flex; align-items:center; justify-content:center; z-index:500; }
.modal-box { background:#fff; border-radius:14px; width:460px; max-width:95vw; box-shadow:0 20px 60px rgba(0,0,0,0.15); }
.modal-header { display:flex; align-items:center; justify-content:space-between; padding:18px 22px; border-bottom:1px solid #f1f5f9; }
.modal-title { font-size:0.95rem; font-weight:800; color:#0f172a; margin:0; }
.icon-btn { background:none; border:none; cursor:pointer; color:#94a3b8; padding:4px; border-radius:6px; display:flex; }
.icon-btn:hover { background:#f1f5f9; color:#475569; }
.modal-body { padding:20px 22px; }
.modal-sub { font-size:0.82rem; color:#64748b; margin:0 0 16px; }
.field-group { display:flex; flex-direction:column; gap:6px; }
.modal-footer { display:flex; justify-content:flex-end; gap:10px; padding:16px 22px; border-top:1px solid #f1f5f9; }
.btn-cancel { background:#f1f5f9; color:#475569; border:none; border-radius:8px; padding:9px 16px; font-size:0.82rem; font-weight:600; cursor:pointer; }
.btn-cancel:hover { background:#e2e8f0; }

@media (max-width:1100px) { .stats-grid { grid-template-columns:repeat(2,1fr); } }
@media (max-width:700px)  { .content { padding:16px; } .stats-grid { grid-template-columns:1fr; } }
</style>