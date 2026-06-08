<template>
  <div class="page-layout">
    <!-- Simple Top Bar for public view -->
    <header class="public-header">
      <div class="header-inner">
        <div class="brand">
          <img class="public-brand-logo" src="/appli-logo.png" alt="TalentFlow" />
        </div>
        <div class="header-actions">
          <router-link to="/login" class="btn btn-ghost">Sign In</router-link>
          <router-link to="/register-candidate" class="btn btn-primary">Create Account</router-link>
        </div>
      </div>
    </header>

    <div class="content-scroll">
      <div class="content-inner">

        <div v-if="loading" class="hs-state">
          <div class="hs-spinner"></div>
          <p>Loading offer details...</p>
        </div>

        <div v-else-if="error" class="error-card-wrapper">
          <div class="info-card">
            <h3 style="color: #ef4444; margin-bottom: 8px;">Offer Unavailable</h3>
            <p style="color: #64748b;">{{ error }}</p>
            <button class="btn btn-outline" style="margin-top: 16px;" @click="$router.push('/')">Go to Home</button>
          </div>
        </div>

        <div v-else-if="offre" class="preview-card">
          <!-- Hero -->
          <div class="hero-section">
            <div class="hero-content">
              <h1 class="hero-title">{{ offre.titre }}</h1>
              <div class="hero-meta">
                <span class="meta-item">
                  <MapPinIcon :size="13" />
                  {{ offre.localisation || 'Remote' }}
                </span>
                <span class="meta-item">
                  <BriefcaseIcon :size="13" />
                  {{ offre.nomEntreprise || 'Company' }}
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
                <div class="section-text rich-content" v-html="offre.description || 'No description provided.'"></div>
              </section>

              <!-- Apply Section for Unauthenticated -->
              <section v-if="!isAuthenticated" class="app-form-preview" style="text-align: center; padding: 40px 20px;">
                <LockIcon :size="48" style="color: #94a3b8; margin-bottom: 16px;" />
                <h3 class="section-heading-sm">Authentication Required</h3>
                <p style="font-size: 13px; color: #64748b; margin-bottom: 24px;">You must be logged in to apply for this position.</p>
                
                <div style="display: flex; gap: 12px; justify-content: center;">
                  <router-link to="/login" class="btn btn-primary">Sign In</router-link>
                  <router-link to="/register-candidate" class="btn btn-outline">Create Account</router-link>
                </div>
              </section>
            </div>

            <!-- Right: Sidebar info -->
            <div class="preview-sidebar">
              <div class="info-card">
                <h4 class="info-title-plain">Job Information</h4>
                <ul class="settings-list">
                  <li><span>Posted</span><span>{{ formatDate(offre.creeLe) }}</span></li>
                  <li v-if="deadlineLabel">
                    <span>Date limite</span>
                    <span>{{ deadlineLabel }}</span>
                  </li>
                  <li>
                    <span>Company</span>
                    <span>{{ offre.nomEntreprise }}</span>
                  </li>
                  <li>
                    <span>Contract</span>
                    <span>{{ formatTypeContrat(offre.typeContrat) }}</span>
                  </li>
                </ul>
              </div>

              <div class="info-card primary-border" style="background:#f8fafc; border-color:rgba(69,74,131,0.2);">
                <p v-if="applicationsClosed" style="font-size: 12px; color:#b45309; margin-bottom: 12px; line-height: 1.5;">
                  Les candidatures sont closes (date limite dépassée).
                </p>
                <p v-else style="font-size: 11px; color:#64748b; margin-bottom: 12px; line-height: 1.5;">By applying, you agree to our terms and privacy policy.</p>
                <button class="btn btn-primary" style="width: 100%;" :disabled="applicationsClosed" @click="handleApplyClick">
                  {{ applicationsClosed ? 'Candidatures closes' : 'Apply Now' }}
                </button>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { getPublicOffre } from '../../services/offreService';
import { authStore } from '../../stores/auth';
import {
  MapPinIcon, FileTextIcon, BriefcaseIcon, LockIcon
} from 'lucide-vue-next'

