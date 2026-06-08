<template>
  <!-- Invitation planifiée : vérifie le créneau avant la salle 3D -->
  <div v-if="sessionPhase === 'checking'" class="gate-screen">
    <div class="gate-card">
      <div class="loader-ring"></div>
      <p class="gate-title">Vérification de votre invitation…</p>
    </div>
  </div>
  <div v-else-if="sessionPhase === 'waiting'" class="gate-screen">
    <div class="gate-card">
      <div class="gate-clock" aria-hidden="true">🕐</div>
      <h2 class="gate-h2">Salle bientôt disponible</h2>
      <p class="gate-sub">L'entretien s'ouvre 5 minutes avant l'heure prévue.</p>
      <p v-if="gateScheduledLabel" class="gate-date">{{ gateScheduledLabel }}</p>
      <p class="gate-hint">Cette page se mettra à jour automatiquement.</p>
    </div>
  </div>
  <div v-else-if="sessionPhase === 'error'" class="gate-screen">
    <div class="gate-card gate-card-err">
      <p class="gate-title">Accès impossible</p>
      <p class="gate-sub">{{ gateErrorMsg }}</p>
      <button type="button" class="gate-btn" @click="goInterviews">Mes entretiens</button>
    </div>
  </div>

  <div v-else class="meet-root">
    <header class="top-bar">
      <div class="top-left">
        <div class="logo-mark">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="brand">RecruitSaaS</span>
        <div class="sep"></div>
        <span class="room-name">{{ roomTitle }}</span>
      </div>
      <div class="top-center">
        <div class="badge-secure">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="#059669"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>
          Chiffré de bout en bout
        </div>
        <div class="timer-pill" :class="{ recording: isStarted }">
          <span class="rec-dot" v-if="isStarted"></span>
          {{ timerDisplay }}
        </div>
        <!-- Progress questions : on exclut la salutation (index 0) de l'affichage -->
        <div v-if="interviewMode && interviewQuestions.length > 1" class="question-progress">
          <span class="q-num">
            Q{{ currentQuestionIndex }}/{{ interviewQuestions.length - 1 }}
          </span>
          <div class="q-bar">
            <div class="q-fill" :style="{ width: (Math.max(0, currentQuestionIndex - 1) / (interviewQuestions.length - 1) * 100) + '%' }"></div>
          </div>
        </div>
      </div>
      <div class="top-right">
        <div class="participant-chips">
          <div class="chip"><div class="chip-av ia">IA</div><span>Recruteur IA</span><div class="chip-status online"></div></div>
          <div class="chip"><div class="chip-av you">V</div><span>Vous</span><div class="chip-status" :class="{ online: camOn || micOn }"></div></div>
        </div>
      </div>
    </header>

    <main class="stage">
      <transition name="fade">
        <div v-if="recruiterBanner" class="recruiter-banner" :class="'banner-' + recruiterBannerKind" role="status">
          <span class="banner-dot" aria-hidden="true"></span>
          <p>{{ recruiterBanner }}</p>
        </div>
      </transition>

      <!-- Question card overlay -->
      <transition name="fade">
        <div v-if="interviewMode && currentQ" class="question-card-overlay">
          <span class="q-type-badge">{{ typeLabel(currentQ.type) }}</span>
          <p class="q-text">{{ currentQ.texte }}</p>
          <div class="q-voice-status" :class="{ listening: isListeningForAnswer }">
            <span class="q-voice-dot"></span>
            {{ isListeningForAnswer ? 'Je vous écoute...' : isSpeaking ? 'Recruteur parle...' : 'Appuyez sur le micro pour répondre' }}
          </div>
          <p v-if="candidateFinal" class="q-transcript">{{ candidateFinal }}</p>
        </div>
      </transition>

      <div class="tile tile-main" :class="{ speaking: isSpeaking }">
        <div class="tile-glow" :class="{ active: isSpeaking }"></div>
        <canvas ref="canvas" class="three-canvas" :style="{ opacity: avatarLoaded ? 1 : 0 }"></canvas>
        <transition name="fade">
          <div v-if="isLoading" class="tile-overlay">
            <div class="loader-ring"></div>
            <p class="overlay-text">Chargement du recruteur IA…</p>
            <p class="overlay-sub">{{ loadingText }}</p>
          </div>
        </transition>
        <transition name="fade">
          <div v-if="loadError && !isLoading" class="tile-overlay error">
            <div class="err-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="#ef4444"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg></div>
            <p class="overlay-text">Impossible de charger l'avatar</p>
            <p class="overlay-sub">Vérifiez que l'API .NET est démarrée sur le port 5202</p>
            <button class="retry-btn" @click="retryLoad">↺ Réessayer</button>
          </div>
        </transition>
        <div v-if="avatarLoaded" class="tile-badge"><div class="badge-dot ia-dot"></div>Recruteur IA · Hôte</div>
        <div class="speak-waves" :class="{ visible: isSpeaking }"><span></span><span></span><span></span><span></span><span></span></div>
      </div>

      <div class="tile tile-self" :class="{ dragging: isDragging }" @mousedown="startDrag" @touchstart.prevent="startDrag">
        <video ref="selfVideo" class="self-video" autoplay muted playsinline :style="{ display: camOn && streamReady ? 'block' : 'none' }"></video>
        <div class="self-placeholder" v-if="!camOn || !streamReady"><div class="self-initials">V</div></div>
        <div class="mic-off-badge" v-if="!micOn"><svg width="12" height="12" viewBox="0 0 24 24" fill="white"><path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3 .22 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/></svg></div>
        <div class="self-badge">Vous · Candidat</div>
      </div>
    </main>

    <div v-if="faceCheckPhase === 'running' || faceCheckPhase === 'failed'" class="face-gate-overlay" role="dialog" aria-modal="true" aria-labelledby="face-gate-title">
      <div class="face-gate-card">
        <template v-if="faceCheckPhase === 'running'">
          <div class="loader-ring face-gate-loader"></div>
          <p id="face-gate-title" class="face-gate-title">Vérification d'identité</p>
          <p class="face-gate-sub">Comparaison entre votre webcam et la photo de profil du dossier…</p>
          <p class="face-gate-hint">Restez face à la caméra, lumière devant vous, sans lunettes de soleil.</p>
        </template>
        <template v-else>
          <p id="face-gate-title" class="face-gate-title">Correspondance non confirmée</p>
          <p class="face-gate-err" role="alert">{{ faceCheckError }}</p>
          <button type="button" class="gate-btn" @click="retryFaceMatch">Réessayer</button>
        </template>
      </div>
    </div>

    <footer class="controls">
      <div class="controls-inner">
        <div class="ctrl-group">
          <button class="ctrl-btn" :class="{ muted: !micOn }" @click="toggleMic">
            <div class="ctrl-icon">
              <svg v-if="micOn" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3 .22 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/></svg>
            </div>
            <span>{{ micOn ? 'Micro' : 'Micro off' }}</span>
          </button>
          <button class="ctrl-btn" :class="{ muted: !camOn }" @click="toggleCam">
            <div class="ctrl-icon">
              <svg v-if="camOn" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/></svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M21 6.5l-4 4V7c0-.55-.45-1-1-1H9.82L21 17.18V6.5zM3.27 2L2 3.27 4.73 6H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.21 0 .39-.08.54-.18L19.73 21 21 19.73 3.27 2z"/></svg>
            </div>
            <span>{{ camOn ? 'Caméra' : 'Caméra off' }}</span>
          </button>
        </div>
        <div class="ctrl-group center">
          <button class="ctrl-btn secondary" :class="{ active: autoRotate }" @click="toggleRotate">
            <div class="ctrl-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 6v3l4-4-4-4v3c-4.42 0-8 3.58-8 8 0 1.57.46 3.03 1.24 4.26L6.7 14.8c-.45-.83-.7-1.79-.7-2.8 0-3.31 2.69-6 6-6zm6.76 1.74L17.3 9.2c.44.84.7 1.79.7 2.8 0 3.31-2.69 6-6 6v-3l-4 4 4 4v-3c4.42 0 8-3.58 8-8 0-1.57-.46-3.03-1.24-4.26z"/></svg></div>
            <span>Rotation</span>
          </button>
          <button class="ctrl-btn end-btn" :disabled="isFinishingInterview" @click="endCall">
            <div class="ctrl-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99 3 13.28 10.73 21 20.01 21c.71 0 .99-.63.99-1.18v-3.45c0-.54-.45-.99-.99-.99z"/></svg></div>
            <span>{{ isFinishingInterview ? 'Finalisation…' : 'Terminer' }}</span>
          </button>
          <button class="ctrl-btn secondary" @click="resetCamera">
            <div class="ctrl-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg></div>
            <span>Reset vue</span>
          </button>
        </div>
        <div class="ctrl-group right">
          <button class="ctrl-btn secondary" @click="toggleFullscreen">
            <div class="ctrl-icon">
              <svg v-if="!isFullscreen" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/></svg>
            </div>
            <span>{{ isFullscreen ? 'Réduire' : 'Plein écran' }}</span>
          </button>
          <button class="ctrl-btn secondary" @click="toggleSidebar">
            <div class="ctrl-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg></div>
            <span>Participants</span>
          </button>
        </div>
      </div>
    </footer>

    <transition name="slide-right">
      <aside class="sidebar" v-if="showSidebar">
        <div class="sidebar-header">
          <h3>Participants (2)</h3>
          <button class="sidebar-close" @click="showSidebar = false">✕</button>
        </div>
        <div class="sidebar-list">
          <div class="sb-row">
            <div class="sb-av ia">IA</div>
            <div class="sb-info"><p class="sb-name">Recruteur IA</p><p class="sb-role">Hôte · Avatar 3D</p></div>
            <div class="sb-indicators"><div class="ind active"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/></svg></div></div>
          </div>
          <div class="sb-row you-row">
            <div class="sb-av you">V</div>
            <div class="sb-info"><p class="sb-name">Vous</p><p class="sb-role">Candidat</p></div>
            <div class="sb-indicators">
              <div class="ind" :class="{ active: micOn, muted: !micOn }"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path v-if="micOn" d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path v-else d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/></svg></div>
              <div class="ind" :class="{ active: camOn, muted: !camOn }"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path v-if="camOn" d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/><path v-else d="M21 6.5l-4 4V7c0-.55-.45-1-1-1H9.82L21 17.18V6.5zM3.27 2L2 3.27 4.73 6H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.21 0 .39-.08.54-.18L19.73 21 21 19.73 3.27 2z"/></svg></div>
            </div>
          </div>
        </div>
        <div class="session-stats">
          <p class="stats-title">Session</p>
          <div class="stat-row"><span>Durée</span><span class="stat-val">{{ timerDisplay }}</span></div>
          <div v-if="interviewMode" class="stat-row">
            <span>Questions</span>
            <span class="stat-val">{{ Math.max(0, currentQuestionIndex) }}/{{ Math.max(0, interviewQuestions.length - 1) }}</span>
          </div>
          <div class="stat-row"><span>Chiffrement</span><span class="stat-val emerald">E2E actif</span></div>
          <div class="stat-row"><span>Qualité</span><span class="stat-val emerald">HD</span></div>
        </div>
      </aside>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import {
  scanAvatarRig, resetFace, speakFrenchSequence, speakFrenchPriorityAlert,
  speakFrenchOnce, stopRecruiterLipSync, updateIdleExpression, updateBlink, updatePresenceRig
} from '@/utils/avatarFacial.js'
import {
  generateInterviewQuestions, evaluateAnswer, generateReport,
  startEntretien, saveAnswer, completeEntretien, buildCompleteEntretienPayload
} from '@/services/entretienService'
import { createInterviewFraudTracker } from '@/utils/interviewFraudTracker.js'

