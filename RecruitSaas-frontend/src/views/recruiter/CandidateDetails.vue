<template>
  <div class="page-layout">
    <main class="main-content">
      <GlobalHeader title="Candidate Details" />

      <div class="state-wrap" v-if="loading">
        <div class="state-card"><div class="state-spinner"></div><p>Loading candidate profile…</p></div>
      </div>

      <div class="content-wrap" v-else-if="candidate">
        <div class="top-bar">
          <button class="back-btn" @click="goBack"><ArrowLeftIcon :size="14" />Candidates</button>
          <span class="sep">/</span>
          <span class="current">{{ candidate.nomCandidat }}</span>
        </div>

        <div class="page-grid">
          <div class="left-col">

            <!-- Hero -->
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
                    <span class="chip" :class="statusChipClass(candidate.statut)"><span class="chip-dot"></span>{{ statusLabel(candidate.statut) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Score -->
            <div class="card">
              <div class="score-strip">
                <div class="gauge-wrap">
                  <svg viewBox="0 0 72 44" width="72" height="44">
                    <path d="M6,42 A32,32 0 0,1 66,42" fill="none" stroke="#E1F5EE" stroke-width="6" stroke-linecap="round"/>
                    <path d="M6,42 A32,32 0 0,1 66,42" fill="none" :stroke="gaugeColor" stroke-width="6" stroke-linecap="round" :stroke-dasharray="`${gaugeLength} 101`"/>
                    <text x="36" y="40" text-anchor="middle" font-size="15" font-weight="600" :fill="gaugeColor" font-family="DM Sans, sans-serif">{{ candidate.scoreIA != null ? Math.round(candidate.scoreIA) : '—' }}</text>
                  </svg>
                </div>
                <div class="score-detail">
                  <p class="score-title">Match score — {{ candidate.titreOffre }}</p>
                  <div class="score-bars">
                    <div class="bar-row"><span class="bar-lbl">Technical</span><div class="bar-bg"><div class="bar-fill bar-green" :style="{ width: matchDimBarWidth('technical') }"></div></div><span class="bar-pct">{{ matchDimBarLabel('technical') }}</span></div>
                    <div class="bar-row"><span class="bar-lbl">Experience</span><div class="bar-bg"><div class="bar-fill bar-amber" :style="{ width: matchDimBarWidth('experience') }"></div></div><span class="bar-pct">{{ matchDimBarLabel('experience') }}</span></div>
                    <div class="bar-row"><span class="bar-lbl">Domain fit</span><div class="bar-bg"><div class="bar-fill bar-green" :style="{ width: matchDimBarWidth('domainFit') }"></div></div><span class="bar-pct">{{ matchDimBarLabel('domainFit') }}</span></div>
                  </div>
                  <p v-if="!scoreBreakdown && candidate.scoreIA != null" class="score-breakdown-hint">Run <strong>Recalculate</strong> for breakdown.</p>
                </div>
              </div>
              <div class="score-actions">
                <button class="action-pill" @click="handleRecalculateScore"><RefreshCwIcon :size="12" />Recalculate</button>
              </div>
            </div>

            <!-- Tabs -->
            <div class="card tabs-card">
              <div class="tabs-nav">
                <button class="tab-btn" :class="{ active: activeTab === 'skills' }" @click="activeTab = 'skills'">
                  <SparklesIcon :size="13" /> Skills & Experience
                </button>
                <button class="tab-btn" :class="{ active: activeTab === 'responses' }" @click="activeTab = 'responses'">
                  Responses<span v-if="formResponses.length" class="tab-count">{{ formResponses.length }}</span>
                </button>
                <button class="tab-btn" :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">
                  Expert Reviews<span v-if="feedbacks.length" class="tab-count">{{ feedbacks.length }}</span>
                </button>
              </div>

              <!-- Tab: Skills -->
              <div v-if="activeTab === 'skills'" class="tab-body">
                <div class="summary-section-top">
                  <div class="summary-header">
                    <div class="tab-section-label" style="margin:0">AI Summary</div>
                    <button class="tab-action-btn-sm" :disabled="processingSummary" @click="handleSummarizeCV">
                      <Wand2Icon :size="11" />{{ processingSummary ? 'Generating…' : 'Generate' }}
                    </button>
                  </div>
                  <div v-if="processingSummary" class="loading-inline"><div class="mini-spin"></div> Summarizing…</div>
                  <div v-else-if="aiSummary" class="summary-box-improved">
                    <div class="summary-content">
                      <div class="summary-icon"><BrainIcon :size="16" /></div>
                      <div class="summary-text">
                        <p v-for="(sentence, i) in parsedSummary" :key="i" class="summary-sentence">{{ sentence }}</p>
                      </div>
                    </div>
                    <div class="summary-highlights" v-if="summaryHighlights.length">
                      <span v-for="h in summaryHighlights" :key="h" class="summary-highlight-tag">{{ h }}</span>
                    </div>
                  </div>
                  <div v-else class="summary-empty">
                    <Wand2Icon :size="20" class="empty-icon-sm" />
                    <p>Click "Generate" to create an AI-powered summary.</p>
                  </div>
                </div>

                <div class="three-col" style="margin-top:18px;">
                  <div>
                    <div class="section-header-row">
                      <div class="tab-section-label" style="margin:0">Skills</div>
                      <button class="tab-action-btn-sm" :disabled="processingSkills" @click="handleExtractSkills">
                        <SparklesIcon :size="11" />{{ processingSkills ? '…' : 'Extract' }}
                      </button>
                    </div>
                    <div v-if="processingSkills" class="loading-inline"><div class="mini-spin"></div> Extracting…</div>
                    <div v-else-if="extractedSkills.length" class="skills-tags" style="margin-top:10px;">
                      <span v-for="(s, i) in extractedSkills" :key="i" class="skill-tag">{{ s }}</span>
                    </div>
                    <div v-else class="section-empty"><SparklesIcon :size="18" class="empty-icon-sm" /><p>No skills yet.</p></div>
                  </div>

                  <div>
                    <div class="section-header-row">
                      <div class="tab-section-label" style="margin:0">Experience</div>
                      <button class="tab-action-btn-sm" :disabled="processingExperience" @click="handleExtractExperience">
                        <BriefcaseIcon :size="11" />{{ processingExperience ? '…' : 'Extract' }}
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
                      <button class="tab-action-btn-sm" :disabled="processingCertifications" @click="handleExtractCertifications">
                        <AwardIcon :size="11" />{{ processingCertifications ? '…' : 'Extract' }}
                      </button>
                    </div>
                    <div v-if="processingCertifications" class="loading-inline"><div class="mini-spin"></div> Extracting…</div>
                    <div v-else-if="certifications.length" class="cert-col-list" style="margin-top:10px;">
                      <div v-for="(cert, i) in certifications" :key="i" class="cert-col-item">
                        <div class="cert-col-icon" :class="certIconClass(cert)"><AwardIcon :size="12" /></div>
                        <div class="cert-col-body">
                          <p class="cert-col-name">{{ cert.nom }}</p>
                          <div class="cert-col-meta">
                            <span v-if="cert.organisme" class="cert-org"><BuildingIcon :size="9" /> {{ cert.organisme }}</span>
                            <span v-if="cert.annee" class="cert-year"><CalendarIcon :size="9" /> {{ cert.annee }}</span>
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

            <!-- ✅ AJOUT COLLÈGUE : Quiz Status (score du quiz visible recruteur) -->
            <CandidateQuizStatus
              ref="quizStatus"
              :candidateId="candidateId"
              :candidate="candidate"
            />

          </div>

          <!-- Sidebar -->
          <div class="right-col">
            <div class="sticky-wrap">
              <div class="card stats-card">
                <div class="stats-grid">
                  <div class="stat-box"><span class="stat-num" :style="{ color: gaugeColor }">{{ candidate.scoreIA != null ? Math.round(candidate.scoreIA) : '—' }}</span><span class="stat-lbl">AI Score</span></div>
                </div>
              </div>

              <div class="card">
                <p class="sb-section-title">Pipeline Actions</p>
                <div class="sb-btn-stack">
                  <button v-if="rapportIAData" class="sb-btn sb-rapport" @click="showRapportIA = true">
                    📊 Rapport entretien IA
                  </button>
                  <button class="sb-btn sb-stage" @click="handleMoveStage"><ArrowRightLeftIcon :size="14" /><span>Move to Stage</span></button>
                </div>
              </div>

              <div class="card">
                <p class="sb-section-title">Resume (CV)</p>
                <button class="sb-btn sb-cv" @click="handleViewCV"><FileTextIcon :size="14" /><span>View Original CV</span><ExternalLinkIcon :size="11" class="trail" /></button>
              </div>

              <div class="card">
                <p class="sb-section-title">Application Info</p>
                <div class="info-list">
                  <div class="info-row"><span class="info-lbl"><CalendarIcon :size="11" /> Applied</span><span class="info-val">{{ formatDate(candidate.creeLe) }}</span></div>
                  <div class="info-row"><span class="info-lbl"><GlobeIcon :size="11" /> Source</span><span class="info-pill">Direct</span></div>
                  <div class="info-row">
                    <span class="info-lbl"><UserIcon :size="11" /> Expert(s)</span>
                    <span v-if="assignedExperts.length" class="info-val">{{ assignedExpertsLabel }}</span>
                    <span v-else class="info-na">Unassigned</span>
                  </div>
                  <div class="info-row" v-if="candidate.statut">
                    <span class="info-lbl"><ActivityIcon :size="11" /> Status</span>
                    <span class="status-pill" :class="statusPillClass(candidate.statut)"><span class="s-dot"></span>{{ statusLabel(candidate.statut) }}</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

      <div class="state-wrap" v-else>
        <div class="state-card"><p>Candidate not found.</p><button class="btn-back" @click="goBack">Return to list</button></div>
      </div>

      <!-- Modal Interview avec calendrier -->
      <transition name="modal-fade">
        <div v-if="showInterviewModal" class="modal-overlay" @click.self="showInterviewModal = false">
          <div class="modal-box modal-interview">
            <div class="modal-header">
              <div>
                <h3 class="modal-title">📅 Schedule Interview</h3>
                <p class="modal-sub" v-if="candidate">
                  <span class="sub-name">{{ candidate.nomCandidat }}</span>
                  <span class="dot-sep">·</span>{{ candidate.titreOffre }}
                </p>
              </div>
              <button class="modal-close" @click="showInterviewModal = false; schedulingDone = false; interviewCreneaux = []">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
              </button>
            </div>
            <div class="modal-body">
              <div v-if="schedulingDone" class="interview-success">
                <div class="success-circle">✓</div>
                <h4>Invitation sent!</h4>
                <p>An email was sent to <strong>{{ candidate.emailCandidat }}</strong> with the available time slots.</p>
                <button class="send-invite-btn" @click="showInterviewModal = false; schedulingDone = false" style="margin-top:8px;">Close</button>
              </div>
              <div v-else>
                <p class="calendar-hint">Select available time slots in the calendar below.</p>
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
                        <button v-for="slot in calTimeSlots" :key="day.iso + '-' + slot" class="mini-slot"
                          :class="{ 'mini-slot-selected': isSlotSelected(day.iso, slot), 'mini-slot-past': isSlotPast(day.iso, slot) }"
                          :disabled="isSlotPast(day.iso, slot)" @click="toggleSlot(day.iso, slot)">{{ slot }}</button>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-if="interviewCreneaux.length" class="selected-slots">
                  <p class="selected-slots-label">{{ interviewCreneaux.length }} slot{{ interviewCreneaux.length > 1 ? 's' : '' }} selected</p>
                  <div class="selected-chips">
                    <span v-for="(c, i) in interviewCreneaux" :key="i" class="slot-chip">
                      {{ formatCreneau(c) }}<button class="chip-remove" @click="interviewCreneaux.splice(i, 1)">×</button>
                    </span>
                  </div>
                </div>
                <p v-else class="creneaux-empty">Click time slots to select them.</p>
                <div class="interview-section" style="margin-top:14px;">
                  <div class="interview-section-label">💬 Message (optional)</div>
                  <textarea v-model="interviewMessage" class="interview-textarea" placeholder="e.g. We would be happy to meet you..." rows="2"></textarea>
                </div>
                <button class="send-invite-btn" @click="handlePlanifier" :disabled="planifying || !interviewCreneaux.length">
                  <VideoIcon :size="14" />{{ planifying ? 'Sending...' : 'Send invitation' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- Modal Pipeline -->
      <transition name="modal-fade">
        <div v-if="showPipelineModal" class="modal-overlay" @click.self="showPipelineModal = false">
          <div class="modal-box">
            <div class="modal-header">
              <div>
                <h3 class="modal-title">Move to Stage</h3>
                <p class="modal-sub" v-if="candidate"><span class="sub-name">{{ candidate.nomCandidat }}</span><span class="dot-sep">·</span>{{ candidate.titreOffre }}</p>
              </div>
              <button class="modal-close" @click="showPipelineModal = false">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
              </button>
            </div>
            <div class="modal-body">
              <CandidatePipelineBoard :candidatures="selectedCandidatureForBoard" :show-header="false" mode="full" :enableDrag="true" @status-change="handlePipelineStatusChange" />
            </div>
          </div>
        </div>
      </transition>
     

      <!-- Rapport IA -->
      <RapportEntretien v-if="showRapportIA && rapportIAData" :rapport="rapportIAData" :questions="rapportIAQuestions" @close="showRapportIA = false" />

      <!-- ✅ Quiz Modal avec events collègue pour refresh du score -->
      <ShortlistQuizModal
        v-model="showQuizModal"
        :offreId="candidate?.offreId || candidate?.OffreId || ''"
        :candidateId="candidateId"
        :candidateName="candidate?.nomCandidat || ''"
        :candidateEmail="candidate?.emailCandidat || ''"
        :titreOffre="candidate?.titreOffre || ''"
        @done="$refs.quizStatus?.fetchQuizInfo()"
        @quiz-scheduled="$refs.quizStatus?.fetchQuizInfo()"
      />
    </main>
  </div>
</template>

<script>
import {
  ArrowLeftIcon, BriefcaseIcon, BuildingIcon, CalendarIcon,
  ArrowRightLeftIcon,
  RefreshCwIcon, BrainIcon, SparklesIcon, Wand2Icon,
  MessageSquareOffIcon, UsersIcon, AwardIcon,
  FileTextIcon, ExternalLinkIcon, GlobeIcon, UserIcon, ActivityIcon,
  VideoIcon, CalendarPlusIcon, ClockIcon, CopyIcon, CheckIcon
} from 'lucide-vue-next'

const GraduationCapIcon = AwardIcon

import AppSidebar              from '../../components/layout/AppSidebar.vue'
import GlobalHeader            from '../../components/layout/GlobalHeader.vue'
import CandidatePipelineBoard  from '../../components/CandidatePipelineBoard.vue'
import ShortlistQuizModal      from '../recruiter/Shortlistquizmodal.vue'
import RapportEntretien        from '../../components/RapportEntretien.vue'
// ✅ AJOUT COLLÈGUE
import CandidateQuizStatus     from '../../components/candidateDetails/CandidateQuizStatus.vue'

import {
  getCandidatureById, recalculateMatchScore, summarizeCv,
  extractSkills, extractExperience, extractCertifications,
  rejectCandidate, updateCandidateStatus,
  getAvisExperts, getExpertsAssignes
} from '../../services/candidatureService'
import { planifierEntretien } from '../../services/entretienService'
import { useNotificationStore } from '../../stores/notification'
import { applicationStatusLabel, formatRecruiterDateTime } from '../../utils/recruiterI18n.js'

export default {
  name: 'CandidateDetails',
  components: {
    AppSidebar, GlobalHeader, CandidatePipelineBoard, ShortlistQuizModal, RapportEntretien,
    CandidateQuizStatus, // ✅ AJOUT COLLÈGUE
    ArrowLeftIcon, BriefcaseIcon, BuildingIcon, CalendarIcon,
    ArrowRightLeftIcon,
    RefreshCwIcon, BrainIcon, SparklesIcon, Wand2Icon, AwardIcon,
    GraduationCapIcon,
    MessageSquareOffIcon, UsersIcon,
    FileTextIcon, ExternalLinkIcon, GlobeIcon, UserIcon, ActivityIcon,
    VideoIcon, CalendarPlusIcon, ClockIcon, CopyIcon, CheckIcon
  },
  setup() {
    const ns = useNotificationStore()
    const toast = {
      success: (m) => ns.addToast({ type: 'success', message: m }),
      error:   (m) => ns.addToast({ type: 'error',   message: m }),
      info:    (m) => ns.addToast({ type: 'info',    message: m })
    }
    return { toast, confirm: (o) => ns.confirm(o) }
  },
  data() {
    return {
      candidateId: null, candidate: null, loading: true,
      showPipelineModal: false, activeTab: 'skills',
      showQuizModal: false,
      aiSummary: '', extractedSkills: [], extractedExperiences: [],
      certifications: [],
      formResponses: [], feedbacks: [], assignedExperts: [],
      processingSkills: false, processingExperience: false,
      processingSummary: false, processingCertifications: false,
      // Interview scheduling
      showInterviewModal: false,
      interviewCreneaux: [],
      interviewMessage: '',
      schedulingDone: false,
      planifying: false,
      calMonday: null,
      tenantCalAllowPastSlots: true,
      // Rapport IA
      showRapportIA: false,
      rapportIAData: null,
      rapportIAQuestions: [],
      scoreBreakdown: null,
    }
  },
  computed: {
    gaugeColor() {
      const s = this.candidate?.scoreIA
      return s == null ? '#CBD5E1' : s >= 80 ? '#1D9E75' : s >= 50 ? '#EF9F27' : '#E24B4A'
    },
    gaugeLength() {
      const s = this.candidate?.scoreIA
      return s != null ? (s / 100) * 101 : 0
    },
    assignedExpertsLabel() {
      const names = this.assignedExperts.map(e => e.nom).filter(Boolean)
      return names.length <= 2 ? names.join(', ') : `${names.slice(0,2).join(', ')} +${names.length-2}`
    },
    selectedCandidatureForBoard() {
      if (!this.candidate) return []
      return [{ id:this.candidate.id, statut:this.candidate.statut, candidatNomComplet:this.candidate.nomCandidat, offreTitre:this.candidate.titreOffre, creeLe:this.candidate.creeLe, offreId:this.candidate.offreId??this.candidate.id, avisExpert:this.candidate.scoreIA!=null?{score:this.candidate.scoreIA/20}:null, tousLesAvis:[] }]
    },
    parsedSummary() {
      if (!this.aiSummary) return []
      return this.aiSummary.replace(/\.\s+/g, '.|').split('|').map(s => s.trim()).filter(s => s.length > 10)
    },
    calWeekDays() {
      if (!this.calMonday) return []
      const today = new Date(); today.setHours(0, 0, 0, 0)
      return Array.from({ length: 7 }, (_, i) => {
        const d = new Date(this.calMonday)
        d.setDate(this.calMonday.getDate() + i)
        return {
          iso: this.toLocalDateIso(d),
          name: d.toLocaleDateString('en-US', { weekday: 'short' }),
          num: d.getDate(),
          isToday: d.toDateString() === today.toDateString()
        }
      })
    },
    calWeekLabel() {
      if (!this.calMonday) return ''
      const end = new Date(this.calMonday); end.setDate(end.getDate() + 6)
      const o = { day: 'numeric', month: 'short' }
      return `${this.calMonday.toLocaleDateString('en-US', o)} – ${end.toLocaleDateString('en-US', o)}`
    },
    calTimeSlots() {
      const slots = []
      for (let h = 0; h < 24; h++) for (let m = 0; m < 60; m += 15)
        slots.push(`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`)
      return slots
    },
    summaryHighlights() {
      if (!this.aiSummary) return []
      const keywords = ['senior','junior','expert','lead','fullstack','frontend','backend','.net','vue','react','angular','python','java','node','aws','azure','5 ans','3 ans','7 ans','10 ans','agile','scrum','devops']
      const lower = this.aiSummary.toLowerCase()
      return keywords.filter(k => lower.includes(k)).slice(0, 5)
    }
  },
  async created() {
    this.candidateId = this.$route.params.id
    if (!this.candidateId) { this.goBack(); return }
    await this.fetchCandidate()
  },
  methods: {
    async fetchCandidate() {
      this.loading = true
      try {
        const res = await getCandidatureById(this.candidateId)
        this.candidate = res.data
        if (this.candidate.analyseCV?.score != null) this.candidate.scoreIA = this.candidate.analyseCV.score
        this.scoreBreakdown = null
        if (this.candidate.analyseCV) {
          this.aiSummary = this.candidate.analyseCV.resume || ''
          try { const parsed = this.candidate.analyseCV.competences ? JSON.parse(this.candidate.analyseCV.competences) : []; this.extractedSkills = Array.isArray(parsed) ? parsed : (parsed?.skills || []) } catch { this.extractedSkills = [] }
          try {
            const raw = this.candidate.analyseCV.experience ? JSON.parse(this.candidate.analyseCV.experience) : []
            this.extractedExperiences = (Array.isArray(raw) ? raw : []).map(e => this.normalizeExperience(e))
          } catch { this.extractedExperiences = [] }
          try { this.certifications = this.candidate.analyseCV.certifications ? JSON.parse(this.candidate.analyseCV.certifications) : [] } catch { this.certifications = [] }
        }
        this.formResponses = this.candidate.formulaireResponses
          ? Object.entries(this.candidate.formulaireResponses).map(([q, a]) => ({ question: q, answer: a }))
          : []
        await this.fetchExpertReviews()
        await this.fetchExpertsAssignes()
        await this.fetchEntretienTermine()
      } catch { this.toast.error('Failed to load candidate details') }
      finally { this.loading = false }
    },
    async fetchExpertReviews() {
      try {
        const res = await getAvisExperts(this.candidateId)
        const rawAvis = Array.isArray(res.data) ? res.data : (res.data?.avis || [])
        this.feedbacks = rawAvis.map(a => ({ id:a.id, author:a.expertNom||'Expert', comment:a.commentaire, timestamp:a.creeLe, score:a.score }))
      } catch { this.feedbacks = [] }
    },
    async fetchExpertsAssignes() {
      try { const res = await getExpertsAssignes(this.candidateId); this.assignedExperts = Array.isArray(res.data) ? res.data : [] }
      catch { this.assignedExperts = [] }
    },
    async fetchEntretienTermine() {
      try {
        const { getEntretiens } = await import('../../services/entretienService')
        const r = await getEntretiens()
        const termine = (r.data || [])
          .filter(e => e.statut === 'Termine' && e.candidatureId === this.candidateId)
          .sort((a, b) => new Date(b.creeLe) - new Date(a.creeLe))[0]
        if (!termine?.rapportIA) return
        const rapport = typeof termine.rapportIA === 'string' ? JSON.parse(termine.rapportIA) : termine.rapportIA
        this.rapportIAData = {
          nomCandidat: termine.nomCandidat || '', titreOffre: termine.titreOffre || '',
          scoreGlobal: rapport?.scoreGlobal ?? termine.score ?? 0,
          mention: rapport?.mention ?? '', recommandation: rapport?.recommandation ?? '',
          resume_executif: rapport?.resume_executif ?? '',
          points_forts: rapport?.points_forts ?? [], points_amelioration: rapport?.points_amelioration ?? [],
          competences_evaluees: rapport?.competences_evaluees ?? [],
          dureeMinutes: rapport?.dureeMinutes ?? termine.dureeMinutes,
          verificationFacialeOk: termine.verificationFacialeOk ?? false,
          nbChangementsOnglet: termine.nbChangementsOnglet ?? 0,
          fraudDetection: rapport?.fraudDetection ?? null,
        }
        if (termine.questionsIA)
          this.rapportIAQuestions = typeof termine.questionsIA === 'string' ? JSON.parse(termine.questionsIA) : termine.questionsIA
      } catch {}
    },
    goBack() { this.$router.push('/recruiter/candidates') },
    handleMoveStage() { this.showPipelineModal = true },
    async handleRecalculateScore() {
      try {
        this.toast.info('Recalculating…')
        const r = await recalculateMatchScore(this.candidateId)
        if (!this.candidate) return
        this.candidate.scoreIA = r.data.score
        const d = r.data
        if (d.technical != null && d.experience != null && d.domainFit != null)
          this.scoreBreakdown = { technical: d.technical, experience: d.experience, domainFit: d.domainFit }
        else this.scoreBreakdown = null
        if (d.statut) this.candidate.statut = d.statut
        if (d.autoDeclined) this.toast.info('Application auto-declined (score below 60%)')
        else this.toast.success('Score updated')
      } catch { this.toast.error('Failed') }
    },
    handleViewCV() {
      if (this.candidate?.cvUrl) {
        const url = this.candidate.cvUrl.startsWith('http') ? this.candidate.cvUrl : `http://localhost:5202/${this.candidate.cvUrl}`
        window.open(url, '_blank')
      } else { this.toast.error('No CV URL found.') }
    },
    async handleSummarizeCV() {
      this.processingSummary = true; this.toast.info('Generating summary…')
      try {
        const r = await summarizeCv(this.candidateId)
        this.aiSummary = r.data.summary || ''
        if (r.data.skills?.length) this.extractedSkills = r.data.skills
        if (r.data.experiences?.length) this.extractedExperiences = r.data.experiences
        if (r.data.warning) this.toast.error(r.data.warning)
        else this.toast.success('Summary generated!')
        await this.fetchCandidate()
      }
      catch { this.toast.error('Failed to generate summary') } finally { this.processingSummary = false }
    },
    async handleExtractSkills() {
      this.processingSkills = true; this.toast.info('Extracting skills…')
      try {
        const r = await extractSkills(this.candidateId)
        this.extractedSkills = r.data.skills || []
        if (r.data.warning) this.toast.error(r.data.warning)
        else if (this.extractedSkills.length) this.toast.success(`${this.extractedSkills.length} skills extracted!`)
        else this.toast.warning('No skills found in this CV.')
        await this.fetchCandidate()
      }
      catch { this.toast.error('Failed to extract skills') } finally { this.processingSkills = false }
    },
    async handleExtractExperience() {
      this.processingExperience = true; this.toast.info('Extracting experience…')
      try {
        const r = await extractExperience(this.candidateId)
        this.extractedExperiences = (r.data.experiences || []).map(e => this.normalizeExperience(e))
        if (r.data.warning) this.toast.error(r.data.warning)
        else if (this.extractedExperiences.length) this.toast.success(`${this.extractedExperiences.length} positions extracted!`)
        else this.toast.warning('No experience found in this CV.')
        await this.fetchCandidate()
      }
      catch { this.toast.error('Failed to extract experience') } finally { this.processingExperience = false }
    },
    async handleExtractCertifications() {
      this.processingCertifications = true; this.toast.info('Extracting certifications…')
      try {
        const r = await extractCertifications(this.candidateId)
        this.certifications = r.data.certifications || []
        this.toast.success(this.certifications.length > 0 ? `${this.certifications.length} certifications found!` : 'No certifications found.')
      } catch { this.toast.error('Failed to extract certifications') } finally { this.processingCertifications = false }
    },
    async handlePipelineStatusChange({ candidateId, toStatus }) {
      if (!candidateId || !toStatus || !this.candidate) return
      try {
        await updateCandidateStatus(candidateId, toStatus)
        this.candidate.statut = toStatus
        this.toast.success(`Status updated to "${toStatus}"`)
        if (toStatus === 'Présélectionné') {
          this.showPipelineModal = false
          this.$nextTick(() => { this.showQuizModal = true })
        }
        if (toStatus === 'Entretien') {
          this.showPipelineModal = false
          this.$nextTick(() => { this.openInterviewModal() })
        }
      } catch { this.toast.error('Failed to update candidate status') }
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
    certIconClass(cert) { return this.isCertif(cert) ? 'cert-icon-certif' : 'cert-icon-diploma' },
    certBadgeClass(cert) { return this.isCertif(cert) ? 'cert-badge-certif' : 'cert-badge-diploma' },
    certLabel(cert) { return this.isCertif(cert) ? 'Certification' : 'Diploma' },
    normalizeExperience(exp) {
      if (!exp || typeof exp !== 'object') return { role: '', entreprise: '', years: '', summary: '' }
      const ns = /^non\s*sp[eé]cifi[eé]$/i
      let entreprise = (exp.entreprise ?? exp.Entreprise ?? '').trim()
      let years = (exp.years ?? exp.Years ?? '').trim()
      if (!entreprise || ns.test(entreprise)) entreprise = 'Not specified'
      if (!years || ns.test(years)) years = 'Not specified'
      return {
        role: exp.role ?? exp.Role ?? '',
        entreprise,
        years,
        summary: exp.summary ?? exp.Summary ?? '',
      }
    },
    initiales(nom) { if (!nom) return '?'; return nom.split(' ').map(p => p[0]).join('').toUpperCase().slice(0,2) },
    formatDate(d)  { if (!d) return '—'; const dt = new Date(d); if (dt.getFullYear() < 1000) return '—'; return dt.toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' }) },
    timeAgo(d) {
      if (!d) return ''
      const diff = Date.now() - new Date(d).getTime()
      if (diff < 60000) return 'Just now'; if (diff < 3600000) return `${Math.floor(diff/60000)}m ago`
      if (diff < 86400000) return `${Math.floor(diff/3600000)}h ago`; return `${Math.floor(diff/86400000)}d ago`
    },
    matchDimBarWidth(dim) { const v = this.scoreBreakdown?.[dim]; if (v == null || Number.isNaN(Number(v))) return '0%'; return Math.min(100, Math.max(0, Math.round(Number(v)))) + '%' },
    matchDimBarLabel(dim) { const v = this.scoreBreakdown?.[dim]; if (v == null || Number.isNaN(Number(v))) return '—'; return Math.min(100, Math.max(0, Math.round(Number(v)))) + '%' },
    statusLabel(s) { return applicationStatusLabel(s) },
    statusChipClass(s) { return { 'Nouvelle':'ch-blue','En cours':'ch-amber','Acceptée':'ch-green','Refusée':'ch-red','Présélectionné':'ch-purple','Entretien':'ch-teal' }[s] || 'ch-neutral' },
    statusPillClass(s) { return { 'Nouvelle':'sp-blue','En cours':'sp-amber','Acceptée':'sp-green','Refusée':'sp-red','Présélectionné':'sp-purple','Entretien':'sp-teal' }[s] || 'sp-blue' },
    openInterviewModal() {
      this.schedulingDone = false; this.interviewCreneaux = []; this.interviewMessage = ''
      this.showInterviewModal = true; this.calMonday = this.getCalMonday(new Date())
    },
    getCalMonday(d) { const day = new Date(d); day.setHours(0,0,0,0); const dow = (day.getDay() + 6) % 7; day.setDate(day.getDate() - dow); return day },
    calPrevWeek() { const d = new Date(this.calMonday); d.setDate(d.getDate() - 7); this.calMonday = d },
    calNextWeek() { const d = new Date(this.calMonday); d.setDate(d.getDate() + 7); this.calMonday = d },
    toLocalDateIso(d) { return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}` },
    isSlotPast(dayIso, time) {
      if (this.tenantCalAllowPastSlots) return false
      const [y,mo,da] = dayIso.split('-').map(Number); const [h,mi] = time.split(':').map(Number)
      return new Date(y, mo-1, da, h, mi, 0, 0) <= new Date()
    },
    isSlotSelected(dayIso, time) {
      const [h,mi] = time.split(':').map(Number)
      return this.interviewCreneaux.some(iso => { const d = new Date(iso); return this.toLocalDateIso(d) === dayIso && d.getHours() === h && d.getMinutes() === mi })
    },
    toggleSlot(dayIso, time) {
      const [y,mo,da] = dayIso.split('-').map(Number); const [h,mi] = time.split(':').map(Number)
      const local = new Date(y, mo-1, da, h, mi, 0, 0)
      const idx = this.interviewCreneaux.findIndex(c => { const d = new Date(c); return this.toLocalDateIso(d) === dayIso && d.getHours() === h && d.getMinutes() === mi })
      if (idx >= 0) this.interviewCreneaux.splice(idx, 1); else this.interviewCreneaux.push(local.toISOString())
    },
    formatCreneau(iso) { return formatRecruiterDateTime(iso) },
    async handlePlanifier() {
      if (!this.interviewCreneaux.length) return
      this.planifying = true
      try {
        await planifierEntretien(this.candidateId, this.interviewCreneaux, this.interviewMessage)
        this.schedulingDone = true
        this.toast.success(`Invitation sent to ${this.candidate.emailCandidat}!`)
      } catch { this.toast.error('Failed to send invitation') }
      finally { this.planifying = false }
    },
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
.page-layout  { display:flex; min-height:100vh; background:#F0F2F7; font-family:'DM Sans',sans-serif; }
.main-content { flex:1; display:flex; flex-direction:column; min-width:0; overflow:hidden; }
.content-wrap { flex:1; overflow-y:auto; padding:22px 28px; max-width:1600px; margin:0 auto; width:100%; box-sizing:border-box; }
.top-bar  { display:flex; align-items:center; gap:8px; margin-bottom:18px; }
.back-btn { display:inline-flex; align-items:center; gap:6px; background:#fff; border:0.5px solid #E2E8F0; color:#475569; font-size:13px; font-weight:600; cursor:pointer; padding:7px 13px; border-radius:8px; font-family:inherit; }
.back-btn:hover { background:#F8FAFC; color:#0F172A; }
.sep { color:#CBD5E1; } .current { font-size:13px; font-weight:600; color:#0F172A; }
.page-grid { display:grid; grid-template-columns:minmax(0,1fr) 280px; gap:18px; align-items:start; }
@media(max-width:1100px) { .page-grid { grid-template-columns:1fr; } }
.left-col { display:flex; flex-direction:column; gap:16px; }
.right-col { position:relative; }
.sticky-wrap { position:sticky; top:22px; display:flex; flex-direction:column; gap:14px; }
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
.ch-blue { background:#E6F1FB; color:#0C447C; border-color:#85B7EB; } .ch-green { background:#EAF3DE; color:#27500A; border-color:#97C459; }
.ch-amber { background:#FAEEDA; color:#633806; border-color:#EF9F27; } .ch-red { background:#FCEBEB; color:#791F1F; border-color:#F09595; }
.ch-purple { background:#EEEDFE; color:#3C3489; border-color:#AFA9EC; } .ch-teal { background:#E1F5EE; color:#085041; border-color:#5DCAA5; }
.ch-neutral { background:#F1F5F9; color:#475569; border-color:#E2E8F0; }
.score-strip { display:grid; grid-template-columns:auto 1fr; gap:18px; align-items:center; padding:16px 20px; border-bottom:0.5px solid #F1F5F9; }
.score-title { font-size:13px; font-weight:600; color:#0F172A; margin:0 0 8px; }
.score-breakdown-hint { font-size:11px; color:#64748B; margin:8px 0 0; }
.score-bars { display:flex; flex-direction:column; gap:5px; }
.bar-row { display:flex; align-items:center; gap:8px; }
.bar-lbl { font-size:11px; color:#94A3B8; width:68px; flex-shrink:0; }
.bar-bg { flex:1; height:3px; background:#F1F5F9; border-radius:99px; overflow:hidden; }
.bar-fill { height:100%; border-radius:99px; }
.bar-green { background:#1D9E75; } .bar-amber { background:#EF9F27; }
.bar-pct { font-size:11px; color:#94A3B8; width:30px; text-align:right; }
.score-actions { display:flex; gap:8px; padding:10px 20px; background:#F8FAFC; }
.action-pill { display:inline-flex; align-items:center; gap:6px; padding:6px 12px; border-radius:8px; font-size:12px; font-weight:600; background:#fff; border:0.5px solid #E2E8F0; color:#475569; cursor:pointer; font-family:inherit; }
.action-pill:hover:not(:disabled) { background:#F1F5F9; color:#0F172A; }
.action-pill:disabled { opacity:0.5; cursor:not-allowed; }
.tabs-nav { display:flex; border-bottom:0.5px solid #F1F5F9; padding:0 12px; overflow-x:auto; }
.tab-btn { display:flex; align-items:center; gap:5px; padding:12px 10px; font-size:12px; font-weight:600; color:#94A3B8; background:none; border:none; cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-0.5px; font-family:inherit; white-space:nowrap; }
.tab-btn.active { color:#0F172A; border-bottom-color:#1A2B4C; }
.tab-count { background:#F1F5F9; color:#475569; font-size:10px; font-weight:700; padding:1px 6px; border-radius:99px; }
.tab-body { padding:20px; }
.tab-section-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:#94A3B8; margin-bottom:10px; }
.section-header-row { display:flex; align-items:center; justify-content:space-between; }
.tab-action-btn-sm { display:inline-flex; align-items:center; gap:5px; padding:4px 10px; border-radius:7px; font-size:11px; font-weight:600; background:#F8FAFC; border:0.5px solid #E2E8F0; color:#0D9488; cursor:pointer; font-family:inherit; }
.tab-action-btn-sm:hover:not(:disabled) { background:#E1F5EE; border-color:#5DCAA5; }
.tab-action-btn-sm:disabled { opacity:0.5; cursor:not-allowed; }
.summary-section-top { background:#F8FAFC; border-radius:12px; padding:16px; border:0.5px solid #E8EDF4; }
.summary-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.summary-box-improved { display:flex; flex-direction:column; gap:10px; }
.summary-content { display:flex; gap:10px; align-items:flex-start; }
.summary-icon { width:28px; height:28px; border-radius:8px; background:linear-gradient(135deg,#1A2B4C,#2d4a8c); color:#B5D4F4; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.summary-text { flex:1; }
.summary-sentence { font-size:13px; color:#334155; line-height:1.65; margin:0 0 6px; }
.summary-highlights { display:flex; flex-wrap:wrap; gap:6px; padding-top:8px; border-top:0.5px solid #E8EDF4; }
.summary-highlight-tag { padding:3px 9px; background:#E6F1FB; color:#0C447C; border-radius:99px; font-size:11px; font-weight:600; border:0.5px solid #85B7EB; }
.summary-empty { display:flex; flex-direction:column; align-items:center; gap:6px; padding:16px; text-align:center; }
.summary-empty p { font-size:12px; color:#CBD5E1; margin:0; max-width:260px; line-height:1.5; }
.section-empty { display:flex; flex-direction:column; align-items:center; gap:6px; padding:16px 0; }
.section-empty p { font-size:12px; color:#CBD5E1; margin:0; }
.section-empty-large { display:flex; flex-direction:column; align-items:center; gap:8px; padding:32px; text-align:center; }
.empty-icon-sm { color:#CBD5E1; } .empty-icon-lg { color:#E2E8F0; }
.empty-title { font-size:14px; font-weight:600; color:#94A3B8; margin:0; }
.three-col { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1fr); gap:16px; }
@media(max-width:900px) { .three-col { grid-template-columns:1fr 1fr; } }
@media(max-width:600px) { .three-col { grid-template-columns:1fr; } }
.cert-col-list { display:flex; flex-direction:column; gap:8px; }
.cert-col-item { display:flex; align-items:flex-start; gap:8px; padding:8px 10px; background:#F8FAFC; border-radius:9px; border:0.5px solid #E8EDF4; }
.cert-col-icon { width:26px; height:26px; border-radius:6px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.cert-col-body { flex:1; min-width:0; }
.cert-col-name { font-size:11px; font-weight:600; color:#0F172A; margin:0 0 3px; line-height:1.4; }
.cert-col-meta { display:flex; gap:6px; flex-wrap:wrap; }
.cert-icon-certif { background:linear-gradient(135deg,#FAEEDA,#EF9F27); color:#633806; }
.cert-icon-diploma { background:linear-gradient(135deg,#EEEDFE,#AFA9EC); color:#3C3489; }
.cert-inline-badge { font-size:9px; font-weight:700; padding:2px 7px; border-radius:99px; white-space:nowrap; flex-shrink:0; }
.cert-badge-certif { background:#FAEEDA; color:#633806; } .cert-badge-diploma { background:#EEEDFE; color:#3C3489; }
.cert-org, .cert-year { display:inline-flex; align-items:center; gap:3px; font-size:10px; color:#94A3B8; }
.skills-tags { display:flex; flex-wrap:wrap; gap:6px; }
.skill-tag { padding:4px 10px; border-radius:7px; font-size:12px; font-weight:600; background:#E6F1FB; color:#0C447C; border:0.5px solid #85B7EB; }
.tl { display:flex; flex-direction:column; }
.tl-item { display:flex; gap:10px; padding-bottom:14px; }
.tl-item:last-child { padding-bottom:0; }
.tl-left { display:flex; flex-direction:column; align-items:center; width:14px; flex-shrink:0; }
.tl-dot { width:9px; height:9px; border-radius:50%; background:#1D9E75; box-shadow:0 0 0 2.5px #E1F5EE; flex-shrink:0; margin-top:3px; }
.tl-line { flex:1; width:1px; background:#E8EDF4; margin:4px 0; }
.tl-body { flex:1; }
.tl-role { font-size:13px; font-weight:700; color:#0F172A; margin:0 0 4px; }
.tl-row { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:4px; }
.tl-co { font-size:11px; padding:2px 8px; background:#F1F5F9; border:0.5px solid #E2E8F0; border-radius:4px; color:#475569; }
.tl-years { font-size:11px; padding:2px 8px; background:#E1F5EE; border:0.5px solid #5DCAA5; border-radius:4px; color:#085041; }
.tl-desc { font-size:12px; color:#475569; line-height:1.5; margin:0; }
.qa-list { display:flex; flex-direction:column; gap:16px; }
.qa-q { display:flex; gap:8px; align-items:flex-start; margin-bottom:6px; }
.qa-idx { min-width:22px; height:18px; background:#F1F5F9; border-radius:4px; font-size:11px; font-weight:700; color:#475569; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:1px; }
.qa-question { font-size:13px; font-weight:600; color:#0F172A; }
.qa-answer { margin-left:30px; font-size:13px; color:#475569; line-height:1.6; padding:10px 14px; background:#F8FAFC; border-left:2px solid #1A2B4C; border-radius:0 8px 8px 0; }
.reviews-list { display:flex; flex-direction:column; gap:0; }
.review-item { display:flex; gap:10px; padding:12px 0; border-bottom:0.5px solid #F8FAFC; }
.review-item:last-of-type { border-bottom:none; }
.rv-avatar { width:30px; height:30px; border-radius:8px; object-fit:cover; flex-shrink:0; }
.rv-body { flex:1; }
.rv-meta { display:flex; align-items:center; gap:7px; margin-bottom:5px; flex-wrap:wrap; }
.rv-name { font-size:13px; font-weight:600; color:#0F172A; }
.rv-badge { font-size:10px; padding:2px 6px; background:#EEEDFE; color:#3C3489; border-radius:4px; font-weight:700; }
.rv-score { font-size:11px; font-weight:700; color:#EF9F27; background:#FAEEDA; padding:2px 7px; border-radius:4px; }
.rv-time { font-size:11px; color:#CBD5E1; margin-left:auto; }
.rv-text { font-size:13px; color:#475569; line-height:1.5; }
.stats-card { overflow:hidden; }
.stats-grid { display:grid; grid-template-columns:1fr; }
.stat-box { padding:14px; text-align:center; border-right:0.5px solid #F1F5F9; }
.stat-box:last-child { border-right:none; }
.stat-num { display:block; font-size:22px; font-weight:700; color:#0F172A; line-height:1; }
.stat-lbl { display:block; font-size:11px; color:#94A3B8; margin-top:4px; text-transform:uppercase; letter-spacing:0.06em; }
.sb-section-title { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8; margin:0 0 12px; padding:16px 16px 0; }
.sb-btn-stack { padding:0 16px 16px; display:flex; flex-direction:column; gap:8px; }
.sb-btn { display:flex; align-items:center; gap:9px; width:100%; padding:9px 12px; border-radius:9px; font-size:13px; font-weight:600; cursor:pointer; font-family:inherit; border:0.5px solid #E2E8F0; background:#F8FAFC; color:#334155; }
.sb-btn span { flex:1; }
.sb-stage:hover { background:#F1F5F9; color:#1A2B4C; }
.sb-rapport { background:#EEF2FF; color:#3730A3; border-color:#C7D2FE; }
.sb-cv { margin:0 16px 16px; width:calc(100% - 32px); } .sb-cv:hover { background:#F1F5F9; }
.trail { margin-left:auto; opacity:0.4; }
.info-list { padding:0 16px 14px; }
.info-row { display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:0.5px solid #F8FAFC; }
.info-row:last-child { border-bottom:none; }
.info-lbl { display:flex; align-items:center; gap:5px; font-size:12px; color:#94A3B8; }
.info-val { font-size:12px; font-weight:600; color:#0F172A; }
.info-pill { font-size:11px; padding:3px 8px; background:#F1F5F9; color:#475569; border-radius:99px; }
.info-na { font-size:12px; color:#CBD5E1; font-style:italic; }
.status-pill { display:inline-flex; align-items:center; gap:4px; font-size:11px; font-weight:700; padding:3px 8px; border-radius:99px; }
.s-dot { width:5px; height:5px; border-radius:50%; background:currentColor; }
.sp-blue { background:#E6F1FB; color:#0C447C; } .sp-green { background:#EAF3DE; color:#27500A; }
.sp-amber { background:#FAEEDA; color:#633806; } .sp-red { background:#FCEBEB; color:#791F1F; }
.sp-purple { background:#EEEDFE; color:#3C3489; } .sp-teal { background:#E1F5EE; color:#085041; }
.mini-spin { width:13px; height:13px; border:2px solid #E2E8F0; border-top-color:#454a83; border-radius:50%; animation:spin 0.6s linear infinite; flex-shrink:0; }
@keyframes spin { to { transform:rotate(360deg); } }
.loading-inline { display:flex; align-items:center; gap:7px; font-size:12px; color:#94A3B8; padding:8px 0; }
.state-wrap { display:flex; align-items:center; justify-content:center; min-height:60vh; }
.state-card { display:flex; flex-direction:column; align-items:center; gap:14px; background:#fff; border-radius:14px; padding:48px 64px; border:0.5px solid #E8EDF4; color:#64748B; font-size:14px; }
.state-spinner { width:32px; height:32px; border:2.5px solid #E2E8F0; border-top-color:#454a83; border-radius:50%; animation:spin 0.8s linear infinite; }
.btn-back { padding:9px 22px; background:#454a83; color:#fff; border:none; border-radius:8px; font-weight:600; cursor:pointer; font-family:inherit; }
.modal-overlay { position:fixed; inset:0; background:rgba(15,23,42,0.5); backdrop-filter:blur(4px); display:flex; align-items:center; justify-content:center; z-index:400; }
.modal-box { background:#fff; border-radius:18px; width:980px; max-width:96vw; max-height:88vh; overflow-y:auto; border:0.5px solid #E8EDF4; }
.modal-interview { width:min(720px, 96vw); max-width:96vw; }
.modal-header { display:flex; justify-content:space-between; align-items:flex-start; padding:20px 26px; border-bottom:0.5px solid #F1F5F9; position:sticky; top:0; background:#fff; z-index:1; }
.modal-title { font-size:15px; font-weight:700; color:#0F172A; margin:0 0 3px; }
.modal-sub { font-size:12px; color:#94A3B8; margin:0; }
.sub-name { color:#475569; font-weight:600; } .dot-sep { margin:0 6px; color:#E2E8F0; }
.modal-close { background:#F8FAFC; border:0.5px solid #E2E8F0; cursor:pointer; color:#94A3B8; padding:6px; border-radius:7px; display:flex; }
.modal-close:hover { background:#F1F5F9; color:#475569; }
.modal-body { padding:22px 26px 28px; }
.modal-fade-enter-active { transition:all 0.2s ease; } .modal-fade-leave-active { transition:all 0.15s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity:0; }
.calendar-hint { font-size:12px; color:#94A3B8; margin:0 0 12px; }
.mini-cal { border:0.5px solid #E8EDF4; border-radius:10px; overflow:hidden; margin-bottom:12px; }
.mini-cal-nav { display:flex; align-items:center; justify-content:space-between; padding:8px 12px; background:#F8FAFC; border-bottom:0.5px solid #E8EDF4; }
.mini-nav-btn { background:none; border:0.5px solid #E2E8F0; border-radius:6px; width:24px; height:24px; cursor:pointer; font-size:16px; color:#475569; display:flex; align-items:center; justify-content:center; }
.mini-nav-btn:hover { background:#F1F5F9; }
.mini-week-label { font-size:12px; font-weight:600; color:#334155; }
.mini-cal-grid { display:grid; grid-template-columns:repeat(7,1fr); }
.mini-day-col { border-right:0.5px solid #F1F5F9; }
.mini-day-col:last-child { border-right:none; }
.mini-day-header { padding:6px 4px; text-align:center; background:#F8FAFC; border-bottom:0.5px solid #F1F5F9; }
.mini-day-header.mini-today .mini-day-num { background:#1A2B4C; color:#fff; border-radius:50%; }
.mini-day-name { display:block; font-size:9px; font-weight:700; text-transform:uppercase; color:#94A3B8; letter-spacing:0.05em; }
.mini-day-num { display:inline-flex; width:20px; height:20px; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#0F172A; }
.mini-slots { display:flex; flex-direction:column; gap:2px; padding:4px; max-height:min(52vh, 420px); overflow-y:auto; overscroll-behavior:contain; }
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
.interview-section-label { display:flex; align-items:center; gap:6px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8; margin-bottom:10px; }
.interview-textarea { width:100%; padding:10px 12px; border:0.5px solid #E2E8F0; border-radius:8px; font-size:13px; font-family:inherit; color:#334155; resize:vertical; box-sizing:border-box; }
.interview-textarea:focus { outline:none; border-color:#1A2B4C; }
.send-invite-btn { display:flex; align-items:center; gap:8px; margin-top:12px; width:100%; padding:12px; background:#1A2B4C; color:#fff; border:none; border-radius:10px; font-size:14px; font-weight:700; cursor:pointer; justify-content:center; font-family:inherit; }
.send-invite-btn:hover:not(:disabled) { background:#243d6a; }
.send-invite-btn:disabled { opacity:0.5; cursor:not-allowed; }
.interview-success { display:flex; flex-direction:column; align-items:center; gap:14px; text-align:center; padding:8px 0; }
.success-circle { width:52px; height:52px; border-radius:50%; background:#E1F5EE; color:#1D9E75; font-size:22px; font-weight:700; display:flex; align-items:center; justify-content:center; }
.interview-success h4 { font-size:16px; font-weight:700; color:#0F172A; margin:0; }
.interview-success p { font-size:13px; color:#475569; margin:0; }
</style>