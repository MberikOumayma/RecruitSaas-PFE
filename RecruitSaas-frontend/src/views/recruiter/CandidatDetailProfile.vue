<template>
  <Teleport to="body">
    <div class="cdp-overlay" @click.self="$emit('close')">
      <div class="cdp-modal" role="dialog" aria-modal="true" aria-labelledby="cdp-title">

        <!-- Close -->
        <button type="button" class="cdp-close" aria-label="Close" @click="$emit('close')">
          <XIcon :size="20" />
        </button>

        <!-- Loading -->
        <div v-if="loading" class="cdp-state">
          <div class="cdp-spinner"></div>
          <p>Loading profile…</p>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="cdp-state cdp-state--err">
          <div class="cdp-err-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <p class="cdp-err-msg">{{ error }}</p>
          <button type="button" class="cdp-btn-retry" @click="load">Retry</button>
        </div>

        <!-- Profile content -->
        <template v-else-if="profile">

          <!-- Hero -->
          <div class="cdp-hero">
            <div class="cdp-hero-bg-shape"></div>
            <div class="cdp-hero-inner">
              <div class="cdp-avatar-wrap">
                <img
                  :src="displayAvatar"
                  :alt="profile.fullName || 'Candidate'"
                  class="cdp-avatar"
                  @error="onImgError"
                />
                <div v-if="seekingLabel" class="cdp-seeking-dot" :title="seekingLabel"></div>
              </div>
              <div class="cdp-hero-text">
                <h2 id="cdp-title" class="cdp-name">{{ profile.fullName || '—' }}</h2>
                <div class="cdp-email-row">
                  <MailIcon :size="15" class="cdp-icon-soft" />
                  <span>{{ profile.email || '—' }}</span>
                </div>
                <div v-if="profile.phone" class="cdp-email-row">
                  <PhoneIcon :size="15" class="cdp-icon-soft" />
                  <span>{{ profile.phone }}</span>
                </div>
                <div class="cdp-hero-badges">
                  <span v-if="seekingLabel" class="cdp-badge cdp-badge--teal">{{ seekingLabel }}</span>
                  <span v-if="profile.location" class="cdp-badge cdp-badge--blue">
                    <MapPinIcon :size="12" /> {{ profile.location }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Body -->
          <div class="cdp-body">

            <!-- Career row -->
            <div class="cdp-section">
              <div class="cdp-section-header">
                <BriefcaseIcon :size="15" class="cdp-section-icon" />
                <h3 class="cdp-section-title">Career</h3>
              </div>
              <div class="cdp-grid-4">
                <div class="cdp-field">
                  <span class="cdp-lbl">Education</span>
                  <span class="cdp-val">{{ formatEducation(profile.education) }}</span>
                </div>
                <div class="cdp-field">
                  <span class="cdp-lbl">Field of study</span>
                  <span class="cdp-val">{{ profile.fieldOfStudy || '—' }}</span>
                </div>
                <div class="cdp-field">
                  <span class="cdp-lbl">Experience</span>
                  <span class="cdp-val">{{ formatExperience(profile.experience) }}</span>
                </div>
                <div class="cdp-field">
                  <span class="cdp-lbl">Availability</span>
                  <span class="cdp-val cdp-val--avail">{{ formatAvailability(profile.availability) }}</span>
                </div>
              </div>
            </div>

            <!-- Bio -->
            <div v-if="profile.bio" class="cdp-section">
              <div class="cdp-section-header">
                <FileTextIcon :size="15" class="cdp-section-icon" />
                <h3 class="cdp-section-title">Bio</h3>
              </div>
              <p class="cdp-bio">{{ profile.bio }}</p>
            </div>

            <!-- Skills -->
            <div v-if="profile.skills && profile.skills.length" class="cdp-section">
              <div class="cdp-section-header">
                <ZapIcon :size="15" class="cdp-section-icon" />
                <h3 class="cdp-section-title">Skills</h3>
              </div>
              <div class="cdp-tags">
                <span v-for="(sk, i) in profile.skills" :key="i" class="cdp-tag">{{ sk }}</span>
              </div>
            </div>

            <!-- Links -->
            <div class="cdp-section cdp-section--last">
              <div class="cdp-section-header">
                <LinkIcon :size="15" class="cdp-section-icon" />
                <h3 class="cdp-section-title">Links</h3>
              </div>
              <div class="cdp-links">
                <a v-if="profile.linkedin"     :href="normalizeUrl(profile.linkedin)"     target="_blank" rel="noopener" class="cdp-link cdp-link--li">
                  <LinkedinIcon :size="16" /> LinkedIn
                </a>
                <a v-if="profile.github"        :href="normalizeUrl(profile.github)"        target="_blank" rel="noopener" class="cdp-link cdp-link--gh">
                  <GithubIcon :size="16" /> GitHub
                </a>
                <a v-if="profile.portfolioUrl" :href="normalizeUrl(profile.portfolioUrl)" target="_blank" rel="noopener" class="cdp-link cdp-link--port">
                  <GlobeIcon :size="16" /> Portfolio
                </a>
                <p v-if="!profile.linkedin && !profile.github && !profile.portfolioUrl" class="cdp-muted">
                  No links provided
                </p>
              </div>
            </div>

          </div>
        </template>

      </div>
    </div>
  </Teleport>
</template>

<script>
import {
  MailIcon, XIcon, LinkedinIcon, GithubIcon, GlobeIcon,
  PhoneIcon, MapPinIcon, BriefcaseIcon, FileTextIcon,
  ZapIcon, LinkIcon
} from 'lucide-vue-next'
import { getCandidateProfileForCandidature } from '../../services/candidatureService.js'

const API_ORIGIN = 'http://localhost:5202'

const SEEKING_LABELS = {
  student:     'Student',
  internship:  'Looking for Internship',
  job:         'Looking for Job',
  freelance:   'Freelance',
  not_looking: 'Not Looking'
}

export default {
  name: 'CandidatDetailProfile',
  components: {
    MailIcon, XIcon, LinkedinIcon, GithubIcon, GlobeIcon,
    PhoneIcon, MapPinIcon, BriefcaseIcon, FileTextIcon, ZapIcon, LinkIcon
  },
  props: {
    candidatureId: { type: String, required: true }
  },
  emits: ['close'],
  data() {
    return {
      loading: true,
      error: null,
      profile: null,
      avatarBroken: false,
      defaultAvatar: 'https://t3.ftcdn.net/jpg/16/93/30/10/360_F_1693301062_WIKjLfV17a39eqipWY1SYTG2fiNTaqwa.jpg'
    }
  },
  computed: {
    displayAvatar() {
      if (this.avatarBroken || !this.profile?.avatarUrl) return this.defaultAvatar
      const u = this.profile.avatarUrl
      if (u.startsWith('http')) return u
      return `${API_ORIGIN}${u.startsWith('/') ? '' : '/'}${u}`
    },
    seekingLabel() {
      const v = this.profile?.seeking
      return v ? (SEEKING_LABELS[v] || v) : ''
    }
  },
  watch: {
    candidatureId: { immediate: true, handler: 'load' }
  },
  methods: {
    async load() {
      this.loading = true
      this.error = null
      this.profile = null
      this.avatarBroken = false
      try {
        const { data } = await getCandidateProfileForCandidature(this.candidatureId)
        if (data?.success && data.data) {
          this.profile = data.data
        } else {
          this.error = data?.message || 'Profile unavailable.'
        }
      } catch (e) {
        this.error = e.response?.data?.message || e.message || 'Unable to load candidate profile.'
      } finally {
        this.loading = false
      }
    },
    onImgError() { this.avatarBroken = true },
    normalizeUrl(url) {
      if (!url) return '#'
      return /^https?:\/\//i.test(url) ? url : `https://${url}`
    },
    formatEducation(v) {
      if (!v) return '—'
      const map = { bac: 'Baccalaureate', licence: 'Licence / Bachelor', master: 'Master', ingenieur: 'Engineering', doctorat: 'PhD', other: 'Other' }
      return map[v] || v
    },
    formatExperience(v) {
      if (v == null || v === '') return '—'
      const map = { 0: 'No experience', 1: '< 1 year', '1-3': '1–3 years', '3-5': '3–5 years', '5+': '5+ years' }
      return map[v] != null ? map[v] : String(v)
    },
    formatAvailability(v) {
      if (!v) return '—'
      const map = { immediate: 'Immediately', '1month': 'Within 1 month', '3months': 'Within 3 months', not_available: 'Not available' }
      return map[v] || v
    }
  }
}
</script>

<style scoped>
/* ── Overlay ── */
.cdp-overlay {
  position: fixed;
  inset: 0;
  z-index: 10050;
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  box-sizing: border-box;
  font-family: 'Inter', -apple-system, sans-serif;
  backdrop-filter: blur(4px);
}

/* ── Modal ── */
.cdp-modal {
  position: relative;
  width: 100%;
  max-width: 880px; /* ✅ Augmenté de 580px → 880px */
  max-height: min(94vh, 920px); /* ✅ Augmenté */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 24px; /* ✅ Plus arrondi */
  box-shadow: 0 40px 80px -16px rgba(15, 23, 42, 0.35), 0 0 0 1px rgba(69,74,131,0.12);
  animation: cdp-pop .3s cubic-bezier(.22,1,.36,1);
}
@keyframes cdp-pop {
  from { opacity: 0; transform: scale(.94) translateY(12px); }
  to   { opacity: 1; transform: scale(1)   translateY(0);   }
}

/* ── Close ── */
.cdp-close {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: rgba(255,255,255,0.18);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background .15s, transform .15s;
}
.cdp-close:hover { 
  background: rgba(255,255,255,0.32);
  transform: scale(1.05);
}

/* ── States ── */
.cdp-state {
  padding: 72px 32px;
  text-align: center;
  color: #64748b;
  font-size: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.cdp-state--err { color: #be123c; }
.cdp-err-icon { color: #e11d48; }
.cdp-err-msg { margin: 0; font-size: 15px; font-weight: 500; }
.cdp-btn-retry {
  padding: 10px 24px; border-radius: 10px; border: 1px solid #e2e8f0;
  background: #fff; color: #454a83; font-weight: 600; font-size: 14px;
  cursor: pointer; font-family: inherit; transition: background .15s, transform .15s;
}
.cdp-btn-retry:hover { 
  background: #f8fafc;
  transform: translateY(-1px);
}

.cdp-spinner {
  width: 44px; height: 44px;
  border: 4px solid #e2e8f0; border-top-color: #454a83;
  border-radius: 50%;
  animation: cdp-spin .7s linear infinite;
}
@keyframes cdp-spin { to { transform: rotate(360deg); } }

/* ── Hero ── */
.cdp-hero {
  background: linear-gradient(135deg, #1e2b5e 0%, #454a83 55%, #373c6b 100%);
  padding: 40px 36px 36px; /* ✅ Plus de padding */
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}
.cdp-hero-bg-shape {
  position: absolute;
  width: 280px; height: 280px; /* ✅ Plus grand */
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
  top: -100px; right: -80px;
  pointer-events: none;
}

.cdp-hero-inner {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  gap: 28px; /* ✅ Plus d'espace */
  padding-right: 44px;
}

.cdp-avatar-wrap {
  position: relative;
  flex-shrink: 0;
  width: 110px; height: 110px; /* ✅ Avatar plus grand */
}
.cdp-avatar {
  width: 110px; height: 110px;
  border-radius: 20px; /* ✅ Plus arrondi */
  object-fit: cover;
  border: 4px solid rgba(255,255,255,0.35);
  background: rgba(255,255,255,0.1);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.cdp-seeking-dot {
  position: absolute;
  bottom: 6px; right: 6px;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: #0D9488;
  border: 3px solid #454a83;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.cdp-hero-text { min-width: 0; flex: 1; }

.cdp-name {
  margin: 0 0 10px;
  font-size: 28px; /* ✅ Titre plus grand */
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.cdp-email-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px; /* ✅ Texte plus lisible */
  color: rgba(255,255,255,0.8);
  margin-bottom: 6px;
  word-break: break-all;
}
.cdp-icon-soft { opacity: .8; flex-shrink: 0; }

.cdp-hero-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}
.cdp-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .05em;
  padding: 6px 14px;
  border-radius: 9999px;
}
.cdp-badge--teal {
  background: rgba(13,148,136,0.35);
  color: #a7f3d0;
  border: 1px solid rgba(13,148,136,0.5);
}
.cdp-badge--blue {
  background: rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.9);
  border: 1px solid rgba(255,255,255,0.25);
}

/* ── Body ── */
.cdp-body {
  padding: 28px 32px 32px; /* ✅ Plus de padding */
  overflow-y: auto;
  flex: 1;
}

/* ── Section ── */
.cdp-section { margin-bottom: 28px; }
.cdp-section--last { margin-bottom: 0; }

.cdp-section-header {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f5f9;
}
.cdp-section-icon { color: #454a83; flex-shrink: 0; }
.cdp-section-title {
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: #454a83;
  margin: 0;
}

/* ── Grid fields ── */
.cdp-grid-4 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
@media (min-width: 640px) { 
  .cdp-grid-4 { grid-template-columns: repeat(4, 1fr); } /* ✅ 4 colonnes sur desktop */
}

.cdp-field {
  background: #f8fafc;
  border: 1px solid #e8ecf4;
  border-radius: 14px; /* ✅ Plus arrondi */
  padding: 16px 18px; /* ✅ Plus de padding */
  display: flex;
  flex-direction: column;
  gap: 7px;
  transition: border-color .15s, box-shadow .15s;
}
.cdp-field:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}
.cdp-lbl {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: #94a3b8;
}
.cdp-val {
  font-size: 15px; /* ✅ Texte plus grand */
  font-weight: 600;
  color: #0f172a;
  line-height: 1.4;
}
.cdp-val--avail { color: #0d9488; }

/* ── Bio ── */
.cdp-bio {
  margin: 0;
  font-size: 15px; /* ✅ Plus lisible */
  line-height: 1.8;
  color: #475569;
  background: #f8fafc;
  border: 1px solid #e8ecf4;
  border-radius: 14px;
  padding: 18px 20px;
}

/* ── Skills ── */
.cdp-tags { display: flex; flex-wrap: wrap; gap: 10px; }
.cdp-tag {
  font-size: 13px; font-weight: 600; padding: 7px 16px; border-radius: 9999px;
  background: rgba(69,74,131,0.1); color: #454a83; border: 1px solid rgba(69,74,131,0.2);
  transition: background .15s, transform .15s;
  cursor: default;
}
.cdp-tag:hover { 
  background: rgba(69,74,131,0.18);
  transform: translateY(-1px);
}

/* ── Links ── */
.cdp-links { display: flex; flex-wrap: wrap; gap: 12px; }
.cdp-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  padding: 10px 18px;
  border-radius: 12px;
  border: 1px solid;
  transition: all .15s;
}
.cdp-link--li  { color: #0a66c2; border-color: rgba(10,102,194,.3); background: rgba(10,102,194,.08); }
.cdp-link--li:hover  { background: rgba(10,102,194,.16); transform: translateY(-1px); }
.cdp-link--gh  { color: #24292f; border-color: rgba(36,41,47,.25); background: rgba(36,41,47,.07); }
.cdp-link--gh:hover  { background: rgba(36,41,47,.14); transform: translateY(-1px); }
.cdp-link--port { color: #0d9488; border-color: rgba(13,148,136,.3); background: rgba(13,148,136,.08); }
.cdp-link--port:hover { background: rgba(13,148,136,.16); transform: translateY(-1px); }

.cdp-muted { margin: 0; font-size: 14px; color: #94a3b8; }

/* ── Scrollbar personnalisée ── */
.cdp-body::-webkit-scrollbar {
  width: 8px;
}
.cdp-body::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}
.cdp-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
.cdp-body::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>