<template>
  <div class="hs-root">
    <AppSidebar />

    <main class="hs-main">
      <GlobalHeader title="Dashboard" />
      <div class="dash-page">
 
        <!-- TOP BAR -->
        <div class="dash-topbar">
          <div>
            <h1 class="dash-title">Welcome back, {{ firstName }}!</h1>
            <p class="dash-sub">Here's what's happening with your job search today.</p>
          </div>
        </div>

        <!-- CONTENT GRID -->
        <div class="dash-grid">

          <!-- LEFT COLUMN -->
          <div class="dash-left">

            <!-- STAT CARDS -->
            <div class="dash-stats">
              <!-- Active Offers Card -->
              <div class="dash-stat-card">
                <div class="dash-stat-top">
                  <div class="dash-stat-icon-wrap">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polygon points="5 3 19 12 5 21 5 3"/>
                    </svg>
                  </div>
                  <span class="dash-stat-lbl">ACTIVE<br>OFFERS</span>
                </div>
                <div class="dash-stat-num">{{ activeOffersCount }}</div>
                <div class="dash-stat-trend">{{ getTrendText() }}</div>
              </div>

              <!-- Pending Interviews Card -->
              <div class="dash-stat-card">
                <div class="dash-stat-top">
                  <div class="dash-stat-icon-wrap">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                      <line x1="16" y1="2" x2="16" y2="6"/>
                      <line x1="8" y1="2" x2="8" y2="6"/>
                      <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                  </div>
                  <span class="dash-stat-lbl">PENDING<br>INTERVIEWS</span>
                </div>
                <div class="dash-stat-num">{{ stats.interviews }}</div>
                <div class="dash-stat-trend">Next: Tomorrow, 10 AM</div>
              </div>
            </div>

            <!-- RECOMMENDED JOBS (AI) -->
            <div class="dash-section">
              <div class="dash-section-header">
                <h3 class="dash-section-title">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                  Recently Published Offers
                </h3>
                <button class="dash-link" @click="$router.push('/offres')">View all offers</button>
              </div>

              <div v-if="loadingJobs" class="dash-loading"><div class="hs-spinner"></div></div>
              <div v-else class="dash-reco-grid">
                <div v-for="job in recommendedJobs" :key="job.id" class="dash-reco-card">
                  <div class="dash-reco-top">
                    <div class="dash-reco-logo" :style="{ background: logoColor(job.titre) }">
                      {{ job.titre ? job.titre.charAt(0).toUpperCase() : '?' }}
                    </div>
                  </div>
                  <h4 class="dash-reco-title">{{ job.titre }}</h4>
                  <p class="dash-reco-company">{{ job.entrepriseNom || '—' }} • {{ job.localisation || 'Remote' }}</p>
                  <div class="dash-reco-tags">
                    <span v-for="tag in (job.tags || [])" :key="tag" class="dash-tag">{{ tag }}</span>
                  </div>
                  <div class="dash-reco-actions">
                    <button class="dash-btn-teal" @click="$router.push({ path: '/offres', query: { applyId: job.id } })">Quick Apply</button>
                  </div>
                </div>
                <div v-if="recommendedJobs.length === 0" class="dash-empty-reco">
                  <p>No recommendations yet — <span class="dash-link" @click="$router.push('/offres')">browse jobs</span></p>
                </div>
              </div>
            </div>

            
          </div>

          <!-- RIGHT COLUMN -->
          <div class="dash-right">

            <!-- NOTIFICATIONS -->
            <div class="dash-card">
              <div class="dash-card-header">
                <div class="dash-card-title-row">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                  </svg>
                  Recent Notifications
                </div>
                <span class="dash-notif-badge">{{ notifications.length }} New</span>
              </div>

              <div class="dash-notif-list">
                <div v-for="notif in notifications" :key="notif.id" class="dash-notif-item">
                  <div class="dash-notif-icon" :style="{ background: notif.color + '20' }">
                    <svg v-if="notif.type === 'calendar'" width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="notif.color" stroke-width="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                      <line x1="16" y1="2" x2="16" y2="6"/>
                      <line x1="8" y1="2" x2="8" y2="6"/>
                      <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    <svg v-else-if="notif.type === 'check'" width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="notif.color" stroke-width="2">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                    <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="notif.color" stroke-width="2">
                      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                      <polyline points="22,6 12,13 2,6"/>
                    </svg>
                  </div>
                  <div class="dash-notif-body">
                    <p class="dash-notif-title">{{ notif.title }}</p>
                    <p class="dash-notif-desc">{{ notif.desc }}</p>
                    <p class="dash-notif-time">{{ notif.time }}</p>
                  </div>
                </div>
              </div>
              <button class="dash-mark-read">Mark all as read</button>
            </div>

            <!-- PROFILE STRENGTH -->
            
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import AppSidebar from '../../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../../components/layout/GlobalHeader.vue'
import { getCandidatOffres } from '../../../services/candidatService'
import { getCandidatures } from '../../../services/candidatureService'

