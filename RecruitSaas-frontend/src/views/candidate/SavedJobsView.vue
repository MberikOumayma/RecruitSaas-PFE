<template>
  <div class="hs-root">
    <AppSidebar />

    <main class="main-content">
      <GlobalHeader title="Saved jobs" subTitle="Offers you bookmarked for later" />

      <div class="content">

        <!-- Loading -->
        <div v-if="loading" class="hs-loading">
          <div class="hs-spinner"></div>
          <span>Loading your saved jobs…</span>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="hs-error">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <p>{{ error }}</p>
          <button class="hs-btn-primary" @click="load">Retry</button>
        </div>

        <!-- Empty state -->
        <div v-else-if="!saved.length" class="hs-empty">
          <div class="hs-empty-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <p class="hs-empty-title">No saved jobs yet</p>
          <p class="hs-empty-sub">Browse jobs and tap the bookmark icon to save them here.</p>
          <router-link to="/offres" class="hs-btn-primary">Explore jobs</router-link>
        </div>

        <!-- Grid -->
        <div v-else class="hs-grid">
          <div
            v-for="o in saved"
            :key="o.id"
            class="hs-jcard"
            @click="goDetail(o.id)"
          >
            <div class="hs-jcard-top">
              <div class="hs-logo-wrap">
                <img
                  v-if="o.logoUrl"
                  :src="o.logoUrl"
                  :alt="o.nomEntreprise || 'Company'"
                  class="hs-logo-img"
                  @error="onLogoError"
                />
                <div v-else class="hs-logo-placeholder">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>
                  </svg>
                </div>
              </div>

              <button
                type="button"
                class="hs-btn-remove"
                :class="{ 'hs-btn-removing': removing === o.id }"
                title="Remove from saved"
                @click.stop="removeOne(o.id)"
              >
                <svg v-if="removing !== o.id" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
                <div v-else class="hs-mini-spinner"></div>
              </button>
            </div>

            <div class="hs-jcard-mid">
              <div class="hs-job-title">{{ o.titre }}</div>
              <div class="hs-company">{{ o.nomEntreprise || '—' }}</div>
            </div>

            <div class="hs-jcard-tags">
              <span v-if="o.localisation" class="hs-tag">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                {{ o.localisation }}
              </span>
              <span v-if="o.typeContrat" class="hs-tag">{{ o.typeContrat }}</span>
              <span v-if="o.teletravail" class="hs-tag">Remote</span>
            </div>

            <div class="hs-jcard-bottom">
              <span class="hs-posted">{{ formatDate(o.creeLe) }}</span>
              <span class="hs-saved-hint">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor" style="margin-right:4px">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                </svg>
                Saved {{ formatSavedDate(o.savedAt) }}
              </span>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script>
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import { fetchSavedJobs, unsaveJob } from '../../utils/savedOffres'

export default {
  name: 'SavedJobsView',
  components: { AppSidebar, GlobalHeader },

  data() {
    return {
      saved: [],
      loading: false,
      error: null,
      removing: null   // offreId en cours de suppression
    }
  },

  mounted() {
    this.load()
    window.addEventListener('saved-jobs-changed', this.load)
  },

  beforeUnmount() {
    window.removeEventListener('saved-jobs-changed', this.load)
  },

  methods: {
    // ✅ MÉTHODE CORRIGÉE : Aplatir les données API
    async load() {
      this.loading = true
      this.error = null
      try {
        const savedJobs = await fetchSavedJobs()
        
        // L'API retourne : [{ id, offreId, savedAt, offre: { id, titre, ... } }]
        // On extrait l'offre et on fusionne avec les métadonnées
        this.saved = savedJobs.map(sj => ({
          ...sj.offre,              // toutes les propriétés de l'offre
          savedAt: sj.savedAt,      // date de sauvegarde
          savedJobId: sj.id         // ID de l'enregistrement SavedJob
        }))
        
      } catch (e) {
        this.error = 'Failed to load saved jobs. Please try again.'
        console.error('[SavedJobsView] load error:', e)
      } finally {
        this.loading = false
      }
    },

    async removeOne(offreId) {
      this.removing = offreId
      try {
        await unsaveJob(offreId)
        // ✅ Filtrer en utilisant l'ID de l'offre (maintenant directement accessible)
        this.saved = this.saved.filter(o => o.id !== offreId)
        // Notifier les autres composants
        window.dispatchEvent(new CustomEvent('saved-jobs-changed', { 
          detail: { offreId, saved: false } 
        }))
      } catch (e) {
        console.error('[SavedJobsView] remove error:', e)
        this.error = 'Could not remove this job. Please try again.'
      } finally {
        this.removing = null
      }
    },

    goDetail(offreId) {
      this.$router.push({ path: '/offres', query: { detailId: String(offreId) } })
    },

    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      if (isNaN(d)) return ''
      const diff = Math.floor((Date.now() - d) / 86400000)
      if (diff === 0) return 'Today'
      if (diff === 1) return 'Yesterday'
      if (diff < 7) return `${diff} days ago`
      if (diff < 14) return '1 week ago'
      return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    },

    formatSavedDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      if (isNaN(d)) return ''
      return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
    },

    onLogoError(e) {
      e.target.style.display = 'none'
      const ph = e.target.parentElement?.querySelector('.hs-logo-placeholder')
      if (ph) ph.style.display = 'flex'
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.hs-root {
  display: flex;
  width: 100%;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, sans-serif;
  background: #f0f2f5;
  color: #1a2035;
}
.main-content { flex: 1; min-width: 0; display: flex; flex-direction: column; min-height: 100vh; }
.content { flex: 1; padding: 28px 32px; overflow-y: auto; }

/* Loading */
.hs-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px 24px;
  color: #6b7a99;
  font-size: 14px;
}
.hs-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e8ecf4;
  border-top-color: #1e3a8a;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
