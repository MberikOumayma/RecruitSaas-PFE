/**
 * Rig facial : morphs ARKit / RPM + mâchoire, clignement, présence (cou), TTS FR homme, lip-sync.
 */

const MOUTH_OPEN_KEYS = [
  'jawopen', 'jaw_open', 'mouthopen', 'mouth_open', 'openmouth',
  'viseme_aa', 'viseme_oh', 'vrc.v_aa', 'vrc.v_oh',
  'mouthwide', 'mouth_wide', 'jaw_openings'
]

const MOUTH_NARROW_KEYS = ['mouthpucker', 'mouth_pucker', 'viseme_u', 'viseme_ou', 'kiss', 'funnel']
const MOUTH_STRETCH_KEYS = ['mouthstretch', 'mouth_stretch', 'viseme_i', 'viseme_e', 'grin']

const SMILE_KEYS = ['mouthsmile', 'smile', 'happy', 'mouth_smile', 'cheeksquint', 'cheek_squint']
const BROW_KEYS = ['browinnerup', 'brow_inner_up', 'browup', 'surprised']

const BLINK_KEYS = [
  'eyeblink', 'eyeblinks', 'blink', 'blinks', 'eyesclose', 'eyes_close', 'eyeclose', 'eye_close',
  'squint', 'blinkleft', 'blinkright', 'eye_l_close', 'eye_r_close', 'close_l', 'close_r',
  'eyesclosed', 'eyes_closed', 'closed_eye', 'eyeblinkleft', 'eyeblinkright', 'eye_blink',
  'eyelid', 'lidclose', 'lids', 'wink',
  // ARKit / Ready Player Me / CC4 variantes fréquentes (sans « eyelook » = regard)
  'eyeblinkl', 'eyeblinkr', 'blink_l', 'blink_r',
  'eyeclose_l', 'eyeclose_r', 'closeeye', 'eyelids', 'eyelidclose', 'lid_close', 'upperlid', 'lowerlid'
]

function shouldDriveBlinkMorph (key) {
  const k = key.toLowerCase().replace(/\s/g, '')
  if (k.includes('mouth') || k.includes('jaw') || k.includes('tongue') || k.includes('teeth')) return false
  if (k.includes('cheek') && !k.includes('eye')) return false
  if (keyMatches(key, BLINK_KEYS)) return true
  if (k.includes('brow')) return false
  if (k.includes('eyelid') && (k.includes('close') || k.includes('upper') || k.includes('lower'))) return true
  if ((k.includes('eye') || k.includes('eyes')) && (k.includes('blink') || k.includes('close') || k.includes('shut')))
    return true
  if (k.includes('squint') && k.includes('eye')) return true
  return false
}

/** Si aucun morph reconnu : recherche large sur tous les blendshapes (noms exotiques). */
function discoverBlinkMorphsFallback (rig) {
  if (!rig?.morphMeshes?.length || rig.blinkMorphTargets?.length) return
  const seen = new Set()
  for (const { mesh, dict } of rig.morphMeshes) {
    for (const key of Object.keys(dict)) {
      const raw = key.toLowerCase().replace(/\s/g, '')
      const k = raw.replace(/[_-]/g, '')
      if (k.includes('mouth') || k.includes('jaw') || k.includes('tongue') || k.includes('teeth')) continue
      if (k.includes('brow') && !k.includes('eye')) continue
      if (k.includes('cheek') && !k.includes('eye')) continue
      const hit =
        k.includes('blink') ||
        (k.includes('eye') && (k.includes('close') || k.includes('shut') || k.includes('squint'))) ||
        (k.includes('lid') && k.includes('eye')) ||
        (k.includes('eyelid') && (k.includes('upper') || k.includes('lower') || k.includes('close')))
      if (!hit) continue
      const idx = dict[key]
      const id = `${mesh.uuid}:${idx}`
      if (seen.has(id)) continue
      seen.add(id)
      rig.blinkMorphTargets.push({ mesh, idx })
    }
  }
}

function collectBlinkAndEyeMeshes (rig, root) {
  rig.blinkMorphTargets = []
  rig.eyeScaleMeshes = []
  const seen = new Set()
  for (const { mesh, dict } of rig.morphMeshes) {
    for (const key of Object.keys(dict)) {
      if (!shouldDriveBlinkMorph(key)) continue
      const idx = dict[key]
      const id = `${mesh.uuid}:${idx}`
      if (seen.has(id)) continue
      seen.add(id)
      rig.blinkMorphTargets.push({ mesh, idx })
    }
  }
  root.traverse((child) => {
    if (!child.isMesh || !child.name) return
    const n = child.name.toLowerCase()
    if (n.includes('brow') || n.includes('lash') || n.includes('teeth') || n.includes('mouth')) return
    const looksLikeEyePart =
      /\beye\b/.test(n) ||
      n.includes('eyeball') ||
      n.includes('eyewhite') ||
      n.includes('eye_white') ||
      n.includes('ocular') ||
      (n.includes('cornea') && !n.includes('hair')) ||
      (n.includes('iris') && !n.includes('hair'))
    if (!looksLikeEyePart) return
    const dict = child.morphTargetDictionary
    const hasMorphs = dict && Object.keys(dict).length > 0
    // Tête RPM : morphs yeux sur le même mesh — le fallback blinkMorphTargets s’en charge.
    if (hasMorphs) return
    rig.eyeScaleMeshes.push({ mesh: child, baseSy: child.scale.y })
  })
}

