<template>
  <div style="display:flex; min-height:100vh; background:#F0F2F7;">
    <AppSidebar />
    <main class="main-content">
      <GlobalHeader title="Interview Calendar" />

      <div class="cal-wrap">

        <!-- Toolbar -->
        <div class="toolbar">
          <div class="toolbar-left">
            <button class="btn-today" @click="goToday">Today</button>
            <div class="nav-arrows">
              <button class="nav-btn" @click="prev">&#8249;</button>
              <button class="nav-btn" @click="next">&#8250;</button>
            </div>
            <span class="week-label">{{ view === 'week' ? weekLabel : monthLabel }}</span>
          </div>
          <div class="toolbar-right">
            <div class="offre-filter" v-if="offres.length > 1">
              <select class="offre-select" v-model="filtreOffreId">
                <option :value="null">All job offers</option>
                <option v-for="o in offres" :key="o.titre" :value="o.titre">{{ o.titre }}</option>
              </select>
            </div>
            <div class="period-btns">
              <button class="period-btn" :class="{ active: view === 'week' }"  @click="view = 'week'">Week</button>
              <button class="period-btn" :class="{ active: view === 'month' }" @click="view = 'month'">Month</button>
            </div>
          </div>
        </div>

        <!-- Stats pills -->
        <div class="stat-pills">
          <span class="stat-pill pill-blue">{{ counts.total }} interview{{ counts.total !== 1 ? 's' : '' }}</span>
          <span class="stat-pill pill-teal">{{ counts.planifie }} scheduled</span>
          <span class="stat-pill pill-amber">{{ counts.attente }} pending</span>
          <span class="stat-pill pill-green">{{ counts.termine }} completed</span>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="center-state">
          <div class="spinner"></div><p>Loading...</p>
        </div>

        <!-- VUE SEMAINE -->
        <div v-else-if="view === 'week'" class="week-view">
          <!-- Header jours -->
          <div class="week-header">
            <div v-for="day in weekDays" :key="day.iso" class="wh-cell" :class="{ 'wh-today': day.isToday }">
              <span class="wh-name">{{ day.name }}</span>
              <span class="wh-num" :class="{ 'wh-num-today': day.isToday }">{{ day.num }}</span>
            </div>
          </div>

          <!-- Corps -->
          <div class="week-body">
            <div v-for="day in weekDays" :key="day.iso" class="wb-col" :class="{ 'wb-today': day.isToday }">
              <!-- Entretiens ce jour -->
              <div
                v-for="e in eventsByDay[day.iso]"
                :key="e.id"
                class="event-card"
                :class="eventClass(e.statut)"
                @click="openDetail(e)"
              >
                <div class="ev-bar" :class="barClass(e.statut)"></div>
                <div class="ev-body">
                  <p class="ev-time">{{ formatTime(e.dateScheduled) }}</p>
                  <p class="ev-name">{{ e.nomCandidat }}</p>
                  <p class="ev-offre">{{ truncate(e.titreOffre, 18) }}</p>
                  <span class="ev-badge" :class="statusClass(e.statut)">{{ statusLabel(e.statut) }}</span>
                </div>
              </div>
              <!-- Colonne vide -->
              <div v-if="!eventsByDay[day.iso] || !eventsByDay[day.iso].length" class="wb-empty"></div>
            </div>
          </div>

          <!-- En attente (sans date) -->
          <div v-if="enAttente.length" class="pending-bar">
            <span class="pending-label">⏳ Awaiting confirmation:</span>
            <span v-for="e in enAttente" :key="e.id" class="pending-chip" @click="openDetail(e)">
              {{ e.nomCandidat }} · {{ truncate(e.titreOffre, 16) }}
            </span>
          </div>
        </div>

        <!-- VUE MOIS -->
        <div v-else class="month-view">
          <div class="month-header">
            <div v-for="d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']" :key="d" class="mh-cell">{{ d }}</div>
          </div>
          <div class="month-body">
            <div v-for="cell in monthCells" :key="cell.iso" class="mc-cell"
              :class="{ 'mc-today': cell.isToday, 'mc-other': !cell.currentMonth }">
              <span class="mc-num">{{ cell.day }}</span>
              <div class="mc-events">
                <div v-for="e in cell.events" :key="e.id"
                  class="mc-event" :class="eventClass(e.statut)"
                  @click="openDetail(e)">
                  {{ formatTime(e.dateScheduled) }} {{ truncate(e.nomCandidat, 10) }}
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Modal -->
      <transition name="fade">
        <div v-if="selected" class="modal-overlay" @click.self="selected = null">
          <div class="modal-box">
            <div class="modal-header">
              <div class="modal-avatar">{{ initiales(selected.nomCandidat) }}</div>
              <div>
                <h3 class="modal-name">{{ selected.nomCandidat }}</h3>
                <p class="modal-offre">{{ selected.titreOffre }}</p>
              </div>
              <button class="modal-close" @click="selected = null">✕</button>
            </div>
            <div class="modal-body">
              <div class="modal-row">
                <span class="modal-lbl">Date</span>
                <span class="modal-val">{{ formatDateFull(selected.dateScheduled) }}</span>
              </div>
              <div class="modal-row">
                <span class="modal-lbl">Status</span>
                <span class="status-pill" :class="statusClass(selected.statut)">{{ statusLabel(selected.statut) }}</span>
              </div>
              <div v-if="selected.score" class="modal-row">
                <span class="modal-lbl">AI score</span>
                <span class="modal-val" :style="{ color: scoreColor(selected.score) }">{{ Math.round(selected.score) }}/100</span>
              </div>
            </div>
            <div class="modal-footer">
              
              <button v-if="['LienEnvoye','Planifie'].includes(selected.statut)" class="mbtn mbtn-cancel" @click="annuler(selected)">Cancel</button>
              <button v-if="selected?.statut === 'Termine' && selected?.rapportIA" class="mbtn mbtn-rapport" @click="ouvrirRapport()">📊 View report</button>
              <button class="mbtn mbtn-view" @click="voirCandidat(selected)">View candidate →</button>
            </div>
          </div>
        </div>
      </transition>

    <!-- Modal Rapport -->
    <RapportEntretien
      v-if="showRapport && rapportData"
      :rapport="rapportData"
      :questions="rapportQuestions"
      @close="showRapport = false"
    />

    </main>
  </div>
