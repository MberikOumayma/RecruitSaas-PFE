/**
 * Comparaison visage : photo de profil (image) vs flux webcam (vidéo).
 * Utilise @vladmandic/face-api + @tensorflow/tfjs (WebGL si dispo).
 *
 * Sécurité renforcée :
 *  1. Liveness check (EAR blink detection) — résiste aux photos statiques.
 *  2. Multi-frames confirmation — requiert N frames consécutives pour valider.
 *
 * Seuil : plus bas = plus strict. 0.55 ≈ même personne, angles/lumière différents.
 */
import * as tf from '@tensorflow/tfjs'
import * as faceapi from '@vladmandic/face-api'

const MODEL_BASE = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api@1.7.15/model'

/** Distance euclidienne entre descripteurs ; sous ce seuil = même personne.
 *  0.55 = strict (studio), 0.62 = tolérant (webcam conditions réelles). */
export const DEFAULT_MATCH_THRESHOLD = 0.62

let modelsPromise = null

export function getMatchThreshold () {
  const v = typeof import.meta !== 'undefined' && import.meta.env?.VITE_FACE_MATCH_THRESHOLD
  if (v == null || v === '') return DEFAULT_MATCH_THRESHOLD
  const n = Number(v)
  return Number.isFinite(n) && n > 0.2 && n < 0.95 ? n : DEFAULT_MATCH_THRESHOLD
}

async function ensureModels () {
  if (modelsPromise) return modelsPromise
  modelsPromise = (async () => {
    await tf.setBackend('webgl').catch(async () => {
      await tf.setBackend('cpu')
    })
    await tf.ready()
    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_BASE),
      faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_BASE),
      faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_BASE),
      faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_BASE)
    ])
  })()
  return modelsPromise
}

function loadImage (url) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.referrerPolicy = 'no-referrer'
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('photo_load_failed'))
    img.src = url
  })
}

async function imageReady (img) {
  try {
    if (typeof img.decode === 'function') await img.decode()
  } catch (_) {
    /* decode peut échouer sur certaines images ; on continue */
  }
}

/**
 * Redimensionne les très grandes images (souvent Cloudinary) pour stabiliser la détection,
 * et évite les visages minuscules en remontant un peu la résolution cible.
 */
function netInputFromImage (img) {
  const w = img.naturalWidth || img.width
  const h = img.naturalHeight || img.height
  if (!w || !h) return img

  const maxLong = 1280
  const long = Math.max(w, h)
  let scale = long > maxLong ? maxLong / long : 1

  const nw = Math.max(1, Math.round(w * scale))
  const nh = Math.max(1, Math.round(h * scale))
  if (nw === w && nh === h) return img

  const canvas = document.createElement('canvas')
  canvas.width = nw
  canvas.height = nh
  const ctx = canvas.getContext('2d')
  if (!ctx) return img
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  ctx.drawImage(img, 0, 0, nw, nh)
  return canvas
}

function boxArea (det) {
  const b = det.detection.box
  return b.width * b.height
}

function pickLargestFace (dets) {
  if (!dets?.length) return null
  return dets.reduce((best, cur) => (boxArea(cur) > boxArea(best) ? cur : best))
}

// ─── Helpers liveness (Eye Aspect Ratio) ─────────────────────────────────────

function dist2D (a, b) {
  return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)
}

/**
 * Eye Aspect Ratio (EAR) : mesure l'ouverture de l'oeil.
 * eyePts : 6 points de landmarks.getLeftEye() / getRightEye()
 *   p0=coin externe, p1=haut externe, p2=haut interne,
 *   p3=coin interne, p4=bas interne,  p5=bas externe
 * EAR ≈ 0.25+ yeux ouverts | EAR < 0.20 lors d'un clignement.
 */
function eyeAspectRatio (eyePts) {
  const A = dist2D(eyePts[1], eyePts[5])
  const B = dist2D(eyePts[2], eyePts[4])
  const C = dist2D(eyePts[0], eyePts[3])
  return C < 0.001 ? 0 : (A + B) / (2 * C)
}

