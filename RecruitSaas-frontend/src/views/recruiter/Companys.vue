<template>
  <div class="page-layout">
    <AppSidebar />
    <main class="main-content">
      <GlobalHeader title="Recruitment portal" />
      <div class="content">
        <div v-if="loading" class="loader-wrap">
          <div class="loader"></div>
        </div>
        <div v-else-if="!tenantDisponible" class="waiting-wrap">
          <div class="waiting-card">
            <div class="waiting-icon">
              <Clock :size="34" color="#94a3b8" />
            </div>
            <h2 class="waiting-title">No company available</h2>
            <p class="waiting-desc">No recruiter account has been approved yet.</p>
            <button class="btn btn-primary" @click="loadCompanies">Refresh</button>
          </div>
        </div>
        <template v-else>
          <div class="page-heading">
            <div>
              <h2 class="page-title">Companies</h2>
              <p class="page-sub">Manage partner companies and their information.</p>
            </div>
            <button class="btn btn-primary" @click="openCreateModal">
              <Plus :size="16" /> Add company
            </button>
          </div>
          <div class="stats-row">
            <div class="stat-card">
              <div class="stat-icon si-gray">
                <Building2 :size="20" />
              </div>
              <div>
                <p class="stat-label">TOTAL COMPANIES</p>
                <p class="stat-val">{{ companies.length }}</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon si-green">
                <TrendingUp :size="20" />
              </div>
              <div>
                <p class="stat-label">ACCOUNT STATUS</p>
                <p class="stat-val sv-green">{{ statutLabel }}</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon si-amber">
                <Briefcase :size="20" />
              </div>
              <div>
                <p class="stat-label">TOTAL OFFERS</p>
                <p class="stat-val sv-amber">{{ totalOffres }}</p>
              </div>
            </div>
          </div>
          <div v-if="error" class="empty-msg">
            <p>{{ error }}</p>
            <button class="btn btn-primary" style="margin-top:12px" @click="loadCompanies">Try again</button>
          </div>
          <div v-else class="cards-grid">
            <div v-for="c in companies" :key="c.id" class="ccard">
              <div class="ccard-top">
                <div class="ccard-logo">
                  <img v-if="c.logoUrl" :src="API_BASE + c.logoUrl" :alt="c.nom" />
                  <Building2 v-else :size="22" color="#94a3b8" />
                </div>
                <span class="ccard-badge badge-active">
                  <CheckCircle2 :size="12" /> Active
                </span>
              </div>
              <h3 class="ccard-name">{{ c.nom }}</h3>
              <p class="ccard-loc">
                <MapPin :size="12" /> {{ c.secteur }}
              </p>
              <div class="ccard-stats">
                <div class="ccard-stat">
                  <p class="ccard-stat-label">EXPERTS</p>
                  <div class="ccard-stat-val"><span>{{ c.expertsCount || 0 }}</span></div>
                </div>
                <div class="ccard-stat">
                  <p class="ccard-stat-label">OFFERS</p>
                  <div class="ccard-stat-val"><span>{{ c.offresCount || 0 }}</span></div>
                </div>
              </div>
              <div class="ccard-footer">
                <div class="ccard-match"><span class="match-label">Created on </span><span class="match-val">{{
                    formatDate(c.creeLe) }}</span></div>
                <div class="ccard-actions">
                  <button @click="openEditModal(c)" title="Edit">
                    <Pencil :size="15" />
                  </button>
                  <button @click="openDeleteModal(c)" class="del" title="Delete">
                    <Trash2 :size="15" />
                  </button>
                </div>
              </div>
            </div>
            <button class="add-card" @click="openCreateModal">
              <Plus :size="38" color="#94a3b8" />
              <span>Add a new partner</span>
            </button>
          </div>
        </template>
      </div>
    </main>
  </div>

  <Teleport to="body">
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-head">
          <div>
            <h2>New company</h2>
            <p class="modal-subtitle">Enter the main company details.</p>
          </div>
          <button class="close-btn" @click="showCreate = false">
            <X :size="20" />
          </button>
        </div>
        <form @submit.prevent="submitCreate" class="modal-form">
          <div class="field"><label>Name *</label><input v-model="form.nom" required /></div>
          <div class="field"><label>Industry *</label><input v-model="form.secteur" required /></div>
          <div class="field"><label>RNE *</label><input v-model="form.rne" required /></div>
          <div class="field"><label>Description</label><textarea v-model="form.description" rows="3"></textarea></div>
          <div class="field"><label>Logo</label><input type="file" accept="image/*"
              @change="e => selectedLogo.create = e.target.files[0]" /></div>
          <div class="modal-footer">
            <button type="button" class="btn-ghost" @click="showCreate = false">Cancel</button>
            <button type="submit" class="btn-submit" :disabled="submitting">{{ submitting ? 'Creating...' : 'Create'
              }}</button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>

  <Teleport to="body">
    <div v-if="showEdit" class="modal-overlay" @click.self="showEdit = false">
      <div class="modal">
        <div class="modal-head">
          <div>
            <h2>Edit company</h2>
            <p class="modal-subtitle">Update your company information.</p>
          </div>
          <button class="close-btn" @click="showEdit = false">
            <X :size="20" />
          </button>
        </div>
        <form @submit.prevent="submitEdit" class="modal-form">
          <div class="field"><label>Name</label><input v-model="editForm.nom" /></div>
          <div class="field"><label>Industry</label><input v-model="editForm.secteur" /></div>
          <div class="field"><label>RNE</label><input v-model="editForm.rne" /></div>
          <div class="field"><label>Description</label><textarea v-model="editForm.description" rows="3"></textarea>
          </div>
          <div class="field"><label>New logo</label><input type="file" accept="image/*"
              @change="e => selectedLogo.edit = e.target.files[0]" /></div>
          <div class="modal-footer">
            <button type="button" class="btn-ghost" @click="showEdit = false">Cancel</button>
            <button type="submit" class="btn-submit" :disabled="submitting">{{ submitting ? 'Saving...' :
              'Save' }}</button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>

  <Teleport to="body">
    <div v-if="showDelete" class="modal-overlay" @click.self="showDelete = false">
      <div class="modal modal-sm">
        <div class="del-center">
          <div class="del-icon">
            <AlertCircle :size="32" color="#ef4444" />
          </div>
          <h2>Delete company</h2>
          <p>Are you sure you want to delete <strong>{{ deleteTarget?.nom }}</strong>?</p>
        </div>
        <div class="modal-footer">
          <button class="btn-ghost" @click="showDelete = false">Cancel</button>
          <button class="btn-delete" @click="confirmDelete" :disabled="submitting">{{ submitting ? 'Deleting...' :
            'Delete' }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import { Plus, Building2, MapPin, Pencil, Trash2, X, Clock, TrendingUp, Briefcase, AlertCircle, CheckCircle2 } from 'lucide-vue-next'
import { formatRecruiterDate, tenantAccountStatusLabel } from '../../utils/recruiterI18n.js'

const API_BASE = 'http://localhost:5202'
const companies = ref([])
const loading = ref(true)
const error = ref(null)
const submitting = ref(false)
const statut = ref('')
const tenantDisponible = ref(false)
const showCreate = ref(false)
const showEdit = ref(false)
const showDelete = ref(false)
const deleteTarget = ref(null)
const selectedLogo = ref({ create: null, edit: null })
const form = ref({ nom: '', secteur: '', rne: '', description: '' })
const editForm = ref({ id: '', nom: '', secteur: '', rne: '', description: '' })
const totalOffres = computed(() => companies.value.reduce((s, c) => s + (c.offresCount || 0), 0))
const statutLabel = computed(() => tenantAccountStatusLabel(statut.value))

onMounted(loadCompanies)

async function loadCompanies() {
  loading.value = true; error.value = null; tenantDisponible.value = false
  try {
    const res = await api.get('/tenant/companies')
    const json = res.data
    statut.value = json.statut ?? ''
    if (!json.success) { companies.value = []; return }
    tenantDisponible.value = true
    companies.value = json.data ?? []
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function submitCreate() {
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('Nom', form.value.nom); fd.append('Secteur', form.value.secteur); fd.append('RNE', form.value.rne)
    if (form.value.description) fd.append('Description', form.value.description)
    if (selectedLogo.value.create) fd.append('logo', selectedLogo.value.create)
    const res = await api.post('/tenant/companies', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (!res.data.success) throw new Error(res.data.message)
    showCreate.value = false; await loadCompanies()
  } catch (e) { error.value = e.message }
  finally { submitting.value = false }
}

async function submitEdit() {
  submitting.value = true
  try {
    const fd = new FormData()
    if (editForm.value.nom) fd.append('Nom', editForm.value.nom)
    if (editForm.value.secteur) fd.append('Secteur', editForm.value.secteur)
    if (editForm.value.rne) fd.append('RNE', editForm.value.rne)
    if (editForm.value.description) fd.append('Description', editForm.value.description)
    if (selectedLogo.value.edit) fd.append('logo', selectedLogo.value.edit)
    const res = await api.put(`/tenant/companies/${editForm.value.id}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (!res.data.success) throw new Error(res.data.message)
    showEdit.value = false; await loadCompanies()
  } catch (e) { error.value = e.message }
  finally { submitting.value = false }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  submitting.value = true
  try {
    const res = await api.delete(`/tenant/companies/${deleteTarget.value.id}`)
    if (!res.data.success) throw new Error(res.data.message)
    showDelete.value = false; deleteTarget.value = null; await loadCompanies()
  } catch (e) { error.value = e.message }
  finally { submitting.value = false }
}

function openCreateModal() { form.value = { nom: '', secteur: '', rne: '', description: '' }; selectedLogo.value.create = null; showCreate.value = true }
function openEditModal(c) { editForm.value = { id: c.id, nom: c.nom, secteur: c.secteur, rne: c.rne, description: c.description || '' }; selectedLogo.value.edit = null; showEdit.value = true }
function openDeleteModal(c) { deleteTarget.value = c; showDelete.value = true }
function formatDate(d) { return formatRecruiterDate(d) }
</script>

<style scoped>
.page-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f8fafc;
  font-family: 'Inter', sans-serif
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden
}

.content {
  flex: 1;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto
}

.page-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
  color: #0f172a
}

.page-sub {
  font-size: 13px;
  color: #64748b;
  margin: 0
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: none
}

.btn-primary {
  background: #454a83;
  color: #fff;
  box-shadow: 0 4px 12px rgba(69, 74, 131, .25)
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px
}

.stat-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 16px
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center
}

.si-gray {
  background: #f1f5f9
}

.si-green {
  background: #ecfdf5
}

.si-amber {
  background: #fffbeb
}

.stat-label {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: .08em
}

.stat-val {
  font-size: 26px;
  font-weight: 800;
  color: #0f172a
}

.sv-green {
  color: #10b981
}

.sv-amber {
  color: #f59e0b
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px
}

.ccard {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column
}

.ccard-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 14px
}

.ccard-logo {
  width: 52px;
  height: 52px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden
}

.ccard-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain
}

.ccard-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 5px
}

.badge-active {
  background: rgba(69, 74, 131, .1);
  color: #454a83
}

.ccard-name {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 5px
}

.ccard-loc {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 20px
}

.ccard-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 18px
}

.ccard-stat {
  background: #f8fafc;
  border-radius: 8px;
  padding: 8px 10px
}

.ccard-stat-label {
  font-size: 10px;
  font-weight: 700;
  color: #64748b;
  letter-spacing: .07em
}

.ccard-stat-val {
  font-size: 13px;
  font-weight: 700;
  color: #0f172a
}

.ccard-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 14px;
  border-top: 1px solid #f1f5f9;
  margin-top: auto
}

.match-label {
  font-size: 10px;
  color: #94a3b8
}

.match-val {
  font-size: 10px;
  font-weight: 700;
  color: #10b981
}

.ccard-actions {
  display: flex;
  gap: 4px
}

.ccard-actions button {
  width: 32px;
  height: 32px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #64748b;
  transition: all .15s
}

.ccard-actions button:hover {
  background: #f1f5f9;
  color: #454a83;
  border-color: #454a83
}

.ccard-actions button.del:hover {
  background: #fef2f2;
  color: #ef4444;
  border-color: #f87171
}

.add-card {
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  background: transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  min-height: 300px
}

.loader-wrap {
  display: flex;
  justify-content: center;
  padding: 80px
}

.loader {
  width: 30px;
  height: 30px;
  border: 3px solid #e2e8f0;
  border-top-color: #454a83;
  border-radius: 50%;
  animation: spin .7s linear infinite
}

@keyframes spin {
  to {
    transform: rotate(360deg)
  }
}

.waiting-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 116px)
}

.waiting-card {
  background: white;
  border-radius: 20px;
  padding: 56px 48px;
  max-width: 480px;
  width: 100%;
  text-align: center;
  border: 1px solid #e2e8f0
}

.waiting-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px
}

.waiting-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 14px
}

.waiting-desc {
  font-size: 14px;
  color: #64748b;
  line-height: 1.7;
  margin-bottom: 28px
}

.empty-msg {
  text-align: center;
  padding: 80px;
  color: #64748b
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, .4);
  z-index: 1000;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  overflow-y: auto
}

.modal {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, .25);
  width: 100%;
  max-width: 520px;
  margin: auto;
  overflow: hidden;
  animation: modal-in .3s ease-out
}

.modal-sm {
  max-width: 400px
}

.modal-head {
  padding: 24px 32px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: flex-start;
  justify-content: space-between
}

.modal-head h2 {
  font-size: 1.25rem;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 4px
}

.modal-subtitle {
  font-size: .85rem;
  color: #64748b;
  margin: 0
}

.close-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #94a3b8;
  cursor: pointer;
  padding: 8px;
  border-radius: 10px;
  display: flex;
  transition: all .2s
}

.close-btn:hover {
  background: #f1f5f9;
  color: #454a83
}

.modal-form {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 14px
}

.modal-form {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 14px
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px
}

.field label {
  font-size: 11px;
  font-weight: 700;
  color: #374151
}

.field input,
.field textarea {
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: .95rem;
  font-family: inherit;
  color: #1e293b;
  width: 100%;
  outline: none;
  transition: all .2s
}

.field input:focus,
.field textarea:focus {
  background: #fff;
  border-color: #454a83;
  box-shadow: 0 0 0 4px rgba(69, 74, 131, .1)
}

.modal-footer {
  display: flex;
  gap: 10px;
  margin-top: 6px
}

.modal-footer button {
  flex: 1
}

.btn-ghost {
  padding: 12px 24px;
  background: transparent;
  border: 1px solid #e2e8f0;
  font-size: .9rem;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  border-radius: 10px;
  transition: all .2s
}

.btn-ghost:hover {
  background: #f8fafc;
  color: #475569
}

.btn-submit {
  padding: 12px 24px;
  background: #454a83;
  border: none;
  font-size: .9rem;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
  border-radius: 10px;
  transition: all .2s
}

.btn-submit:hover:not(:disabled) {
  background: #363a6a;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(69, 74, 131, .2)
}

.btn-delete {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer
}

.del-center {
  text-align: center;
  margin-bottom: 22px
}

.del-icon {
  width: 52px;
  height: 52px;
  background: #fef2f2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: translateY(10px) scale(.98)
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1)
  }
}
</style>
