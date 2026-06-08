<template>
  <div class="meet-wrapper">

    <!-- ── HEADER ─────────────────────────────────── -->
    <div class="meet-header">
      <div>
        <p class="meet-title">Entretien — Recruteur IA</p>
        <p class="meet-sub">RecruitSaaS · Salle virtuelle</p>
      </div>
      <div class="secure">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="#059669">
          <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1s3.1 1.39 3.1 3.1v2z"/>
        </svg>
        Chiffré de bout en bout
      </div>
    </div>

    <!-- ── MAIN AREA ───────────────────────────────── -->
    <div class="meet-main">

      <!-- Tuile avatar principale -->
      <div class="main-tile" ref="mainTile">
        <div class="speaking-ring" :class="{ active: isSpeaking }"></div>

        <canvas ref="canvas" class="three-canvas" :style="{ display: avatarLoaded ? 'block' : 'none' }"></canvas>

        <div v-if="isLoading" class="loader-overlay">
          <div class="spinner"></div>
          <p>{{ loadingText }}</p>
        </div>

        <div v-if="loadError && !isLoading && !avatarLoaded" class="error-overlay">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="#ef4444">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <p>Impossible de charger l'avatar</p>
          <p class="error-sub">Vérifiez que l'API .NET est démarrée</p>
        </div>

        <div v-if="avatarLoaded" class="name-badge">{{ avatarName }}</div>
      </div>

      <!-- Sidebar -->
      <div class="sidebar">
        <div class="self-tile">
          <div class="self-avatar">Vous</div>
          <p class="self-name">Vous (candidat)</p>
        </div>
        <div class="participants-card">
          <p class="participants-title">Participants</p>
          <div class="p-row">
            <div class="p-dot ia">IA</div>
            <div>
              <p class="p-name">Recruteur IA</p>
              <p class="p-role">Hôte · Avatar 3D</p>
            </div>
            <div class="p-online"></div>
          </div>
          <div class="p-row">
            <div class="p-dot you">V</div>
            <div>
              <p class="p-name">Vous</p>
              <p class="p-role">Candidat</p>
            </div>
            <div class="p-online blue"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── BARRE CONTRÔLES ─────────────────────────── -->
    <div class="controls-bar">
      <div class="bar-left">
        <div class="rec-dot"></div>
        <span class="timer">{{ timerDisplay }}</span>
      </div>

      <div class="bar-center">
        <button class="ctrl" :class="{ off: !micOn }" @click="toggleMic" title="Micro">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
          </svg>
        </button>
        <button class="ctrl" :class="{ off: !camOn }" @click="toggleCam" title="Caméra">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
          </svg>
        </button>
        <button class="ctrl end" @click="endCall" title="Terminer">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99 3 13.28 10.73 21 20.01 21c.71 0 .99-.63.99-1.18v-3.45c0-.54-.45-.99-.99-.99z"/>
          </svg>
        </button>
      </div>

      <div class="bar-right">
        <button class="ctrl-sm" :class="{ active: autoRotate }" @click="toggleRotate" title="Rotation">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 6v3l4-4-4-4v3c-4.42 0-8 3.58-8 8 0 1.57.46 3.03 1.24 4.26L6.7 14.8c-.45-.83-.7-1.79-.7-2.8 0-3.31 2.69-6 6-6zm6.76 1.74L17.3 9.2c.44.84.7 1.79.7 2.8 0 3.31-2.69 6-6 6v-3l-4 4 4 4v-3c4.42 0 8-3.58 8-8 0-1.57-.46-3.03-1.24-4.26z"/>
          </svg>
        </button>
        <button class="ctrl-sm" @click="resetCamera" title="Reset caméra">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
          </svg>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import {
  scanAvatarRig,
  resetFace,
  proceduralLipFlutter,
  updateBlink,
  updatePresenceRig
} from '@/utils/avatarFacial.js'

const API_AVATAR_URL = 'http://localhost:5202/avatars/recruteur.glb'

const props = defineProps({ avatarUrl: { type: String, default: '' } })
const emit = defineEmits(['loaded', 'ended'])

const mainTile  = ref(null)
const canvas    = ref(null)