const fraudTracker = createInterviewFraudTracker()

const AVATAR_URL = 'http://localhost:5202/avatars/recruteur.glb'
const route  = useRoute()
const router = useRouter()

function tokenFromRoute () {
  const q = route.query.token
  if (typeof q === 'string' && q.length) return q
  if (Array.isArray(q) && q[0]) return q[0]
  return ''
}

const interviewToken            = ref(tokenFromRoute())
const interviewPhotoProfilUrl   = ref(null)
const faceCheckPhase            = ref('idle')
const faceCheckError            = ref('')
const faceBiometricSkipped      = ref(false)
const sessionPhase              = ref(interviewToken.value ? 'checking' : 'ready')
const gateErrorMsg              = ref('')
const gateScheduled             = ref(null)
const roomTitle                 = ref('Entretien — Recruteur IA')
let gatePollTimer = null

// ── Questions IA ──────────────────────────────────────────────────────────────
const interviewQuestions    = ref([])
const currentQuestionIndex  = ref(0)
const interviewMode         = ref(false)
const interviewStartTime    = ref(null)
const interviewTitreOffre   = ref('')
const interviewNomCandidat  = ref('')
const isListeningForAnswer  = ref(false)
// ✅ FIX : flag pour savoir si la salutation a déjà été traitée
const salutationDone        = ref(false)
const isFinishingInterview  = ref(false)
let   interviewToken2       = ''

function hasInterviewProgress () {
  if (!interviewMode.value) return false
  if (currentQuestionIndex.value > 0) return true
  return interviewQuestions.value.some(q => q.reponse && String(q.reponse).trim())
}

const currentQ = computed(() => interviewQuestions.value[currentQuestionIndex.value] || null)

const gateScheduledLabel = computed(() => {
  if (!gateScheduled.value) return ''
  return new Date(gateScheduled.value).toLocaleString('fr-FR', {
    weekday:'long', day:'numeric', month:'long', year:'numeric', hour:'2-digit', minute:'2-digit'
  })
})

function goInterviews () { router.push('/interviews') }

async function verifyInterviewSlot () {
  const t = interviewToken.value
  if (!t) { interviewPhotoProfilUrl.value = null; return { ok: true, data: null } }
  const res  = await api.get(`/entretiens/public/${encodeURIComponent(t)}/rejoindre`)
  const data = res.data
  gateScheduled.value       = data?.dateScheduled ? new Date(data.dateScheduled) : null
  if (data?.titreOffre)     roomTitle.value = data.titreOffre
  interviewPhotoProfilUrl.value = data?.photoProfilUrl ?? data?.PhotoProfilUrl ?? null
  await loadInterviewQuestions(data)
  return { ok: !!data?.estActif, data }
}

// ── Chargement des questions ──────────────────────────────────────────────────
async function loadInterviewQuestions (data) {
  if (!data?.titreOffre) return
  interviewTitreOffre.value  = data.titreOffre || ''
  interviewNomCandidat.value = data.nomCandidat || ''
  interviewToken2            = interviewToken.value

  try {
    if (data.questionsIA) {
      const saved = JSON.parse(data.questionsIA)
      if (Array.isArray(saved) && saved.length) {
        interviewQuestions.value = saved
        interviewMode.value = true
        return
      }
    }
    const questions = await generateInterviewQuestions(
      data.titreOffre,
      data.descriptionOffre || '',
      data.competences || []
    )
    interviewQuestions.value = questions
    interviewMode.value = questions.length > 0
    if (interviewToken2 && questions.length) {
      startEntretien(interviewToken2, questions).catch(() => {})
    }
  } catch (e) {
    console.warn('[Interview] Questions IA non disponibles — mode conversation libre')
  }
}

// ── Pose la question courante ─────────────────────────────────────────────────
function askCurrentQuestion () {
  const q = interviewQuestions.value[currentQuestionIndex.value]
  if (!q) return
  interviewStartTime.value = interviewStartTime.value || Date.now()
  fraudTracker.markQuestionAsked()
  if (streamReady.value && selfVideo.value) fraudTracker.start(selfVideo.value)

  // ✅ FIX : pas de numéro de question pour la salutation (index 0)
  if (q.type !== 'salutation') {
    // On affiche Q1, Q2... en soustrayant 1 pour ignorer la salutation
    const numQuestion = currentQuestionIndex.value  // index 1 = Q1, index 2 = Q2...
    const totalQuestions = interviewQuestions.value.length - 1
    showRecruiterBanner(`Question ${numQuestion} / ${totalQuestions}`, 'info')
  }

  recruiterSay(q.texte)
}

