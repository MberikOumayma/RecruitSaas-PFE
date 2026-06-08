/**
 * Collecte les métriques de proctoring pendant l'entretien
 * pour FraudPredictor v5 (aligné sur fraud_config_v5.json).
 */

export function createInterviewFraudTracker () {
  const state = {
    tab_changes: 0,
    window_blurs: 0,
    no_face_count: 0,
    multi_face_polls: 0,
    face_checks: 0,
    gaze_away_count: 0,
    gaze_horizontal_count: 0,
    phone_likely_count: 0,
    face_partial_count: 0,
    answer_delays: [],
    answer_word_counts: [],
    answer_durations: [],
    alertes: [],
    questionAskedAt: null,
    _pollTimer: null,
    _videoEl: null,
    _onVisibility: null,
    _onBlur: null,
    _onFocus: null,
    _started: false,
  }

  function recordTabChange () {
    state.tab_changes += 1
    state.alertes.push({ type: 'tab_change', at: Date.now() })
  }

  function recordWindowBlur () {
    state.window_blurs += 1
    state.alertes.push({ type: 'window_blur', at: Date.now() })
  }

  function markQuestionAsked () {
    state.questionAskedAt = Date.now()
  }

  function recordAnswer (reponseText, durationSec = null) {
    const delaySec = state.questionAskedAt
      ? (Date.now() - state.questionAskedAt) / 1000
      : 1.5
    state.answer_delays.push(delaySec)
    const words = String(reponseText || '').trim().split(/\s+/).filter(Boolean)
    state.answer_word_counts.push(words.length)
    const dur = durationSec ?? Math.max(delaySec * 0.6, 1)
    state.answer_durations.push(dur)
    state.questionAskedAt = null
  }

  async function pollVideoFrame () {
    if (!state._videoEl || state._videoEl.readyState < 2) return
    try {
      const mod = await import('@/utils/faceIdentityMatch.js')
      const scan = await mod.scanVideoProctoring(state._videoEl)
      state.face_checks += 1
      if (scan.count === 0) state.no_face_count += 1
      if (scan.count > 1) {
        state.multi_face_polls += 1
        state.alertes.push({ type: 'multi_face', count: scan.count, at: Date.now() })
      }
      if (scan.gazeHorizontal) {
        state.gaze_horizontal_count += 1
        state.gaze_away_count += 1
        state.alertes.push({ type: 'gaze_side', at: Date.now() })
      }
      if (scan.phoneLikely) {
        state.phone_likely_count += 1
        state.alertes.push({ type: 'phone_likely', at: Date.now() })
      }
      if (scan.facePartial) state.face_partial_count += 1
    } catch {
      /* face-api optional during interview */
    }
  }

  function start (videoEl) {
    state._videoEl = videoEl || state._videoEl
    if (state._started) return
    state._started = true

    state._onVisibility = () => {
      if (document.hidden) recordTabChange()
    }
    state._onBlur = () => recordWindowBlur()
    state._onFocus = () => {}
    document.addEventListener('visibilitychange', state._onVisibility)
    window.addEventListener('blur', state._onBlur)
    window.addEventListener('focus', state._onFocus)
    if (state._videoEl) {
      pollVideoFrame()
      state._pollTimer = window.setInterval(() => { pollVideoFrame() }, 1000)
    }
  }

  function stop () {
    if (state._pollTimer) {
      clearInterval(state._pollTimer)
      state._pollTimer = null
    }
    if (state._onVisibility) document.removeEventListener('visibilitychange', state._onVisibility)
    if (state._onBlur) window.removeEventListener('blur', state._onBlur)
    if (state._onFocus) window.removeEventListener('focus', state._onFocus)
    state._onVisibility = null
    state._onBlur = null
    state._onFocus = null
    state._videoEl = null
    state._started = false
  }

  function computeFrontendScore (feats) {
    // Calibré sur dataset v5 (Score frontend mean ≈ 0.44)
    let score = 0.08
    score += Math.min(feats.tab_changes * 0.045, 0.22)
    score += Math.min(feats.window_blurs * 0.04, 0.18)
    score += feats.face_absence_ratio * 0.55
    score += feats.gaze_away_ratio * 0.42
    score += Math.min(feats.multi_face_count * 0.12, 0.15)
    if (feats.phone_detected >= 1) score += 0.28
    if (feats.book_detected >= 1) score += 0.12
    if (feats.extra_person >= 1) score += 0.18
    score += Math.min(feats.suspicious_obj_count * 0.15, 0.2)
    if (feats.answer_speed > 4.5) score += 0.06
    if (feats.answer_delay > 4) score += 0.05
    return Math.min(1, Math.round(score * 1000) / 1000)
  }

  function getMetrics () {
    const checks = Math.max(state.face_checks, 1)
    const face_absence_ratio = Math.round((state.no_face_count / checks) * 1000) / 1000
    const totalGaze = state.gaze_away_count
    const gaze_away_ratio = Math.round((totalGaze / checks) * 1000) / 1000
    const gaze_horizontal_ratio = Math.round((state.gaze_horizontal_count / checks) * 1000) / 1000
    const phoneRatio = state.phone_likely_count / checks
    const answer_delay = state.answer_delays.length
      ? state.answer_delays.reduce((a, b) => a + b, 0) / state.answer_delays.length
      : 1.5
    let answer_speed = 2.0
    if (state.answer_word_counts.length && state.answer_durations.length) {
      const wpm = state.answer_word_counts.map((w, i) =>
        (w / Math.max(state.answer_durations[i], 0.5)) * 60
      )
      answer_speed = wpm.reduce((a, b) => a + b, 0) / wpm.length / 60
    }

    const extra_person = state.multi_face_polls >= 1 ? 1 : 0
    let phoneDetected = state.phone_likely_count >= 1 && phoneRatio >= 0.05 ? 1 : 0
    if (face_absence_ratio > 0.15 && state.phone_likely_count >= 1) phoneDetected = 1
    if (state.phone_likely_count >= 3) phoneDetected = 1

    // Nb objets suspects (dataset mean ≈ 0.74) : flags binaires, pas somme brute d'événements
    let suspicious_obj_count = phoneDetected
    if (state.face_partial_count >= 2) suspicious_obj_count += 1
    if (state.gaze_horizontal_count >= Math.ceil(checks * 0.08)) suspicious_obj_count += 1

    const base = {
      tab_changes: state.tab_changes,
      window_blurs: state.window_blurs,
      no_face_count: state.no_face_count,
      multi_face_count: state.multi_face_polls,
      face_absence_ratio,
      gaze_away_count: totalGaze,
      gaze_away_ratio,
      gaze_down_count: 0,
      gaze_down_ratio: 0,
      gaze_horizontal_count: state.gaze_horizontal_count,
      gaze_horizontal_ratio,
      phone_likely_count: state.phone_likely_count,
      face_partial_count: state.face_partial_count,
      face_checks: state.face_checks,
      phone_detected: phoneDetected,
      book_detected: 0,
      laptop_detected: 0,
      extra_person,
      suspicious_obj_count,
      answer_delay: Math.round(answer_delay * 100) / 100,
      answer_speed: Math.round(answer_speed * 100) / 100,
    }
    base.frontend_fraud_score = computeFrontendScore(base)
    return base
  }

  function formatAlertesForApi () {
    return state.alertes.map((a) => {
      if (typeof a === 'string') return a
      const parts = [a.type || 'alert']
      if (a.count != null) parts.push(`count=${a.count}`)
      if (a.at != null) parts.push(`at=${a.at}`)
      return parts.join(':')
    })
  }

  return {
    start,
    stop,
    markQuestionAsked,
    recordAnswer,
    recordTabChange,
    getMetrics,
    getAlertes: () => [...state.alertes],
    formatAlertesForApi,
  }
}