</template>

<script>
import AppSidebar   from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import { getEntretiens, annulerEntretien } from '../../services/entretienService'
import { useNotificationStore } from '../../stores/notification'
import {
  formatRecruiterDateTime,
  formatRecruiterTime,
  interviewStatusLabel,
  interviewMentionLabel,
} from '../../utils/recruiterI18n.js'
import { authStore } from '../../stores/auth'

import RapportEntretien from '../../components/RapportEntretien.vue'

export default {
  name: 'InterviewsCalendar',
  components: { AppSidebar, GlobalHeader, RapportEntretien },
  setup() {
    const ns = useNotificationStore()
    return {
      toast: {
        success: m => ns.addToast({ type: 'success', message: m }),
        error:   m => ns.addToast({ type: 'error',   message: m })
      }
    }
  },
  data() {
    const today = new Date()
    return {
      entretiens:    [],
      loading:       true,
      view:          'week',
      currentMonday: this.getMonday(today),
      currentMonth:  new Date(today.getFullYear(), today.getMonth(), 1),
      selected:      null,
      showRapport:   false,
      rapportData:   null,
      rapportQuestions: [],
      filtreOffreId: null,
      offres:        []
    }
  },
  computed: {
    filteredEntretiens() {
      if (!this.filtreOffreId) return this.entretiens
      return this.entretiens.filter(e => e.titreOffre === this.filtreOffreId)
    },
    counts() {
      return {
        total:   this.filteredEntretiens.length,
        planifie: this.filteredEntretiens.filter(e => ['Planifie','EnCours'].includes(e.statut)).length,
        attente:  this.enAttente.length,
        termine:  this.filteredEntretiens.filter(e => e.statut === 'Termine').length
      }
    },
    enAttente() {
      return this.filteredEntretiens.filter(e => e.statut === 'LienEnvoye' && !e.dateScheduled)
    },
    weekDays() {
      const today = new Date(); today.setHours(0,0,0,0)
      return Array.from({ length: 7 }, (_, i) => {
        const d = new Date(this.currentMonday)
        d.setDate(this.currentMonday.getDate() + i)
        return {
          iso:     this.localIso(d),
          name:    d.toLocaleDateString('en-US', { weekday: 'short' }),
          num:     d.getDate(),
          isToday: d.toDateString() === today.toDateString()
        }
      })
    },
    weekLabel() {
      const end = new Date(this.currentMonday); end.setDate(end.getDate() + 6)
      const o = { day: 'numeric', month: 'short' }
      return `${this.currentMonday.toLocaleDateString('en-US', o)} – ${end.toLocaleDateString('en-US', o)} ${end.getFullYear()}`
    },
    monthLabel() {
      return this.currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    },
    eventsByDay() {
      const map = {}
      this.filteredEntretiens
        .filter(e => e.dateScheduled)
        .forEach(e => {
          const iso = this.localIso(new Date(e.dateScheduled))
          if (!map[iso]) map[iso] = []
          map[iso].push(e)
        })
      return map
    },
    monthCells() {
      const cells = []
      const today = new Date(); today.setHours(0,0,0,0)
      const year  = this.currentMonth.getFullYear()
      const month = this.currentMonth.getMonth()
      const first = new Date(year, month, 1)
      const startDow = (first.getDay() + 6) % 7
      const start = new Date(first); start.setDate(first.getDate() - startDow)
      for (let i = 0; i < 42; i++) {
        const d = new Date(start); d.setDate(start.getDate() + i)
        const iso = this.localIso(d)
        cells.push({
          iso, day: d.getDate(),
          isToday:      d.toDateString() === today.toDateString(),
          currentMonth: d.getMonth() === month,
          events:       (this.eventsByDay[iso] || [])
        })
      }
      return cells
    }
  },
  async created() {
    await this.load()
    this._interval = setInterval(this.load, 30000)
  },
  beforeUnmount() { clearInterval(this._interval) },
  methods: {
    async load() {
      try {
        const r = await getEntretiens()
        this.entretiens = r.data || []
        // Extrait les offres distinctes pour le filtre
        const seen = new Set()
        this.offres = this.entretiens
          .filter(e => e.titreOffre && !seen.has(e.titreOffre) && seen.add(e.titreOffre))
          .map(e => ({ titre: e.titreOffre }))
      }
      catch { this.toast.error('Failed to load interviews') }
      finally { this.loading = false }
    },
    getMonday(d) {
      const day = new Date(d); day.setHours(0,0,0,0)
      const dow = (day.getDay() + 6) % 7
      day.setDate(day.getDate() - dow); return day
    },
    goToday() {
      this.currentMonday = this.getMonday(new Date())
      this.currentMonth  = new Date(new Date().getFullYear(), new Date().getMonth(), 1)
    },
    prev() {
      if (this.view === 'week') { const d = new Date(this.currentMonday); d.setDate(d.getDate()-7); this.currentMonday = d }
      else { const d = new Date(this.currentMonth); d.setMonth(d.getMonth()-1); this.currentMonth = d }
    },
    next() {
      if (this.view === 'week') { const d = new Date(this.currentMonday); d.setDate(d.getDate()+7); this.currentMonday = d }
      else { const d = new Date(this.currentMonth); d.setMonth(d.getMonth()+1); this.currentMonth = d }
    },
    openDetail(e) {
      this.selected = e
      this.rapportData = null
      this.rapportQuestions = []

      if (e.statut === 'Termine') {
        // rapportIA peut être un objet ou une string JSON
        let rapport = null
        if (e.rapportIA) {
          try {
            rapport = typeof e.rapportIA === 'string' ? JSON.parse(e.rapportIA) : e.rapportIA
          } catch { rapport = null }
        }

        // Construit un rapport minimal si null ou parsing échoué
        this.rapportData = {
          nomCandidat:           e.nomCandidat  || '',
          titreOffre:            e.titreOffre   || '',
          scoreGlobal:           rapport?.scoreGlobal  ?? e.score ?? 0,
          mention:               rapport?.mention       ?? this.scoreMention(e.score),
          recommandation:        rapport?.recommandation ?? '',
          resume_executif:       rapport?.resume_executif ?? '',
          points_forts:          rapport?.points_forts ?? [],
          points_amelioration:   rapport?.points_amelioration ?? [],
          competences_evaluees:  rapport?.competences_evaluees ?? [],
          commentaire_recruteur: rapport?.commentaire_recruteur ?? '',
          dureeMinutes:          rapport?.dureeMinutes ?? e.dureeMinutes,
          nbQuestionsRepondues:  rapport?.nbQuestionsRepondues ?? 0,
          verificationFacialeOk: e.verificationFacialeOk ?? false,
          nbChangementsOnglet:   e.nbChangementsOnglet ?? 0,
          fraudDetection:        rapport?.fraudDetection ?? null,
        }

        // Questions
        if (e.questionsIA) {
          try {
            this.rapportQuestions = typeof e.questionsIA === 'string'
              ? JSON.parse(e.questionsIA) : e.questionsIA
          } catch { this.rapportQuestions = [] }
        }
      }
    },
    ouvrirRapport() {
      if (this.rapportData) { this.showRapport = true; this.selected = null }
    },
    voirCandidat(e) {
      const isExpert = authStore.user?.role === 'Expert'
      if (isExpert) {
        this.$router.push({ path: '/expert/candidates', query: { candidatId: e.candidatureId } })
      } else {
        this.$router.push(`/recruiter/candidates/${e.candidatureId}`)
      }
      this.selected = null
    },
    async annuler(e) {
      if (!confirm(`Cancel the interview with ${e.nomCandidat}?`)) return
      try { await annulerEntretien(e.id); e.statut = 'Annule'; this.selected = null; this.toast.success('Cancelled') }
      catch { this.toast.error('Something went wrong') }
    },
    rejoindre(e) { window.open(`/interview/${e.lienToken}/rejoindre`, '_blank') },
    localIso(d) {
      return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    },
    formatTime(d)    { if (!d) return '—'; return formatRecruiterTime(d) },
    formatDateFull(d) { if (!d) return '—'; return formatRecruiterDateTime(d) },
    initiales(n)  { if (!n) return '?'; return n.split(' ').map(p=>p[0]).join('').toUpperCase().slice(0,2) },
    truncate(s,n) { return s && s.length > n ? s.slice(0,n)+'…' : s||'—' },
    statusLabel(s) { return interviewStatusLabel(s) },
    statusClass(s) { return { LienEnvoye:'st-wait', Planifie:'st-ok', EnCours:'st-live', Termine:'st-done', Annule:'st-cancel' }[s]||'' },
    eventClass(s)  { return { LienEnvoye:'ev-wait', Planifie:'ev-ok', EnCours:'ev-live', Termine:'ev-done', Annule:'ev-cancel' }[s]||'' },
    barClass(s)    { return { LienEnvoye:'bar-wait', Planifie:'bar-ok', EnCours:'bar-live', Termine:'bar-done', Annule:'bar-cancel' }[s]||'' },
    scoreColor(s)  { return s >= 80 ? '#1D9E75' : s >= 50 ? '#EF9F27' : '#E24B4A' },
    scoreMention(s) {
      if (!s) return ''
      if (s >= 85) return interviewMentionLabel('Excellent')
      if (s >= 70) return interviewMentionLabel('Bien')
      if (s >= 50) return interviewMentionLabel('Satisfaisant')
      return interviewMentionLabel('Insuffisant')
    }
  }
}
</script>