export default {
  name: 'PublicJobView',
  components: {
    MapPinIcon, FileTextIcon, BriefcaseIcon, LockIcon
  },
  data() {
    return {
      offre: null,
      loading: true,
      error: null
    };
  },
  computed: {
    isAuthenticated() {
      return !!authStore.token && !!authStore.user;
    },
    applicationsClosed() {
      if (!this.offre) return false
      const raw = this.offre.dateLimiteCandidatures ?? this.offre.DateLimiteCandidatures
      if (!raw) return false
      const lim = new Date(raw)
      const now = new Date()
      const limUtc = Date.UTC(lim.getUTCFullYear(), lim.getUTCMonth(), lim.getUTCDate())
      const nowUtc = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())
      return nowUtc > limUtc
    },
    deadlineLabel() {
      if (!this.offre) return ''
      const raw = this.offre.dateLimiteCandidatures ?? this.offre.DateLimiteCandidatures
      if (!raw) return ''
      return new Date(raw).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
    },
  },
  async mounted() {
    const token = this.$route.params.token;
    try {
      const res = await getPublicOffre(token);
      this.offre = res.data;

      // If already connected as a Candidate, redirect to apply page (unless candidatures closes)
      if (this.isAuthenticated && authStore.user?.role === 'Candidat' && !this.applicationsClosed) {
        this.$router.replace(`/offres/${this.offre.id}`);
        return;
      }
    } catch (err) {
      this.error = err.response?.data?.message || 'The job link is invalid, expired, or the offer is no longer public.';
    } finally {
      this.loading = false;
    }
  },
  methods: {
    formatTypeContrat(type) {
      const types = ['CDI', 'CDD', 'Stage', 'Freelance', 'Alternance'];
      return typeof type === 'number' ? types[type] : type;
    },
    formatDate(date) {
      if (!date) return 'Recently';
      return new Date(date).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });
    },
    handleApplyClick() {
      if (this.applicationsClosed) return
      if (this.isAuthenticated) {
        if (authStore.user?.role === 'Candidat' && this.offre) {
           this.$router.push(`/offres/${this.offre.id}`);
        } else {
           this.$router.push('/dashboard');
        }
      } else {
        this.$router.push('/login');
      }
    }
  }
};
</script>

<style scoped>
.page-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: #f5f7f8;
  font-family: 'Inter', sans-serif;
}

.public-header {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
}

.header-inner {
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.public-brand-logo {
  height: clamp(26px, 4.2vw, 42px);
  width: auto;
  max-width: min(220px, 72vw);
  object-fit: contain;
  display: block;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 32px 24px;
}

.content-inner {
  max-width: 900px;
  margin: 0 auto;
}

.error-card-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

/* ── Preview card ── */
.preview-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.hero-section {
  background: linear-gradient(135deg, #454a83 0%, #30345d 100%);
  min-height: 180px;
  display: flex;
  align-items: flex-end;
  padding: 32px;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.section-icon { color: #454a83; }

.section-text {
  font-size: 14px;
  color: #0c0d0f;
  line-height: 1.7;
  margin: 0;
  text-align: left;
}

.rich-content :deep(p) { margin-bottom: 1em; }
.rich-content :deep(h2) { font-size: 1.1rem; font-weight: 700; margin: 1.25rem 0 0.5rem; color: #0f172a; }

/* Apply Form Card Placeholder */
.app-form-preview {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.section-heading-sm {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 10px;
  color: #0f172a;
}

/* ── Right sidebar ── */
.preview-sidebar { display: flex; flex-direction: column; gap: 16px; }

.info-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 18px;
}

.info-title-plain { font-size: 13px; font-weight: 700; margin: 0 0 12px; color: #0f172a; }
.settings-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; font-size: 12px; color: #475569; }
.settings-list li { display: flex; justify-content: space-between; }

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s, background 0.15s;
  font-family: inherit;
  text-decoration: none;
}
.btn-primary { background: #454a83; color: #fff; }
.btn-primary:hover:not(:disabled) { opacity: 0.85; }
.btn-ghost { background: transparent; color: #475569; }
.btn-ghost:hover { color: #0f172a; background: #e2e8f0; }
.btn-outline { background: transparent; border: 1px solid #e2e8f0; color: #334155; }
.btn-outline:hover { background: #f8fafc; }

/* Loading State */
.hs-state { text-align: center; padding: 60px 20px; color: #7a8db3; }
.hs-spinner {
  width: 36px; height: 36px; border: 3px solid #e4e8f2; border-top-color: #3b5bdb; border-radius: 50%;
  animation: hs-spin .7s linear infinite; margin: 0 auto 14px;
}

@keyframes hs-spin { to { transform: rotate(360deg); } }

@media (max-width: 860px) {
  .preview-body { grid-template-columns: 1fr; }
  .public-header { padding: 0 14px; }
  .header-inner { flex-wrap: wrap; row-gap: 10px; }
  .brand { min-width: 0; flex: 1 1 auto; }
  .public-brand-logo { max-width: min(180px, 78vw); height: clamp(24px, 5.5vw, 36px); }
}
</style>