// ── Gère la réponse structurée ────────────────────────────────────────────────
async function handleStructuredAnswer (reponseText) {
  const q = interviewQuestions.value[currentQuestionIndex.value]
  if (!q) return
  isListeningForAnswer.value = false
  stopListening()

  // ✅ FIX : CAS SALUTATION — pas d'évaluation IA, transition vers Q1
  if (q.type === 'salutation') {
    interviewQuestions.value[currentQuestionIndex.value] = {
      ...q,
      reponse: reponseText,
      score: null,
      feedback: ''
    }
    salutationDone.value = true
    currentQuestionIndex.value = 1  // passe à la vraie première question

    const transition = "Merci pour cette présentation. Passons maintenant aux questions de l'entretien."
    recruiterSay(transition)
    setTimeout(() => askCurrentQuestion(), 3500)
    return
  }

  // ✅ CAS QUESTIONS NORMALES : évaluation IA
  fraudTracker.recordAnswer(reponseText)
  let score = 50, feedback = ''
  try {
    const ev = await evaluateAnswer(q.texte, reponseText, interviewTitreOffre.value)
    score    = ev.score    || 50
    feedback = ev.feedback || ''
  } catch (e) {
    console.warn('[Interview] Évaluation échouée:', e)
  }

  interviewQuestions.value[currentQuestionIndex.value] = { ...q, reponse: reponseText, score, feedback }

  if (interviewToken2) {
    saveAnswer(interviewToken2, { questionId: q.id, reponse: reponseText, score, feedback }).catch(() => {})
  }

  const isLast = currentQuestionIndex.value >= interviewQuestions.value.length - 1
  if (isLast) {
    recruiterSay("Merci pour vos réponses. Je génère votre rapport d'entretien, un instant...")
    setTimeout(() => finishStructuredInterview(), 2500)
  } else {
    const transitions = [
      "Merci. Passons à la question suivante.",
      "Très bien. Continuons.",
      "D'accord, question suivante.",
      "Je note. Voici la prochaine question."
    ]
    const msg = transitions[currentQuestionIndex.value % transitions.length]
    recruiterSay(msg)
    currentQuestionIndex.value++
    setTimeout(() => askCurrentQuestion(), 3500)
  }
}

// ── Génère et sauvegarde le rapport ──────────────────────────────────────────
async function finishStructuredInterview () {
  const duree = Math.floor((Date.now() - (interviewStartTime.value || Date.now())) / 60000)
  fraudTracker.stop()
  const fraudMetrics = fraudTracker.getMetrics()
  const verifOk = faceCheckPhase.value === 'ok'
  const alertes = fraudTracker.formatAlertesForApi()
  const token = interviewToken2 || interviewToken.value

  const payloadFor = (rapport) => buildCompleteEntretienPayload(interviewQuestions.value, {
    rapport, duree, fraudMetrics, verifOk, alertes
  })

  if (token) {
    try {
      await completeEntretien(token, payloadFor(null))
    } catch (e) {
      console.warn('[Interview] completeEntretien échoué:', e)
      return false
    }
  } else if (interviewMode.value) {
    return false
  }

  if (token) {
    generateReport(
      interviewTitreOffre.value,
      interviewNomCandidat.value,
      interviewQuestions.value,
      duree,
      { fraudMetrics, verificationFacialeOk: verifOk, timeoutMs: 45000 }
    ).then((rapport) => {
      if (rapport) return completeEntretien(token, payloadFor(rapport))
    }).catch(() => {})
  }

  recruiterSay("Votre entretien est terminé. Merci pour votre participation. Vous serez contacté prochainement par l'équipe RH.")
  return true
}

async function runInterviewGate () {
  if (!interviewToken.value) return
  sessionPhase.value = 'checking'
  try {
    const { ok } = await verifyInterviewSlot()
    if (ok) {
      sessionPhase.value = 'ready'
      await nextTick()
      await bootEntretienSession()
      return
    }
    sessionPhase.value = 'waiting'
    gatePollTimer = window.setInterval(async () => {
      try {
        const { ok: active } = await verifyInterviewSlot()
        if (active) {
          clearInterval(gatePollTimer); gatePollTimer = null
          sessionPhase.value = 'ready'
          await nextTick()
          await bootEntretienSession()
        }
      } catch {}
    }, 15000)
  } catch (e) {
    sessionPhase.value = 'error'
    interviewPhotoProfilUrl.value = null
    gateErrorMsg.value = e?.response?.data?.message || 'Lien invalide ou expiré.'
  }
}

async function bootEntretienSession () {
  document.addEventListener('visibilitychange', onDocumentVisibility)
  window.addEventListener('pagehide', onWindowPageHide)
  initThree()
  let glbUrl = AVATAR_URL
  try { const av = await api.get('/avatar/recruteur'); if (av.data?.url) glbUrl = av.data.url } catch {}
  loadGLB(glbUrl)
  await initMedia()
  bindRecognitionHandlers()
}

const canvas    = ref(null)
const selfVideo = ref(null)
const avatarLoaded  = ref(false)
const isLoading     = ref(false)
const loadError     = ref(false)
const loadingText   = ref('')
const isSpeaking    = ref(false)
const autoRotate    = ref(false)
const micOn         = ref(true)
const camOn         = ref(true)
const isStarted     = ref(false)
const isFullscreen  = ref(false)
const showSidebar   = ref(false)
const streamReady   = ref(false)
const timerSec      = ref(0)
const isDragging    = ref(false)
let   timerInterval = null
let   mediaStream   = null

let scene, camera, renderer, clock, mixer, avatar, animFrameId
let avatarRig = null
let cancelWelcomeSpeech = null
const expressionState = { timer: 2.5, active: false, elapsed: 0, kind: null, dur: 0.4 }
const blinkState      = { timer: 3, phase: 'idle', elapsed: 0 }
let presenceHoldUntil = 0

const recruiterBanner     = ref('')
const recruiterBannerKind = ref('info')
let recruiterBannerTimer = null

const candidateInterim    = ref('')
const candidateFinal      = ref('')
const recruiterLastReply  = ref('')
let conversationStep      = 0
const identityGateDone    = ref(false)
let recognition           = null
let recognitionActive     = false
let recognitionRestartTimer = null

function typeLabel (type) {
  const m = {
    salutation:      '👋 Accueil',
    introduction:    '👋 Introduction',
    technique:       '⚙️ Technique',
    comportementale: '🧠 Comportementale',
    situation:       '📋 Mise en situation',
    perspective:     '🎯 Perspective'
  }
  return m[type] || type
}

function clearRecognitionRestart () {
  if (recognitionRestartTimer) clearTimeout(recognitionRestartTimer)
  recognitionRestartTimer = null
}

function sanitizeTranscript (t) {
  return String(t||'').replace(/\s+/g,' ').replace(/^[\s,.;:!?-]+|[\s,.;:!?-]+$/g,'').trim()
}

function ensureRecognition () {
  if (recognition) return recognition
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SR) return null
  const r = new SR()
  r.lang = 'fr-FR'; r.continuous = true; r.interimResults = true; r.maxAlternatives = 1
  recognition = r
  return r
}

function stopListening () { clearRecognitionRestart(); recognitionActive = false; try { recognition?.stop() } catch {} }

function startListening () {
  if (!micOn.value || isSpeaking.value) return
  const r = ensureRecognition()
  if (!r) { showRecruiterBanner("Reconnaissance vocale non disponible. Utilisez Chrome ou Edge.", 'info'); return }
  if (recognitionActive) return
  recognitionActive = true
  try { r.start() } catch {}
}