export function rigSupportsBlink (rig) {
  return !!(
    rig &&
    (rig.blinkMorphTargets?.length > 0 ||
      rig.eyeScaleMeshes?.length > 0 ||
      rig.eyelidBones?.length > 0)
  )
}

const LOWER_FACE_PATTERN_SETS = [
  MOUTH_OPEN_KEYS, MOUTH_NARROW_KEYS, MOUTH_STRETCH_KEYS, SMILE_KEYS, BROW_KEYS
]

function keyMatches (name, patterns) {
  const k = name.toLowerCase().replace(/\s/g, '')
  return patterns.some((p) => k.includes(p.replace(/\./g, '')))
}

function isBlinkMorphKey (key) {
  return keyMatches(key, BLINK_KEYS)
}

function isLowerFaceMorphKey (key) {
  return LOWER_FACE_PATTERN_SETS.some((p) => keyMatches(key, p))
}

export function scanAvatarRig (root) {
  const rig = {
    jawBone: null,
    neckBone: null,
    headBone: null,
    morphMeshes: [],
    eyelidBones: [],
    _jawOrigX: null,
    _storedJaw: false,
    _neckOrig: null,
    _headOrig: null
  }

  root.traverse((child) => {
    if (child.isBone) {
      const n = child.name.toLowerCase()
      if (!rig.jawBone && (n.includes('jaw') || n.includes('mandible') || n.includes('chin')))
        rig.jawBone = child
      if (!rig.neckBone && n.includes('neck')) rig.neckBone = child
      if (
        !rig.headBone &&
        (n === 'head' || n.endsWith(':head') || (n.includes('head') && !n.includes('fore') && !n.includes('forearm')))
      )
        rig.headBone = child
      const looksEyelidBone =
        n.includes('eyelid') ||
        n.includes('eye_lid') ||
        n.includes('eyelids') ||
        (n.includes('lid') &&
          (n.includes('upper') || n.includes('lower')) &&
          (n.includes('eye') || n.includes('_l_') || n.includes('_r_') || n.endsWith('_l') || n.endsWith('_r')))
      if (looksEyelidBone && !n.includes('brow')) {
        rig.eyelidBones.push({ bone: child, rx0: child.rotation.x, rz0: child.rotation.z })
      }
    }
    if (child.isMesh && child.morphTargetInfluences?.length && child.morphTargetDictionary)
      rig.morphMeshes.push({ mesh: child, dict: child.morphTargetDictionary })
  })

  if (rig.neckBone) {
    rig._neckOrig = { x: rig.neckBone.rotation.x, y: rig.neckBone.rotation.y, z: rig.neckBone.rotation.z }
  }
  if (rig.headBone) {
    rig._headOrig = { x: rig.headBone.rotation.x, y: rig.headBone.rotation.y, z: rig.headBone.rotation.z }
  }

  collectBlinkAndEyeMeshes(rig, root)
  discoverBlinkMorphsFallback(rig)

  return rig
}

function ensureJawOrig (rig) {
  if (rig.jawBone && !rig._storedJaw) {
    rig._jawOrigX = rig.jawBone.rotation.x
    rig._storedJaw = true
  }
}

export function setMorphByPatterns (rig, patterns, amount) {
  const a = Math.max(0, Math.min(1, amount))
  for (const { mesh, dict } of rig.morphMeshes) {
    for (const key of Object.keys(dict)) {
      if (keyMatches(key, patterns)) {
        const idx = dict[key]
        mesh.morphTargetInfluences[idx] = a
        break
      }
    }
  }
}

export function setMouthOpenAmount (rig, amount) {
  ensureJawOrig(rig)
  const a = Math.max(0, Math.min(1, amount))
  setMorphByPatterns(rig, MOUTH_OPEN_KEYS, a * 0.92)
  if (rig.jawBone && rig._storedJaw) rig.jawBone.rotation.x = rig._jawOrigX + a * 0.44
}

export function setSmileAmount (rig, amount) {
  setMorphByPatterns(rig, SMILE_KEYS, Math.max(0, Math.min(1, amount)) * 0.65)
}

export function setBrowRaise (rig, amount) {
  setMorphByPatterns(rig, BROW_KEYS, Math.max(0, Math.min(1, amount)) * 0.5)
}

/** Bouche fermée + formes secondaires à zéro (sans toucher aux yeux / clignement). */
export function setMouthNarrowAmount (rig, amount) {
  setMorphByPatterns(rig, MOUTH_NARROW_KEYS, Math.max(0, Math.min(1, amount)) * 0.75)
}