const avatarLoaded  = ref(false)
const isLoading     = ref(false)
const loadError     = ref(false)
const loadingText   = ref('Chargement du recruteur IA...')
const avatarName    = ref('Recruteur IA')
const isSpeaking    = ref(false)
const autoRotate    = ref(false)
const micOn         = ref(true)
const camOn         = ref(true)
const timerSec      = ref(0)
let   timerInterval = null

const timerDisplay = computed(() => {
  const m = String(Math.floor(timerSec.value / 60)).padStart(2, '0')
  const s = String(timerSec.value % 60).padStart(2, '0')
  return `${m}:${s}`
})

let scene, camera, renderer, clock, mixer, avatar, animFrameId = null
let avatarRig = null
let lipPhase = 0
const blinkState = { timer: 1.4, phase: 'idle', elapsed: 0 }

function initThree () {
  const tile = mainTile.value
  const cvs  = canvas.value
  const W = tile.clientWidth, H = tile.clientHeight

  scene = new THREE.Scene()
  // Fond studio clair, professionnel
  scene.background = new THREE.Color(0xf0f2f5)
  scene.fog = new THREE.Fog(0xf0f2f5, 10, 22)

  camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 50)
  camera.position.set(0, 1.45, 1.5)
  camera.lookAt(0, 1.3, 0)

  renderer = new THREE.WebGLRenderer({ canvas: cvs, antialias: true })
  renderer.setSize(W, H)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.outputEncoding = THREE.sRGBEncoding
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap

  buildStudio()
  buildLights()
  clock = new THREE.Clock()
  window.addEventListener('resize', onResize)
  animate()
}

function buildStudio () {
  const addMesh = (geo, mat) => {
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial(mat))
    scene.add(m); return m
  }
  const floor = addMesh(new THREE.PlaneGeometry(12, 12), { color: 0xe8eaed, roughness: 0.9 })
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true

  const back = addMesh(new THREE.PlaneGeometry(12, 7), { color: 0xf8f9fa, roughness: 0.95 })
  back.position.set(0, 3.5, -4)

  const table = addMesh(new THREE.BoxGeometry(2.6, 0.05, 0.9), { color: 0xffffff, roughness: 0.25, metalness: 0.08 })
  table.position.set(0, 0.72, 0.5); table.castShadow = true; table.receiveShadow = true

  ;[[-1.1,0],[1.1,0],[-1.1,.9],[1.1,.9]].forEach(([x,z]) => {
    const leg = addMesh(new THREE.BoxGeometry(0.04, 0.72, 0.04), { color: 0xd1d5db, metalness: 0.5 })
    leg.position.set(x, 0.36, z)
  })
}

function buildLights () {
  // Lumière ambiante très forte — essentielle pour un fond clair
  scene.add(new THREE.AmbientLight(0xffffff, 2.0))

  // Key light principale — simuler un softbox studio
  const key = new THREE.SpotLight(0xfffaf5, 4.0, 15, Math.PI / 4.2, 0.55)
  key.position.set(1.5, 5.5, 3.5)
  key.castShadow = true; key.shadow.bias = -0.001
  key.shadow.mapSize.width = 1024; key.shadow.mapSize.height = 1024
  scene.add(key)

  // Fill light opposé — adoucit les ombres
  const fill = new THREE.DirectionalLight(0xeef6ff, 1.8)
  fill.position.set(-3, 3.5, 2); scene.add(fill)

  // Rim/backlight — sépare l'avatar du fond
  const rim = new THREE.SpotLight(0xffffff, 2.5, 12, Math.PI / 5, 0.7)
  rim.position.set(0, 5, -3.5); scene.add(rim)

  // Lumière frontale basse — supprime les ombres sous le menton
  const low = new THREE.DirectionalLight(0xffffff, 0.8)
  low.position.set(0, 0.5, 3); scene.add(low)

  // Haut de la tête (contre-jour subtil)
  const top = new THREE.PointLight(0xfff8e7, 1.0, 6)
  top.position.set(0, 6, 0.5); scene.add(top)
}

function animate () {
  animFrameId = requestAnimationFrame(animate)
  const d = clock.getDelta()
  if (mixer) mixer.update(d)
  if (autoRotate.value && avatar) avatar.rotation.y += 0.004
  lipPhase += d * 11
  updatePresenceRig(avatarRig, d, { isSpeaking: isSpeaking.value })
  updateBlink(avatarRig, blinkState, d, { isSpeaking: isSpeaking.value })
  if (isSpeaking.value && avatarRig) proceduralLipFlutter(avatarRig, 0.42, lipPhase)
  renderer.render(scene, camera)
}