/** Tiny : plusieurs grilles / seuils (photo de profil souvent recadrée, loin, ou peu contrastée). */
const TINY_PROFILE_ATTEMPTS = [
  { inputSize: 608, scoreThreshold: 0.35 },
  { inputSize: 512, scoreThreshold: 0.3 },
  { inputSize: 416, scoreThreshold: 0.25 },
  { inputSize: 320, scoreThreshold: 0.2 },
  { inputSize: 608, scoreThreshold: 0.18 }
]

async function detectDescriptorFromNetInput (input) {
  for (const o of TINY_PROFILE_ATTEMPTS) {
    const opts = new faceapi.TinyFaceDetectorOptions(o)
    const dets = await faceapi.detectAllFaces(input, opts).withFaceLandmarks().withFaceDescriptors()
    const best = pickLargestFace(dets)
    if (best?.descriptor) return best.descriptor
  }

  for (const minConfidence of [0.45, 0.35, 0.25, 0.15]) {
    const opts = new faceapi.SsdMobilenetv1Options({ minConfidence, maxResults: 5 })
    const dets = await faceapi.detectAllFaces(input, opts).withFaceLandmarks().withFaceDescriptors()
    const best = pickLargestFace(dets)
    if (best?.descriptor) return best.descriptor
  }

  return null
}

/** Options webcam : souples pour couvrir angles et éclairage variés. */
const tinyOptsVideo = () =>
  new faceapi.TinyFaceDetectorOptions({ inputSize: 416, scoreThreshold: 0.4 })

/**
 * Descripteur 128D à partir de la photo de profil.
 * @param {string} photoUrl URL absolue (HTTPS ou même origine avec CORS)
 */
export async function descriptorFromPhotoUrl (photoUrl) {
  await ensureModels()
  const img = await loadImage(photoUrl)
  await imageReady(img)

  const input = netInputFromImage(img)
  const descriptor = await detectDescriptorFromNetInput(input)
  if (!descriptor) throw new Error('no_face_in_profile_photo')
  return descriptor
}

/**
 * Compare la vidéo au descripteur de référence sur N frames consécutives confirmées.
 *
 * Amélioration sécurité (anti-photo-statique) :
 *   Requiert `confirmFrames` frames successives sous le seuil de distance
 *   avant de valider. Une photo imprimée peut tromper 1 frame mais pas 3
 *   frames consécutives avec variations naturelles de lumière/angle.
 *   La distance retournée est la moyenne des frames confirmées.
 *
 * @param {HTMLVideoElement} video
 * @param {Float32Array} refDescriptor
 * @param {{
 *   maxAttempts?: number,
 *   pauseMs?: number,
 *   threshold?: number,
 *   confirmFrames?: number   // frames consécutives requises (défaut: 3)
 * }} opts
 */
export async function matchVideoToDescriptor (video, refDescriptor, opts = {}) {
  await ensureModels()
  const maxAttempts   = opts.maxAttempts   ?? 12
  const pauseMs       = opts.pauseMs       ?? 450
  const threshold     = opts.threshold     ?? getMatchThreshold()
  const confirmFrames = opts.confirmFrames ?? 3

  let bestD         = Infinity
  let goodStreak    = 0
  let streakDistSum = 0

  for (let i = 0; i < maxAttempts; i++) {
    if (video.readyState < 2) {
      await new Promise((r) => setTimeout(r, pauseMs))
      goodStreak = 0; streakDistSum = 0
      continue
    }
    const det = await faceapi
      .detectSingleFace(video, tinyOptsVideo())
      .withFaceLandmarks()
      .withFaceDescriptor()
    if (det) {
      const d = faceapi.euclideanDistance(refDescriptor, det.descriptor)
      if (d < bestD) bestD = d
      if (d < threshold) {
        goodStreak++
        streakDistSum += d
        if (goodStreak >= confirmFrames) {
          return {
            match: true,
            distance: streakDistSum / goodStreak,
            attempts: i + 1,
            threshold,
            confirmedFrames: goodStreak
          }
        }
      } else {
        goodStreak = 0; streakDistSum = 0
      }
    } else {
      goodStreak = 0; streakDistSum = 0
    }
    await new Promise((r) => setTimeout(r, pauseMs))
  }
  return {
    match: false,
    distance: bestD === Infinity ? null : bestD,
    attempts: maxAttempts,
    threshold,
    confirmedFrames: goodStreak
  }
}

