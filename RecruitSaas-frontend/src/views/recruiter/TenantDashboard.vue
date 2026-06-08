<template>
  <div class="page-layout">
    <AppSidebar />
    <main class="main-content">
      <GlobalHeader title="Recruitment portal" />
      <div class="content">
        <div class="page-heading">
          <div>
            <h2 class="page-title">Dashboard</h2>
            <p class="page-sub">Overview of your recruitment activity</p>
          </div>
          <button class="btn btn-primary" @click="goCreateOffer">
            <Plus :size="16" /> New job offer
          </button>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-head">
              <div class="stat-icon si-indigo">
                <Briefcase :size="18" />
              </div>
              <span class="trend positive">{{ trends.activeOffers }}</span>
            </div>
            <p class="stat-value">{{ kpis.activeOffers }}</p>
            <p class="stat-label">published Offers</p>
          </div>
          <div class="stat-card">
            <div class="stat-head">
              <div class="stat-icon si-blue">
                <FileText :size="18" />
              </div>
              <span class="trend positive">{{ trends.monthApplications }}</span>
            </div>
            <p class="stat-value">{{ kpis.monthApplications }}</p>
            <p class="stat-label">Total Applications (this month)</p>
          </div>
          
          <div class="stat-card">
            <div class="stat-head">
              <div class="stat-icon si-green">
                <UserCheck :size="18" />
              </div>
              <span class="trend positive">{{ trends.hires }}</span>
            </div>
            <p class="stat-value">{{ kpis.hires }}</p>
            <p class="stat-label">Filled Offers / Hires</p>
          </div>
        </div>

        <section class="section-card">
          <div class="section-head">
            <h3>Recent offers</h3>
            <button class="btn btn-ghost" @click="$router.push('/recruiter/jobs')">View all offers</button>
          </div>
          <div v-if="loadingOffers" class="state">Loading offers...</div>
          <div v-else-if="recentOffers.length === 0" class="state">No recent offers.</div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Job Title</th>
                <th>Company</th>
                <th>Status</th>
                <th>Applications</th>
                <th>Date Posted</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="offer in recentOffers" :key="offer.id">
                <td class="strong">{{ offer.title }}</td>
                <td>{{ offer.company }}</td>
                <td>
                  <span class="badge" :class="offer.status === 'Published' ? 'badge-active' : 'badge-draft'">{{
                    offer.status }}</span>
                </td>
                <td>{{ offer.candidates }}</td>
                <td>{{ offer.datePosted }}</td>
              </tr>
            </tbody>
          </table>
        </section>

        <section class="section-card">
          <div class="section-head">
            <h3>Recent Applications</h3>
            <button class="btn btn-ghost" @click="$router.push('/recruiter/candidates')">View all candidates</button>
          </div>
          <div v-if="loadingApplications" class="state">Loading...</div>
          <div v-else-if="recentApplications.length === 0" class="state">No recent applications.</div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Candidate Name</th>
                <th>Job Applied</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recentApplications" :key="item.id">
                <td class="strong">{{ item.nomCandidat }}</td>
                <td>{{ item.titreOffre }}</td>
                <td><span class="badge" :class="statusClass(item.statut)">{{ statusLabel(item.statut) }}</span></td>
                <td>{{ formatDate(item.creeLe) }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Briefcase, FileText, Clock3, UserCheck } from 'lucide-vue-next'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import { getOffres } from '../../services/offreService'
import { getCandidatures } from '../../services/candidatureService'
import { applicationStatusLabel, formatRecruiterDate } from '../../utils/recruiterI18n.js'

const offers = ref([])
const applications = ref([])
const loadingOffers = ref(false)
const loadingApplications = ref(false)
const router = useRouter()

onMounted(async () => {
  await Promise.all([loadOffers(), loadApplications()])
})

async function loadOffers() {
  loadingOffers.value = true
  try {
    const res = await getOffres(null, null, null)
    offers.value = (res.data || []).map((o) => ({
      id: o.id,
      title: o.titre || o.title || 'Untitled',
      company: o.nomEntreprise || '-',
      candidates: o.nombreCandidats || 0,
      estPublie: o.estPublie,
      creeLe: o.creeLe
    }))
  } finally {
    loadingOffers.value = false
  }
}

