<template>
  <div class="hs-list-page">
    <div class="hs-hero">
      <div class="hs-hero-blob hs-hero-blob--1"></div>
      <div class="hs-hero-blob hs-hero-blob--2"></div>
      <div class="hs-hero-inner">
        <h1 class="hs-hero-title">Find your next career move</h1>
        <p class="hs-hero-sub">Discover opportunities tailored to your profile</p>
        <div class="hs-hero-search">
          <div class="hs-glass-input">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="q" placeholder="Job title, skills, keywords..." />
          </div>
          <div class="hs-glass-input hs-glass-input--loc">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            <input v-model="qLoc" placeholder="Location..." />
          </div>
          <button class="hs-btn-search" @click="applySearch">Search</button>
        </div>
        <div class="hs-stats-strip">
          <div class="hs-stat-pill"><span class="hs-stat-n">{{ offres.length }}</span><span class="hs-stat-l">Open positions</span></div>
          <div class="hs-stat-pill"><span class="hs-stat-n">{{ companiesCount }}</span><span class="hs-stat-l">Companies</span></div>
          <div class="hs-stat-pill"><span class="hs-stat-n">{{ newThisWeek }}</span><span class="hs-stat-l">New this week</span></div>
        </div>
      </div>
    </div>

    <div class="hs-filters-row">
      <span class="hs-filter-lbl"></span>
      <button v-for="f in filters" :key="f.value" class="hs-pill" :class="{ 'hs-pill--on': activeFilter === f.value }" @click="activeFilter = f.value">{{ f.label }}</button>
    </div>

    <div v-if="loading" class="hs-state">
      <div class="hs-spinner"></div><p>Loading opportunities...</p>
    </div>
    <div v-else-if="err" class="hs-state">
      <div class="hs-err-icon">x</div><p class="hs-err-msg">{{ err }}</p>
      <button class="hs-btn-search" style="margin-top:12px" @click="$emit('retry')">Retry</button>
    </div>

    <div v-else class="hs-grid">
      <div v-for="o in filtered" :key="o.id" class="hs-jcard" @click="$emit('open-detail', o.id)">
        <div class="hs-jcard-top">
          <div class="hs-logo-wrap">
            <img v-if="companyLogo(o)" :src="companyLogo(o)" :alt="companyName(o)" class="hs-logo-img" />
            <div v-else class="hs-logo-placeholder">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
            </div>
          </div>
          <div class="hs-badges">
            <span v-if="isHot(o)" class="hs-badge hs-badge--hot">Hot</span>
            <span v-if="isNew(o)" class="hs-badge hs-badge--new">New</span>
            <span v-if="o.matchScore" class="hs-badge hs-badge--match">{{ o.matchScore }}% match</span>
          </div>
        </div>
        <div class="hs-jcard-mid">
          <div class="hs-job-title">{{ o.titre }}</div>
          <div class="hs-company">{{ companyName(o) }}</div>
        </div>
        <div class="hs-jcard-tags">
          <span v-if="o.localisation" class="hs-tag">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            {{ o.localisation }}
          </span>
          <span v-if="o.typeContrat" class="hs-tag">{{ o.typeContrat }}</span>
          <span v-if="o.teletravail" class="hs-tag">Remote</span>
        </div>
        <div class="hs-jcard-bottom">
          <span class="hs-posted">{{ formatDate(o.creeLe) }}</span>
          <div class="hs-actions" @click.stop>
            <button
              type="button"
              class="hs-btn-save"
              :class="{ 'hs-btn-save--on': isSaved(o.id), 'hs-btn-save--loading': savingId === o.id }"
              :title="isSaved(o.id) ? 'Remove from saved' : 'Save job'"
              :disabled="savingId === o.id"
              @click="onToggleSave(o)"
            >
              <svg v-if="savingId === o.id" class="hs-save-spin" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/></svg>
              <svg v-else width="13" height="13" viewBox="0 0 24 24" :fill="isSaved(o.id) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            </button>
            <button class="hs-btn-apply" @click.stop="$emit('start-apply', o.id)">
              Apply
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </button>
          </div>
        </div>
      </div>
      <div v-if="!filtered.length" class="hs-empty">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <p>No jobs match your search.</p>
      </div>
    </div>
  </div>