export function setMouthStretchAmount (rig, amount) {
  setMorphByPatterns(rig, MOUTH_STRETCH_KEYS, Math.max(0, Math.min(1, amount)) * 0.7)
}

export function setBlinkAmount (rig, t) {
  if (!rig) return
  const a = Math.max(0, Math.min(1, t))
  if (rig.blinkMorphTargets?.length) {
    for (const { mesh, idx } of rig.blinkMorphTargets) {
      mesh.morphTargetInfluences[idx] = a
    }
  } else {
    for (const { mesh, dict } of rig.morphMeshes) {
      for (const key of Object.keys(dict)) {
        if (isBlinkMorphKey(key)) mesh.morphTargetInfluences[dict[key]] = a
      }
    }
  }
  if (rig.eyeScaleMeshes?.length) {
    const f = 1 - 0.88 * a
    for (const { mesh, baseSy } of rig.eyeScaleMeshes) mesh.scale.y = baseSy * f
  }
  if (rig.eyelidBones?.length) {
    for (const { bone, rx0, rz0 } of rig.eyelidBones) {
      bone.rotation.x = rx0 + a * 0.55
      bone.rotation.z = rz0 + a * 0.04
    }
  }
}

/** Applique ouverture + voyelles (étroit / étiré) pour lip-sync plus crédible. */
export function applySpeakingViseme (rig, open, { narrow = 0, stretch = 0 } = {}) {
  setMouthOpenAmount(rig, open)
  setMouthNarrowAmount(rig, narrow)
  setMouthStretchAmount(rig, stretch)
}

export function resetLowerFace (rig) {
  if (!rig) return
  for (const { mesh, dict } of rig.morphMeshes) {
    for (const key of Object.keys(dict)) {
      if (isBlinkMorphKey(key)) continue
      if (isLowerFaceMorphKey(key)) mesh.morphTargetInfluences[dict[key]] = 0
    }
  }
  if (rig.jawBone && rig._storedJaw) rig.jawBone.rotation.x = rig._jawOrigX
}

export function resetFace (rig) {
  if (!rig) return
  for (const { mesh } of rig.morphMeshes) {
    mesh.morphTargetInfluences.fill(0)
  }
  if (rig.eyeScaleMeshes?.length) {
    for (const { mesh, baseSy } of rig.eyeScaleMeshes) mesh.scale.y = baseSy
  }
  if (rig.eyelidBones?.length) {
    for (const { bone, rx0, rz0 } of rig.eyelidBones) {
      bone.rotation.x = rx0
      bone.rotation.z = rz0
    }
  }
  if (rig.jawBone && rig._storedJaw) rig.jawBone.rotation.x = rig._jawOrigX
}

export function proceduralLipFlutter (rig, baseOpen, phase) {
  const amp = 0.08 + baseOpen * 0.14
  const wobble =
    amp * Math.sin(phase * 15.5) + (0.04 + baseOpen * 0.06) * Math.sin(phase * 24.2 + 1.1)
  setMouthOpenAmount(rig, Math.min(1, Math.max(0, baseOpen + wobble)))
}

/**
 * Léger mouvement du cou / tête — micro-présence + **respiration** type thorax (12–18 cycles/min).
 * Quand `isSpeaking` est faux, une micro-oscillation de mâchoire renforce l’effet « respire ».
 */
export function updatePresenceRig (rig, delta, { isSpeaking = false } = {}) {
  if (!rig) return
  const pivot = rig.neckBone || rig.headBone
  const o = rig.neckBone ? rig._neckOrig : rig._headOrig
  if (!pivot || !o) return
  const amp = rig.neckBone ? 1 : 0.55
  rig._aliveT = (rig._aliveT || 0) + delta
  const t = rig._aliveT
  // ~0.24 Hz ≈ 14 respirations/min (inhale / exhale lent)
  rig._breathT = (rig._breathT || 0) + delta
  const b = rig._breathT
  const breath = Math.sin(b * Math.PI * 2 * 0.24)
  const breathSlow = Math.sin(b * Math.PI * 2 * 0.11)
  // Inhale : légère extension du haut du buste (cou en X), exhale : retombée
  const chest = (breath * 0.024 + breathSlow * 0.008) * amp
  pivot.rotation.x =
    o.x +
    chest +
    (Math.sin(t * 0.62) * 0.011 + Math.sin(t * 1.55) * 0.0035) * amp
  pivot.rotation.y = o.y + (Math.sin(t * 0.38) * 0.017 + Math.sin(t * 0.9) * 0.005) * amp
  pivot.rotation.z = o.z + (Math.sin(t * 0.48) * 0.006 + breath * 0.0035) * amp

  if (!isSpeaking && rig.jawBone && rig._storedJaw) {
    ensureJawOrig(rig)
    const jawBreath = breath * 0.018 + Math.sin(b * Math.PI * 2 * 0.47) * 0.006
    rig.jawBone.rotation.x = rig._jawOrigX + jawBreath
  }
}