const API_BASE = 'http://localhost:5202'

function parseJwt(token) {
  try { return JSON.parse(atob(token.split('.')[1])) } catch { return {} }
}

export default {
  name: 'CandidatDashboard',
  components: { AppSidebar, GlobalHeader },
  data() {
    const token = localStorage.getItem('token')
    const payload = token ? parseJwt(token) : {}
    const email = payload.email
               || payload['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress']
               || ''
    const stored = localStorage.getItem('username') || ''
    const raw = stored || email.split('@')[0] || 'Candidate'
    return {
      firstName: raw.charAt(0).toUpperCase() + raw.slice(1),
      loadingJobs: true,
      profileStrength: 0, // ✅ Initialisé à 0, sera calculé dynamiquement
      profileData: null,  // ✅ Stocke les données du profil
      stages: ['Applied', 'Screening', 'Interview', 'Offer'],
      stats: { applications: 12, interviews: 4, aiMatch: 92 },
      applications: [],
      allOffers: [],
      recommendedJobs: [],
      notifications: [
        { id: 1, type: 'calendar', color: '#6366f1', title: 'Interview Scheduled',  desc: 'With HR at FinTech Global for tomorrow at 10:00 AM.', time: '2 hours ago' },
        { id: 2, type: 'check',    color: '#14b8a6', title: 'Application Update',   desc: 'Your profile was viewed by 3 recruiters today.',       time: '5 hours ago' },
        { id: 3, type: 'message',  color: '#f59e0b', title: 'New Message',          desc: 'Recruiter Sarah sent you a follow-up message.',          time: 'Yesterday' }
      ]
    }
  },
  computed: {
    activeOffersCount() {
      return this.allOffers.length || this.recommendedJobs.length
    },
    
    newOffersThisWeek() {
      const oneWeekAgo = new Date()
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
      
      return this.allOffers.filter(offer => {
        const offerDate = new Date(offer.creeLe || offer.datePublication || Date.now())
        return offerDate >= oneWeekAgo
      }).length
    },

    // ✅ Couleur dynamique selon le score
    profileStrengthColor() {
      if (this.profileStrength >= 80) return '#10b981' // vert
      if (this.profileStrength >= 50) return '#f59e0b' // orange
      return '#ef4444' // rouge
    },

    // ✅ Texte d'aide dynamique
    profileStrengthHint() {
      if (this.profileStrength >= 80) return "Great profile! You're highly visible."
      if (this.profileStrength >= 50) return 'Add more info to increase visibility.'
      return 'Complete your profile to get noticed.'
    }
  },
  async mounted() {
    const token = localStorage.getItem('token')
    if (!token) { this.$router.push('/login'); return }
    await Promise.all([
      this.loadRecommended(), 
      this.loadApplications(), 
      this.loadAllOffers(),
      this.loadProfileStrength() // ✅ Charger le taux de complétion
    ])
  },
  methods: {
    // ✅ Navigation vers ProfileView
    goToProfile() {
      this.$router.push('/profile')
    },

    // ✅ Charger et calculer le taux de complétion du profil
    async loadProfileStrength() {
      const token = localStorage.getItem('token')
      if (!token) return

      try {
        const res = await fetch(`${API_BASE}/api/candidat/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        })

        if (res.ok) {
          const result = await res.json()
          if (result.success && result.data) {
            this.profileData = result.data
            this.profileStrength = this.calculateProfileStrength(result.data)
          }
        }
      } catch (err) {
        console.error('❌ Error loading profile strength:', err)
        // Fallback: calculer avec données partielles si disponibles
        this.profileStrength = this.calculateProfileStrength(this.profileData || {})
      }
    },

    // ✅ Calculer le score de complétion (0-100)
    calculateProfileStrength(data) {
      if (!data) return 0

      // Champs importants à vérifier
      const fields = [
        'fullName', 'email', 'phone', 'location', 'bio',
        'seeking', 'education', 'fieldOfStudy', 'experience',
        'availability', 'linkedin', 'github', 'portfolioUrl'
      ]

      // Compter les champs remplis
      const filled = fields.filter(f => data[f]?.trim()).length
      
      // Bonus pour les compétences
      const hasSkills = Array.isArray(data.skills) && data.skills.length > 0 ? 1 : 0
      
      // Bonus pour l'avatar
      const hasAvatar = data.avatarUrl ? 1 : 0

      // Calcul: (champs remplis + bonus) / (total champs + bonus max) * 100
      const total = fields.length + 2 // +2 pour skills et avatar
      const score = Math.round(((filled + hasSkills + hasAvatar) / total) * 100)

      return Math.min(score, 100) // Cap à 100%
    },

    async loadAllOffers() {
      try {
        const { data } = await getCandidatOffres()
        this.allOffers = Array.isArray(data) ? data : []
      } catch (e) {
        console.warn('Erreur chargement offres:', e.message)
        this.allOffers = []
      }
    },
    
    getTrendText() {
      const count = this.newOffersThisWeek
      if (count === 0) return 'No new offers this week'
      if (count === 1) return '+1 new this week'
      return `+${count} new this week`
    },
    
    async loadApplications() {
      try {
        const { data } = await getCandidatures()
        const list = Array.isArray(data) ? data : (data?.data || data?.items || [])
        this.applications = list.slice(0, 3).map(a => ({
          id:         a.id,
          titre:      a.offreNom || a.titreOffre || a.titre || '—',
          entreprise: a.entrepriseNom || a.entreprise || '—',
          statut:     a.statut || 'In Review',
          stage:      a.stage || 1
        }))
        this.stats.applications = list.length
      } catch (e) {
        console.warn('Applications non chargées:', e.message)
      }
    },
    
    async loadRecommended() {
      this.loadingJobs = true
      try {
        const { data } = await getCandidatOffres()
        const allTags = [[]]
        this.recommendedJobs = data.slice(0, 4).map((j, i) => ({
          ...j,
          matchScore: [98, 95, 91, 88][i] || 85,
          tags: allTags[i] || []
        }))
      } catch (e) {
        this.recommendedJobs = []
      } finally {
        this.loadingJobs = false
      }
    },
    
    logoColor(t) {
      if (!t) return '#1e3a5f'
      const c = ['#1e3a5f','#1a3c2e','#3b1f4e','#2e1f1a','#1a2e3b']
      let h = 0
      for (let i = 0; i < t.length; i++) h = t.charCodeAt(i) + ((h << 5) - h)
      return c[Math.abs(h) % c.length]
    },
    
    statusClass(s) {
      const v = (s || '').toLowerCase()
      if (v === 'accepted' || v === 'offer') return 'status-green'
      if (v === 'rejected')                  return 'status-red'
      if (v === 'interview')                 return 'status-blue'
      return 'status-teal'
    }
  }
}
</script>

<style scoped>
.hs-root  { display: flex; min-height: 100vh; background: #f1f5f9; font-family: 'Inter', sans-serif; }
.hs-main  { flex: 1; min-width: 0; overflow-y: auto; }
.dash-page { padding: 28px 32px; }

/* Topbar */
.dash-topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.dash-title { font-size: 22px; font-weight: 700; color: #0f172a; margin: 0 0 4px; }
.dash-sub   { font-size: 13px; color: #64748b; margin: 0; }
.dash-topbar-right { display: flex; align-items: center; gap: 10px; }

/* Buttons */
.dash-btn-primary {
  display: inline-flex; align-items: center; gap: 7px;
  background: #1A2B4C; color: white; border: none; border-radius: 8px;
  padding: 9px 18px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit;
}
.dash-btn-primary:hover { opacity: 0.88; }
.dash-btn-primary-sm {
  background: #1A2B4C; color: white; border: none; border-radius: 6px;
  padding: 7px 14px; font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit;
}
.dash-btn-teal {
  flex: 1; background: #14b8a6; color: white; border: none; border-radius: 8px;
  padding: 10px; font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit;
}
.dash-btn-teal:hover { background: #0d9488; }
.dash-btn-ghost-sm {
  background: none; color: #475569; border: 1px solid #e2e8f0; border-radius: 6px;
  padding: 7px 14px; font-size: 12px; font-weight: 500; cursor: pointer; font-family: inherit;
}
.dash-btn-ghost-sm:hover { background: #f1f5f9; }
.dash-btn-outline-full {
  width: 100%; padding: 9px; background: none; border: 1px solid #1A2B4C; color: #1A2B4C;
  border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit;
  transition: all 0.15s;
}
.dash-btn-outline-full:hover { background: #1A2B4C; color: white; transform: translateY(-1px); }
.dash-icon-btn {
  width: 38px; height: 38px; background: white; border: 1px solid #e2e8f0; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; color: #64748b; cursor: pointer;
}
.dash-icon-btn-sm {
  width: 30px; height: 30px; background: #f1f5f9; border: none; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; color: #64748b; cursor: pointer;
}
.dash-link { font-size: 12px; color: #1A2B4C; background: none; border: none; cursor: pointer; font-weight: 600; font-family: inherit; }
.dash-link:hover { text-decoration: underline; }

/* Stats */
.dash-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.dash-stat-card { background: #1A2B4C; border-radius: 12px; padding: 20px; color: white; overflow: hidden; }
.dash-stat-top  { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 14px; }
.dash-stat-icon-wrap {
  width: 36px; height: 36px; border-radius: 8px; background: rgba(255,255,255,0.12);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.dash-stat-lbl { font-size: 9px; font-weight: 700; letter-spacing: 0.1em; color: rgba(255,255,255,0.55); line-height: 1.4; text-transform: uppercase; }
.dash-stat-num { font-size: 2.2rem; font-weight: 700; line-height: 1; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.dash-stat-match-badge { font-size: 11px; font-weight: 700; background: rgba(20,184,166,0.25); color: #14b8a6; padding: 3px 8px; border-radius: 9999px; }
.dash-stat-trend { font-size: 11px; color: rgba(255,255,255,0.5); }

/* Grid */
.dash-grid { display: grid; grid-template-columns: 1fr 320px; gap: 20px; align-items: start; }
.dash-left  { display: flex; flex-direction: column; gap: 20px; }
.dash-right { display: flex; flex-direction: column; gap: 16px; }

/* Section */
.dash-section { background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 20px; }
.dash-section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.dash-section-title { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 700; color: #0f172a; margin: 0; }
.dash-section-actions { display: flex; gap: 6px; }

/* Reco cards */
.dash-reco-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.dash-reco-card { background: #1A2B4C; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.dash-reco-top  { display: flex; justify-content: space-between; align-items: flex-start; }
.dash-reco-logo {
  width: 42px; height: 42px; border-radius: 10px; color: white; font-weight: 700; font-size: 18px;
  display: flex; align-items: center; justify-content: center;
}
.dash-match-pill { font-size: 10px; font-weight: 700; background: rgba(20,184,166,0.2); color: #14b8a6; padding: 3px 8px; border-radius: 9999px; }
.dash-reco-title   { font-size: 14px; font-weight: 700; color: white; margin: 0; }
.dash-reco-company { font-size: 11px; color: rgba(255,255,255,0.5); margin: 0; }
.dash-reco-tags    { display: flex; flex-wrap: wrap; gap: 5px; }
.dash-tag { font-size: 10px; font-weight: 600; background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.7); padding: 3px 7px; border-radius: 5px; }
.dash-reco-actions { display: flex; gap: 8px; margin-top: 4px; }
.dash-empty-reco   { padding: 20px; text-align: center; color: #94a3b8; font-size: 13px; }

/* App cards */
.dash-app-list { display: flex; flex-direction: column; gap: 14px; }
.dash-app-card { border: 1px solid #f1f5f9; border-radius: 10px; padding: 16px; background: #f8fafc; }
.dash-app-header { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.dash-app-logo {
  width: 40px; height: 40px; border-radius: 8px; flex-shrink: 0; color: white;
  font-weight: 700; font-size: 16px; display: flex; align-items: center; justify-content: center;
}
.dash-app-info { flex: 1; }
.dash-app-title   { font-size: 14px; font-weight: 700; color: #0f172a; margin: 0 0 3px; }
.dash-app-company { font-size: 12px; color: #64748b; margin: 0; }
.dash-status-pill { font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 9999px; white-space: nowrap; }
.status-teal  { background: rgba(20,184,166,0.15); color: #0d9488; }
.status-green { background: #dcfce7; color: #166534; }
.status-red   { background: #fee2e2; color: #991b1b; }
.status-blue  { background: #dbeafe; color: #1d4ed8; }

/* Progress */
.dash-progress-section { margin-bottom: 14px; }
.dash-progress-label {
  display: flex; justify-content: space-between; font-size: 9px; font-weight: 700;
  color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px;
}
.dash-stages {
  display: grid; grid-template-columns: repeat(4, 1fr);
  position: relative; text-align: center;
}
.dash-stage-line {
  position: absolute; top: 6px; left: 12.5%; right: 12.5%;
  height: 2px; background: #e2e8f0; z-index: 0; border-radius: 9999px;
}
.dash-stage-line-fill { height: 100%; background: #14b8a6; border-radius: 9999px; transition: width 0.4s; }
.dash-stage { display: flex; flex-direction: column; align-items: center; gap: 6px; position: relative; z-index: 1; }
.dash-stage-dot { width: 14px; height: 14px; border-radius: 50%; border: 2px solid; }
.dash-stage-done { background: #14b8a6; border-color: #14b8a6; }
.dash-stage-todo { background: white; border-color: #e2e8f0; }
.dash-stage-label { font-size: 10px; color: #64748b; font-weight: 500; }
.dash-app-footer { display: flex; justify-content: flex-end; gap: 8px; }
.dash-app-empty { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 32px; color: #94a3b8; font-size: 13px; }

/* Right cards */
.dash-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 18px; }
.dash-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.dash-card-title-row { display: flex; align-items: center; gap: 7px; font-size: 14px; font-weight: 700; color: #0f172a; }
.dash-card-title-only { font-size: 14px; font-weight: 700; color: #0f172a; margin: 0 0 14px; }
.dash-notif-badge { background: #1A2B4C; color: white; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 9999px; }
.dash-notif-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 14px; }
.dash-notif-item { display: flex; gap: 10px; }
.dash-notif-icon { width: 36px; height: 36px; border-radius: 8px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.dash-notif-body { flex: 1; }
.dash-notif-title { font-size: 13px; font-weight: 700; color: #0f172a; margin: 0 0 3px; }
.dash-notif-desc  { font-size: 11px; color: #64748b; margin: 0 0 3px; line-height: 1.4; }
.dash-notif-time  { font-size: 10px; color: #94a3b8; margin: 0; }
.dash-mark-read {
  width: 100%; padding: 8px; background: none; border: 1px solid #e2e8f0; border-radius: 7px;
  font-size: 12px; font-weight: 600; color: #475569; cursor: pointer; font-family: inherit;
}
.dash-mark-read:hover { background: #f1f5f9; }

/* Profile ring */
.dash-profile-ring-row { display: flex; align-items: center; gap: 16px; margin-bottom: 14px; }
.dash-ring-wrap { position: relative; width: 80px; height: 80px; flex-shrink: 0; }
.dash-ring-label { 
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; 
  font-size: 14px; font-weight: 700; transition: color 0.3s;
}
.dash-profile-hint { font-size: 12px; color: #64748b; line-height: 1.5; margin: 0; transition: color 0.3s; }

/* Loading */
.dash-loading { display: flex; justify-content: center; padding: 32px; }
.hs-spinner {
  width: 28px; height: 28px; border: 3px solid #e2e8f0; border-top-color: #1A2B4C;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 1100px) {
  .dash-grid { grid-template-columns: 1fr; }
  .dash-right { flex-direction: row; flex-wrap: wrap; }
  .dash-card  { flex: 1; min-width: 260px; }
}
@media (max-width: 768px) {
  .dash-page      { padding: 16px; }
  .dash-stats     { grid-template-columns: 1fr; }
  .dash-reco-grid { grid-template-columns: 1fr; }
}
</style>