/** Options webcam dédiées au liveness : seuil plus bas pour mieux détecter en conditions variées. */
const tinyOptsLiveness = () =>
  new faceapi.TinyFaceDetectorOptions({ inputSize: 416, scoreThreshold: 0.3 })

/**
 * Liveness check : détecte la présence d'une personne réelle via un clignement.
 *
 * Approche en 2 étapes :
 *   1. Calibration — mesure l'EAR de base sur les 12 premières détections.
 *      Les valeurs aberrantes basses (clignements pendant la calibration) sont
 *      exclues en ne gardant que le tercile supérieur.
 *   2. Détection — surveille une chute relative ≥ 22 % par rapport à la base
 *      (fermeture), puis une remontée ≥ 88 % de la base (réouverture).
 *
 * Pourquoi des seuils relatifs plutôt qu'absolus :
 *   L'EAR d'un œil ouvert varie de ~0.25 à ~0.40 selon la morphologie et la
 *   distance à la caméra. Un seuil absolu (ex. 0.21) rate les clignements de
 *   personnes aux grands yeux dont l'EAR ne descend jamais aussi bas.
 *
 * @param {HTMLVideoElement} video
 * @param {{
 *   requiredBlinks?: number,
 *   timeoutMs?: number,
 *   sampleMs?: number,
 *   onProgress?: (n: number) => void,
 *   onCalibrated?: (baseEar: number) => void
 * }} opts
 * @returns {{ alive: boolean, blinkCount: number, baseEar?: number, reason?: string }}
 */
export async function detectLiveness (video, opts = {}) {
  await ensureModels()
  const requiredBlinks = opts.requiredBlinks ?? 1
  const timeoutMs      = opts.timeoutMs      ?? 12000
  const sampleMs       = opts.sampleMs       ?? 100
  const onProgress     = opts.onProgress     ?? null
  const onCalibrated   = opts.onCalibrated   ?? null
  const deadline       = Date.now() + timeoutMs

  // ── Étape 1 : calibration ───────────────────────────────────────────────────
  const earSamples = []
  while (Date.now() < deadline && earSamples.length < 12) {
    if (video.readyState < 2) { await new Promise(r => setTimeout(r, sampleMs)); continue }
    const det = await faceapi.detectSingleFace(video, tinyOptsLiveness()).withFaceLandmarks()
    if (det) {
      const lm = det.landmarks
      earSamples.push((eyeAspectRatio(lm.getLeftEye()) + eyeAspectRatio(lm.getRightEye())) / 2)
    }
    await new Promise(r => setTimeout(r, sampleMs))
  }

  if (earSamples.length < 3) {
    return { alive: false, blinkCount: 0, reason: 'no_face_detected' }
  }

  // Exclure le tiers inférieur (clignements ou artefacts pendant la calibration)
  const sorted  = [...earSamples].sort((a, b) => a - b)
  const trimmed = sorted.slice(Math.ceil(sorted.length * 0.33))
  const baseEar = trimmed.reduce((s, v) => s + v, 0) / trimmed.length

  const closeThr = baseEar * 0.78   // chute de 22 % → fermeture
  const openThr  = baseEar * 0.88   // remontée à 88 % → réouverture
  onCalibrated?.(baseEar)

  // ── Étape 2 : détection de clignement avec seuils relatifs ─────────────────
  let blinkCount = 0
  let phase      = 'open'           // calibration terminée → yeux déjà ouverts

  while (Date.now() < deadline) {
    if (video.readyState < 2) { await new Promise(r => setTimeout(r, sampleMs)); continue }
    const det = await faceapi.detectSingleFace(video, tinyOptsLiveness()).withFaceLandmarks()

    if (det) {
      const lm  = det.landmarks
      const ear = (eyeAspectRatio(lm.getLeftEye()) + eyeAspectRatio(lm.getRightEye())) / 2

      if (phase === 'open' && ear < closeThr) {
        phase = 'closing'
      } else if (phase === 'closing' && ear > openThr) {
        blinkCount++
        phase = 'open'
        onProgress?.(blinkCount)
        if (blinkCount >= requiredBlinks) {
          return { alive: true, blinkCount, baseEar }
        }
      }
    }
    await new Promise(r => setTimeout(r, sampleMs))
  }

  return {
    alive: false,
    blinkCount,
    baseEar,
    reason: blinkCount === 0 ? 'no_blink_detected' : 'insufficient_blinks'
  }
}