/**
 * Clignement procédural (fermeture rapide puis réouverture). Fonctionne aussi pendant la parole.
 */
export function updateBlink (rig, state, delta, { isSpeaking = false } = {}) {
  if (!rigSupportsBlink(rig)) return

  state.timer = (state.timer || 0) - delta

  if (state.phase === 'blink') {
    state.elapsed = (state.elapsed || 0) + delta
    const down = 0.048
    const hold = 0.032
    const up = 0.072
    let w = 0
    if (state.elapsed < down) w = state.elapsed / down
    else if (state.elapsed < down + hold) w = 1
    else if (state.elapsed < down + hold + up) w = 1 - (state.elapsed - down - hold) / up
    else {
      state.phase = 'idle'
      state.elapsed = 0
      // ~1 clignement toutes les 3 s (léger jitter pour éviter l’effet métronome)
      state.timer = isSpeaking ? 2.4 + Math.random() * 0.5 : 2.88 + Math.random() * 0.28
      setBlinkAmount(rig, 0)
      return
    }
    const curve = w < 0.5 ? 2 * w * w : 1 - Math.pow(-2 * w + 2, 2) / 2
    setBlinkAmount(rig, curve)
    return
  }

  if (state.timer <= 0) {
    state.phase = 'blink'
    state.elapsed = 0
  }
}

const MALE_HINTS =
  /male|homme|\bpaul\b|\bhenri\b|\bdenis\b|\bdaniel\b|\bgilles\b|\bnicolas\b|\bthierry\b|\bjacques\b|\barnaud\b|\bmarc\b|\bthomas\b|\bmathieu\b|\bclaude\b|\blouis\b|\bphilippe\b|\bgeorges\b|\bbruno\b|\bpatrick\b|\bvincent\b|\bfranck\b|\bfrank\b|\bcedric\b|\bcédric\b|\bjulien\b|\bsebastien\b|\bsébastien\b|\bgregoire\b|\bgrégoire\b|\bmaurice\b|\bgerard\b|\bgérard\b|\bjean\b|\bpierre\b|\bmichel\b|\bandre\b|\bchristophe\b|\bantoine\b|\bfabrice\b|\bstephane\b|\bstéphane\b|\bolivier\b|\bmaxime\b|\bbenjamin\b|\balexandre\b|\bjonathan\b|\bflorian\b|\bromain\b|\bkevin\b|\byves\b|\bhugo\b|\bleo\b|\bléo\b|\btheo\b|\bthéo\b|\braphael\b|\braphaël\b|\bquentin\b|\baxel\b|\bnoah\b|\benzo\b|\blucas\b|\bnathan\b|\bmathis\b|\btimeo\b|\btiméo\b|\bgael\b|\bgaël\b|\bremy\b|\brémy\b|\bclément\b|\bclement\b|\bvalentin\b|\baugustin\b|\bcharles\b|\bfrancois\b|\bfrançois\b|\bbaptiste\b|\balexis\b|\bdavid\b|\bjames\b|\bmark\b/i

const FEMALE_HINTS =
  /female|femme|hortense|julie|léa|\blea\b|aude|caroline|véronique|veronique|chloé|chloe|zira|virginie|hélène|helene|émilie|emilie|evelyne|calista|celine|céline|sophie|camille|lea\b|lea\b|amélie|amelie|nathalie|isabelle|catherine|sandrine|valérie|valerie|sylvie|chantal|brigitte|martine|nicole|monique|danielle|colette|josiane|françoise|francoise|claire|marine|laura|sarah|emma|lea\b|manon|lilou|zoé|zoe|elodie|élodie|pauline|margot|alice|juliette|rose|jade|louise|anna|elena|léna|lena|ines|inès|agathe|louna|romy|romy|romy/i

function pickFrenchMaleVoice () {
  const all = speechSynthesis.getVoices()
  const fr = all.filter((x) => /^fr/i.test(x.lang || '') || /fr[-_](fr|ca|ch|be)/i.test(x.lang || ''))
  const label = (v) => `${v.name} ${v.voiceURI || ''}`

  const explicitMale = fr.filter((v) => MALE_HINTS.test(label(v)))
  if (explicitMale.length) return explicitMale[0]

  const notFemale = fr.filter((v) => !FEMALE_HINTS.test(label(v)))
  if (notFemale.length) return notFemale[0]

  return fr[0] || all.find((x) => /^fr/i.test(x.lang || '')) || null
}

let recruiterLipRaf = null
let recruiterLipInterval = null

/** Arrête l'animation labiale (entre phrases ou avant une alerte prioritaire). */
export function stopRecruiterLipSync () {
  if (recruiterLipRaf) {
    cancelAnimationFrame(recruiterLipRaf)
    recruiterLipRaf = null
  }
  if (recruiterLipInterval !== null) {
    clearInterval(recruiterLipInterval)
    recruiterLipInterval = null
  }
}

