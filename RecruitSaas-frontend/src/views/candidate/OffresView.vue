<template>
  <div class="hs-root">
    <AppSidebar />

    <main class="main-content">
      <GlobalHeader title="Job Exploration" subTitle="Find your next career move" />

      <div class="content">
        <div class="candidate-grid">
          <div class="main-column">
            <OffreList
              :offres="offres"
              :loading="loading"
              :err="err"
              @open-detail="goToOffer"
              @start-apply="goToOffer"
              @retry="fetchOffres"
            />
          </div>

          <!-- RIGHT PANEL -->
          <aside class="side-column">
            <!-- Profile Strength Card avec cercle -->
            <div class="info-card profile-card">
              <h3 class="card-title">Profile Strength</h3>
              
              <!-- Cercle de progression -->
              <div class="profile-circle-wrapper">
                <svg class="profile-circle" viewBox="0 0 120 120">
                  <!-- Cercle de fond -->
                  <circle
                    class="circle-bg"
                    cx="60"
                    cy="60"
                    r="52"
                    stroke="#e8edf5"
                    stroke-width="8"
                    fill="none"
                  />
                  <!-- Cercle de progression -->
                  <circle
                    class="circle-progress"
                    cx="60"
                    cy="60"
                    r="52"
                    :stroke="strengthColor"
                    stroke-width="8"
                    fill="none"
                    :stroke-dasharray="circleDasharray"
                    :stroke-linecap="profileStrength > 0 && profileStrength < 100 ? 'round' : 'butt'"
                    transform="rotate(-90 60 60)"
                    :style="{ transition: 'stroke-dasharray 1s ease' }"
                  />
                  <!-- Texte au centre -->
                  <text
                    x="60"
                    y="55"
                    text-anchor="middle"
                    :fill="strengthColor"
                    font-size="28"
                    font-weight="800"
                  >
                    {{ profileStrength }}%
                  </text>
                  <text
                    x="60"
                    y="75"
                    text-anchor="middle"
                    fill="#aab3c9"
                    font-size="9"
                    font-weight="600"
                  >
                    COMPLETE
                  </text>
                </svg>
              </div>

              <!-- Barre de progression linéaire (optionnelle) -->
              <div class="comp-row">
                <span>Completion</span>
                <span class="comp-pct" :style="{ color: strengthColor }">{{ profileStrength }}%</span>
              </div>
              <div class="prog-bar">
                <div class="prog-fill" :style="{ width: profileStrength + '%', background: strengthColor }"></div>
              </div>
              
              <p class="strength-hint" :style="{ color: strengthHintColor }">
                {{ strengthHint }}
              </p>
              
              <!-- Bouton Complete Profile -->
              <button class="btn-outline" @click="goToProfile">
                Complete Profile
              </button>
            </div>

            <!-- Dans la section "Trending Skills" -->
<div class="info-card">
  <h3 class="card-title"> Trending Skills</h3>
  <div class="skills-tags">
    <span class="tag tag-hot">Generative AI</span>
    <span class="tag tag-hot">LLM Engineering</span>
    <span class="tag">Prompt Engineering</span>
    <span class="tag tag-hot">RAG Systems</span>
    <span class="tag">MLOps & Model Deployment</span>
    <span class="tag">Vector Databases</span>
    <span class="tag tag-hot">Agentic Workflows</span>
    <span class="tag">Edge AI / TinyML</span>
    <span class="tag">AI Ethics & Governance</span>
    <span class="tag">Cloud-Native Architecture</span>
    <span class="tag tag-hot">Platform Engineering</span>
    <span class="tag">FinOps & Cost Optimization</span>
  </div>
</div>
          </aside>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import OffreList from './components/OffreList.vue'
import { getCandidatOffres } from '../../services/candidatService'

const API_BASE = 'http://localhost:5202'

function parseJwt(token) {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload))
  } catch {
    return {}
  }
}

function initialsFromEmail(email) {
  if (!email) return '?'
  return email.charAt(0).toUpperCase()
}