function buildRecruiterReply (text) {
  if (interviewMode.value && interviewQuestions.value.length) return null
  const t = text.toLowerCase()
  const has = (re) => re.test(t)
  if (identityGateDone.value && has(/\b(bonjour|salut|hello)\b/)) return "Bonjour. Pour commencer, présentez-vous en quelques phrases."
  if (has(/\b(merci|d'accord|ok)\b/)) return "Très bien. Parlez-moi de votre expérience la plus récente."
  if (has(/\b(expérience|stage|projet)\b/)) return "Quels ont été vos principaux résultats ou réalisations ?"
  if (has(/\b(compétence|technolog|\.net|vue|python|sql)\b/)) return "Laquelle maîtrisez-vous le mieux ? Comment l'avez-vous utilisée concrètement ?"
  if (has(/\b(je ne sais pas|pas sûr)\b/)) return "Pas de souci. Donnez-moi un exemple simple de votre façon de travailler."
  if (has(/\b(au revoir|bye)\b/)) return "Merci pour votre temps. Avant de terminer, avez-vous une question pour moi ?"
  if (conversationStep === 0) { conversationStep = 1; return "Présentez-vous brièvement : votre parcours et ce que vous recherchez." }
  return "Pouvez-vous préciser et donner un exemple concret ?"
}

function recruiterSay (text, { bannerKind = 'info' } = {}) {
  if (!avatarRig) return
  cancelWelcomeIfPlaying(); stopListening()
  recruiterLastReply.value = text
  showRecruiterBanner(text, bannerKind)
  speakFrenchOnce(text, avatarRig, {
    onSpeaking: (v) => { isSpeaking.value = v },
    onEnd: () => {
      isListeningForAnswer.value = interviewMode.value
      recognitionRestartTimer = setTimeout(() => startListening(), 350)
    }
  })
}

// ✅ FIX PRINCIPAL : handleCandidateUtterance gère correctement la salutation
function handleCandidateUtterance (text) {
  const clean = sanitizeTranscript(text)
  if (!clean) return
  candidateFinal.value = clean
  showRecruiterBanner(`Vous : ${clean}`, 'info')

  if (interviewMode.value) {
    handleStructuredAnswer(clean)
    return
  }
  const reply = buildRecruiterReply(clean)
  if (reply) recruiterSay(reply, { bannerKind: 'info' })
}

function bindRecognitionHandlers () {
  const r = ensureRecognition()
  if (!r || r._bound) return
  r._bound = true
  r.onresult = (event) => {
    let interim = '', finalText = ''
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const res = event.results[i]
      const transcript = res[0]?.transcript || ''
      if (res.isFinal) finalText += transcript
      else interim += transcript
    }
    interim = sanitizeTranscript(interim); finalText = sanitizeTranscript(finalText)
    candidateInterim.value = interim
    if (finalText) { candidateFinal.value = finalText; handleCandidateUtterance(finalText) }
  }
  r.onerror = () => { recognitionActive = false; clearRecognitionRestart(); if (micOn.value && !isSpeaking.value) recognitionRestartTimer = setTimeout(() => startListening(), 900) }
  r.onend   = () => { recognitionActive = false; if (micOn.value && !isSpeaking.value) recognitionRestartTimer = setTimeout(() => startListening(), 450) }
}

const TTS_CAM_OFF   = "J'ai remarqué que votre caméra est éteinte. Merci de la rallumer pour poursuivre l'entretien."
const TTS_PAGE_AWAY = "Il semble que vous ayez quitté la page. Revenez sur l'entretien s'il vous plaît."
const lastAlertAt   = { cam: 0, page: 0 }
const ALERT_COOLDOWN_MS = 16000

function showRecruiterBanner (message, kind = 'info') {
  recruiterBanner.value = message; recruiterBannerKind.value = kind
  if (recruiterBannerTimer) clearTimeout(recruiterBannerTimer)
  recruiterBannerTimer = setTimeout(() => { recruiterBanner.value = ''; recruiterBannerTimer = null }, 14000)
}

function cancelWelcomeIfPlaying () { if (cancelWelcomeSpeech) { cancelWelcomeSpeech(); cancelWelcomeSpeech = null } }

function speakPriorityRecruiter (text, kind) {
  const now = Date.now(); const key = kind === 'cam' ? 'cam' : 'page'
  if (now - lastAlertAt[key] < ALERT_COOLDOWN_MS) return
  lastAlertAt[key] = now
  const short = kind === 'cam' ? "Caméra requise — rallumez-la pour continuer l'entretien." : "Vous avez quitté la page — revenez sur l'entretien."
  showRecruiterBanner(short, kind)
  if (!avatarRig) return
  speakFrenchPriorityAlert(text, avatarRig, { beforeSpeak: cancelWelcomeIfPlaying, onSpeaking: (v) => { isSpeaking.value = v }, onEnd: () => {} })
}

const hadVideoSession = ref(false)
watch([streamReady, camOn], ([ready, cam]) => { if (ready && cam) hadVideoSession.value = true }, { immediate: true })
watch([camOn, streamReady, avatarLoaded], ([on, ready, loaded]) => {
  if (!ready || !loaded) return
  if (!on && hadVideoSession.value) speakPriorityRecruiter(TTS_CAM_OFF, 'cam')
  if (on && recruiterBannerKind.value === 'cam') recruiterBanner.value = ''
})
watch(micOn, (on) => { if (!on) stopListening(); else setTimeout(() => startListening(), 250) })
watch(isSpeaking, (v) => { if (v) stopListening(); else setTimeout(() => startListening(), 350) })

function onDocumentVisibility () {
  if (!avatarLoaded.value) return
  if (document.hidden) speakPriorityRecruiter(TTS_PAGE_AWAY, 'page')
  else if (recruiterBannerKind.value === 'page') recruiterBanner.value = ''
}
function onWindowPageHide () { if (avatarLoaded.value) speakPriorityRecruiter(TTS_PAGE_AWAY, 'page') }
onBeforeRouteLeave((_to, _from, next) => { if (avatarLoaded.value) speakPriorityRecruiter(TTS_PAGE_AWAY, 'page'); next() })

const PHRASES_BIOMETRIC_OK = [
  "Bonjour. Votre visage correspond à la photo enregistrée dans votre dossier.",
  "Installez-vous confortablement. Nous allons commencer l'entretien."
]
const PHRASES_BIOMETRIC_SKIPPED = [
  "Bonjour. Aucune photo de profil disponible pour la comparaison automatique.",
  "Nous allons commencer l'entretien dans un instant."
]

async function runFacialIdentityGate () {
  stopListening(); faceCheckError.value = ''
  const url = String(interviewPhotoProfilUrl.value || '').trim()
  if (!url) { faceBiometricSkipped.value = true; faceCheckPhase.value = 'skipped'; return true }
  faceBiometricSkipped.value = false; faceCheckPhase.value = 'running'
  try {
    const mod = await import('@/utils/faceIdentityMatch.js')
    const ref = await mod.descriptorFromPhotoUrl(url)
    const res = await mod.matchVideoToDescriptor(selfVideo.value, ref, { maxAttempts: 14, pauseMs: 500, threshold: mod.getMatchThreshold() })
    if (!res.match) {
      faceCheckPhase.value = 'failed'
      faceCheckError.value = res.distance != null ? `Le visage ne correspond pas assez (écart ${res.distance.toFixed(2)}). Améliorez la lumière, face caméra.` : 'Aucun visage détecté.'
      return false
    }
    faceCheckPhase.value = 'ok'; return true
  } catch (e) {
    faceCheckPhase.value = 'failed'
    faceCheckError.value = e?.message === 'photo_load_failed' ? "Impossible de charger la photo de profil." : e?.message === 'no_face_in_profile_photo' ? 'Aucun visage sur la photo de profil.' : e?.message || 'Erreur comparaison faciale.'
    return false
  }
}

async function retryFaceMatch () {
  if (faceCheckPhase.value !== 'failed') return
  faceCheckPhase.value = 'idle'
  const ok = await runFacialIdentityGate()
  if (ok) startWelcomeExperience()
}

const timerDisplay = computed(() => {
  const m = String(Math.floor(timerSec.value / 60)).padStart(2,'0')
  const s = String(timerSec.value % 60).padStart(2,'0')
  return `${m}:${s}`
})

function startTimer () { if (timerInterval) return; isStarted.value = true; timerInterval = setInterval(() => timerSec.value++, 1000) }
function stopTimer  () { clearInterval(timerInterval); timerInterval = null }

async function initMedia () {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    if (selfVideo.value) {
      selfVideo.value.srcObject = mediaStream
      streamReady.value = true
      if (interviewMode.value) fraudTracker.start(selfVideo.value)
    }
    mediaStream.getVideoTracks().forEach(t => t.addEventListener('ended', onVideoTrackEnded))
  } catch { streamReady.value = false }
}
function onVideoTrackEnded () { if (!streamReady.value) return; camOn.value = false }
function toggleMic () { micOn.value = !micOn.value; if (mediaStream) mediaStream.getAudioTracks().forEach(t => { t.enabled = micOn.value }) }
function toggleCam () { camOn.value = !camOn.value; if (mediaStream) mediaStream.getVideoTracks().forEach(t => { t.enabled = camOn.value }) }
function stopMedia () {
  if (mediaStream) {
    mediaStream.getVideoTracks().forEach(t => t.removeEventListener('ended', onVideoTrackEnded))
    mediaStream.getTracks().forEach(t => t.stop())
    mediaStream = null; streamReady.value = false
  }
}
function toggleFullscreen () {
  if (!document.fullscreenElement) { document.documentElement.requestFullscreen(); isFullscreen.value = true }
  else { document.exitFullscreen(); isFullscreen.value = false }
}
function toggleSidebar () { showSidebar.value = !showSidebar.value }
function startDrag (e) { isDragging.value = true; const up = () => { isDragging.value = false; window.removeEventListener('mouseup', up) }; window.addEventListener('mouseup', up) }

function initThree () {
  const cvs = canvas.value; const W = cvs.parentElement.clientWidth; const H = cvs.parentElement.clientHeight
  scene = new THREE.Scene(); scene.background = new THREE.Color(0xf0f2f5); scene.fog = new THREE.FogExp2(0xf0f2f5, 0.025)
  camera = new THREE.PerspectiveCamera(42, W / H, 0.1, 50); camera.position.set(0, 1.45, 1.5); camera.lookAt(0, 1.3, 0)
  renderer = new THREE.WebGLRenderer({ canvas: cvs, antialias: true })
  renderer.setSize(W, H); renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); renderer.shadowMap.enabled = true
  buildStudio(); buildLights(); clock = new THREE.Clock(); window.addEventListener('resize', onResize); animate()
}