</template>

<script>
// ✅ SEUL import autorisé pour les favoris — plus aucun import depuis utils/savedOffres.js
import { fetchSavedJobs, saveJob, unsaveJob } from '@/utils/savedOffres'

export default {
  name: 'OffreList',
  props: {
    offres:  { type: Array,   required: true },
    loading: { type: Boolean, default: false },
    err:     { type: String,  default: null  }
  },
  data() {
    return {
      savedIds:     new Set(),
      savingId:     null,
      q:            '',
      qLoc:         '',
      activeFilter: 'all',
      filters: [
        { label: 'All jobs',   value: 'all'       },
        { label: 'Full-time',  value: 'full-time'  },
        { label: 'Remote',     value: 'remote'     },
        { label: 'IT & Tech',  value: 'it'         },
        { label: 'Finance',    value: 'finance'    },
        { label: 'Marketing',  value: 'marketing'  },
        { label: 'Design',     value: 'design'     },
      ]
    }
  },
  async mounted() {
    await this.loadSavedIds()
    window.addEventListener('saved-jobs-changed', this.onSavedChanged)
  },
  beforeUnmount() {
    window.removeEventListener('saved-jobs-changed', this.onSavedChanged)
  },
  computed: {
    companiesCount() {
      return new Set(this.offres.map(o => this.companyNameRaw(o)).filter(Boolean)).size
    },
    newThisWeek() {
      const week = 7 * 24 * 60 * 60 * 1000
      return this.offres.filter(o => { const d = new Date(o.creeLe); return !isNaN(d) && Date.now() - d < week }).length
    },
    filtered() {
      return this.offres.filter(o => {
        const title   = (o.titre        || '').toLowerCase()
        const loc     = (o.localisation || '').toLowerCase()
        const cat     = (o.categorie    || '').toLowerCase()
        const contrat = (o.typeContrat  || '').toLowerCase()
        return (
          (!this.q    || title.includes(this.q.toLowerCase())) &&
          (!this.qLoc || loc.includes(this.qLoc.toLowerCase())) &&
          this.matchFilter(o, cat, contrat, loc)
        )
      })
    }
  },
  methods: {
    async loadSavedIds() {
      try {
        const list = await fetchSavedJobs()
        this.savedIds = new Set(list.map(s => String(s.offreId)))
      } catch {
        this.savedIds = new Set()
      }
    },
    onSavedChanged(event) {
      if (event?.detail?.offreId != null) {
        const id = String(event.detail.offreId)
        const next = new Set(this.savedIds)
        event.detail.saved ? next.add(id) : next.delete(id)
        this.savedIds = next
      } else {
        this.loadSavedIds()
      }
    },
    isSaved(offreId) {
      return this.savedIds.has(String(offreId))
    },
    async onToggleSave(offre) {
      if (this.savingId === offre.id) return
      this.savingId = offre.id
      const id = String(offre.id)
      const wasSaved = this.savedIds.has(id)
      const next = new Set(this.savedIds)
      wasSaved ? next.delete(id) : next.add(id)
      this.savedIds = next
      try {
        wasSaved ? await unsaveJob(offre.id) : await saveJob(offre.id)
        window.dispatchEvent(new CustomEvent('saved-jobs-changed', { detail: { offreId: offre.id, saved: !wasSaved } }))
      } catch (e) {
        const rollback = new Set(this.savedIds)
        wasSaved ? rollback.add(id) : rollback.delete(id)
        this.savedIds = rollback
        console.error('[OffreList] toggle save error:', e)
      } finally {
        this.savingId = null
      }
    },
    applySearch() {},
    companyNameRaw(o) {
      if (!o) return ''
      return o.entrepriseNom || o.nomEntreprise || o.entreprise?.nom || o.entreprise?.name || o.companyName || o.company?.nom || o.company?.name || o.tenant?.nom || o.tenant?.name || ''
    },
    companyName(o)  { return this.companyNameRaw(o) || '—' },
    companyLogo(o)  {
      if (!o) return null
      return o.logoUrl || o.entrepriseLogo || o.entreprise?.logoUrl || o.entreprise?.logo || o.company?.logoUrl || o.company?.logo || o.tenant?.logoUrl || o.tenant?.logo || null
    },
    matchFilter(o, cat, contrat, loc) {
      switch (this.activeFilter) {
        case 'all':       return true
        case 'full-time': return contrat.includes('full') || contrat.includes('cdi') || contrat.includes('temps plein')
        case 'remote':    return o.teletravail || loc.includes('remote')
        case 'it':        return cat.includes('it') || cat.includes('tech') || cat.includes('développ') || cat.includes('dev')
        case 'finance':   return cat.includes('financ') || cat.includes('compta')
        case 'marketing': return cat.includes('market') || cat.includes('comm')
        case 'design':    return cat.includes('design') || cat.includes('ux') || cat.includes('ui')
        default:          return true
      }
    },
    isNew(o)  { const d = new Date(o.creeLe); return !isNaN(d) && Date.now() - d < 3 * 86400000 },
    isHot(o)  { return o.isHot || o.candidaturesCount > 20 },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      if (isNaN(d)) return ''
      const diff = Math.floor((Date.now() - d) / 86400000)
      if (diff === 0) return 'Today'
      if (diff === 1) return 'Yesterday'
      if (diff < 7)  return `${diff} days ago`
      if (diff < 14) return '1 week ago'
      return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
    }
  }
}
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
.hs-list-page { padding-bottom: 2rem; }
.hs-hero { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #1e40af 100%); border-radius: 20px; padding: 36px 32px 32px; margin-bottom: 28px; position: relative; overflow: hidden; }
.hs-hero-blob { position: absolute; border-radius: 50%; pointer-events: none; }
.hs-hero-blob--1 { top: -60px; right: -60px; width: 260px; height: 260px; background: rgba(99,102,241,.18); }
.hs-hero-blob--2 { bottom: -40px; left: 40%; width: 180px; height: 180px; background: rgba(56,189,248,.10); }
.hs-hero-inner { position: relative; z-index: 1; }
.hs-hero-title { font-size: 24px; font-weight: 700; color: #fff; margin-bottom: 6px; }
.hs-hero-sub { font-size: 13px; color: rgba(255,255,255,.55); margin-bottom: 24px; }
.hs-hero-search { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
.hs-glass-input { display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,.10); border: 0.5px solid rgba(255,255,255,.20); border-radius: 12px; padding: 0 14px; height: 42px; flex: 1; min-width: 180px; backdrop-filter: blur(8px); }
.hs-glass-input svg { color: rgba(255,255,255,.5); flex-shrink: 0; }
.hs-glass-input input { background: transparent; border: none; outline: none; font-size: 13px; color: #fff; font-family: inherit; width: 100%; }
.hs-glass-input input::placeholder { color: rgba(255,255,255,.35); }
.hs-glass-input--loc { max-width: 200px; }
.hs-btn-search { height: 42px; padding: 0 20px; background: #3b82f6; border: none; border-radius: 12px; color: #fff; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; white-space: nowrap; transition: background .15s; }
.hs-btn-search:hover { background: #2563eb; }
.hs-stats-strip { display: flex; gap: 10px; flex-wrap: wrap; }
.hs-stat-pill { background: rgba(255,255,255,.10); border: 0.5px solid rgba(255,255,255,.15); border-radius: 10px; padding: 8px 16px; backdrop-filter: blur(6px); display: flex; flex-direction: column; }
.hs-stat-n { font-size: 18px; font-weight: 700; color: #fff; line-height: 1.2; }
.hs-stat-l { font-size: 11px; color: rgba(255,255,255,.45); margin-top: 2px; }
.hs-filters-row { display: flex; gap: 8px; margin-bottom: 22px; flex-wrap: wrap; align-items: center; }
.hs-filter-lbl { font-size: 12px; color: #6b7a99; margin-right: 4px; }
.hs-pill { display: inline-flex; align-items: center; gap: 4px; padding: 5px 14px; border-radius: 20px; font-size: 12px; cursor: pointer; border: 1px solid #dde1ea; background: #fff; color: #6b7a99; font-family: inherit; transition: all .15s; }
.hs-pill:hover { border-color: #3b82f6; color: #3b82f6; }
.hs-pill--on { background: #eff6ff; border-color: #3b82f6; color: #1d4ed8; font-weight: 600; }
.hs-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.hs-jcard { background: #fff; border: 1px solid #e8ecf4; border-radius: 16px; padding: 20px; cursor: pointer; transition: border-color .2s, transform .2s, box-shadow .2s; display: flex; flex-direction: column; gap: 14px; }
.hs-jcard:hover { border-color: #3b82f6; transform: translateY(-3px); box-shadow: 0 8px 24px rgba(59,130,246,.1); }
.hs-jcard-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.hs-logo-wrap { width: 48px; height: 48px; min-width: 48px; border-radius: 12px; background: #f4f6fb; border: 1px solid #e8ecf4; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.hs-logo-img { width: 100%; height: 100%; object-fit: contain; border-radius: 11px; }
.hs-logo-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
.hs-logo-placeholder svg { color: #bec8dd; }
.hs-badges { display: flex; flex-direction: column; align-items: flex-end; gap: 5px; }
.hs-badge { font-size: 10px; font-weight: 600; padding: 3px 9px; border-radius: 20px; white-space: nowrap; }
.hs-badge--new { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.hs-badge--hot { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }
.hs-badge--match { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.hs-job-title { font-size: 14px; font-weight: 700; color: #1a2035; margin-bottom: 4px; line-height: 1.4; }
.hs-company { font-size: 12px; color: #6b7a99; }
.hs-jcard-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.hs-tag { display: inline-flex; align-items: center; gap: 3px; font-size: 11px; color: #6b7a99; background: #f4f6fb; border-radius: 6px; padding: 3px 9px; }
.hs-jcard-bottom { display: flex; align-items: center; justify-content: space-between; padding-top: 12px; border-top: 1px solid #f0f3f9; margin-top: auto; }
.hs-posted { font-size: 11px; color: #aab3c9; }
.hs-actions { display: flex; align-items: center; gap: 6px; }
.hs-btn-save { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border: 1px solid #dde1ea; border-radius: 8px; background: transparent; color: #6b7a99; cursor: pointer; transition: all .15s; }
.hs-btn-save:hover { border-color: #3b82f6; color: #3b82f6; }
.hs-btn-save--on { border-color: #3b82f6; background: #eff6ff; color: #1d4ed8; }
.hs-btn-save--loading { opacity: 0.6; cursor: not-allowed; }
.hs-btn-save:disabled { pointer-events: none; }
.hs-save-spin { animation: hs-spin .6s linear infinite; transform-origin: center; }
@keyframes hs-spin { to { transform: rotate(360deg); } }
.hs-btn-apply { display: inline-flex; align-items: center; gap: 5px; padding: 7px 14px; border: none; border-radius: 9px; background: #1e3a8a; color: #fff; font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit; transition: background .15s; }
.hs-btn-apply:hover { background: #1e40af; }
.hs-state { grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: #7a8db3; }
.hs-spinner { width: 36px; height: 36px; border: 3px solid #e4e8f2; border-top-color: #3b82f6; border-radius: 50%; animation: hs-spin .7s linear infinite; margin: 0 auto 14px; }
.hs-err-icon { font-size: 28px; color: #ef4444; margin-bottom: 8px; }
.hs-err-msg { color: #444; font-size: 14px; }
.hs-empty { grid-column: 1 / -1; display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px 20px; color: #aab3c9; }
.hs-empty p { font-size: 14px; }
@media (max-width: 700px) {
  .hs-hero { padding: 24px 18px 22px; }
  .hs-hero-title { font-size: 20px; }
  .hs-glass-input--loc { display: none; }
  .hs-grid { grid-template-columns: 1fr; }
}
</style>