watch(isSpeaking, (v) => {
  if (!v && avatarRig) resetFace(avatarRig)
})

function loadGLB (url) {
  isLoading.value = true; loadError.value = false
  loadingText.value = 'Chargement du recruteur IA...'; avatarLoaded.value = false
  const loader = new GLTFLoader()
  loader.load(url,
    (gltf) => {
      if (avatar) scene.remove(avatar)
      avatar = gltf.scene
      const box = new THREE.Box3().setFromObject(avatar)
      const size = box.getSize(new THREE.Vector3())
      const center = box.getCenter(new THREE.Vector3())
      const scale = 1.75 / size.y
      avatar.scale.setScalar(scale)
      avatar.position.set(-center.x * scale, -box.min.y * scale, 0.3)
      avatar.traverse(n => { if (n.isMesh) { n.castShadow = true; n.receiveShadow = true } })
      scene.add(avatar)
      avatarRig = scanAvatarRig(avatar)
      if (gltf.animations?.length) {
        mixer = new THREE.AnimationMixer(avatar)
        const idle = gltf.animations.find(a => /idle/i.test(a.name)) ?? gltf.animations[0]
        mixer.clipAction(idle).reset().fadeIn(0.35).play()
      }
      isLoading.value = false; avatarLoaded.value = true
      startTimer(); emit('loaded')
    },
    (progress) => {
      if (progress.total) loadingText.value = `Chargement... ${Math.round(progress.loaded / progress.total * 100)}%`
    },
    (error) => { console.error('[AvatarViewer] Erreur GLB :', error); isLoading.value = false; loadError.value = true }
  )
}

function onResize () {
  const tile = mainTile.value
  if (!tile || !renderer) return
  const W = tile.clientWidth, H = tile.clientHeight
  camera.aspect = W / H; camera.updateProjectionMatrix(); renderer.setSize(W, H)
}

function resetCamera () {
  camera.position.set(0, 1.45, 1.5); camera.lookAt(0, 1.3, 0)
  if (avatar) avatar.rotation.y = 0
}

function toggleRotate () { autoRotate.value = !autoRotate.value }

function toggleMic () {
  micOn.value = !micOn.value
  if (micOn.value && avatar) { isSpeaking.value = true; setTimeout(() => { isSpeaking.value = false }, 3000) }
  else { isSpeaking.value = false }
}

function toggleCam () { camOn.value = !camOn.value }

function endCall () {
  if (!confirm("Terminer l'appel ?")) return
  stopTimer(); timerSec.value = 0
  if (avatarRig) resetFace(avatarRig)
  if (avatar) { scene.remove(avatar); avatar = null }
  avatarRig = null
  mixer = null; avatarLoaded.value = false; isSpeaking.value = false; autoRotate.value = false
  emit('ended')
}

function startTimer () {
  if (timerInterval) return
  timerInterval = setInterval(() => { timerSec.value++ }, 1000)
}
function stopTimer () { clearInterval(timerInterval); timerInterval = null }

