<template>
  <div class="card hero-card">
    <div class="hero-banner"></div>
    <div class="hero-body">
      <div class="hero-avatar">{{ initiales(candidate.nomCandidat) }}</div>
      <div class="hero-info">
        <h2 class="hero-name">{{ candidate.nomCandidat }}</h2>
        <p class="hero-email">{{ candidate.emailCandidat }}</p>
        <div class="hero-chips">
          <span class="chip chip-blue"><BriefcaseIcon :size="11" />{{ candidate.titreOffre }}</span>
          <span class="chip chip-neutral"><BuildingIcon :size="11" />{{ candidate.nomEntreprise }}</span>
          <span class="chip chip-green" v-if="candidate.creeLe"><CalendarIcon :size="11" />Applied {{ formatDate(candidate.creeLe) }}</span>
          <span class="chip" :class="statusChipClass(candidate.statut)"><span class="chip-dot"></span>{{ candidate.statut }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { BriefcaseIcon, BuildingIcon, CalendarIcon } from 'lucide-vue-next'

export default {
  name: 'CandidateHero',
  components: {
    BriefcaseIcon, BuildingIcon, CalendarIcon
  },
  props: {
    candidate: {
      type: Object,
      required: true
    }
  },
  methods: {
    initiales(nom) { if (!nom) return '?'; return nom.split(' ').map(p => p[0]).join('').toUpperCase().slice(0,2) },
    formatDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' }) },
    statusChipClass(s) { return { 'Nouvelle':'ch-blue','En cours':'ch-amber','Acceptée':'ch-green','Refusée':'ch-red','Présélectionné':'ch-purple','Entretien':'ch-teal' }[s] || 'ch-neutral' }
  }
}
</script>

<style scoped>
.card { background:#fff; border-radius:14px; border:0.5px solid #E8EDF4; overflow:hidden; }
.hero-banner { height:48px; background:#1A2B4C; }
.hero-body   { display:flex; gap:14px; align-items:flex-end; padding:0 20px 18px; margin-top:-24px; }
.hero-avatar { width:48px; height:48px; border-radius:10px; background:#2d4a8c; color:#B5D4F4; display:flex; align-items:center; justify-content:center; font-size:15px; font-weight:600; flex-shrink:0; border:2.5px solid #fff; }
.hero-info { flex:1; padding-top:28px; }
.hero-name  { font-size:17px; font-weight:700; color:#0F172A; margin:0; }
.hero-email { font-size:12px; color:#64748B; margin:2px 0 0; }
.hero-chips { display:flex; gap:6px; flex-wrap:wrap; margin-top:10px; }
.chip { display:inline-flex; align-items:center; gap:4px; padding:4px 9px; border-radius:7px; font-size:12px; font-weight:600; border:0.5px solid #E2E8F0; background:#F1F5F9; color:#475569; }
.chip-dot { width:5px; height:5px; border-radius:50%; background:currentColor; }
.ch-blue   { background:#E6F1FB; color:#0C447C; border-color:#85B7EB; }
.ch-green  { background:#EAF3DE; color:#27500A; border-color:#97C459; }
.ch-amber  { background:#FAEEDA; color:#633806; border-color:#EF9F27; }
.ch-red    { background:#FCEBEB; color:#791F1F; border-color:#F09595; }
.ch-purple { background:#EEEDFE; color:#3C3489; border-color:#AFA9EC; }
.ch-teal   { background:#E1F5EE; color:#085041; border-color:#5DCAA5; }
.ch-neutral { background:#F1F5F9; color:#475569; border-color:#E2E8F0; }
</style>
