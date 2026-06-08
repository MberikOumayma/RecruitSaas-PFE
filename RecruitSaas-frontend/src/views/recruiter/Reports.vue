<template>
  <div class="page-layout">
    <AppSidebar />
    <main class="main-content">
      <GlobalHeader title="Recruitment portal" />
      <div class="content">

        <!-- Heading -->
        <div class="page-heading">
          <div>
            <h2 class="page-title">Reports & Analytics</h2>
            <p class="page-sub">Export recruitment data and AI insights in one click</p>
          </div>
        </div>

        <!-- KPI Cards -->
        <div class="kpi-grid">
          <div class="kpi-card" v-for="k in kpis" :key="k.label">
            <div class="kpi-icon-wrap" :style="{ background: k.iconBg }">
              <component :is="k.icon" :size="20" :style="{ color: k.iconColor }" />
            </div>
            <div>
              <p class="kpi-label">{{ k.label }}</p>
              <p class="kpi-value" :style="{ color: k.valueColor || '#0F172A' }">
                {{ kpiData[k.key] != null ? kpiData[k.key] : '—' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Section: Global exports -->
        <div class="section-card">
          <div class="section-header">
            <div class="section-icon-wrap">
              <DatabaseIcon :size="18" />
            </div>
            <div>
              <h3 class="section-title">Global Exports</h3>
              <p class="section-sub">Download the full candidate base with AI scores</p>
            </div>
          </div>
          <div class="export-actions">
            <button class="export-btn btn-excel" @click="exportAllExcel" :disabled="exporting.allExcel">
              <component :is="exporting.allExcel ? 'Loader2Icon' : 'TableIcon'" :size="16"
                :class="{ spin: exporting.allExcel }" />
              {{ exporting.allExcel ? 'Generating…' : 'All Candidates — Excel' }}
            </button>
          </div>
        </div>

        <!-- Section: Per-offer reports -->
        <div class="section-card">
          <div class="section-header">
            <div class="section-icon-wrap">
              <BriefcaseIcon :size="18" />
            </div>
            <div>
              <h3 class="section-title">Per Offer Reports</h3>
              <p class="section-sub">Select a job offer to export its candidates list</p>
            </div>
          </div>

          <!-- Offer picker -->
          <div class="offer-picker-row">
            <select class="filter-select" v-model="selectedOffreId" @change="onOfferChange">
              <option value="">— Select a job offer —</option>
              <option v-for="o in offres" :key="o.id" :value="o.id">{{ o.titre }}</option>
            </select>
            <button class="export-btn btn-excel" :disabled="!selectedOffreId || exporting.offerExcel"
              @click="exportOfferExcel">
              <component :is="exporting.offerExcel ? 'Loader2Icon' : 'TableIcon'" :size="16"
                :class="{ spin: exporting.offerExcel }" />
              {{ exporting.offerExcel ? 'Generating…' : 'Candidates — Excel' }}
            </button>
          </div>
        </div>

        <!-- Section: How it works -->
        <div class="info-card">
          <InfoIcon :size="16" class="info-icon" />
          <p class="info-text">
            Reports are generated server-side. Files are downloaded directly to your browser.
            PDF and Word exports per candidate are available in the
            <router-link to="/recruiter/candidates" class="info-link">Candidate Details</router-link> page.
          </p>
        </div>

      </div>
    </main>
  </div>
</template>

<script>
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import {
  BarChart2Icon, UsersIcon, BriefcaseIcon, BrainIcon,
  TableIcon, DatabaseIcon, InfoIcon, Loader2Icon
} from 'lucide-vue-next'
import { getGlobalKpis, downloadOfferCandidatesExcel } from '../../services/reportService.js'
import { getOffres } from '../../services/offreService.js'
import { useNotificationStore } from '../../stores/notification'

export default {
  name: 'Reports',
  components: {
    AppSidebar, GlobalHeader,
    BarChart2Icon, UsersIcon, BriefcaseIcon, BrainIcon,
    TableIcon, DatabaseIcon, InfoIcon, Loader2Icon
  },
  setup() {
    const ns = useNotificationStore()
    const toast = {
      success: (m) => ns.addToast({ type: 'success', message: m }),
      error: (m) => ns.addToast({ type: 'error', message: m }),
      info: (m) => ns.addToast({ type: 'info', message: m })
    }
    return { toast }
  },
  data() {
    return {
      kpiData: { total: null, avgScore: null, accepted: null, offers: null },
      offres: [],
      selectedOffreId: '',
      selectedOffreTitre: '',
      exporting: { allExcel: false, offerExcel: false }
    }
  },
  computed: {
    kpis() {
      return [
        { key: 'total', label: 'Total Applications', icon: 'UsersIcon', iconBg: 'rgba(69,74,131,0.1)', iconColor: '#454a83' },
        { key: 'avgScore', label: 'Avg AI Score', icon: 'BrainIcon', iconBg: 'rgba(13,148,136,0.1)', iconColor: '#0D9488', valueColor: '#0D9488' },
        { key: 'accepted', label: 'Accepted', icon: 'BarChart2Icon', iconBg: 'rgba(22,163,74,0.1)', iconColor: '#16a34a', valueColor: '#16a34a' },
        { key: 'offers', label: 'Active Offers', icon: 'BriefcaseIcon', iconBg: 'rgba(245,158,11,0.1)', iconColor: '#d97706' }
      ]
    }
  },
  async created() {
    await Promise.all([this.fetchKpis(), this.fetchOffres()])
  },
  methods: {
    async fetchKpis() {
      try {
        const res = await getGlobalKpis()
        const d = res.data
        this.kpiData = {
          total: d.totalCandidatures ?? d.total,
          avgScore: d.scoreMoyenIA != null ? Math.round(d.scoreMoyenIA) + '%' : null,
          accepted: d.acceptees ?? d.accepted,
          offers: d.totalOffres ?? d.offers
        }
      } catch {
        // KPI endpoint may not exist yet — silently fail
      }
    },
    async fetchOffres() {
      try {
        const res = await getOffres()
        this.offres = (res.data || []).map(o => ({
          id: o.id,
          titre: o.titre || o.title || 'Untitled'
        }))
      } catch {
        this.toast.error('Failed to load job offers.')
      }
    },
    onOfferChange() {
      const o = this.offres.find(x => x.id === this.selectedOffreId)
      this.selectedOffreTitre = o?.titre || 'offer'
    },
    async exportAllExcel() {
      this.exporting.allExcel = true
      try {
        await downloadOfferCandidatesExcel('all', 'all_candidates')
        this.toast.success('Excel downloaded!')
      } catch {
        this.toast.error('Failed to generate Excel report.')
      } finally {
        this.exporting.allExcel = false
      }
    },
    async exportOfferExcel() {
      if (!this.selectedOffreId) return
      this.exporting.offerExcel = true
      try {
        await downloadOfferCandidatesExcel(this.selectedOffreId, this.selectedOffreTitre)
        this.toast.success('Excel downloaded!')
      } catch {
        this.toast.error('Failed to generate Excel report.')
      } finally {
        this.exporting.offerExcel = false
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

.content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Heading */
.page-heading { margin-bottom: 4px; }
.page-title { font-size: 24px; font-weight: 700; color: #0F172A; margin: 0 0 6px; }
.page-sub { font-size: 14px; color: #64748B; margin: 0; }

/* KPI grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.kpi-card {
  background: #fff;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s;
}

.kpi-card:hover { box-shadow: 0 4px 12px rgba(69, 74, 131, 0.1); }

.kpi-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94A3B8;
  margin: 0 0 4px;
}

.kpi-value {
  font-size: 26px;
  font-weight: 700;
  margin: 0;
  line-height: 1;
}

/* Section cards */
.section-card {
  background: #fff;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.section-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(69, 74, 131, 0.08);
  color: #454a83;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 4px;
}

.section-sub {
  font-size: 13px;
  color: #64748B;
  margin: 0;
}

/* Export buttons */
.export-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-family: inherit;
  transition: opacity 0.15s, transform 0.1s;
}

.export-btn:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.export-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-excel { background: #16a34a; color: #fff; }

.spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Offer picker */
.offer-picker-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  flex: 1;
  min-width: 240px;
  height: 44px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 0 14px;
  font-size: 14px;
  color: #0F172A;
  outline: none;
  font-family: inherit;
  cursor: pointer;
}

/* Info card */
.info-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: rgba(69, 74, 131, 0.05);
  border: 1px solid rgba(69, 74, 131, 0.15);
  border-radius: 10px;
  padding: 16px 18px;
}

.info-icon { color: #454a83; flex-shrink: 0; margin-top: 1px; }

.info-text {
  font-size: 13px;
  color: #475569;
  margin: 0;
  line-height: 1.6;
}

.info-link {
  color: #454a83;
  font-weight: 600;
  text-decoration: none;
}

.info-link:hover { text-decoration: underline; }
</style>