function buildStudio () {
  const mesh = (geo, mat) => { const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial(mat)); scene.add(m); return m }
  const floor = mesh(new THREE.PlaneGeometry(14, 14), { color: 0xe8eaed, roughness: 0.9, metalness: 0 }); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true
  mesh(new THREE.PlaneGeometry(14, 8), { color: 0xf8f9fa, roughness: 0.95 }).position.set(0, 4, -4.5)
  const desk = mesh(new THREE.BoxGeometry(2.4, 0.06, 0.85), { color: 0xffffff, roughness: 0.3, metalness: 0.1 }); desk.position.set(0, 0.72, 0.5); desk.castShadow = true; desk.receiveShadow = true
  ;[[-1.05,0],[1.05,0],[-1.05,.85],[1.05,.85]].forEach(([x,z]) => { const l = mesh(new THREE.BoxGeometry(0.04, 0.72, 0.04), { color: 0xd1d5db, metalness: 0.4, roughness: 0.3 }); l.position.set(x, 0.36, z) })
}

function buildLights () {
  scene.add(new THREE.AmbientLight(0xffffff, 1.4))
  const key = new THREE.SpotLight(0xfffaf0, 3.5, 14, Math.PI / 4.5, 0.5); key.position.set(1.5, 5, 3); key.castShadow = true; key.shadow.bias = -0.001; key.shadow.mapSize.width = 1024; key.shadow.mapSize.height = 1024; scene.add(key)
  const fill = new THREE.DirectionalLight(0xe8f0fe, 1.2); fill.position.set(-3, 4, 2); scene.add(fill)
  const rim = new THREE.SpotLight(0xffffff, 2.0, 10, Math.PI / 5, 0.6); rim.position.set(0, 4, -3); scene.add(rim)
  const low = new THREE.DirectionalLight(0xffffff, 0.5); low.position.set(0, -1, 2); scene.add(low)
  const ground = new THREE.PointLight(0xd1fae5, 0.4, 4); ground.position.set(0, 0.8, 0.5); scene.add(ground)
}

function animate () {
  animFrameId = requestAnimationFrame(animate)
  const d = clock.getDelta()
  if (mixer) mixer.update(d)
  if (autoRotate.value && avatar) avatar.rotation.y += 0.003
  if (performance.now() > presenceHoldUntil) updatePresenceRig(avatarRig, d, { isSpeaking: isSpeaking.value })
  updateIdleExpression(avatarRig, expressionState, d, { suppress: isSpeaking.value })
  updateBlink(avatarRig, blinkState, d, { isSpeaking: isSpeaking.value })
  renderer.render(scene, camera)
}

function onResize () {
  const cvs = canvas.value; if (!cvs || !renderer) return
  const W = cvs.parentElement.clientWidth, H = cvs.parentElement.clientHeight
  camera.aspect = W / H; camera.updateProjectionMatrix(); renderer.setSize(W, H)
}