onMounted(() => {
  initThree()
  loadGLB(props.avatarUrl || API_AVATAR_URL)
})
onBeforeUnmount(() => {
  cancelAnimationFrame(animFrameId); stopTimer()
  window.removeEventListener('resize', onResize); renderer?.dispose()
})
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.meet-wrapper {
  background: #f3f4f6;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 580px;
  font-family: -apple-system, 'Segoe UI', sans-serif;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

.meet-header {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  padding: 10px 18px;
  display: flex; align-items: center; justify-content: space-between;
  flex-shrink: 0;
}
.meet-title { font-size: 13px; color: #111827; font-weight: 500; }
.meet-sub   { font-size: 11px; color: #9ca3af; }
.secure     { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #059669; }

.meet-main {
  flex: 1;
  display: grid; grid-template-columns: 1fr 195px;
  gap: 8px; padding: 8px; min-height: 0;
}

.main-tile {
  background: #f0f2f5;
  border-radius: 10px;
  position: relative; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid #e5e7eb;
}

.three-canvas { width: 100% !important; height: 100% !important; }

.speaking-ring {
  position: absolute; inset: 0; border-radius: 10px;
  border: 3px solid transparent; pointer-events: none; transition: border-color .3s;
}
.speaking-ring.active {
  border-color: #10b981;
  animation: ringPulse 1.5s ease-in-out infinite;
}
@keyframes ringPulse {
  0%,100% { border-color: #10b981; }
  50%      { border-color: #34d399; }
}

.loader-overlay {
  position: absolute; inset: 0; background: #f8fafc;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 14px;
}
.spinner {
  width: 36px; height: 36px;
  border: 2.5px solid #e5e7eb; border-top-color: #059669;
  border-radius: 50%; animation: spin .9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loader-overlay p { font-size: 12px; color: #6b7280; }

.error-overlay {
  position: absolute; inset: 0; background: #f8fafc;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 10px;
}
.error-overlay p   { font-size: 13px; color: #374151; }
.error-overlay .error-sub { font-size: 11px; color: #9ca3af; }

.name-badge {
  position: absolute; bottom: 12px; left: 12px;
  background: rgba(255,255,255,0.92); backdrop-filter: blur(8px);
  color: #374151; font-size: 12px; font-weight: 500;
  padding: 4px 10px; border-radius: 6px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.sidebar { display: flex; flex-direction: column; gap: 8px; }

.self-tile {
  background: #e5e7eb; border-radius: 10px;
  flex: 1; min-height: 0;
  display: flex; align-items: center; justify-content: center;
  position: relative; border: 1px solid #d1d5db;
}
.self-avatar {
  width: 50px; height: 50px; border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  display: flex; align-items: center; justify-content: center;
  font-size: 17px; font-weight: 600; color: white;
}
.self-name { position: absolute; bottom: 8px; left: 10px; font-size: 10px; color: #6b7280; }

.participants-card {
  background: #ffffff; border-radius: 10px; padding: 10px;
  border: 1px solid #e5e7eb;
}
.participants-title {
  font-size: 9px; color: #9ca3af;
  text-transform: uppercase; letter-spacing: .08em; margin-bottom: 10px;
}
.p-row { display: flex; align-items: center; gap: 7px; margin-bottom: 7px; }
.p-dot {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; color: white; flex-shrink: 0;
}
.p-dot.ia  { background: linear-gradient(135deg, #059669, #10b981); }
.p-dot.you { background: linear-gradient(135deg, #3b82f6, #6366f1); }
.p-name { font-size: 11px; color: #111827; }
.p-role { font-size: 9px; color: #9ca3af; }
.p-online { width: 6px; height: 6px; border-radius: 50%; background: #10b981; margin-left: auto; }
.p-online.blue { background: #3b82f6; }

.controls-bar {
  background: #ffffff; border-top: 1px solid #e5e7eb;
  padding: 10px 18px;
  display: flex; align-items: center; justify-content: space-between;
  flex-shrink: 0;
}
.bar-left  { display: flex; align-items: center; gap: 8px; }
.rec-dot   { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; animation: recPulse 1.5s ease-in-out infinite; }
@keyframes recPulse { 0%,100% { opacity:1 } 50% { opacity:.3 } }
.timer     { font-size: 12px; color: #6b7280; font-variant-numeric: tabular-nums; }

.bar-center { display: flex; align-items: center; gap: 10px; }
.ctrl {
  width: 44px; height: 44px; border-radius: 50%; border: 1px solid #e5e7eb;
  background: #f9fafb; color: #374151;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background .15s, box-shadow .15s;
}
.ctrl:hover { background: #f3f4f6; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.ctrl.off   { background: #fef2f2; border-color: #fecaca; color: #ef4444; }
.ctrl.end   { background: #ef4444; border-color: #ef4444; color: white; }
.ctrl.end:hover { background: #dc2626; border-color: #dc2626; }

.bar-right { display: flex; align-items: center; gap: 8px; }
.ctrl-sm {
  width: 34px; height: 34px; border-radius: 8px; border: 1px solid #e5e7eb;
  background: #f9fafb; color: #6b7280;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background .15s;
}
.ctrl-sm:hover  { background: #f3f4f6; }
.ctrl-sm.active { background: #f0fdf4; border-color: #bbf7d0; color: #059669; }
</style>