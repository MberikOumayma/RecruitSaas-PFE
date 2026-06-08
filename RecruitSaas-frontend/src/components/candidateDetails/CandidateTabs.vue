<template>
  <div class="card tabs-card">
    <div class="tabs-nav">
      <button class="tab-btn" :class="{ active: activeTab === 'skills' }" @click="$emit('update:activeTab', 'skills')">
        <SparklesIcon :size="15" /> Skills & Experience
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'responses' }" @click="$emit('update:activeTab', 'responses')">
        Responses<span v-if="formResponses.length" class="tab-count">{{ formResponses.length }}</span>
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'reviews' }" @click="$emit('update:activeTab', 'reviews')">
        Team Reviews<span v-if="feedbacks.length" class="tab-count">{{ feedbacks.length }}</span>
      </button>
    </div>

    <!-- Tab: Skills & Experience -->
    <div v-if="activeTab === 'skills'" class="tab-body">
      <div class="summary-section-top">
        <div class="summary-header">
          <div class="tab-section-label" style="margin:0">AI Summary</div>
          <button class="tab-action-btn-sm" :disabled="processingSummary" @click="$emit('summarize')">
            <Wand2Icon :size="18" />{{ processingSummary ? 'Generating…' : 'Generate' }}
          </button>
        </div>
        <div v-if="processingSummary" class="loading-inline"><div class="mini-spin"></div> Summarizing…</div>
        <div v-else-if="aiSummary" class="summary-box-improved">
          <div class="summary-content">
            <div class="summary-icon"><BrainIcon :size="18" /></div>
            <div class="summary-text">
              <p v-for="(sentence, i) in parsedSummary" :key="i" class="summary-sentence">{{ sentence }}</p>
            </div>
          </div>
        </div>
        <div v-else class="summary-empty">
          <Wand2Icon :size="20" class="empty-icon-sm" />
          <p> Click "Generate" to create an AI-powered summary of this candidate's profile.</p>
        </div>
      </div>

      <div class="three-col" style="margin-top:18px;">
        <div>
          <div class="section-header-row">
            <div class="tab-section-label" style="margin:0">Skills</div>
            <button class="tab-action-btn-sm" :disabled="processingSkills" @click="$emit('extract-skills')">
              <SparklesIcon :size="18" />{{ processingSkills ? '…' : 'Extract' }}
            </button>
          </div>
          <div v-if="processingSkills" class="loading-inline"><div class="mini-spin"></div> Extracting…</div>
          <div v-else-if="extractedSkills.length" class="skills-tags" style="margin-top:10px;">
            <span v-for="(s, i) in extractedSkills" :key="i" class="skill-tag">{{ s }}</span>
          </div>
          <div v-else class="section-empty">
            <SparklesIcon :size="18" class="empty-icon-sm" />
            <p>No skills yet.</p>
          </div>
        </div>

        <div>
          <div class="section-header-row">
            <div class="tab-section-label" style="margin:0">Experience</div>
            <button class="tab-action-btn-sm" :disabled="processingExperience" @click="$emit('extract-experience')">
              <BriefcaseIcon :size="18" />{{ processingExperience ? '…' : 'Extract' }}
            </button>
          </div>
          <div v-if="processingExperience" class="loading-inline"><div class="mini-spin"></div> Extracting…</div>
          <div v-else-if="extractedExperiences.length" class="tl" style="margin-top:10px;">
            <div v-for="(exp, i) in extractedExperiences" :key="i" class="tl-item">
              <div class="tl-left"><div class="tl-dot"></div><div v-if="i < extractedExperiences.length - 1" class="tl-line"></div></div>
              <div class="tl-body">
                <p class="tl-role">{{ exp.role }}</p>
                <div class="tl-row">
                  <span class="tl-co" v-if="exp.entreprise">🏢 {{ exp.entreprise }}</span>
                  <span class="tl-years" v-if="exp.years">📅 {{ exp.years }}</span>
                </div>
                <p class="tl-desc" v-if="exp.summary">{{ exp.summary }}</p>
              </div>
            </div>
          </div>
          <div v-else class="section-empty"><BriefcaseIcon :size="18" class="empty-icon-sm" /><p>No experience yet.</p></div>
        </div>

        <div>
          <div class="section-header-row">
            <div class="tab-section-label" style="margin:0">Certifications</div>
            <button class="tab-action-btn-sm" :disabled="processingCertifications" @click="$emit('extract-certifications')">
              <AwardIcon :size="18" />{{ processingCertifications ? '…' : 'Extract' }}
            </button>
          </div>
          <div v-if="processingCertifications" class="loading-inline"><div class="mini-spin"></div> Extracting…</div>
          <div v-else-if="certifications.length" class="cert-col-list" style="margin-top:10px;">
            <div v-for="(cert, i) in certifications" :key="i" class="cert-col-item">
              <div class="cert-col-icon" :class="certIconClass(cert)"><AwardIcon :size="12" /></div>
              <div class="cert-col-body">
                <p class="cert-col-name">{{ cert.nom }}</p>
                <div class="cert-col-meta">
                  <span class="cert-org" v-if="cert.organisme"><BuildingIcon :size="9" /> {{ cert.organisme }}</span>
                  <span class="cert-year" v-if="cert.annee"><CalendarIcon :size="9" /> {{ cert.annee }}</span>
                </div>
              </div>
              <span class="cert-inline-badge" :class="certBadgeClass(cert)">{{ certLabel(cert) }}</span>
            </div>
          </div>
          <div v-else class="section-empty"><AwardIcon :size="18" class="empty-icon-sm" /><p>No certifications yet.</p></div>
        </div>
      </div>
    </div>

    <!-- Tab: Responses -->
    <div v-if="activeTab === 'responses'" class="tab-body">
      <div v-if="formResponses.length" class="qa-list">
        <div v-for="(qa, i) in formResponses" :key="i" class="qa-item">
          <div class="qa-q"><span class="qa-idx">Q{{ i + 1 }}</span><span class="qa-question">{{ qa.question }}</span></div>
          <div class="qa-answer">{{ qa.answer }}</div>
        </div>
      </div>
      <div v-else class="section-empty-large">
        <MessageSquareOffIcon :size="28" class="empty-icon-lg" />
        <p class="empty-title">No questionnaire responses</p>
      </div>
    </div>

    <!-- Tab: Expert Reviews -->
    <div v-if="activeTab === 'reviews'" class="tab-body">
      <div v-if="feedbacks.length" class="reviews-list">
        <div v-for="fb in feedbacks" :key="fb.id" class="review-item">
          <img :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(fb.author)}&background=1A2B4C&color=fff&bold=true&size=64`" class="rv-avatar" :alt="fb.author" />
          <div class="rv-body">
            <div class="rv-meta">
              <span class="rv-name">{{ fb.author }}</span>
              <span class="rv-badge">Expert</span>
              <span class="rv-score" v-if="fb.score != null">⭐ {{ fb.score }}/5</span>
              <span class="rv-time">{{ timeAgo(fb.timestamp) }}</span>
            </div>
            <p class="rv-text">{{ fb.comment }}</p>
          </div>
        </div>
      </div>
      <div v-else class="section-empty-large">
        <UsersIcon :size="28" class="empty-icon-lg" />
        <p class="empty-title">No expert reviews yet</p>
      </div>
    </div>
  </div>
</template>

<script>
import {
  SparklesIcon, Wand2Icon, BrainIcon, BriefcaseIcon, AwardIcon, MessageSquareOffIcon, UsersIcon, BuildingIcon, CalendarIcon
} from 'lucide-vue-next'

export default {
  name: 'CandidateTabs',
  components: {
    SparklesIcon, Wand2Icon, BrainIcon, BriefcaseIcon, AwardIcon, MessageSquareOffIcon, UsersIcon, BuildingIcon, CalendarIcon
  },
  props: {
    activeTab: { type: String, required: true },
    formResponses: { type: Array, default: () => [] },
    feedbacks: { type: Array, default: () => [] },
    aiSummary: { type: String, default: '' },
    parsedSummary: { type: Array, default: () => [] },
    extractedSkills: { type: Array, default: () => [] },
    extractedExperiences: { type: Array, default: () => [] },
    certifications: { type: Array, default: () => [] },
    processingSummary: { type: Boolean, default: false },
    processingSkills: { type: Boolean, default: false },
    processingExperience: { type: Boolean, default: false },
    processingCertifications: { type: Boolean, default: false }
  },
  methods: {
    timeAgo(d) {
      if (!d) return ''; const diff = Date.now() - new Date(d).getTime()
      if (diff < 60000) return 'Just now'; if (diff < 3600000) return `${Math.floor(diff/60000)}m ago`
      if (diff < 86400000) return `${Math.floor(diff/3600000)}h ago`; return `${Math.floor(diff/86400000)}d ago`
    },
    isCertif(cert) {
      if (cert.type === 'certification') return true
      if (cert.type === 'diploma') return false
      const nom = (cert.nom || '').toLowerCase()
      const org = (cert.organisme || '').toLowerCase()
      const diplomaKeywords = ['baccalauréat', 'baccalaureat', 'baccalaureate', 'master', 'licence', 'doctorat', 'doctorate', 'phd', 'engineering degree', "bachelor's degree", 'bachelor degree', 'cycle ingénieur', 'cycle ingenieur', 'high school', 'dut', 'bts', 'diplôme national', 'diplome national']
      const certKeywords = ['aws', 'azure', 'google', 'cisco', 'pmp', 'oracle', 'microsoft', 'comptia', 'certified', 'certification', 'certificate', 'nvidia', 'udemy', 'coursera', 'simplilearn', 'linkedin', 'datacamp', 'deeplearn', 'scrum', 'toeic', 'ielts', 'toefl', 'delf', 'flutter', 'blockchain', 'block chain', 'big data', 'deep learning', 'gpu']
      if (diplomaKeywords.some(k => nom.includes(k))) return false
      return certKeywords.some(k => nom.includes(k) || org.includes(k))
    },
    certIconClass(cert)  { return this.isCertif(cert) ? 'cert-icon-certif' : 'cert-icon-diploma' },
    certBadgeClass(cert) { return this.isCertif(cert) ? 'cert-badge-certif' : 'cert-badge-diploma' },
    certLabel(cert)      { return this.isCertif(cert) ? 'Certification' : 'Diploma' }
  }
}
</script>

<style scoped>
.card { background:#fff; border-radius:14px; border:0.5px solid #E8EDF4; overflow:hidden; }
.tabs-nav { display:flex; border-bottom:0.5px solid #F1F5F9; padding:0 12px; overflow-x:auto; }
.tab-btn { display:flex; align-items:center; gap:5px; padding:12px 10px; font-size:14px; font-weight:600; color:#94A3B8; background:none; border:none; cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-0.5px; font-family:inherit; white-space:nowrap; }
.tab-btn.active { color:#0F172A; border-bottom-color:#1A2B4C; }
.tab-count { background:#F1F5F9; color:#475569; font-size:10px; font-weight:700; padding:1px 6px; border-radius:99px; }
.tab-body { padding:20px; }
.tab-section-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:#94A3B8; margin-bottom:10px; }
.section-header-row { display:flex; align-items:center; justify-content:space-between; }
.tab-action-btn-sm { display:inline-flex; align-items:center; gap:5px; padding:4px 10px; border-radius:7px; font-size:13px; font-weight:600; background:#F8FAFC; border:0.5px solid #E2E8F0; color:#0D9488; cursor:pointer; font-family:inherit; }
.tab-action-btn-sm:hover:not(:disabled) { background:#E1F5EE; border-color:#5DCAA5; }
.tab-action-btn-sm:disabled { opacity:0.5; cursor:not-allowed; }

.summary-section-top { background:#F8FAFC; border-radius:12px; padding:16px; border:0.5px solid #E8EDF4; }
.summary-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.summary-box-improved { display:flex; flex-direction:column; gap:10px; }
.summary-content { display:flex; gap:10px; align-items:flex-start; }
.summary-icon { width:28px; height:28px; border-radius:8px; background:linear-gradient(135deg,#1A2B4C,#2d4a8c); color:#B5D4F4; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.summary-text { flex:1; }
.summary-sentence { font-size:13px; color:#334155; line-height:1.65; margin:0 0 6px; }
.summary-empty {  display:flex; flex-direction:column; align-items:center; gap:6px; padding:16px; text-align:center; }
.summary-empty p { font-size:12px; color:#060a0f; margin:0; }
.three-col { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1fr); gap:16px; }
@media(max-width:900px) { .three-col { grid-template-columns:1fr 1fr; } }
@media(max-width:600px) { .three-col { grid-template-columns:1fr; } }

.skills-tags { display:flex; flex-wrap:wrap; gap:6px; }
.skill-tag { padding:4px 10px; border-radius:7px; font-size:12px; font-weight:600; background:#E6F1FB; color:#0C447C; border:0.5px solid #85B7EB; }

.tl { display:flex; flex-direction:column; }
.tl-item { display:flex; gap:10px; padding-bottom:14px; }
.tl-item:last-child { padding-bottom:0; }
.tl-left { display:flex; flex-direction:column; align-items:center; width:14px; flex-shrink:0; }
.tl-dot  { width:9px; height:9px; border-radius:50%; background:#1D9E75; box-shadow:0 0 0 2.5px #E1F5EE; flex-shrink:0; margin-top:3px; }
.tl-line { flex:1; width:1px; background:#E8EDF4; margin:4px 0; }
.tl-body { flex:1; }
.tl-role { font-size:13px; font-weight:700; color:#0F172A; margin:0 0 4px; }
.tl-row  { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:4px; }
.tl-co   { font-size:11px; padding:2px 8px; background:#F1F5F9; border:0.5px solid #E2E8F0; border-radius:4px; color:#475569; }
.tl-years { font-size:11px; padding:2px 8px; background:#E1F5EE; border:0.5px solid #5DCAA5; border-radius:4px; color:#085041; }
.tl-desc { font-size:12px; color:#475569; line-height:1.5; margin:0; }

.cert-col-list { display:flex; flex-direction:column; gap:8px; }
.cert-col-item { display:flex; align-items:flex-start; gap:8px; padding:8px 10px; background:#F8FAFC; border-radius:9px; border:0.5px solid #E8EDF4; }
.cert-col-icon { width:26px; height:26px; border-radius:6px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.cert-col-body { flex:1; min-width:0; }
.cert-col-name { font-size:11px; font-weight:600; color:#0F172A; margin:0 0 3px; line-height:1.4; }
.cert-col-meta { display:flex; gap:6px; flex-wrap:wrap; }
.cert-org, .cert-year { display:inline-flex; align-items:center; gap:3px; font-size:10px; color:#94A3B8; }
.cert-icon-certif { background:linear-gradient(135deg,#FAEEDA,#EF9F27); color:#633806; }
.cert-icon-diploma { background:linear-gradient(135deg,#EEEDFE,#AFA9EC); color:#3C3489; }
.cert-inline-badge { font-size:9px; font-weight:700; padding:2px 7px; border-radius:99px; white-space:nowrap; flex-shrink:0; }
.cert-badge-certif { background:#FAEEDA; color:#633806; }
.cert-badge-diploma { background:#EEEDFE; color:#3C3489; }

.qa-list { display:flex; flex-direction:column; gap:16px; }
.qa-q    { display:flex; gap:8px; align-items:flex-start; margin-bottom:6px; }
.qa-idx  { min-width:22px; height:18px; background:#F1F5F9; border-radius:4px; font-size:11px; font-weight:700; color:#475569; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:1px; }
.qa-question { font-size:13px; font-weight:600; color:#0F172A; }
.qa-answer { margin-left:30px; font-size:13px; color:#475569; line-height:1.6; padding:10px 14px; background:#F8FAFC; border-left:2px solid #1A2B4C; border-radius:0 8px 8px 0; }

.reviews-list { display:flex; flex-direction:column; gap:0; }
.review-item { display:flex; gap:10px; padding:12px 0; border-bottom:0.5px solid #F8FAFC; }
.review-item:last-of-type { border-bottom:none; }
.rv-avatar { width:30px; height:30px; border-radius:8px; object-fit:cover; flex-shrink:0; }
.rv-body { flex:1; }
.rv-meta { display:flex; align-items:center; gap:7px; margin-bottom:5px; flex-wrap:wrap; }
.rv-name  { font-size:13px; font-weight:600; color:#0F172A; }
.rv-badge { font-size:10px; padding:2px 6px; background:#EEEDFE; color:#3C3489; border-radius:4px; font-weight:700; }
.rv-score { font-size:11px; font-weight:700; color:#EF9F27; background:#FAEEDA; padding:2px 7px; border-radius:4px; }
.rv-time  { font-size:11px; color:#CBD5E1; margin-left:auto; }
.rv-text  { font-size:13px; color:#475569; line-height:1.5; }

.section-empty { display:flex; flex-direction:column; align-items:center; gap:6px; padding:16px 0; }
.section-empty p { font-size:12px; color:#010102; margin:0; }
.section-empty-large { display:flex; flex-direction:column; align-items:center; gap:8px; padding:32px; text-align:center; }
.empty-icon-sm { color:#113961; } .empty-icon-lg { color:#1a4a88; }
.empty-title { font-size:14px; font-weight:600; color:#94A3B8; margin:0; }

.mini-spin { width:13px; height:13px; border:2px solid #E2E8F0; border-top-color:#454a83; border-radius:50%; animation:spin 0.6s linear infinite; flex-shrink:0; }
@keyframes spin { to { transform:rotate(360deg); } }
.loading-inline { display:flex; align-items:center; gap:7px; font-size:12px; color:#94A3B8; padding:8px 0; }
</style>