async function loadApplications() {
  loadingApplications.value = true
  try {
    const res = await getCandidatures({})
    applications.value = res.data || []
  } finally {
    loadingApplications.value = false
  }
}

const sortedOffers = computed(() => [...offers.value].sort((a, b) => new Date(b.creeLe || 0) - new Date(a.creeLe || 0)))
const recentOffers = computed(() => sortedOffers.value.slice(0, 5).map((o) => ({
  ...o,
  status: o.estPublie ? 'Published' : 'Draft',
  datePosted: formatDate(o.creeLe)
})))
const sortedApplications = computed(() => [...applications.value].sort((a, b) => new Date(b.creeLe || 0) - new Date(a.creeLe || 0)))
const recentApplications = computed(() => sortedApplications.value.slice(0, 10))

const kpis = computed(() => {
  const now = new Date()
  const m = now.getMonth()
  const y = now.getFullYear()
  const monthApps = applications.value.filter((a) => {
    const d = new Date(a.creeLe)
    return d.getMonth() === m && d.getFullYear() === y
  })
  const accepted = applications.value.filter((a) => a.statut === 'Acceptée' || a.statut === 'Acceptee')
  const durations = accepted.map((a) => {
    const start = new Date(a.creeLe).getTime()
    const end = new Date(a.modifieLe || a.misAJourLe || a.creeLe).getTime()
    return Math.max(0, (end - start) / (1000 * 60 * 60 * 24))
  })
  const avg = durations.length ? `${Math.round(durations.reduce((s, n) => s + n, 0) / durations.length)} days` : '-'
  return {
    activeOffers: offers.value.filter((o) => o.estPublie).length,
    monthApplications: monthApps.length,
    avgRecruitmentDays: avg,
    hires: accepted.length
  }
})

const trends = computed(() => ({
  activeOffers: '+12%',
  monthApplications: '+8%',
  avgRecruitmentDays: '-2 days',
  hires: '+5%'
}))

function statusClass(status) {
  if (status === 'published' || status === 'published') return 'badge-success'
  if (status === 'draft' || status === 'draft') return 'badge-danger'
  if (status === 'En cours') return 'badge-warning'
  return 'badge-active'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return formatRecruiterDate(dateStr)
}

function statusLabel(statut) {
  return applicationStatusLabel(statut)
}

function goCreateOffer() {
  router.push('/recruiter/jobs/create/new/step1')
}
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
  overflow-y: auto;
  /* THIS is the key */

}

.content {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;

}

.page-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-end
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 8px
}

.page-sub {
  margin: 0;
  color: #64748b;
  font-size: 13px
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700
}

.btn-primary {
  background: #454a83;
  color: #fff
}

.btn-ghost {
  background: #f8fafc;
  color: #454a83;
  border: 1px solid #e2e8f0
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  width: 100%;
}

.stat-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px
}

.stat-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px
}

.stat-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center
}

.si-indigo {
  background: #eef2ff;
  color: #454a83
}

.si-blue {
  background: #eff6ff;
  color: #1d4ed8
}

.si-amber {
  background: #fffbeb;
  color: #d97706
}

.si-green {
  background: #ecfdf5;
  color: #059669
}

.trend {
  font-size: 12px;
  font-weight: 700
}

.positive {
  color: #10b981
}

.warning {
  color: #f59e0b
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  color: #0f172a
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin: 4px 0 0
}

.section-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid #e2e8f0
}

.section-head h3 {
  margin: 0;
  font-size: 16px;
  color: #0f172a
}

.table {
  width: 100%;
  border-collapse: collapse
}

.table th {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: #64748b;
  background: #f8fafc;
  padding: 12px 16px;
  text-align: left
}

.table td {
  padding: 12px 16px;
  border-top: 1px solid #f1f5f9;
  font-size: 13px;
  color: #334155
}

.strong {
  font-weight: 700;
  color: #0f172a
}

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700
}

.badge-active {
  background: rgba(69, 74, 131, .12);
  color: #454a83
}

.badge-draft {
  background: #f1f5f9;
  color: #64748b
}

.badge-success {
  background: #dcfce7;
  color: #16a34a
}

.badge-danger {
  background: #ffe4e6;
  color: #e11d48
}

.badge-warning {
  background: #fffbeb;
  color: #d97706
}

.state {
  padding: 24px;
  color: #64748b;
  font-size: 13px
}
</style>
