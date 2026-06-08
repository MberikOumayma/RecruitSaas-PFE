<template>
  <transition name="modal-fade">
    <div v-if="modelValue" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box modal-interview">
        <div class="modal-header">
          <div>
            <h3 class="modal-title">📅 Schedule Interview</h3>
            <p class="modal-sub" v-if="candidate">
              <span class="sub-name">{{ candidate.nomCandidat }}</span>
              <span class="dot-sep">·</span>{{ candidate.titreOffre }}
            </p>
          </div>
          <button class="modal-close" @click="closeModal">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
          </button>
        </div>
        <div class="modal-body">

          <!-- Succès : email envoyé -->
          <div v-if="schedulingDone" class="interview-success">
            <div class="success-circle">✓</div>
            <h4>Invitation envoyée !</h4>
            <p>Un email a été envoyé automatiquement à <strong>{{ candidate?.emailCandidat }}</strong> avec les créneaux disponibles.</p>
            <div class="success-steps">
              <div class="step-item">
                <span class="step-dot done">1</span>
                <span>Email envoyé au candidat ✓</span>
              </div>
              <div class="step-item">
                <span class="step-dot pending">2</span>
                <span>Le candidat choisit son créneau</span>
              </div>
              <div class="step-item">
                <span class="step-dot pending">3</span>
                <span>L'entretien apparaît dans votre calendrier</span>
              </div>
            </div>
            <button class="send-invite-btn" @click="closeModal" style="margin-top:8px;">
              Fermer
            </button>
          </div>

          <!-- Formulaire planification avec calendrier -->
          <div v-else>
            <p class="calendar-hint">Sélectionnez les créneaux disponibles directement dans le calendrier ci-dessous.</p>

            <!-- Mini calendrier hebdomadaire -->
            <div class="mini-cal">
              <div class="mini-cal-nav">
                <button class="mini-nav-btn" @click="calPrevWeek">‹</button>
                <span class="mini-week-label">{{ calWeekLabel }}</span>
                <button class="mini-nav-btn" @click="calNextWeek">›</button>
              </div>
              <div class="mini-cal-grid">
                <div v-for="day in calWeekDays" :key="day.iso" class="mini-day-col">
                  <div class="mini-day-header" :class="{ 'mini-today': day.isToday }">
                    <span class="mini-day-name">{{ day.name }}</span>
                    <span class="mini-day-num">{{ day.num }}</span>
                  </div>
                  <div class="mini-slots">
                    <button
                      v-for="slot in calTimeSlots"
                      :key="day.iso + '-' + slot"
                      class="mini-slot"
                      :class="{ 'mini-slot-selected': isSlotSelected(day.iso, slot), 'mini-slot-past': isSlotPast(day.iso, slot) }"
                      :disabled="isSlotPast(day.iso, slot)"
                      @click="toggleSlot(day.iso, slot)"
                    >{{ slot }}</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Créneaux sélectionnés -->
            <div v-if="interviewCreneaux.length" class="selected-slots">
              <p class="selected-slots-label">{{ interviewCreneaux.length }} créneau{{ interviewCreneaux.length > 1 ? 'x' : '' }} sélectionné{{ interviewCreneaux.length > 1 ? 's' : '' }}</p>
              <div class="selected-chips">
                <span v-for="(c, i) in interviewCreneaux" :key="i" class="slot-chip">
                  {{ formatCreneau(c) }}
                  <button class="chip-remove" @click="interviewCreneaux.splice(i, 1)">×</button>
                </span>
              </div>
            </div>
            <p v-else class="creneaux-empty">Cliquez sur les créneaux pour les sélectionner.</p>

            <!-- Message personnalisé -->
            <div class="interview-section" style="margin-top:14px;">
              <div class="interview-section-label">💬 Message (optionnel)</div>
              <textarea
                v-model="interviewMessage"
                class="interview-textarea"
                placeholder="Ex: Bonjour, nous serions ravis de vous rencontrer..."
                rows="2"
              ></textarea>
            </div>

            <button
              class="send-invite-btn"
              @click="handlePlanifier"
              :disabled="planifying || !interviewCreneaux.length"
            >
              <VideoIcon :size="14" />
              {{ planifying ? 'Envoi en cours...' : "Envoyer l'invitation" }}
            </button>
          </div>

        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import { VideoIcon } from 'lucide-vue-next'