function performWave () {
  if (!avatar) return
  let upperArm = null, foreArm = null, hand = null, spine = null, shoulder = null
  avatar.traverse((child) => {
    if (!child.isBone) return; const n = child.name.toLowerCase()
    const uP = ['mixamorig:rightarm','rightarm','right_arm','upperarm_r','arm_r','r_upperarm','arm_02_r','shoulder_r','r_arm','bip01_r_upperarm','r_uparm']
    for (const p of uP) if (n === p || n.includes(p)) { upperArm = child; break }
    const fP = ['mixamorig:rightforearm','rightforearm','right_forearm','lowerarm_r','forearm_r','r_forearm','arm_03_r','rightlowerarm','r_lowerarm','bip01_r_forearm']
    for (const p of fP) if (n === p || n.includes(p)) { foreArm = child; break }
    if ((n.includes('right')||n.includes('_r'))&&(n.includes('hand')||n.includes('wrist'))) hand = child
    if (!spine&&(n.includes('spine')||n.includes('chest')||n.includes('thorax'))) spine = child
    if (!shoulder&&(n.includes('rightshoulder')||n.includes('shoulder_r')||n.includes('clavicle_r')||n.includes('rightclavicle'))) shoulder = child
  })
  console.log('🦴 upperArm:',upperArm?.name??'❌','foreArm:',foreArm?.name??'❌','hand:',hand?.name??'—')
  const primary = upperArm ?? foreArm; const secondary = upperArm ? foreArm : null
  if (!primary) { console.warn('❌ Aucun bone bras trouvé'); return }
  const origPrimX=primary.rotation.x,origPrimY=primary.rotation.y,origPrimZ=primary.rotation.z
  const origSecX=secondary?.rotation.x??0,origSecY=secondary?.rotation.y??0,origHandZ=hand?.rotation.z??0
  const origSpineZ=spine?.rotation.z??0,origSpineX=spine?.rotation.x??0,origShlZ=shoulder?.rotation.z??0
  const LIFT_X=-0.60,LIFT_Y=-0.45,LIFT_Z=-0.10,FLEX_FA=-0.75,PALM_Y=1.4,WAVE_AMP=0.16,DURATION=2600
  const easeOut=t=>1-Math.pow(1-t,3); const easeInOut=t=>t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2
  const start=Date.now()
  function tick(){
    const p=Math.min(1,(Date.now()-start)/DURATION); let ax=0,ay=0,az=0,bx=0,by=0,hz=0
    if(p<0.20){const t=easeOut(p/0.20);ax=LIFT_X*t;ay=LIFT_Y*t;az=LIFT_Z*t;bx=FLEX_FA*t*0.6;by=PALM_Y*t*0.5;if(spine){spine.rotation.z=origSpineZ+0.07*t;spine.rotation.x=origSpineX-0.03*t}if(shoulder)shoulder.rotation.z=origShlZ-0.14*t}
    else if(p<0.32){const t=easeOut((p-0.20)/0.12);ax=LIFT_X;ay=LIFT_Y;az=LIFT_Z;bx=FLEX_FA*(0.6+0.4*t);by=PALM_Y*(0.5+0.5*t);if(spine){spine.rotation.z=origSpineZ+0.07;spine.rotation.x=origSpineX-0.03}if(shoulder)shoulder.rotation.z=origShlZ-0.14}
    else if(p<0.78){const t=(p-0.32)/0.46;const decay=1-t*0.40;const waveZ=Math.sin(t*Math.PI*3.0)*WAVE_AMP*decay;const waveX=Math.sin(t*Math.PI*1.5)*0.035;const waveY=Math.sin(t*Math.PI*1.5)*0.03;ax=LIFT_X+waveX;ay=LIFT_Y+waveY;az=LIFT_Z+waveZ;bx=FLEX_FA+Math.sin(t*Math.PI*3.0)*0.04;by=PALM_Y;hz=Math.sin(t*Math.PI*6.5)*0.07+Math.sin(t*Math.PI*10.3)*0.03;if(spine)spine.rotation.z=origSpineZ+0.07+waveZ*0.07;if(shoulder)shoulder.rotation.z=origShlZ-0.14+waveZ*0.05}
    else{const t=easeInOut((p-0.78)/0.22);ax=LIFT_X*(1-t);ay=LIFT_Y*(1-t);az=LIFT_Z*(1-t);bx=FLEX_FA*(1-t);by=PALM_Y*(1-t);if(spine){spine.rotation.z=origSpineZ+0.07*(1-t);spine.rotation.x=origSpineX-0.03*(1-t)}if(shoulder)shoulder.rotation.z=origShlZ-0.14*(1-t)}
    primary.rotation.x=origPrimX+ax;primary.rotation.y=origPrimY+ay;primary.rotation.z=origPrimZ+az
    if(secondary){secondary.rotation.x=origSecX+bx;secondary.rotation.y=origSecY+by}
    if(hand)hand.rotation.z=origHandZ+hz
    if(p<1){requestAnimationFrame(tick)}else{primary.rotation.set(origPrimX,origPrimY,origPrimZ);if(secondary){secondary.rotation.x=origSecX;secondary.rotation.y=origSecY}if(hand)hand.rotation.z=origHandZ;if(spine){spine.rotation.z=origSpineZ;spine.rotation.x=origSpineX}if(shoulder)shoulder.rotation.z=origShlZ;console.log('✅ Salut terminé')}
  }
  tick(); console.log('👋 Salut naturel lancé')
}

function performHeadNod () {
  if (!avatar) return; presenceHoldUntil = performance.now() + 980
  let neck = null, head = null
  avatar.traverse(c => { if(!c.isBone) return; const n=c.name.toLowerCase(); if(n.includes('neck'))neck=c; if(!head&&n.includes('head')&&!n.includes('forehead')&&!n.includes('forearm'))head=c })
  const pivot=neck||head; if(!pivot)return
  const base=pivot===avatarRig?.neckBone&&avatarRig._neckOrig?avatarRig._neckOrig:pivot===avatarRig?.headBone&&avatarRig._headOrig?avatarRig._headOrig:{x:pivot.rotation.x,y:pivot.rotation.y,z:pivot.rotation.z}
  const DURATION=900; const start=Date.now(); const ease=t=>t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2
  function tick(){const p=Math.min(1,(Date.now()-start)/DURATION);const w=Math.sin(p*Math.PI)*0.11;pivot.rotation.x=base.x+w*ease(p);pivot.rotation.y=base.y+Math.sin(p*Math.PI*2)*0.02;pivot.rotation.z=base.z;if(p<1)requestAnimationFrame(tick);else pivot.rotation.set(base.x,base.y,base.z)}
  tick()
}

// ✅ FIX PRINCIPAL : startWelcomeExperience lance la salutation (Q0) après le discours de bienvenue
function startWelcomeExperience () {
  if (cancelWelcomeSpeech) { cancelWelcomeSpeech(); cancelWelcomeSpeech = null }
  identityGateDone.value = true
  salutationDone.value = false
  const phrases = faceBiometricSkipped.value ? PHRASES_BIOMETRIC_SKIPPED : PHRASES_BIOMETRIC_OK

  setTimeout(() => performHeadNod(), 350)
  setTimeout(() => performWave(), 750)
  setTimeout(() => {
    if (!avatarRig) avatarRig = scanAvatarRig(avatar)
    cancelWelcomeSpeech = speakFrenchSequence(phrases, avatarRig, {
      onSpeaking: (v) => { isSpeaking.value = v },
      onComplete: () => {
        cancelWelcomeSpeech = null
        conversationStep = 1

        if (interviewMode.value && interviewQuestions.value.length) {
          showRecruiterBanner('Entretien en cours — répondez à voix haute', 'info')
          // ✅ On démarre toujours à l'index 0 (salutation)
          currentQuestionIndex.value = 0
          setTimeout(() => askCurrentQuestion(), 800)
        } else {
          showRecruiterBanner('Vous pouvez répondre à voix haute.', 'info')
          recognitionRestartTimer = setTimeout(() => startListening(), 450)
        }
      },
      welcomeSmile: 0.4, lipPrecision: true
    })
  }, 1100)
}

function scheduleWave () {
  const check = setInterval(async () => {
    if (avatarLoaded.value && avatar && streamReady.value && selfVideo.value && camOn.value) {
      clearInterval(check)
      const ok = await runFacialIdentityGate()
      if (!ok) return
      startWelcomeExperience()
    }
  }, 100)
  setTimeout(() => clearInterval(check), 12000)
}

function loadGLB (url) {
  isLoading.value = true; loadError.value = false; avatarLoaded.value = false; loadingText.value = "Connexion à l'API…"
  const loader = new GLTFLoader()
  loader.load(url,
    (gltf) => {
      if (avatar) scene.remove(avatar); avatar = gltf.scene
      const box = new THREE.Box3().setFromObject(avatar); const size = box.getSize(new THREE.Vector3()); const sc = 1.75 / size.y
      avatar.scale.setScalar(sc); avatar.position.set(-box.getCenter(new THREE.Vector3()).x*sc,-box.min.y*sc,0.3)
      avatar.traverse(n => { if(n.isMesh){n.castShadow=true;n.receiveShadow=true} })
      scene.add(avatar); avatarRig = scanAvatarRig(avatar); mixer = new THREE.AnimationMixer(avatar)
      if (gltf.animations?.length) { const idle=gltf.animations.find(a=>/idle/i.test(a.name))??gltf.animations[0]; mixer.clipAction(idle).reset().fadeIn(0.4).play() }
      console.log('✅ Avatar chargé'); isLoading.value = false; avatarLoaded.value = true; startTimer(); scheduleWave()
    },
    (p) => { if(p.total)loadingText.value=`${Math.round(p.loaded/p.total*100)} %` },
    (error) => { console.error('❌ Erreur avatar:', error); isLoading.value = false; loadError.value = true }
  )
}

function retryLoad () { loadGLB(AVATAR_URL) }
function resetCamera () { camera.position.set(0,1.45,1.5); camera.lookAt(0,1.3,0); if(avatar)avatar.rotation.y=0 }
function toggleRotate () { autoRotate.value = !autoRotate.value }