/**
 * Enchaîne des phrases — voix française **masculine** si disponible, pitch légèrement bas.
 * Lip-sync : visèmes pilotés par le **temps** de la phrase (aligné sur la durée estimée du TTS),
 * renforcés par `onboundary` quand le navigateur l’expose.
 * @param {object} [callbacks.welcomeSmile] 0–1 : sourire aux lèvres pendant la salutation (séquence).
 * @param {object} [callbacks.lipPrecision] réduit le flutter labial pour coller davantage au texte.
 */
export function speakFrenchSequence (phrases, rig, callbacks = {}) {
  const { onSpeaking, onComplete, onPhraseStart, welcomeSmile = 0, lipPrecision = true } = callbacks

  let cancelled = false
  let mouthTarget = 0
  let mouthCurrent = 0
  let narrowTarget = 0
  let narrowCurrent = 0
  let stretchTarget = 0
  let stretchCurrent = 0

  /** État partagé entre onstart et la boucle labiale (repère temporel = audio TTS). */
  const lipCtx = {
    chars: /** @type {string[]} */ ([]),
    tSpeech: 0,
    rate: 0.94,
    smileAmt: 0,
    precision: lipPrecision
  }

  const vowels = /[aàâäeéèêëiïîoôöuùûüyæœ]/i
  const wideOpen = /[aàâäoôö]/i
  const midOpen = /[eéèêëuùûü]/i
  const narrowVowel = /[iïîy]/i
  const roundVowel = /[oôöuùûü]/i
  const semiOpen = /[lmnrvw]/i
  const plosive = /[pbtdkg]/i

  function stopLipLoop () {
    stopRecruiterLipSync()
    lipCtx.chars = []
    lipCtx.tSpeech = 0
  }

  function lipTick (animT0) {
    const phase = (performance.now() - animT0) / 1000
    const decay = lipCtx.precision ? 0.952 : 0.968
    mouthTarget *= decay
    narrowTarget *= 0.94
    stretchTarget *= 0.94

    // Avance dans le texte au rythme du temps écoulé (meilleure cohérence avec ce qui est dit)
    if (lipCtx.chars.length && lipCtx.tSpeech > 0) {
      const elapsed = (performance.now() - lipCtx.tSpeech) / 1000
      const n = lipCtx.chars.length
      const cps = 11.0 * (lipCtx.rate || 0.94)
      const estDur = Math.max(0.95, n / cps)
      const progress = Math.min(1, elapsed / estDur)
      const floatIdx = progress * Math.max(0, n - 1)
      const i0 = Math.floor(floatIdx)
      const i1 = Math.min(n - 1, i0 + 1)
      const frac = floatIdx - i0
      pulseFromChar(lipCtx.chars[i0], lipCtx.chars[i0 + 1])
      if (frac > 0.12) pulseFromChar(lipCtx.chars[i1], lipCtx.chars[i1 + 1])
      if (frac > 0.55 && i1 < n - 1) pulseFromChar(lipCtx.chars[i1 + 1], lipCtx.chars[i1 + 2])
    }

    const opening = mouthTarget > mouthCurrent + 0.02
    const lipSpeedOpen = lipCtx.precision ? 0.62 : 0.52
    const lipSpeedClose = lipCtx.precision ? 0.3 : 0.22
    mouthCurrent += (mouthTarget - mouthCurrent) * (opening ? lipSpeedOpen : lipSpeedClose)
    narrowCurrent += (narrowTarget - narrowCurrent) * (lipCtx.precision ? 0.45 : 0.38)
    stretchCurrent += (stretchTarget - stretchCurrent) * (lipCtx.precision ? 0.45 : 0.38)

    const flutterBase = mouthCurrent * (0.88 + 0.12 * Math.sin(phase * 3.1))
    const w1 = lipCtx.precision ? 0.015 : 0.07
    const w1m = lipCtx.precision ? 0.045 : 0.11
    const w2 = lipCtx.precision ? 0.008 : 0.035
    const w2m = lipCtx.precision ? 0.022 : 0.05
    const wobble =
      (w1 + mouthCurrent * w1m) * Math.sin(phase * (lipCtx.precision ? 10.5 : 16.2)) +
      (w2 + mouthCurrent * w2m) * Math.sin(phase * (lipCtx.precision ? 17 : 25) + 0.9)
    const open = Math.min(1, Math.max(0, flutterBase + wobble))
    applySpeakingViseme(rig, open, { narrow: narrowCurrent, stretch: stretchCurrent })

    if (lipCtx.smileAmt > 0) {
      const damp = 1 - Math.min(1, open * 0.52)
      const live = lipCtx.smileAmt * damp * (0.9 + 0.1 * Math.sin(phase * 2.05))
      setSmileAmount(rig, live)
    }

    recruiterLipRaf = requestAnimationFrame(() => lipTick(animT0))
  }

  function startLipLoop () {
    stopLipLoop()
    const animT0 = performance.now()
    recruiterLipRaf = requestAnimationFrame(() => lipTick(animT0))
  }

  function pulseFromChar (ch, nextCh) {
    if (!ch || ch === ' ' || ch === '’' || ch === "'") return

    let open = 0.2
    let narrow = 0
    let stretch = 0

    if (vowels.test(ch)) {
      if (wideOpen.test(ch)) open = 0.94
      else if (narrowVowel.test(ch)) {
        open = 0.52
        narrow = 0.42
        stretch = 0.38
      } else if (roundVowel.test(ch)) {
        open = 0.72
        narrow = 0.55
      } else if (midOpen.test(ch)) open = 0.82
      else open = 0.78
    } else if (semiOpen.test(ch)) open = 0.36
    else if (plosive.test(ch)) {
      open = 0.08
      if (nextCh && vowels.test(nextCh)) open = 0.28
    } else open = 0.16

    mouthTarget = Math.max(mouthTarget, open)
    narrowTarget = Math.max(narrowTarget, narrow)
    stretchTarget = Math.max(stretchTarget, stretch)
  }

  function pulseWord (word) {
    if (!word) return
    const w = word.normalize('NFC')
    for (let i = 0; i < w.length; i++) pulseFromChar(w[i], w[i + 1])
  }

  let index = 0

  function speakNext () {
    if (cancelled || index >= phrases.length) {
      stopLipLoop()
      mouthTarget = 0
      mouthCurrent = 0
      narrowTarget = narrowCurrent = stretchTarget = stretchCurrent = 0
      resetLowerFace(rig)
      onSpeaking?.(false)
      onComplete?.()
      return
    }

    const phraseIdx = index
    const text = phrases[index]
    index++
    onPhraseStart?.(text, phraseIdx)

    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'fr-FR'
    u.rate = 0.94

    const maleVoice = pickFrenchMaleVoice()
    if (maleVoice) {
      u.voice = maleVoice
      u.pitch = FEMALE_HINTS.test(`${maleVoice.name} ${maleVoice.voiceURI || ''}`) ? 0.88 : 0.93
    } else {
      u.pitch = 0.88
    }

    u.onstart = () => {
      onSpeaking?.(true)
      mouthTarget = 0.26
      narrowTarget = 0
      stretchTarget = 0

      const flat = text.replace(/\s+/g, ' ').trim()
      lipCtx.chars = flat.length ? [...flat] : []
      lipCtx.tSpeech = performance.now()
      lipCtx.rate = u.rate || 0.94
      lipCtx.precision = lipPrecision
      const nPh = Math.max(1, phrases.length)
      lipCtx.smileAmt = welcomeSmile > 0 ? welcomeSmile * (1 - (phraseIdx / nPh) * 0.22) : 0

      startLipLoop()
    }

    u.onboundary = (e) => {
      const name = e.name || ''
      if (name === 'word' && e.charIndex != null) {
        const i = e.charIndex
        const len = Math.max(1, e.charLength || 1)
        const word = text.slice(i, i + len).replace(/[^a-zA-ZÀ-ÿ0-9'-]/g, '')
        pulseWord(word)
        return
      }
      if ((name === 'sentence' || name === '') && e.charIndex != null) {
        const i = e.charIndex
        const slice = text.slice(i, i + Math.max(1, e.charLength || 2))
        for (let j = 0; j < slice.length; j++) pulseFromChar(slice[j], slice[j + 1])
      }
    }

    u.onend = () => {
      stopRecruiterLipSync()
      mouthTarget = 0
      mouthCurrent = 0
      narrowTarget = narrowCurrent = stretchTarget = stretchCurrent = 0
      resetLowerFace(rig)
      speakNext()
    }

    u.onerror = () => {
      stopRecruiterLipSync()
      resetFace(rig)
      onSpeaking?.(false)
      onComplete?.()
    }

    if (speechSynthesis.paused) speechSynthesis.resume()
    speechSynthesis.speak(u)
  }

  speechSynthesis.cancel()
  // Chrome bug: cancel() peut laisser le moteur TTS en état "stalled/paused".
  // resume() force le retour à l'état "running" pour que le prochain speak() joue.
  speechSynthesis.resume()

  let kicked = false
  const kick = () => {
    if (cancelled || kicked) return
    kicked = true
    if (speechSynthesis.paused) speechSynthesis.resume()
    speakNext()
  }
  if (speechSynthesis.getVoices().length) setTimeout(kick, 80)
  else {
    speechSynthesis.onvoiceschanged = () => {
      speechSynthesis.onvoiceschanged = null
      setTimeout(kick, 80)
    }
    setTimeout(kick, 500)
  }

  return () => {
    cancelled = true
    speechSynthesis.cancel()
    stopLipLoop()
    resetFace(rig)
    onSpeaking?.(false)
  }
}

/**
 * Une seule phrase. Lip-sync aligné sur le temps (comme la séquence).
 * @param {number} [opts.phraseSmile] 0–1 sourire léger pendant cette phrase (ex. réponses chaleureuses).
 */
export function speakFrenchOnce (text, rig, { onSpeaking, onEnd, lipPrecision = true, phraseSmile = 0 } = {}) {
  if (!text || !rig) {
    onEnd?.()
    return
  }

  let mouthTarget = 0
  let mouthCurrent = 0
  let narrowTarget = 0
  let narrowCurrent = 0
  let stretchTarget = 0
  let stretchCurrent = 0

  const lipCtx = {
    chars: /** @type {string[]} */ ([]),
    tSpeech: 0,
    rate: 0.94,
    smileAmt: 0,
    precision: lipPrecision
  }

  const vowels = /[aàâäeéèêëiïîoôöuùûüyæœ]/i
  const wideOpen = /[aàâäoôö]/i
  const midOpen = /[eéèêëuùûü]/i
  const narrowVowel = /[iïîy]/i
  const roundVowel = /[oôöuùûü]/i
  const semiOpen = /[lmnrvw]/i
  const plosive = /[pbtdkg]/i

  function lipTick (animT0) {
    const phase = (performance.now() - animT0) / 1000
    const decay = lipCtx.precision ? 0.952 : 0.968
    mouthTarget *= decay
    narrowTarget *= 0.94
    stretchTarget *= 0.94

    if (lipCtx.chars.length && lipCtx.tSpeech > 0) {
      const elapsed = (performance.now() - lipCtx.tSpeech) / 1000
      const n = lipCtx.chars.length
      const cps = 11.0 * (lipCtx.rate || 0.94)
      const estDur = Math.max(0.95, n / cps)
      const progress = Math.min(1, elapsed / estDur)
      const floatIdx = progress * Math.max(0, n - 1)
      const i0 = Math.floor(floatIdx)
      const i1 = Math.min(n - 1, i0 + 1)
      const frac = floatIdx - i0
      pulseFromChar(lipCtx.chars[i0], lipCtx.chars[i0 + 1])
      if (frac > 0.12) pulseFromChar(lipCtx.chars[i1], lipCtx.chars[i1 + 1])
      if (frac > 0.55 && i1 < n - 1) pulseFromChar(lipCtx.chars[i1 + 1], lipCtx.chars[i1 + 2])
    }

    const opening = mouthTarget > mouthCurrent + 0.02
    const lipSpeedOpen = lipCtx.precision ? 0.62 : 0.52
    const lipSpeedClose = lipCtx.precision ? 0.3 : 0.22
    mouthCurrent += (mouthTarget - mouthCurrent) * (opening ? lipSpeedOpen : lipSpeedClose)
    narrowCurrent += (narrowTarget - narrowCurrent) * (lipCtx.precision ? 0.45 : 0.38)
    stretchCurrent += (stretchTarget - stretchCurrent) * (lipCtx.precision ? 0.45 : 0.38)
    const flutterBase = mouthCurrent * (0.88 + 0.12 * Math.sin(phase * 3.1))
    const w1 = lipCtx.precision ? 0.015 : 0.07
    const w1m = lipCtx.precision ? 0.045 : 0.11
    const w2 = lipCtx.precision ? 0.008 : 0.035
    const w2m = lipCtx.precision ? 0.022 : 0.05
    const wobble =
      (w1 + mouthCurrent * w1m) * Math.sin(phase * (lipCtx.precision ? 10.5 : 16.2)) +
      (w2 + mouthCurrent * w2m) * Math.sin(phase * (lipCtx.precision ? 17 : 25) + 0.9)
    const open = Math.min(1, Math.max(0, flutterBase + wobble))
    applySpeakingViseme(rig, open, { narrow: narrowCurrent, stretch: stretchCurrent })
    if (lipCtx.smileAmt > 0) {
      const damp = 1 - Math.min(1, open * 0.52)
      const live = lipCtx.smileAmt * damp * (0.9 + 0.1 * Math.sin(phase * 2.05))
      setSmileAmount(rig, live)
    }
    recruiterLipRaf = requestAnimationFrame(() => lipTick(animT0))
  }

  function pulseFromChar (ch, nextCh) {
    if (!ch || ch === ' ' || ch === '’' || ch === "'") return
    let open = 0.2
    let narrow = 0
    let stretch = 0
    if (vowels.test(ch)) {
      if (wideOpen.test(ch)) open = 0.94
      else if (narrowVowel.test(ch)) {
        open = 0.52
        narrow = 0.42
        stretch = 0.38
      } else if (roundVowel.test(ch)) {
        open = 0.72
        narrow = 0.55
      } else if (midOpen.test(ch)) open = 0.82
      else open = 0.78
    } else if (semiOpen.test(ch)) open = 0.36
    else if (plosive.test(ch)) {
      open = 0.08
      if (nextCh && vowels.test(nextCh)) open = 0.28
    } else open = 0.16
    mouthTarget = Math.max(mouthTarget, open)
    narrowTarget = Math.max(narrowTarget, narrow)
    stretchTarget = Math.max(stretchTarget, stretch)
  }

  function pulseWord (word) {
    if (!word) return
    const w = word.normalize('NFC')
    for (let i = 0; i < w.length; i++) pulseFromChar(w[i], w[i + 1])
  }

  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'fr-FR'
  u.rate = 0.94
  const maleVoice = pickFrenchMaleVoice()
  if (maleVoice) {
    u.voice = maleVoice
    u.pitch = FEMALE_HINTS.test(`${maleVoice.name} ${maleVoice.voiceURI || ''}`) ? 0.88 : 0.93
  } else u.pitch = 0.88

  u.onstart = () => {
    onSpeaking?.(true)
    mouthTarget = 0.26
    narrowTarget = 0
    stretchTarget = 0
    stopRecruiterLipSync()
    const flat = text.replace(/\s+/g, ' ').trim()
    lipCtx.chars = flat.length ? [...flat] : []
    lipCtx.tSpeech = performance.now()
    lipCtx.rate = u.rate || 0.94
    lipCtx.precision = lipPrecision
    lipCtx.smileAmt = Math.max(0, Math.min(1, phraseSmile))
    const animT0 = performance.now()
    recruiterLipRaf = requestAnimationFrame(() => lipTick(animT0))
  }

  u.onboundary = (e) => {
    const name = e.name || ''
    if (name === 'word' && e.charIndex != null) {
      const i = e.charIndex
      const len = Math.max(1, e.charLength || 1)
      const word = text.slice(i, i + len).replace(/[^a-zA-ZÀ-ÿ0-9'-]/g, '')
      pulseWord(word)
      return
    }
    if ((name === 'sentence' || name === '') && e.charIndex != null) {
      const i = e.charIndex
      const slice = text.slice(i, i + Math.max(1, e.charLength || 2))
      for (let j = 0; j < slice.length; j++) pulseFromChar(slice[j], slice[j + 1])
    }
  }

  u.onend = () => {
    stopRecruiterLipSync()
    mouthTarget = mouthCurrent = 0
    narrowTarget = narrowCurrent = stretchTarget = stretchCurrent = 0
    resetLowerFace(rig)
    onSpeaking?.(false)
    onEnd?.()
  }

  u.onerror = () => {
    stopRecruiterLipSync()
    resetFace(rig)
    onSpeaking?.(false)
    onEnd?.()
  }

  speechSynthesis.speak(u)
}

/**
 * Interrompt la synthèse en cours, coupe le lip-sync, puis lit une alerte (caméra, onglet, etc.).
 */
export function speakFrenchPriorityAlert (text, rig, { onSpeaking, onEnd, beforeSpeak } = {}) {
  beforeSpeak?.()
  speechSynthesis.cancel()
  stopRecruiterLipSync()
  resetLowerFace(rig)
  onSpeaking?.(false)

  const run = () => speakFrenchOnce(text, rig, { onSpeaking, onEnd })
  if (speechSynthesis.getVoices().length) setTimeout(run, 50)
  else {
    speechSynthesis.onvoiceschanged = () => {
      speechSynthesis.onvoiceschanged = null
      setTimeout(run, 50)
    }
    setTimeout(run, 400)
  }
}

/**
 * Micro-expressions idle (sans clignement — géré à part).
 */
export function updateIdleExpression (rig, state, delta, { suppress = false } = {}) {
  if (!rig || suppress) {
    // En parole, ne pas forcer le sourire à 0 : le lip-sync / salutation peut l’animer.
    if (rig) setBrowRaise(rig, 0)
    return
  }

  state.timer = (state.timer || 0) - delta
  if (state.active) {
    state.elapsed = (state.elapsed || 0) + delta
    const dur = state.dur || 0.45
    const p = Math.min(1, state.elapsed / dur)
    const ease = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2
    if (state.kind === 'smile') setSmileAmount(rig, ease * 0.55 * (1 - p * 0.3))
    else if (state.kind === 'brow') setBrowRaise(rig, ease * 0.7 * (1 - p * 0.2))
    else if (state.kind === 'mouth') {
      setMouthOpenAmount(rig, ease * 0.12)
      setSmileAmount(rig, ease * 0.2)
    }
    if (p >= 1) {
      state.active = false
      state.elapsed = 0
      state.timer = 5 + Math.random() * 9
      resetLowerFace(rig)
      if (rig._storedJaw && rig.jawBone) rig.jawBone.rotation.x = rig._jawOrigX
    }
    return
  }

  if (state.timer <= 0) {
    const kinds = ['smile', 'brow', 'mouth']
    state.kind = kinds[Math.floor(Math.random() * kinds.length)]
    state.active = true
    state.elapsed = 0
    state.dur = 0.35 + Math.random() * 0.35
    state.timer = 0
  }
}