import { planifierEntretien } from '../../services/entretienService'
import { useNotificationStore } from '../../stores/notification'

export default {
  name: 'CandidateInterviewModal',
  components: { VideoIcon },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    candidate: {
      type: Object,
      default: null
    }
  },
  emits: ['update:modelValue'],
  setup() {
    const ns = useNotificationStore()
    const toast = {
      success: (m) => ns.addToast({ type: 'success', message: m }),
      error:   (m) => ns.addToast({ type: 'error',   message: m }),
      info:    (m) => ns.addToast({ type: 'info',    message: m })
    }
    return { toast }
  },
  data() {
    return {
      interviewCreneaux: [],
      interviewMessage: '',
      schedulingDone: false,
      planifying: false,
      calMonday: null,
      tenantCalAllowPastSlots: true,
    }
  },
  watch: {
    modelValue(newVal) {
      if (newVal) {
        this.schedulingDone = false
        this.interviewCreneaux = []
        this.interviewMessage = ''
        this.calMonday = this.getCalMonday(new Date())
      }
    }
  },
  computed: {
    calWeekDays() {
      if (!this.calMonday) return []
      const today = new Date(); today.setHours(0, 0, 0, 0)
      return Array.from({ length: 7 }, (_, i) => {
        const d = new Date(this.calMonday)
        d.setDate(this.calMonday.getDate() + i)
        return {
          iso: this.toLocalDateIso(d),
          name: d.toLocaleDateString('fr-FR', { weekday: 'short' }),
          num: d.getDate(),
          isToday: d.toDateString() === today.toDateString()
        }
      })
    },
    calWeekLabel() {
      if (!this.calMonday) return ''
      const end = new Date(this.calMonday); end.setDate(end.getDate() + 6)
      const o = { day: 'numeric', month: 'short' }
      return `${this.calMonday.toLocaleDateString('fr-FR', o)} – ${end.toLocaleDateString('fr-FR', o)}`
    },
    calTimeSlots() {
      const slots = []
      for (let h = 0; h < 24; h++) {
        for (let m = 0; m < 60; m += 15) {
          slots.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`)
        }
      }
      return slots
    }
  },
  methods: {
    closeModal() {
      this.$emit('update:modelValue', false)
      this.schedulingDone = false
      this.interviewCreneaux = []
    },
    getCalMonday(d) {
      const day = new Date(d); day.setHours(0,0,0,0)
      const dow = (day.getDay() + 6) % 7
      day.setDate(day.getDate() - dow)
      return day
    },
    calPrevWeek() {
      const d = new Date(this.calMonday); d.setDate(d.getDate() - 7); this.calMonday = d
    },
    calNextWeek() {
      const d = new Date(this.calMonday); d.setDate(d.getDate() + 7); this.calMonday = d
    },
    toLocalDateIso(d) {
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    },
    isSlotPast(dayIso, time) {
      if (import.meta.env.VITE_TENANT_CAL_IGNORE_PAST === 'true') return false
      if (this.tenantCalAllowPastSlots) return false
      const [y, mo, da] = dayIso.split('-').map(Number)
      const [h, mi] = time.split(':').map(Number)
      const d = new Date(y, mo - 1, da, h, mi, 0, 0)
      return d <= new Date()
    },
    isSlotSelected(dayIso, time) {
      const [h, mi] = time.split(':').map(Number)
      return this.interviewCreneaux.some(isoStr => {
        const d = new Date(isoStr)
        return this.toLocalDateIso(d) === dayIso && d.getHours() === h && d.getMinutes() === mi
      })
    },
    toggleSlot(dayIso, time) {
      const [y, mo, da] = dayIso.split('-').map(Number)
      const [h, mi] = time.split(':').map(Number)
      const local = new Date(y, mo - 1, da, h, mi, 0, 0)
      const idx = this.interviewCreneaux.findIndex(c => {
        const d = new Date(c)
        return this.toLocalDateIso(d) === dayIso && d.getHours() === h && d.getMinutes() === mi
      })
      if (idx >= 0) this.interviewCreneaux.splice(idx, 1)
      else this.interviewCreneaux.push(local.toISOString())
    },
    formatCreneau(iso) {
      return new Date(iso).toLocaleDateString('fr-FR', {
        weekday: 'short', day: 'numeric', month: 'short',
        hour: '2-digit', minute: '2-digit'
      })
    },
    async handlePlanifier() {
      if (!this.interviewCreneaux.length) return
      this.planifying = true
      try {
        await planifierEntretien(this.candidate.id, this.interviewCreneaux, this.interviewMessage)
        this.schedulingDone = true
        this.toast.success('Invitation sent!')
      } catch {
        this.toast.error("Error sending invitation")
      } finally {
        this.planifying = false
      }
    }
  }
}
</script>

<style scoped>
/* Modal */
.modal-overlay { position:fixed; inset:0; background:rgba(15,23,42,0.5); backdrop-filter:blur(4px); display:flex; align-items:center; justify-content:center; z-index:400; }
.modal-box { background:#fff; border-radius:18px; width:980px; max-width:96vw; max-height:88vh; overflow-y:auto; border:0.5px solid #E8EDF4; }
.modal-header { display:flex; justify-content:space-between; align-items:flex-start; padding:20px 26px; border-bottom:0.5px solid #F1F5F9; position:sticky; top:0; background:#fff; z-index:1; }
.modal-title { font-size:15px; font-weight:700; color:#0F172A; margin:0 0 3px; }
.modal-sub   { font-size:12px; color:#94A3B8; margin:0; }
.sub-name    { color:#475569; font-weight:600; }
.dot-sep     { margin:0 6px; color:#E2E8F0; }
.modal-close { background:#F8FAFC; border:0.5px solid #E2E8F0; cursor:pointer; color:#94A3B8; padding:6px; border-radius:7px; display:flex; }
.modal-close:hover { background:#F1F5F9; color:#475569; }
.modal-body  { padding:22px 26px 28px; }
.modal-fade-enter-active { transition:all 0.2s ease; }
.modal-fade-leave-active { transition:all 0.15s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity:0; }

/* ── Schedule Interview Modal ── */
.modal-interview { width: min(720px, 96vw); max-width: 96vw; }

.interview-section-label { display:flex; align-items:center; gap:6px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8; margin-bottom:10px; }

.creneaux-list { display:flex; flex-direction:column; gap:6px; margin-top:10px; }
.creneau-item { display:flex; align-items:center; gap:8px; padding:7px 12px; background:#F8FAFC; border-radius:8px; border:0.5px solid #E8EDF4; font-size:12px; color:#334155; }
.creneau-item span { flex:1; }

.interview-textarea { width:100%; padding:10px 12px; border:0.5px solid #E2E8F0; border-radius:8px; font-size:13px; font-family:inherit; color:#334155; resize:vertical; box-sizing:border-box; }
.interview-textarea:focus { outline:none; border-color:#1A2B4C; }

.send-invite-btn { display:flex; align-items:center; gap:8px; margin-top:12px; width:100%; padding:12px; background:#1A2B4C; color:#fff; border:none; border-radius:10px; font-size:14px; font-weight:700; cursor:pointer; justify-content:center; font-family:inherit; }
.send-invite-btn:hover:not(:disabled) { background:#243d6a; }
.send-invite-btn:disabled { opacity:0.5; cursor:not-allowed; }

/* Mini calendrier dans modal */
.calendar-hint { font-size:12px; color:#94A3B8; margin:0 0 12px; }
.mini-cal { border:0.5px solid #E8EDF4; border-radius:10px; overflow:hidden; margin-bottom:12px; }
.mini-cal-nav { display:flex; align-items:center; justify-content:space-between; padding:8px 12px; background:#F8FAFC; border-bottom:0.5px solid #E8EDF4; }
.mini-nav-btn { background:none; border:0.5px solid #E2E8F0; border-radius:6px; width:24px; height:24px; cursor:pointer; font-size:16px; color:#475569; display:flex; align-items:center; justify-content:center; }
.mini-nav-btn:hover { background:#F1F5F9; }
.mini-week-label { font-size:12px; font-weight:600; color:#334155; }
.mini-cal-grid { display:grid; grid-template-columns:repeat(7,1fr); }
.mini-day-col { border-right:0.5px solid #F1F5F9; } .mini-day-col:last-child { border-right:none; }
.mini-day-header { padding:6px 4px; text-align:center; background:#F8FAFC; border-bottom:0.5px solid #F1F5F9; }
.mini-day-header.mini-today .mini-day-num { background:#1A2B4C; color:#fff; border-radius:50%; }
.mini-day-name { display:block; font-size:9px; font-weight:700; text-transform:uppercase; color:#94A3B8; letter-spacing:0.05em; }
.mini-day-num  { display:inline-flex; width:20px; height:20px; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#0F172A; }
.mini-slots {
  display:flex; flex-direction:column; gap:2px; padding:4px;
  max-height: min(52vh, 420px);
  overflow-y: auto;
  overscroll-behavior: contain;
}
.mini-slot { width:100%; padding:3px 2px; border-radius:4px; border:0.5px solid #E2E8F0; background:#fff; font-size:8px; font-weight:600; color:#475569; cursor:pointer; font-family:inherit; text-align:center; line-height:1.2; }
.mini-slot:hover:not(:disabled) { border-color:#1A2B4C; background:#EEF2FA; color:#1A2B4C; }
.mini-slot.mini-slot-selected { background:#1A2B4C; color:#fff; border-color:#1A2B4C; }
.mini-slot.mini-slot-past { opacity:0.25; cursor:not-allowed; }
.selected-slots { margin-bottom:8px; }
.selected-slots-label { font-size:11px; font-weight:700; color:#0D9488; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 6px; }
.selected-chips { display:flex; flex-wrap:wrap; gap:4px; }
.slot-chip { display:inline-flex; align-items:center; gap:4px; background:#E1F5EE; color:#085041; border-radius:99px; padding:3px 10px; font-size:11px; font-weight:600; }
.chip-remove { background:none; border:none; cursor:pointer; color:#085041; font-size:14px; padding:0; line-height:1; }
.creneaux-empty { font-size:12px; color:#CBD5E1; font-style:italic; margin:8px 0 0; }

.interview-success { display:flex; flex-direction:column; align-items:center; gap:14px; text-align:center; padding:8px 0; }
.success-circle { width:52px; height:52px; border-radius:50%; background:#E1F5EE; color:#1D9E75; font-size:22px; font-weight:700; display:flex; align-items:center; justify-content:center; }
.interview-success h4 { font-size:16px; font-weight:700; color:#0F172A; margin:0; }
.interview-success p { font-size:13px; color:#475569; margin:0; }

.success-steps { width: 100%; display: flex; flex-direction: column; gap: 8px; margin-top: 10px; background: #F8FAFC; padding: 12px; border-radius: 8px; text-align: left; }
.step-item { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #475569; }
.step-dot { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; font-size: 11px; font-weight: bold; }
.step-dot.done { background: #1D9E75; color: #fff; }
.step-dot.pending { background: #E2E8F0; color: #94A3B8; }
</style>