export default {
  name: 'Offres',
  components: {
    AppSidebar,
    GlobalHeader,
    OffreList
  },
  data() {
    const token = localStorage.getItem('token')
    const payload = token ? parseJwt(token) : {}
    const email = payload.email || payload['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'] || ''

    return {
      loading: false,
      err: null,
      offres: [],
      scores: {},
      userName: email || 'Candidate',
      userInitials: initialsFromEmail(email),
      profileData: {
        fullName: '',
        email: '',
        phone: '',
        location: '',
        bio: '',
        seeking: '',
        education: '',
        portfolioUrl: '',
        skills: []
      }
    }
  },
  computed: {
    // Calcul du taux de complétion du profil
    profileStrength() {
      const fields = ['fullName', 'email', 'phone', 'location', 'bio', 'seeking', 'education', 'portfolioUrl']
      const filled = fields.filter(f => this.profileData[f]?.trim()).length
      const hasSkills = this.profileData.skills?.length > 0 ? 1 : 0
      return Math.round(((filled + hasSkills) / (fields.length + 1)) * 100)
    },

    // Couleur basée sur le pourcentage
    strengthColor() {
      if (this.profileStrength >= 80) return '#10b981' // vert
      if (this.profileStrength >= 50) return '#f59e0b' // orange
      return '#ef4444' // rouge
    },

    // Couleur du texte d'aide
    strengthHintColor() {
      if (this.profileStrength >= 80) return '#10b981'
      if (this.profileStrength >= 50) return '#f59e0b'
      return '#6b7a99'
    },

    // Texte d'aide
    strengthHint() {
      if (this.profileStrength >= 80) return "Great profile! You're highly visible."
      if (this.profileStrength >= 50) return 'Add more info to increase visibility.'
      return 'Complete your profile to get noticed.'
    },

    // Calcul SVG stroke-dasharray
    circleDasharray() {
      const circumference = 2 * Math.PI * 52 // r=52
      const offset = circumference - (this.profileStrength / 100) * circumference
      return `${offset} ${circumference}`
    }
  },
  methods: {
    async fetchOffres() {
      this.loading = true
      this.err = null
      try {
        const { data } = await getCandidatOffres()
        this.offres = data
        this.assignScores(data)
      } catch (e) {
        console.error('❌ API Error:', e)
        this.err = `Impossible de charger les offres (${e.message}).`
      } finally {
        this.loading = false
      }
    },

    // ✅ Charger le profil pour calculer le taux de complétion
    async fetchProfile() {
      const token = localStorage.getItem('token')
      if (!token) return

      try {
        const res = await fetch(`${API_BASE}/api/candidat/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        })

        if (res.ok) {
          const result = await res.json()
          if (result.success && result.data) {
            this.profileData = {
              fullName: result.data.fullName || '',
              email: result.data.email || '',
              phone: result.data.phone || '',
              location: result.data.location || '',
              bio: result.data.bio || '',
              seeking: result.data.seeking || '',
              education: result.data.education || '',
              portfolioUrl: result.data.portfolioUrl || '',
              skills: Array.isArray(result.data.skills) ? result.data.skills : []
            }
          }
        }
      } catch (err) {
        console.error('❌ Error fetching profile:', err)
      }
    },

    // ✅ Navigation vers ProfileView
    goToProfile() {
      this.$router.push('/profile')
    },

    assignScores(list) {
      list.forEach(o => {
        if (!this.scores[o.id]) {
          this.scores[o.id] = Math.floor(Math.random() * 25) + 70
        }
      })
    },

    goToOffer(id) {
      this.$router.push(`/offres/${id}`)
    }
  },

  async mounted() {
    const token = localStorage.getItem('token')
    if (!token) {
      window.location.href = '/login'
      return
    }
    const payload = parseJwt(token)
    if (payload.exp && Date.now() / 1000 > payload.exp) {
      localStorage.removeItem('token')
      window.location.href = '/login'
      return
    }

    // Charger les offres ET le profil
    await Promise.all([
      this.fetchOffres(),
      this.fetchProfile()
    ])

    const applyId = this.$route.query.applyId
    const detailId = this.$route.query.detailId

    if (detailId && !applyId) {
      this.$router.push(`/offres/${detailId}`)
      return
    }

    if (applyId) {
      this.$router.push(`/offres/${applyId}`)
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Layout ─────────────────────────────────────── */
.hs-root { display: flex; width: 100%; min-height: 100vh; font-family: 'Inter', -apple-system, sans-serif; background: #f0f2f5; color: #1a2035; }
.main-content { flex: 1; min-width: 0; display: flex; flex-direction: column; min-height: 100vh; }
.content { flex: 1; padding: 28px 32px; overflow-y: auto; }
.candidate-grid { display: flex; gap: 24px; align-items: flex-start; }
.main-column { flex: 1; min-width: 0; }

/* ── Side Column ────────────────────────────────── */
.side-column { width: 280px; min-width: 280px; flex-shrink: 0; display: flex; flex-direction: column; gap: 16px; position: sticky; top: 28px; height: fit-content; }
.info-card { background: #fff; border-radius: 14px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.06); border: 1px solid #e8ecf4; }
.card-title { font-size: 13px; font-weight: 700; color: #1a2035; margin: 0 0 14px; }

/* ── Profile Circle ─────────────────────────────── */
.profile-circle-wrapper {
  display: flex;
  justify-content: center;
  margin: 16px 0;
}
.profile-circle {
  width: 120px;
  height: 120px;
}
.circle-bg {
  fill: none;
  stroke: #e8edf5;
  stroke-width: 8;
}
.circle-progress {
  fill: none;
  stroke-width: 8;
  transition: stroke-dasharray 1s ease;
}

/* ── Progress Bar ───────────────────────────────── */
.comp-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #6b7a99; margin-bottom: 8px; }
.comp-pct { font-weight: 700; }
.prog-bar { height: 7px; background: #e8edf5; border-radius: 6px; overflow: hidden; margin-bottom: 12px; }
.prog-fill { height: 100%; border-radius: 6px; transition: width 0.5s ease, background 0.3s; }

/* ── Hint & Button ──────────────────────────────── */
.strength-hint { font-size: 11.5px; margin-bottom: 14px; line-height: 1.4; text-align: center; }
.btn-outline { width: 100%; padding: 10px; border: 2px solid #3b5bdb; border-radius: 8px; background: transparent; color: #3b5bdb; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; transition: all .15s; }
.btn-outline:hover { background: #3b5bdb; color: #fff; transform: translateY(-1px); }

/* ── Skills Tags ────────────────────────────────── */
.skills-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { background: #f0f4ff; color: #3b5bdb; border-radius: 20px; padding: 5px 12px; font-size: 12px; font-weight: 500; }

/* Tags de base */
.tag {
  background: linear-gradient(135deg, #f0f4ff 0%, #e6eaff 100%);
  color: #3b5bdb;
  border: 1px solid #c7d2fe;
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: default;
}

.tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 91, 219, 0.15);
  border-color: #3b5bdb;
}

/* 🔥 Tags "HOT" - les plus tendances */
.tag-hot {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border: 1px solid #fcd34d;
  position: relative;
  animation: pulse-glow 2.5s ease-in-out infinite;
}

.tag-hot::before {
  position: absolute;
  top: -6px;
  right: -6px;
  font-size: 10px;
  animation: bounce 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.3); }
  50% { box-shadow: 0 0 0 6px rgba(245, 158, 11, 0); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* 🆕 Tags "NEW" - émergents */
.tag-new {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #166534;
  border: 1px solid #86efac;
}

.tag-new::after {
  content: 'NEW';
  font-size: 8px;
  font-weight: 800;
  background: #16a34a;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 6px;
  vertical-align: middle;
}

/* 🧠 Tags "AI" - spécialisés IA */
.tag-ai {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #5b21b6;
  border: 1px solid #c4b5fd;
  font-weight: 700;
}

/* Responsive pour les petits écrans */
@media (max-width: 768px) {
  .skills-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .tag {
    font-size: 10px;
    padding: 5px 10px;
  }
}
/* ── Responsive ─────────────────────────────────── */
@media (max-width: 1200px) { .side-column { display: none; } }
@media (max-width: 768px) { .content { padding: 16px; } }
</style>