<style scoped>
* { box-sizing: border-box; }
.main-content { flex:1; display:flex; flex-direction:column; font-family:'DM Sans',system-ui,sans-serif; background:#F0F2F7; overflow:hidden; }
.cal-wrap { flex:1; overflow-y:auto; padding:20px 24px; }

/* Toolbar */
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:10px; }
.toolbar-left { display:flex; align-items:center; gap:10px; }
.btn-today { padding:7px 16px; background:#1A2B4C; color:#fff; border:none; border-radius:8px; font-size:13px; font-weight:700; cursor:pointer; font-family:inherit; }
.btn-today:hover { background:#243d6a; }
.nav-arrows { display:flex; gap:2px; }
.nav-btn { width:30px; height:30px; background:#fff; border:0.5px solid #E2E8F0; border-radius:8px; font-size:18px; cursor:pointer; display:flex; align-items:center; justify-content:center; color:#475569; }
.nav-btn:hover { background:#F1F5F9; }
.week-label { font-size:14px; font-weight:700; color:#0F172A; }
.period-btns { display:flex; background:#E2E8F0; border-radius:9px; padding:3px; }
.period-btn { padding:6px 16px; border-radius:7px; border:none; font-size:13px; font-weight:600; cursor:pointer; font-family:inherit; color:#64748b; background:transparent; }
.period-btn.active { background:#fff; color:#1A2B4C; box-shadow:0 1px 3px rgba(0,0,0,0.1); }

/* Stats */
.stat-pills { display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; }
.stat-pill { font-size:12px; font-weight:700; padding:4px 12px; border-radius:99px; }
.pill-blue  { background:#E6F1FB; color:#0C447C; }
.pill-teal  { background:#E1F5EE; color:#085041; }
.pill-amber { background:#FAEEDA; color:#633806; }
.pill-green { background:#EAF3DE; color:#27500A; }

/* Center state */
.center-state { display:flex; flex-direction:column; align-items:center; padding:60px 0; gap:10px; color:#94A3B8; }
.spinner { width:28px; height:28px; border:2.5px solid #E2E8F0; border-top-color:#1A2B4C; border-radius:50%; animation:spin 0.7s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }

/* Week view */
.week-view { background:#fff; border-radius:14px; border:0.5px solid #E8EDF4; overflow:hidden; }

.week-header { display:grid; grid-template-columns:repeat(7,1fr); background:#F8FAFC; border-bottom:1px solid #E8EDF4; }
.wh-cell { padding:12px 8px; text-align:center; border-right:0.5px solid #F1F5F9; }
.wh-cell:last-child { border-right:none; }
.wh-cell.wh-today { background:rgba(26,43,76,0.04); }
.wh-name { display:block; font-size:10px; font-weight:700; text-transform:uppercase; color:#94A3B8; letter-spacing:0.06em; margin-bottom:4px; }
.wh-num  { display:inline-flex; width:28px; height:28px; align-items:center; justify-content:center; font-size:14px; font-weight:700; color:#0F172A; border-radius:50%; }
.wh-num-today { background:#1A2B4C; color:#fff; }

.week-body { display:grid; grid-template-columns:repeat(7,1fr); min-height:200px; }
.wb-col { border-right:0.5px solid #F1F5F9; padding:8px 6px; display:flex; flex-direction:column; gap:6px; }
.wb-col:last-child { border-right:none; }
.wb-col.wb-today { background:rgba(26,43,76,0.02); }
.wb-empty { flex:1; }

/* Event cards */
.event-card { border-radius:8px; padding:8px; cursor:pointer; display:flex; gap:0; position:relative; overflow:hidden; }
.event-card:hover { opacity:0.85; transform:translateY(-1px); }
.ev-bar  { width:3px; border-radius:2px; flex-shrink:0; margin-right:7px; }
.ev-body { flex:1; min-width:0; }
.ev-time  { font-size:12px; font-weight:800; margin:0 0 2px; }
.ev-name  { font-size:12px; font-weight:700; margin:0 0 1px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.ev-offre { font-size:10px; margin:0 0 4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.ev-badge { font-size:9px; font-weight:700; padding:1px 6px; border-radius:99px; }

.ev-ok   { background:#E6F1FB; } .ev-ok .ev-time,.ev-ok .ev-name { color:#0C447C; } .ev-ok .ev-offre { color:#378ADD; }
.ev-live { background:#FCEBEB; } .ev-live .ev-time,.ev-live .ev-name { color:#791F1F; } .ev-live .ev-offre { color:#E24B4A; }
.ev-done { background:#EAF3DE; } .ev-done .ev-time,.ev-done .ev-name { color:#27500A; } .ev-done .ev-offre { color:#639922; }
.ev-wait { background:#FAEEDA; } .ev-wait .ev-time,.ev-wait .ev-name { color:#633806; } .ev-wait .ev-offre { color:#BA7517; }
.ev-cancel { background:#F1F5F9; opacity:0.6; } .ev-cancel .ev-time,.ev-cancel .ev-name { color:#64748B; }

.bar-ok { background:#1A2B4C; } .bar-live { background:#E24B4A; animation:pulse 1.5s infinite; }
.bar-done { background:#1D9E75; } .bar-wait { background:#EF9F27; } .bar-cancel { background:#CBD5E1; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

.st-wait  { background:#FAEEDA; color:#633806; }
.st-ok    { background:#E6F1FB; color:#0C447C; }
.st-live  { background:#FCEBEB; color:#791F1F; }
.st-done  { background:#EAF3DE; color:#27500A; }
.st-cancel { background:#F1F5F9; color:#94A3B8; }

/* Pending bar */
.pending-bar { display:flex; align-items:center; gap:8px; padding:10px 16px; background:#FFF7ED; border-top:0.5px solid #FED7AA; flex-wrap:wrap; }
.pending-label { font-size:12px; font-weight:700; color:#C2410C; white-space:nowrap; }
.pending-chip  { font-size:11px; font-weight:600; padding:3px 10px; background:#FFEDD5; color:#9A3412; border-radius:99px; cursor:pointer; }
.pending-chip:hover { background:#FED7AA; }

/* Month view */
.month-view { background:#fff; border-radius:14px; border:0.5px solid #E8EDF4; overflow:hidden; }
.month-header { display:grid; grid-template-columns:repeat(7,1fr); background:#F8FAFC; border-bottom:1px solid #E8EDF4; }
.mh-cell { padding:10px; text-align:center; font-size:11px; font-weight:700; text-transform:uppercase; color:#94A3B8; letter-spacing:0.06em; }
.month-body { display:grid; grid-template-columns:repeat(7,1fr); }
.mc-cell { min-height:90px; border-right:0.5px solid #F1F5F9; border-bottom:0.5px solid #F1F5F9; padding:6px; }
.mc-other { background:#FAFAFA; }
.mc-today { background:rgba(26,43,76,0.03); }
.mc-num   { font-size:12px; font-weight:700; color:#475569; display:inline-flex; width:22px; height:22px; align-items:center; justify-content:center; border-radius:50%; margin-bottom:4px; }
.mc-today .mc-num { background:#1A2B4C; color:#fff; }
.mc-events { display:flex; flex-direction:column; gap:2px; }
.mc-event  { font-size:10px; font-weight:600; padding:2px 5px; border-radius:4px; cursor:pointer; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* Modal */
.modal-overlay { position:fixed; inset:0; background:rgba(15,23,42,0.5); backdrop-filter:blur(4px); display:flex; align-items:center; justify-content:center; z-index:500; }
.modal-box { background:#fff; border-radius:16px; width:400px; max-width:95vw; border:0.5px solid #E8EDF4; }
.modal-header { display:flex; align-items:center; gap:12px; padding:20px; border-bottom:0.5px solid #F1F5F9; }
.modal-avatar { width:40px; height:40px; border-radius:50%; background:#1A2B4C; color:#B5D4F4; display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:700; flex-shrink:0; }
.modal-name  { font-size:15px; font-weight:700; color:#0F172A; margin:0; }
.modal-offre { font-size:12px; color:#64748B; margin:2px 0 0; }
.modal-close { margin-left:auto; background:#F1F5F9; border:none; width:26px; height:26px; border-radius:7px; cursor:pointer; font-size:13px; color:#475569; }
.modal-body  { padding:16px 20px; display:flex; flex-direction:column; gap:10px; }
.modal-row   { display:flex; align-items:center; justify-content:space-between; }
.modal-lbl   { font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; }
.modal-val   { font-size:14px; font-weight:600; color:#0F172A; }
.status-pill { font-size:11px; font-weight:700; padding:3px 10px; border-radius:99px; }
.modal-footer { display:flex; gap:8px; padding:12px 20px; background:#F8FAFC; border-top:0.5px solid #F1F5F9; flex-wrap:wrap; }
.mbtn { padding:7px 14px; border-radius:8px; font-size:12px; font-weight:700; cursor:pointer; border:1px solid transparent; font-family:inherit; }
.mbtn-join   { background:#1A2B4C; color:#fff; } .mbtn-join:hover { background:#243d6a; }
.mbtn-cancel { background:#FCEBEB; color:#dc2626; border-color:#FCA5A5; }
.mbtn-view   { background:#F8FAFC; color:#475569; border-color:#E2E8F0; }
.mbtn-rapport { background:#EEF2FF; color:#3730A3; border-color:#C7D2FE; }

.fade-enter-active { transition:opacity 0.2s; } .fade-leave-active { transition:opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity:0; }
.offre-filter { display:flex; align-items:center; }
.offre-select { padding:7px 12px; border:0.5px solid #E2E8F0; border-radius:8px; font-size:13px; font-family:inherit; color:#334155; background:#fff; cursor:pointer; min-width:180px; max-width:260px; }
.offre-select:focus { outline:none; border-color:#1A2B4C; }
</style>