async function endCall () {
  if (isFinishingInterview.value) return
  if (!confirm("Terminer l'entretien ?")) return

  isFinishingInterview.value = true
  try {
    if (hasInterviewProgress()) {
      const ok = await finishStructuredInterview()
      if (!ok) {
        alert("Impossible de finaliser l'entretien. Vérifiez votre connexion et réessayez.")
        return
      }
    }
  } finally {
    isFinishingInterview.value = false
  }

  if (cancelWelcomeSpeech) { cancelWelcomeSpeech(); cancelWelcomeSpeech = null }
  speechSynthesis.cancel(); stopRecruiterLipSync(); stopListening(); stopTimer(); stopMedia()
  timerSec.value = 0; isStarted.value = false; recruiterBanner.value = ''
  if (recruiterBannerTimer) { clearTimeout(recruiterBannerTimer); recruiterBannerTimer = null }
  if (avatarRig) resetFace(avatarRig)
  if (avatar) { scene.remove(avatar); avatar = null }
  mixer = null; avatarRig = null; avatarLoaded.value = false; isSpeaking.value = false
  goInterviews()
}

window.debugBones = () => { if(!avatar){console.log('Avatar non chargé');return}; console.log('=== BONES ==='); avatar.traverse(c=>{if(c.isBone)console.log(c.name)}) }
window.testWave = () => performWave()

onMounted(async () => {
  if (interviewToken.value) { await runInterviewGate() }
  else { sessionPhase.value = 'ready'; await nextTick(); await bootEntretienSession() }
})