.hs-mini-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #fecaca;
  border-top-color: #ef4444;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Error */
.hs-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 24px;
  background: #fff;
  border: 1px solid #fecaca;
  border-radius: 16px;
  max-width: 400px;
  margin: 40px auto;
  color: #ef4444;
  text-align: center;
}
.hs-error p { font-size: 14px; }

/* Empty */
.hs-empty {
  padding: 72px 24px;
  text-align: center;
  background: #fff;
  border: 1px solid #e8ecf4;
  border-radius: 16px;
  max-width: 480px;
  margin: 40px auto;
  color: #aab3c9;
}
.hs-empty-icon {
  margin: 0 auto 16px;
  opacity: 0.6;
  animation: float 3s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
.hs-empty svg { display: block; }
.hs-empty-title { font-size: 17px; font-weight: 700; color: #1a2035; margin-bottom: 8px; }
.hs-empty-sub { font-size: 13px; color: #6b7a99; margin-bottom: 22px; line-height: 1.5; }

.hs-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 22px;
  border-radius: 10px;
  background: #1e3a8a;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
}
.hs-btn-primary:hover { background: #1e40af; transform: translateY(-1px); }

/* Grid */
.hs-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }

/* Card */
.hs-jcard {
  background: #fff;
  border: 1px solid #e8ecf4;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.hs-jcard:hover {
  border-color: #3b82f6;
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.12);
}
.hs-jcard-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }

.hs-logo-wrap {
  width: 48px; height: 48px; min-width: 48px;
  border-radius: 12px; background: #f4f6fb;
  border: 1px solid #e8ecf4;
  display: flex; align-items: center; justify-content: center; overflow: hidden;
}
.hs-logo-img { width: 100%; height: 100%; object-fit: contain; border-radius: 11px; }
.hs-logo-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
.hs-logo-placeholder svg { color: #bec8dd; }

.hs-btn-remove {
  width: 36px; height: 36px;
  border-radius: 10px;
  border: 1px solid #e8ecf4;
  background: #fff;
  color: #94a3b8;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}
.hs-btn-remove:hover, .hs-btn-removing {
  border-color: #fecaca; background: #fef2f2; color: #ef4444;
}

.hs-job-title {
  font-size: 15px; font-weight: 700; color: #1a2035;
  margin-bottom: 4px; line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}
.hs-company { font-size: 13px; color: #6b7a99; }
.hs-jcard-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.hs-tag {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; color: #6b7a99; background: #f4f6fb;
  border-radius: 6px; padding: 4px 10px; font-weight: 500;
}
.hs-jcard-bottom {
  display: flex; align-items: center; justify-content: space-between;
  padding-top: 12px; border-top: 1px solid #f0f3f9; margin-top: auto;
}
.hs-posted { font-size: 11px; color: #aab3c9; }
.hs-saved-hint {
  display: inline-flex; align-items: center;
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.05em;
  color: #1d4ed8; background: #eff6ff;
  border: 1px solid #bfdbfe; padding: 4px 10px; border-radius: 20px;
}

@media (max-width: 700px) {
  .content { padding: 16px; }
  .hs-grid { grid-template-columns: 1fr; }
  .hs-jcard { padding: 16px; }
}
.content::-webkit-scrollbar { width: 6px; }
.content::-webkit-scrollbar-track { background: transparent; }
.content::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.content::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>