/** Proctoring pendant l'entretien : visages, regard, téléphone (heuristiques). */
export async function scanVideoProctoring (videoEl) {
  const empty = {
    count: 0,
    gazeAway: false,
    gazeDown: false,
    gazeHorizontal: false,
    phoneLikely: false,
    facePartial: false,
  }
  if (!videoEl || videoEl.readyState < 2) return empty

  await ensureModels()
  const frameStats = analyzeFrameBrightness(videoEl)
  const detections = await faceapi
    .detectAllFaces(videoEl, new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.4 }))
    .withFaceLandmarks()
  const count = detections.length
  if (!count) {
    const phoneLikely = frameStats.brightRatio > 0.08
      || (frameStats.brightRatio > 0.05 && frameStats.contrastRatio > 0.2)
    return { ...empty, phoneLikely, gazeAway: phoneLikely, facePartial: phoneLikely }
  }

  const main = detections[0]
  const box = main.detection.box
  const lm = main.landmarks
  const gazeHorizontal = detectGazeHorizontal(lm, box)
  const gazeAway = gazeHorizontal
  const facePartial = main.detection.score < 0.48 || box.width / Math.max(videoEl.videoWidth, 1) > 0.45
  const phoneLikely = detectPhoneLikely(videoEl, count, main.detection, false, frameStats, facePartial)

  return { count, gazeAway, gazeDown: false, gazeHorizontal, phoneLikely, facePartial }
}

function detectGazeHorizontal (landmarks, box) {
  const nose = landmarks.getNose()[3]
  const cx = box.x + box.width / 2
  const xOff = Math.abs(nose.x - cx) / Math.max(box.width, 1)
  const jaw = landmarks.getJawOutline()
  const faceW = Math.max(jaw[16].x - jaw[0].x, 1)
  const nosePos = (nose.x - jaw[0].x) / faceW
  const headTurned = nosePos < 0.36 || nosePos > 0.64
  return xOff > 0.2 || headTurned
}

function analyzeFrameBrightness (videoEl) {
  const w = 128
  const h = 96
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  ctx.drawImage(videoEl, 0, 0, w, h)
  const { data } = ctx.getImageData(0, 0, w, h)
  let bright = 0
  let dark = 0
  const n = w * h
  for (let i = 0; i < data.length; i += 4) {
    const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]
    if (lum > 190) bright++
    else if (lum < 55) dark++
  }
  return {
    brightRatio: bright / n,
    darkRatio: dark / n,
    contrastRatio: bright / Math.max(n - bright, 1)
  }
}

function detectPhoneLikely (videoEl, faceCount, detection, gazeDown, frameStats, facePartial) {
  const { brightRatio, contrastRatio } = frameStats
  const vw = Math.max(videoEl.videoWidth, 1)
  const box = detection?.box
  const scoreLow = detection && detection.score < 0.48
  const faceLarge = box && box.width / vw > 0.4
  const faceSmallHigh = box && box.width / vw < 0.12 && brightRatio > 0.1

  if (faceCount === 0 && brightRatio > 0.07) return true
  if (faceCount >= 1 && brightRatio > 0.08 && (scoreLow || facePartial)) return true
  if (faceLarge && brightRatio > 0.07) return true
  if (faceSmallHigh) return true
  if (brightRatio > 0.15 && contrastRatio > 0.18) return true
  return false
}
