<template>
  <div class="quiz-app">
    <div v-if="screen === 'loading'" class="screen-center">
      <div class="loader-pulse"></div>
      <p class="loading-text">Loading Assessment...</p>
    </div>

    <!-- WELCOME SCREEN -->
    <div v-if="screen === 'welcome'" class="screen-welcome">
      <div class="glass-card welcome-card">
        <div class="brand-badge">RecruitSaaS <span>AI</span></div>
        <h1 class="welcome-title">{{ quizData.titreOffre }}</h1>
        <p class="welcome-desc">{{ quizData.instructions || 'You are about to begin your technical assessment. Please ensure you are in a quiet environment.' }}</p>
        
        <div class="stats-grid">
          <div class="stat-box">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            <strong>{{ questions.length }}</strong>
            <small>Questions</small>
          </div>
          <div class="stat-box">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            <strong>{{ maxTimePerQ }}s</strong>
            <small>Per Question</small>
          </div>
          <div class="stat-box">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            <strong>~{{ Math.ceil(questions.length * maxTimePerQ / 60) }}m</strong>
            <small>Est. Total Time</small>
          </div>
        </div>

        <div v-if="!quizTimeReached" class="lock-block">
          <div class="lock-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
          </div>
          <p>Unlocks on <strong>{{ formatDate(scheduledDate) }}</strong></p>
          <div v-if="countdown" class="countdown-modern">
            <div class="cd-item"><span>{{ countdown.d }}</span><small>Days</small></div>
            <div class="cd-sep">:</div>
            <div class="cd-item"><span>{{ countdown.h }}</span><small>Hours</small></div>
            <div class="cd-sep">:</div>
            <div class="cd-item"><span>{{ countdown.m }}</span><small>Mins</small></div>
            <div class="cd-sep">:</div>
            <div class="cd-item"><span>{{ countdown.s }}</span><small>Secs</small></div>
          </div>
        </div>
        <button v-else class="btn-primary start-btn" @click="startQuiz">
          Start Assessment
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </button>
      </div>
    </div>

    <!-- QUIZ SCREEN -->
    <div v-if="screen === 'quiz'" class="screen-quiz">
      <div class="quiz-topbar">
        <div class="progress-container">
          <div class="progress-info">
            <span class="progress-text">Question {{ currentIndex + 1 }} of {{ questions.length }}</span>
            <span class="progress-pct">{{ Math.round(progressPct) }}%</span>
          </div>
          <div class="progress-bar-modern"><div class="progress-fill-modern" :style="{ width: progressPct + '%' }"></div></div>
        </div>
        <div class="timer-modern" :class="{ 'timer-warn': timerPct < 30, 'timer-danger': timerPct < 15, 'pulse': timerPct < 15 }">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          {{ timeLeft }}s
        </div>
      </div>

      <main class="quiz-main">
        <transition name="slide-up" mode="out-in">
          <div class="question-card" :key="currentIndex">
            <h2 class="q-title">{{ currentQ.question }}</h2>
            <div class="choices-modern">
              <button
                v-for="(choice, ci) in currentQ.choices" :key="ci"
                class="choice-btn" :class="{ 'is-selected': selectedAnswer === ci }"
                :disabled="timeLeft === 0" @click="selectedAnswer = ci"
              >
                <div class="choice-letter">{{ ['A','B','C'][ci] }}</div>
                <div class="choice-text">{{ choice }}</div>
                <div class="choice-check" v-if="selectedAnswer === ci">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                </div>
              </button>
            </div>
            
            <div class="q-actions">
              <div v-if="timeLeft === 0" class="timeout-msg">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                Time's up! Moving to next question...
              </div>
              <button v-else class="btn-primary next-btn" :disabled="selectedAnswer === null" @click="nextQuestion">
                {{ currentIndex + 1 < questions.length ? 'Next Question' : 'Submit Assessment' }}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
              </button>
            </div>
          </div>
        </transition>
      </main>
    </div>

    <!-- RESULTS SCREEN -->
    <div v-if="screen === 'results'" class="screen-results">
      <div class="results-container">
        <div class="results-hero">
          <div class="score-ring" :class="gradeClass">
            <svg class="score-svg" viewBox="0 0 36 36">
              <path class="score-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              <path class="score-fill" :stroke-dasharray="percentage + ', 100'" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            </svg>
            <div class="score-content">
              <span class="s-pct">{{ percentage }}%</span>
              <span class="s-txt">Score</span>
            </div>
          </div>
          
          <h1 class="result-title">{{ resultTitle }}</h1>
          <p class="result-subtitle">You got <strong>{{ score }}</strong> out of <strong>{{ questions.length }}</strong> correct.</p>
          
          <div class="results-metrics">
            <div class="metric m-correct"><div class="m-val">{{ score }}</div><div class="m-lbl">Correct</div></div>
            <div class="metric m-wrong"><div class="m-val">{{ questions.length - score - timeouts }}</div><div class="m-lbl">Incorrect</div></div>
            <div class="metric m-time"><div class="m-val">{{ timeouts }}</div><div class="m-lbl">Timeouts</div></div>
          </div>
        </div>

        <div class="detailed-review">
          <h3 class="review-title">Detailed Performance</h3>
          
          <div v-for="(r, i) in results" :key="i" class="review-card" :class="r.is_correct ? 'is-correct' : r.candidate_answer_index === -1 ? 'is-timeout' : 'is-wrong'">
            <div class="review-head">
              <span class="r-num">Q{{ r.question_id }}</span>
              <span class="r-text">{{ r.question }}</span>
              <div class="r-status" v-if="r.is_correct">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Correct
              </div>
              <div class="r-status" v-else-if="r.candidate_answer_index === -1">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> Timeout
              </div>
              <div class="r-status" v-else>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg> Incorrect
              </div>
            </div>
            
            <div class="review-options">
              <div v-for="(c, ci) in r.choices" :key="ci" class="r-option"
                :class="{ 
                  'o-correct': ci === r.correct_index, 
                  'o-wrong': ci === r.candidate_answer_index && ci !== r.correct_index 
                }">
                <span class="o-letter">{{ ['A','B','C'][ci] }}</span>
                <span class="o-text">{{ c }}</span>
                <svg v-if="ci === r.correct_index" class="o-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <svg v-if="ci === r.candidate_answer_index && ci !== r.correct_index" class="o-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </div>
            </div>
          </div>
        </div>
        
        <div class="results-footer">
          <button class="btn-primary btn-large" :disabled="confirming" @click="confirmAndExit">
            {{ confirming ? 'Returning...' : 'Return to Dashboard' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="errorMsg" class="toast-error">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
      {{ errorMsg }}
    </div>
  </div>
</template>

<script>
import { getQuizByToken, submitResult, confirmCompletion } from '../../services/quizService'

export default {
  name: 'QuizInterface',
  data() {
    return {
      screen: 'loading',
      quizToken: null,
      scheduledDate: null,
      quizTimeReached: false,
      countdown: null,
      countdownTimer: null,
      quizData: { candidateName: '', titreOffre: '', instructions: '' },
      questions: [],
      currentIndex: 0,
      selectedAnswer: null,
      answers: [],
      timeSpent: [],
      timeLeft: 0,
      maxTimePerQ: 60,
      timerInterval: null,
      score: 0, results: [], grade: '',
      percentage: 0, timeouts: 0, totalTimeSec: 0,
      confirming: false, errorMsg: '',
    }
  },
  computed: {
    currentQ()    { return this.questions[this.currentIndex] || {} },
    progressPct() { return this.questions.length > 0 ? (this.currentIndex / this.questions.length) * 100 : 0 },
    timerPct()    { return this.maxTimePerQ > 0 ? (this.timeLeft / this.maxTimePerQ) * 100 : 0 },
    resultTitle() {
      if (this.percentage >= 90) return 'Outstanding Performance!'
      if (this.percentage >= 75) return 'Great Job!'
      if (this.percentage >= 60) return 'Good Effort'
      return 'Keep Practicing'
    },
    gradeClass() {
      return { A: 'grade-a', B: 'grade-b', C: 'grade-c', D: 'grade-d', F: 'grade-f' }[this.grade] || ''
    }
  },
  async created() {
    this.quizToken = this.$route?.params?.token || window.location.pathname.split('/quiz/')[1]
    await this.loadQuiz()
  },
  beforeUnmount() {
    clearInterval(this.timerInterval)
    clearInterval(this.countdownTimer)
  },
  methods: {
    formatDate(iso) {
      if (!iso) return '—'
      return new Date(iso).toLocaleString('en-US', { weekday: 'long', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    },
    startCountdown(target) {
      clearInterval(this.countdownTimer)
      const tick = () => {
        const diff = target - new Date()
        if (diff <= 0) { clearInterval(this.countdownTimer); this.countdown = null; this.quizTimeReached = true; return }
        this.countdown = {
          d: String(Math.floor(diff / 86400000)).padStart(2, '0'),
          h: String(Math.floor((diff % 86400000) / 3600000)).padStart(2, '0'),
          m: String(Math.floor((diff % 3600000) / 60000)).padStart(2, '0'),
          s: String(Math.floor((diff % 60000) / 1000)).padStart(2, '0'),
        }
      }
      tick(); this.countdownTimer = setInterval(tick, 1000)
    },
    async loadQuiz() {
      this.screen = 'loading'
      try {
        const { data } = await getQuizByToken(this.quizToken)
        this.scheduledDate = data.scheduledDate
        this.quizData = {
          candidateName: data.candidateName || 'Candidate',
          titreOffre:    data.titreOffre    || '',
          instructions:  data.instructions  || '',
        }
        this.questions = (data.questions || []).map((q, i) => ({
          id:            q.id || i + 1,
          question:      q.question,
          choices:       [q.choiceA ?? q.choices?.[0] ?? '', q.choiceB ?? q.choices?.[1] ?? '', q.choiceC ?? q.choices?.[2] ?? ''],
          explanation:   q.explanation || '',
          time_limit:    q.timeLimit ?? q.time_limit ?? data.timePerQuestion ?? 60,
        }))
        this.maxTimePerQ = this.questions[0]?.time_limit || data.timePerQuestion || 60
        const quizTime = new Date(data.scheduledDate)
        if (new Date() >= quizTime) {
          this.quizTimeReached = true
        } else {
          this.startCountdown(quizTime)
        }
        this.screen = 'welcome'
      } catch {
        this.errorMsg = 'Quiz not found or already completed.'
        this.screen = 'welcome'
      }
    },
    startQuiz() {
      if (!this.quizTimeReached) return
      this.currentIndex = 0
      this.answers   = new Array(this.questions.length).fill(-1)
      this.timeSpent = new Array(this.questions.length).fill(0)
      this.screen = 'quiz'
      this.selectedAnswer = null
      this.startTimer()
    },
    startTimer() {
      clearInterval(this.timerInterval)
      const q = this.questions[this.currentIndex]
      this.timeLeft = this.maxTimePerQ = q ? q.time_limit : 60
      this.timerInterval = setInterval(() => {
        this.timeSpent[this.currentIndex]++
        this.timeLeft--
        if (this.timeLeft <= 0) {
          this.timeLeft = 0
          clearInterval(this.timerInterval)
          this.answers[this.currentIndex] = this.selectedAnswer !== null ? this.selectedAnswer : -1
          setTimeout(() => this.nextQuestion(), 1800)
        }
      }, 1000)
    },
    nextQuestion() {
      clearInterval(this.timerInterval)
      if (this.answers[this.currentIndex] === -1 && this.selectedAnswer !== null)
        this.answers[this.currentIndex] = this.selectedAnswer
      else if (this.answers[this.currentIndex] === -1)
        this.answers[this.currentIndex] = -1
      else
        this.answers[this.currentIndex] = this.selectedAnswer !== null ? this.selectedAnswer : -1

      if (this.currentIndex + 1 < this.questions.length) {
        this.currentIndex++
        this.selectedAnswer = null
        this.startTimer()
      } else {
        this.finishQuiz()
      }
    },
    async finishQuiz() {
      clearInterval(this.timerInterval)
      this.screen = 'loading'
      await this._submitResult()
      this.screen = 'results'
    },
    async _submitResult() {
      try {
        const { data } = await submitResult({
          quizToken:  this.quizToken,
          answers:    this.answers,
          timeSpent:  this.timeSpent,
        })
        this.score = data.score || 0
        this.percentage = data.percentage || 0
        this.grade = data.grade || 'F'
        this.timeouts = data.timeouts || 0
        this.totalTimeSec = data.totalTimeSec || 0
        this.results = data.results || []
      } catch (e) { 
        console.error("Submission failed", e);
        this.errorMsg = "Failed to submit results correctly.";
      }
    },
    async confirmAndExit() {
      this.confirming = true
      try {
        await confirmCompletion({ quizToken: this.quizToken, completed: true })
      } catch { /* non-blocking */ } finally {
        this.confirming = false
        this.$router?.push('/dashboard')?.catch(() => { window.location.href = '/dashboard' })
      }
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
  --primary: #4F46E5;
  --primary-hover: #4338CA;
  --success: #10B981;
  --danger: #EF4444;
  --warning: #F59E0B;
  --bg-gradient: linear-gradient(135deg, #F0F4FF 0%, #F8FAFC 100%);
  --surface: #FFFFFF;
  --border: #E2E8F0;
  --text-main: #0F172A;
  --text-muted: #64748B;
}

* { box-sizing: border-box; font-family: 'Inter', sans-serif; }

.quiz-app {
  min-height: 100vh; width: 100vw; 
  background: var(--bg-gradient);
  color: var(--text-main);
  display: flex; flex-direction: column;
}

/* Loading Screen */
.screen-center {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 20px;
}
.loader-pulse {
  width: 50px; height: 50px; border-radius: 50%;
  background: var(--primary);
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.5; box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.7); }
  70% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 20px rgba(79, 70, 229, 0); }
  100% { transform: scale(0.8); opacity: 0.5; box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }
}
.loading-text { font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 600; color: var(--text-main); }

/* Common UI Elements */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  color: #22a72d !important; border: none; border-radius: 12px;
  font-family: 'Outfit', sans-serif; font-weight: 600; cursor: pointer;
  transition: all 0.2s; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
}
.btn-primary * { color: #FFFFFF !important; }
.btn-primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4); }
.btn-primary:active:not(:disabled) { transform: translateY(0); }
.btn-primary:disabled { background: #E2E8F0; color: #64748B !important; cursor: not-allowed; box-shadow: none; border: 1px solid #CBD5E1; }
.btn-primary:disabled * { color: #64748B !important; }

/* Welcome Screen */
.screen-welcome { flex: 1; display: flex; align-items: center; justify-content: center; padding: 24px; }
.welcome-card { max-width: 680px; width: 100%; padding: 48px 40px; text-align: center; }
.brand-badge {
  display: inline-block; font-family: 'Outfit', sans-serif; font-size: 14px; font-weight: 800;
  padding: 6px 16px; background: rgba(79, 70, 229, 0.1); color: var(--primary);
  border-radius: 99px; margin-bottom: 24px; letter-spacing: 0.05em;
}
.brand-badge span { color: var(--success); }
.welcome-title { font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 800; color: var(--text-main); margin: 0 0 16px; line-height: 1.2; letter-spacing: -0.02em; }
.welcome-desc { font-size: 16px; color: var(--text-muted); line-height: 1.6; margin: 0 0 32px; max-width: 500px; margin-inline: auto; }

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px; }
.stat-box {
  background: white; border: 1px solid var(--border); border-radius: 16px;
  padding: 20px; display: flex; flex-direction: column; align-items: center; gap: 8px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
}
.stat-box svg { color: var(--primary); }
.stat-box strong { font-family: 'Outfit', sans-serif; font-size: 24px; font-weight: 700; color: var(--text-main); line-height: 1; }
.stat-box small { font-size: 12px; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }

.lock-block { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.lock-icon { width: 48px; height: 48px; background: rgba(15, 23, 42, 0.05); color: var(--text-muted); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.countdown-modern { display: flex; gap: 12px; align-items: center; }
.cd-item { display: flex; flex-direction: column; align-items: center; background: white; padding: 12px 16px; border-radius: 12px; border: 1px solid var(--border); min-width: 64px; }
.cd-item span { font-family: 'Outfit', sans-serif; font-size: 24px; font-weight: 700; color: var(--primary); }
.cd-item small { font-size: 10px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
.cd-sep { font-size: 24px; font-weight: 700; color: var(--text-muted); }

.start-btn { padding: 16px 32px; font-size: 18px; width: 100%; max-width: 300px; }

/* Quiz Screen */
.screen-quiz { flex: 1; display: flex; flex-direction: column; }
.quiz-topbar {
  background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border); padding: 16px 32px;
  display: flex; align-items: center; justify-content: space-between; gap: 32px;
  position: sticky; top: 0; z-index: 10;
}
.progress-container { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.progress-info { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; color: var(--text-main); }
.progress-pct { color: var(--primary); }
.progress-bar-modern { width: 100%; height: 8px; background: #E2E8F0; border-radius: 99px; overflow: hidden; }
.progress-fill-modern { height: 100%; background: linear-gradient(90deg, #4F46E5, #818CF8); transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1); }

.timer-modern {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px; background: rgba(79, 70, 229, 0.1);
  color: var(--primary); border-radius: 99px;
  font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 700;
  transition: all 0.3s;
}
.timer-warn { background: rgba(245, 158, 11, 0.1); color: var(--warning); }
.timer-danger { background: rgba(239, 68, 68, 0.1); color: var(--danger); }
.timer-danger.pulse { animation: timerPulse 1s infinite; }
@keyframes timerPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }

.quiz-main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 24px; }
.question-card {
  max-width: 800px; width: 100%;
  background: white; border-radius: 24px; padding: 48px;
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1);
  border: 1px solid var(--border);
}
.q-title {
  font-family: 'Outfit', sans-serif; font-size: 26px; font-weight: 600;
  color: var(--text-main); margin: 0 0 32px; line-height: 1.4;
}

.choices-modern { display: flex; flex-direction: column; gap: 16px; margin-bottom: 32px; }
.choice-btn {
  display: flex; align-items: center; gap: 16px;
  width: 100%; padding: 16px 20px;
  background: white; border: 2px solid var(--border);
  border-radius: 16px; text-align: left; cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.choice-btn:hover:not(:disabled) {
  border-color: #A5B4FC; background: #EEF2FF; transform: translateY(-2px);
}
.choice-btn.is-selected {
  border-color: var(--primary); background: #EEF2FF;
  box-shadow: 0 8px 20px rgba(79, 70, 229, 0.15);
}
.choice-letter {
  width: 32px; height: 32px; border-radius: 10px;
  background: #F1F5F9; color: var(--text-muted);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Outfit', sans-serif; font-size: 14px; font-weight: 700;
  transition: all 0.2s;
}
.choice-btn.is-selected .choice-letter { background: var(--primary); color: white; }
.choice-text { flex: 1; font-size: 16px; font-weight: 500; color: var(--text-main); line-height: 1.5; }
.choice-check { color: var(--primary); display: flex; align-items: center; }

.q-actions { display: flex; justify-content: flex-end; align-items: center; min-height: 48px; }
.timeout-msg { display: flex; align-items: center; gap: 8px; color: var(--danger); font-weight: 600; font-size: 15px; }
.next-btn { padding: 12px 28px; font-size: 16px; }

/* Results Screen */
.screen-results { padding: 48px 24px; display: flex; justify-content: center; }
.results-container { max-width: 800px; width: 100%; display: flex; flex-direction: column; gap: 32px; }

.results-hero {
  background: white; border-radius: 32px; padding: 48px; text-align: center;
  border: 1px solid var(--border); box-shadow: 0 20px 40px -10px rgba(0,0,0,0.05);
}
.score-ring {
  position: relative; width: 180px; height: 180px; margin: 0 auto 24px;
}
.score-svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.score-bg { fill: none; stroke: #F1F5F9; stroke-width: 3; }
.score-fill { fill: none; stroke: var(--primary); stroke-width: 3; stroke-linecap: round; transition: stroke-dasharray 1s ease-out; }
.score-content {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.s-pct { font-family: 'Outfit', sans-serif; font-size: 42px; font-weight: 800; color: var(--text-main); line-height: 1; }
.s-txt { font-size: 14px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; }

.grade-a .score-fill { stroke: var(--success); }
.grade-b .score-fill { stroke: #34D399; }
.grade-c .score-fill { stroke: #FBBF24; }
.grade-d .score-fill { stroke: var(--warning); }
.grade-f .score-fill { stroke: var(--danger); }

.result-title { font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 800; color: var(--text-main); margin: 0 0 8px; }
.result-subtitle { font-size: 16px; color: var(--text-muted); margin: 0 0 32px; }
.result-subtitle strong { color: var(--text-main); font-weight: 700; }

.results-metrics { display: flex; justify-content: center; gap: 16px; }
.metric { padding: 16px 24px; border-radius: 16px; background: #F8FAFC; min-width: 120px; }
.m-val { font-family: 'Outfit', sans-serif; font-size: 28px; font-weight: 800; margin-bottom: 4px; }
.m-lbl { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.m-correct { background: rgba(16, 185, 129, 0.1); color: var(--success); }
.m-wrong { background: rgba(239, 68, 68, 0.1); color: var(--danger); }
.m-time { background: rgba(245, 158, 11, 0.1); color: var(--warning); }

.detailed-review { margin-top: 16px; }
.review-title { font-family: 'Outfit', sans-serif; font-size: 24px; font-weight: 700; color: var(--text-main); margin: 0 0 24px; }

.review-card {
  background: white; border: 1px solid var(--border); border-radius: 16px;
  margin-bottom: 16px; overflow: hidden;
}
.review-head {
  padding: 16px 20px; background: #F8FAFC; border-bottom: 1px solid var(--border);
  display: flex; align-items: flex-start; gap: 12px;
}
.r-num { background: var(--text-main); color: white; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 6px; }
.r-text { flex: 1; font-weight: 600; font-size: 15px; color: var(--text-main); line-height: 1.4; }
.r-status { display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 99px; }

.is-correct .r-status { background: rgba(16, 185, 129, 0.1); color: var(--success); }
.is-wrong .r-status { background: rgba(239, 68, 68, 0.1); color: var(--danger); }
.is-timeout .r-status { background: rgba(245, 158, 11, 0.1); color: var(--warning); }
.is-correct { border-left: 4px solid var(--success); }
.is-wrong { border-left: 4px solid var(--danger); }
.is-timeout { border-left: 4px solid var(--warning); }

.review-options { padding: 16px 20px; display: flex; flex-direction: column; gap: 8px; }
.r-option { display: flex; align-items: center; gap: 12px; padding: 10px 16px; border-radius: 10px; background: #F8FAFC; font-size: 14px; }
.o-letter { font-weight: 700; color: var(--text-muted); }
.o-text { flex: 1; color: var(--text-main); }
.o-correct { background: rgba(16, 185, 129, 0.1); font-weight: 600; color: var(--success); }
.o-correct .o-letter, .o-correct .o-text { color: var(--success); }
.o-wrong { background: rgba(239, 68, 68, 0.1); color: var(--danger); text-decoration: line-through; opacity: 0.8; }
.o-icon { margin-left: auto; }

.results-footer { text-align: center; margin-top: 32px; }
.btn-large { padding: 16px 40px; font-size: 16px; }

.toast-error {
  position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
  background: var(--danger); color: white; padding: 12px 24px;
  border-radius: 12px; font-weight: 600; font-size: 14px;
  display: flex; align-items: center; gap: 10px; z-index: 1000;
  box-shadow: 0 10px 25px rgba(239, 68, 68, 0.3);
}

/* Transitions */
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-up-enter-from { opacity: 0; transform: translateY(20px); }
.slide-up-leave-to { opacity: 0; transform: translateY(-20px); }
</style>