onBeforeUnmount(() => {
  if (gatePollTimer) { clearInterval(gatePollTimer); gatePollTimer = null }
  document.removeEventListener('visibilitychange', onDocumentVisibility)
  window.removeEventListener('pagehide', onWindowPageHide)
  if (cancelWelcomeSpeech) cancelWelcomeSpeech()
  speechSynthesis.cancel(); stopRecruiterLipSync(); stopListening()
  fraudTracker.stop()
  if (recruiterBannerTimer) clearTimeout(recruiterBannerTimer)
  cancelAnimationFrame(animFrameId); stopTimer(); stopMedia()
  window.removeEventListener('resize', onResize); renderer?.dispose()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
.gate-screen{position:fixed;inset:0;z-index:9999;background:#f3f4f6;display:flex;align-items:center;justify-content:center;font-family:'DM Sans',sans-serif;padding:24px}
.gate-card{background:#fff;border-radius:16px;border:1px solid #e5e7eb;padding:40px 36px;max-width:420px;text-align:center;box-shadow:0 10px 40px rgba(0,0,0,0.08)}
.gate-card-err{border-color:#fecaca}.gate-clock{font-size:40px;margin-bottom:12px}.gate-h2{font-size:18px;font-weight:700;color:#111827;margin:0 0 8px}
.gate-title{font-size:15px;font-weight:600;color:#111827;margin:0 0 8px}.gate-sub{font-size:14px;color:#64748b;margin:0 0 12px;line-height:1.5}
.gate-date{font-size:13px;font-weight:600;color:#1A2B4C;margin:0 0 8px;text-transform:capitalize}.gate-hint{font-size:12px;color:#94a3b8;margin:0}
.gate-btn{margin-top:16px;padding:10px 20px;border-radius:10px;border:none;background:#1A2B4C;color:#fff;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit}
.gate-btn:hover{background:#243d6a}
.face-gate-overlay{position:absolute;inset:0;z-index:60;background:rgba(15,23,42,0.55);display:flex;align-items:center;justify-content:center;padding:24px;backdrop-filter:blur(4px)}
.face-gate-card{max-width:420px;width:100%;background:#fff;border-radius:16px;padding:28px 24px;box-shadow:0 20px 50px rgba(0,0,0,0.2);text-align:center;font-family:'DM Sans',sans-serif}
.face-gate-title{font-size:18px;font-weight:600;color:#111827;margin:16px 0 8px}.face-gate-sub{font-size:14px;color:#4b5563;line-height:1.5;margin:0 0 8px}
.face-gate-hint{font-size:12px;color:#6b7280;margin:0}.face-gate-err{font-size:14px;color:#b91c1c;line-height:1.5;margin:12px 0 20px;text-align:left}
.face-gate-loader{margin:0 auto}
.meet-root{position:fixed;inset:0;background:#f3f4f6;display:flex;flex-direction:column;font-family:'DM Sans',sans-serif;color:#111827;overflow:hidden}
.top-bar{position:relative;z-index:10;display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:56px;background:#fff;border-bottom:1px solid #e5e7eb;flex-shrink:0;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
.top-left{display:flex;align-items:center;gap:12px}.top-center{display:flex;align-items:center;gap:10px}.top-right{display:flex;align-items:center}
.logo-mark{width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#059669,#10b981);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.brand{font-size:14px;font-weight:600;color:#111827;letter-spacing:-0.02em}.sep{width:1px;height:16px;background:#e5e7eb}.room-name{font-size:13px;color:#6b7280;font-weight:400}
.badge-secure{display:flex;align-items:center;gap:5px;font-size:11px;color:#059669;padding:4px 10px;border-radius:20px;background:#f0fdf4;border:1px solid #bbf7d0}
.timer-pill{font-family:'DM Mono',monospace;font-size:12px;color:#6b7280;padding:4px 12px;border-radius:20px;background:#f9fafb;border:1px solid #e5e7eb;display:flex;align-items:center;gap:6px;transition:all .3s}
.timer-pill.recording{color:#374151;background:#fef2f2;border-color:#fecaca}
.rec-dot{width:6px;height:6px;border-radius:50%;background:#ef4444;animation:recPulse 1.5s ease-in-out infinite}
@keyframes recPulse{0%,100%{opacity:1}50%{opacity:.3}}
.question-progress{display:flex;align-items:center;gap:8px}.q-num{font-size:11px;font-weight:700;color:#1A2B4C;white-space:nowrap}
.q-bar{width:80px;height:4px;background:#e5e7eb;border-radius:2px;overflow:hidden}.q-fill{height:100%;background:#1D9E75;border-radius:2px;transition:width 0.5s}
.participant-chips{display:flex;gap:8px}
.chip{display:flex;align-items:center;gap:7px;padding:5px 10px 5px 5px;border-radius:20px;background:#f9fafb;border:1px solid #e5e7eb;font-size:12px;color:#374151}
.chip-av{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;color:white}
.chip-av.ia{background:linear-gradient(135deg,#059669,#10b981)}.chip-av.you{background:linear-gradient(135deg,#3b82f6,#6366f1)}
.chip-status{width:6px;height:6px;border-radius:50%;background:#d1d5db}.chip-status.online{background:#10b981}
.stage{position:relative;z-index:5;flex:1;min-height:0;overflow:hidden}
.recruiter-banner{position:absolute;top:14px;left:50%;transform:translateX(-50%);z-index:25;max-width:min(540px,94vw);padding:12px 18px;border-radius:12px;display:flex;align-items:flex-start;gap:12px;font-size:14px;line-height:1.45;font-weight:500;box-shadow:0 10px 40px rgba(0,0,0,0.12);pointer-events:none}
.recruiter-banner .banner-dot{width:8px;height:8px;border-radius:50%;margin-top:6px;flex-shrink:0}
.recruiter-banner.banner-cam{background:#fffbeb;border:1px solid #fcd34d;color:#78350f}.recruiter-banner.banner-cam .banner-dot{background:#d97706}
.recruiter-banner.banner-page{background:#eff6ff;border:1px solid #93c5fd;color:#1e3a5f}.recruiter-banner.banner-page .banner-dot{background:#2563eb}
.recruiter-banner.banner-info .banner-dot{background:#059669}
.question-card-overlay{position:absolute;bottom:16px;left:16px;z-index:20;max-width:380px;background:rgba(15,23,42,0.85);backdrop-filter:blur(12px);border-radius:14px;padding:16px;border:1px solid rgba(255,255,255,0.1)}
.q-type-badge{font-size:10px;font-weight:700;color:#B5D4F4;text-transform:uppercase;letter-spacing:0.08em;display:block;margin-bottom:8px}
.q-text{font-size:14px;color:#fff;line-height:1.5;margin:0 0 10px}
.q-voice-status{display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;padding:4px 10px;border-radius:99px;background:rgba(255,255,255,0.1);color:#94A3B8;width:fit-content}
.q-voice-dot{width:5px;height:5px;border-radius:50%;background:#64748B}
.q-voice-status.listening{background:rgba(29,158,117,0.2);color:#1D9E75}.q-voice-status.listening .q-voice-dot{background:#1D9E75;animation:recPulse 0.8s infinite}
.q-transcript{font-size:12px;color:#94A3B8;margin:8px 0 0;font-style:italic}
.tile-main{position:absolute;inset:0;background:#f0f2f5}
.three-canvas{width:100%!important;height:100%!important;display:block;transition:opacity .6s}
.tile-glow{position:absolute;inset:0;pointer-events:none;border:3px solid transparent;transition:border-color .3s}
.tile-glow.active{border-color:#10b981;box-shadow:inset 0 0 40px rgba(16,185,129,0.1);animation:glowPulse 1.5s ease-in-out infinite}
@keyframes glowPulse{0%,100%{box-shadow:inset 0 0 40px rgba(16,185,129,0.1)}50%{box-shadow:inset 0 0 70px rgba(16,185,129,0.2)}}
.tile-overlay{position:absolute;inset:0;z-index:5;background:#f8fafc;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px}
.loader-ring{width:48px;height:48px;border:2px solid #e5e7eb;border-top-color:#059669;border-radius:50%;animation:spin .9s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.overlay-text{font-size:14px;color:#374151;font-weight:500}.overlay-sub{font-size:12px;color:#9ca3af}
.retry-btn{margin-top:4px;padding:8px 20px;border-radius:8px;background:#f0fdf4;border:1px solid #bbf7d0;color:#059669;font-size:13px;cursor:pointer}
.tile-badge{position:absolute;bottom:20px;left:20px;z-index:6;display:flex;align-items:center;gap:7px;padding:6px 14px;border-radius:8px;background:rgba(255,255,255,0.9);backdrop-filter:blur(12px);border:1px solid #e5e7eb;font-size:12px;font-weight:500;color:#374151;box-shadow:0 2px 8px rgba(0,0,0,0.08)}
.badge-dot{width:7px;height:7px;border-radius:50%}.ia-dot{background:#10b981;box-shadow:0 0 6px #10b981}
.speak-waves{position:absolute;bottom:20px;right:20px;z-index:6;display:flex;align-items:flex-end;gap:3px;height:24px;opacity:0;transition:opacity .3s}
.speak-waves.visible{opacity:1}
.speak-waves span{width:3px;background:#059669;border-radius:2px;animation:wave 1.2s ease-in-out infinite}
.speak-waves span:nth-child(1){height:6px;animation-delay:0s}.speak-waves span:nth-child(2){height:14px;animation-delay:.1s}.speak-waves span:nth-child(3){height:22px;animation-delay:.2s}.speak-waves span:nth-child(4){height:14px;animation-delay:.3s}.speak-waves span:nth-child(5){height:6px;animation-delay:.4s}
@keyframes wave{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.4)}}
.tile-self{position:absolute;bottom:24px;right:24px;z-index:20;width:200px;height:140px;border-radius:14px;overflow:hidden;background:#e5e7eb;border:2px solid #fff;box-shadow:0 8px 32px rgba(0,0,0,0.15);cursor:move;transition:border-color .3s,transform .2s}
.tile-self:hover{border-color:#10b981;transform:scale(1.02)}.tile-self.dragging{transform:scale(1.04);border-color:#059669}
.self-video{width:100%;height:100%;object-fit:cover}
.self-placeholder{width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#e5e7eb,#d1d5db)}
.self-initials{width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#6366f1);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:white}
.self-badge{position:absolute;bottom:8px;left:8px;font-size:10px;color:#f9fafb;padding:3px 8px;border-radius:5px;background:rgba(0,0,0,0.5);backdrop-filter:blur(6px)}
.mic-off-badge{position:absolute;top:8px;right:8px;width:24px;height:24px;border-radius:6px;background:rgba(239,68,68,0.9);display:flex;align-items:center;justify-content:center}
.controls{position:relative;z-index:10;background:#fff;border-top:1px solid #e5e7eb;padding:12px 24px;flex-shrink:0;box-shadow:0 -1px 3px rgba(0,0,0,0.04)}
.controls-inner{display:flex;align-items:center;justify-content:space-between;max-width:900px;margin:0 auto}
.ctrl-group{display:flex;align-items:center;gap:8px}.ctrl-group.center{gap:10px}
.ctrl-btn{display:flex;flex-direction:column;align-items:center;gap:4px;padding:10px 16px;border-radius:12px;border:1px solid #e5e7eb;background:#f9fafb;color:#374151;cursor:pointer;transition:background .2s,color .2s,transform .15s;min-width:64px}
.ctrl-btn:hover{background:#f3f4f6;color:#111827;transform:translateY(-1px);box-shadow:0 2px 8px rgba(0,0,0,0.08)}
.ctrl-btn span{font-size:10px;font-family:'DM Sans',sans-serif;white-space:nowrap}
.ctrl-btn.muted{background:#fef2f2;border-color:#fecaca;color:#dc2626}.ctrl-btn.secondary{background:#f9fafb;border-color:#e5e7eb}
.ctrl-btn.secondary.active{background:#f0fdf4;border-color:#bbf7d0;color:#059669}
.ctrl-icon{display:flex;align-items:center;justify-content:center}
.end-btn{background:#ef4444!important;border-color:#ef4444!important;color:white!important;padding:12px 28px;min-width:80px}
.end-btn:hover{background:#dc2626!important;border-color:#dc2626!important}
.sidebar{position:fixed;top:56px;right:0;bottom:72px;z-index:30;width:280px;background:#fff;border-left:1px solid #e5e7eb;display:flex;flex-direction:column;padding:20px;gap:20px;box-shadow:-4px 0 16px rgba(0,0,0,0.06)}
.sidebar-header{display:flex;align-items:center;justify-content:space-between}
.sidebar-header h3{font-size:14px;font-weight:600;color:#111827}
.sidebar-close{background:none;border:none;color:#9ca3af;cursor:pointer;font-size:16px;padding:2px 6px;border-radius:4px;transition:color .2s}
.sidebar-close:hover{color:#374151}.sidebar-list{display:flex;flex-direction:column;gap:10px}
.sb-row{display:flex;align-items:center;gap:12px;padding:12px;border-radius:10px;background:#f9fafb;border:1px solid #e5e7eb}
.you-row{border-color:#c7d2fe;background:#eef2ff}
.sb-av{width:36px;height:36px;border-radius:10px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white}
.sb-av.ia{background:linear-gradient(135deg,#059669,#10b981)}.sb-av.you{background:linear-gradient(135deg,#3b82f6,#6366f1)}
.sb-name{font-size:13px;color:#111827;font-weight:500}.sb-role{font-size:11px;color:#9ca3af}.sb-indicators{margin-left:auto;display:flex;gap:5px}
.ind{width:26px;height:26px;border-radius:7px;background:#f3f4f6;border:1px solid #e5e7eb;display:flex;align-items:center;justify-content:center;color:#9ca3af}
.ind.active{background:#f0fdf4;border-color:#bbf7d0;color:#059669}.ind.muted{background:#fef2f2;border-color:#fecaca;color:#ef4444}
.session-stats{margin-top:auto;padding:16px;border-radius:10px;background:#f9fafb;border:1px solid #e5e7eb}
.stats-title{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#9ca3af;margin-bottom:12px}
.stat-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f3f4f6;font-size:12px;color:#6b7280}
.stat-row:last-child{border-bottom:none}.stat-val{font-family:'DM Mono',monospace;color:#374151}.stat-val.emerald{color:#059669}
.fade-enter-active,.fade-leave-active{transition:opacity .3s}.fade-enter-from,.fade-leave-to{opacity:0}
.slide-right-enter-active,.slide-right-leave-active{transition:transform .3s cubic-bezier(.4,0,.2,1),opacity .3s}
.slide-right-enter-from,.slide-right-leave-to{transform:translateX(100%);opacity:0}
</style>