<template>
  <transition name="modal-fade">
    <div v-if="modelValue" class="overlay" @click.self="$emit('update:modelValue', false)">
      <div class="modal">

        <!-- STEP 1: Configure & Generate -->
        <div v-if="step === 1" class="step-container">
          <div class="modal-head">
            <div class="head-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/><path d="M16 2v4M8 2v4M3 10h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            </div>
            <div class="head-titles">
              <h2 class="modal-title">Schedule Knowledge Quiz</h2>
              <p class="modal-sub"><span class="sub-name">{{ candidateName }}</span><span class="dot">·</span>{{ titreOffre }}</p>
            </div>
            <button class="close-btn" @click="$emit('update:modelValue', false)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="form-section">
              <div class="form-field full">
                <label>Quiz Date & Time <span class="req">*</span></label>
                <div class="input-wrap">
                  <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  <input type="datetime-local" v-model="quizDate" class="field-input with-icon" :min="minDate" />
                </div>
                <p class="field-hint">The quiz link will become active exactly at this time.</p>
              </div>

              <div class="form-grid">
                <div class="form-field">
                  <label>Number of Questions</label>
                  <div class="stepper-wrap">
                    <button class="step-btn" @click="numQuestions = Math.max(3, numQuestions - 1)">−</button>
                    <div class="step-val">{{ numQuestions }}</div>
                    <button class="step-btn" @click="numQuestions = Math.min(20, numQuestions + 1)">+</button>
                  </div>
                </div>

                <div class="form-field">
                  <label>Time per Question</label>
                  <div class="stepper-wrap">
                    <button class="step-btn" @click="timePerQ = Math.max(15, timePerQ - 5)">−</button>
                    <div class="step-val">{{ timePerQ }}s</div>
                    <button class="step-btn" @click="timePerQ = Math.min(300, timePerQ + 5)">+</button>
                  </div>
                </div>
              </div>

              <div class="form-field full">
                <label>Additional Instructions (optional)</label>
                <textarea v-model="instructions" class="field-textarea" rows="3" placeholder="e.g. Please ensure you have a stable internet connection..." />
              </div>
            </div>
          </div>

          <div class="modal-foot">
            <button class="btn-cancel" @click="$emit('update:modelValue', false)">Cancel</button>
            <button class="btn-primary" :disabled="!quizDate || generating" @click="generateQuestions">
              <span v-if="generating" class="spin"></span>
              <span>{{ generating ? 'Generating AI Quiz...' : 'Generate Questions' }}</span>
              <svg v-if="!generating" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
          </div>
        </div>

        <!-- STEP 2: Review & Edit -->
        <div v-if="step === 2" class="step-container">
          <div class="modal-head">
            <div class="head-icon review-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <div class="head-titles">
              <h2 class="modal-title">Review Questions</h2>
              <p class="modal-sub">{{ questions.length }} questions · {{ timePerQ }}s each · {{ formatDate(quizDate) }}</p>
            </div>
            <button class="close-btn" @click="$emit('update:modelValue', false)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
            </button>
          </div>

          <div class="modal-body questions-body">
            <div class="q-toolbar">
              <span class="q-count">Review generated questions for <strong>{{ titreOffre }}</strong></span>
              <button class="btn-add-q" @click="addQuestion">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Add Question
              </button>
            </div>

            <div v-for="(q, qi) in questions" :key="qi" class="q-edit-card">
              <div class="q-edit-head">
                <div class="q-badge">Q{{ qi + 1 }}</div>
                <div class="q-correct-pill" v-if="q.correct_index >= 0 && q.correct_index <= 2">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  Answer {{ ['A','B','C'][q.correct_index] }}
                </div>
                <button class="btn-remove-q" @click="removeQuestion(qi)" v-if="questions.length > 1" title="Remove Question">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </button>
              </div>
              <div class="q-edit-body">
                <textarea v-model="q.question" class="q-text-input" rows="2" placeholder="Enter question text…"/>
                <div class="choices-edit">
                  <div v-for="(choice, ci) in q.choices" :key="ci" class="choice-edit-row" :class="{ 'is-correct': q.correct_index === ci }">
                    <button class="correct-radio" :class="{ active: q.correct_index === ci }" @click="q.correct_index = ci" :title="`Mark choice ${['A','B','C'][ci]} as correct`">
                      {{ ['A','B','C'][ci] }}
                    </button>
                    <input v-model="q.choices[ci]" class="choice-input" :placeholder="`Choice ${['A','B','C'][ci]} text…`" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-foot">
            <button class="btn-cancel" @click="step = 1">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
              Back
            </button>
            <button class="btn-primary" :disabled="!isValid || scheduling" @click="scheduleQuiz">
              <span v-if="scheduling" class="spin"></span>
              <span>{{ scheduling ? 'Scheduling...' : 'Schedule & Notify Candidate' }}</span>
              <svg v-if="!scheduling" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>
        </div>

        <!-- STEP 3: Confirmation -->
        <div v-if="step === 3" class="step-confirm">
          <div class="success-anim">
            <div class="confirm-icon-wrap">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
          </div>
          <h2 class="confirm-title">Quiz Scheduled Successfully!</h2>
          <p class="confirm-sub">An invitation email has been sent to <strong>{{ candidateEmail }}</strong>.</p>
          
          <div class="confirm-card">
            <div class="detail-row">
              <span class="detail-lbl">Candidate</span>
              <strong class="detail-val">{{ candidateName }}</strong>
            </div>
            <div class="detail-row">
              <span class="detail-lbl">Scheduled Date</span>
              <strong class="detail-val">{{ formatDate(quizDate) }}</strong>
            </div>
            <div class="detail-row">
              <span class="detail-lbl">Questions</span>
              <strong class="detail-val">{{ questions.length }} ({{ timePerQ }}s each)</strong>
            </div>
          </div>
          <button class="btn-primary full-width" @click="close">Return to Dashboard</button>
        </div>

      </div>
    </div>
  </transition>
</template>

<script>
import { generateQuiz, scheduleQuiz as apiScheduleQuiz } from '../../services/quizService'

export default {
  name: 'ShortlistQuizModal',
  emits: ['update:modelValue', 'done', 'quiz-scheduled'],
  props: {
    modelValue:     { type: Boolean, default: false },
    offreId:        { type: [String, Number], required: true },
    candidateId:    { type: [String, Number], required: true },
    candidateName:  { type: String, default: '' },
    candidateEmail: { type: String, default: '' },
    titreOffre:     { type: String, default: '' },
  },
  data() {
    return {
      step: 1,
      quizDate: '',
      numQuestions: 10,
      timePerQ: 60,
      instructions: '',
      generating: false,
      scheduling: false,
      questions: [],
    }
  },
  computed: {
    minDate() {
      const d = new Date()
      d.setMinutes(d.getMinutes() + 10)
      return d.toISOString().slice(0, 16)
    },
    isValid() {
      return this.questions.length > 0 &&
        this.questions.every(q =>
          q.question.trim() &&
          q.choices.length === 3 &&
          q.choices.every(c => c.trim()) &&
          q.correct_index >= 0 && q.correct_index <= 2
        )
    }
  },
  methods: {
    formatDate(iso) {
      if (!iso) return '—'
      return new Date(iso).toLocaleString('en-US', {
        weekday: 'short', month: 'short', day: 'numeric',
        year: 'numeric', hour: '2-digit', minute: '2-digit'
      })
    },

    async generateQuestions() {
      this.generating = true
      try {
        const { data } = await generateQuiz(this.offreId, this.numQuestions, this.timePerQ)
        this.questions = (data.questions || []).map((q, i) => ({
          id:            q.id || i + 1,
          question:      q.question || '',
          choices:       Array.isArray(q.choices)
            ? [...q.choices]
            : [q.choiceA || '', q.choiceB || '', q.choiceC || ''],
          correct_index: Math.min(2, Math.max(0, parseInt(q.correct_index ?? q.correctIndex, 10) || 0)),
          time_limit:    q.time_limit ?? q.timeLimit ?? this.timePerQ,
        }))
        this.step = 2
      } catch (e) {
        alert('Failed to generate questions: ' + (e.response?.data?.message || e.message))
      } finally {
        this.generating = false
      }
    },

    addQuestion() {
      this.questions.push({
        id: this.questions.length + 1,
        question: '', choices: ['', '', ''],
        correct_index: 0, time_limit: this.timePerQ
      })
    },

    removeQuestion(idx) {
      this.questions.splice(idx, 1)
      this.questions.forEach((q, i) => { q.id = i + 1 })
    },

    async scheduleQuiz() {
      this.scheduling = true
      try {
        const payload = {
          candidatureId:   this.candidateId,
          scheduledDate:   new Date(this.quizDate).toISOString(),
          timePerQuestion: this.timePerQ,
          instructions:    this.instructions || null,
          questions: this.questions.map(q => ({
            id:           q.id,
            question:     q.question,
            choiceA:      q.choices[0],
            choiceB:      q.choices[1],
            choiceC:      q.choices[2],
            correctIndex: q.correct_index,
            timeLimit:    q.time_limit,
          }))
        }
        const { data } = await apiScheduleQuiz(payload)
        this.quizLink = `${window.location.origin}/quiz/${data.quizToken}`
        this.step = 3
        this.$emit('quiz-scheduled', { candidateId: this.candidateId, quizToken: data.quizToken })
      } catch (e) {
        alert('Failed to schedule quiz: ' + (e.response?.data?.message || e.message))
      } finally {
        this.scheduling = false
      }
    },

    close() {
      this.$emit('update:modelValue', false)
      this.$emit('done')
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
  --surface: #FFFFFF;
  --background: #F8FAFC;
  --border: #E2E8F0;
  --text-main: #0F172A;
  --text-muted: #64748B;
  --ring: rgba(79, 70, 229, 0.2);
}

.overlay {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 1rem;
}

.modal {
  background: var(--surface);
  border-radius: 24px;
  width: 720px; max-width: 96vw; max-height: 90vh;
  display: flex; flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255,255,255,0.1) inset;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
  position: relative;
}

.step-container {
  display: flex; flex-direction: column; max-height: 90vh;
}

.modal-head {
  display: flex; align-items: flex-start; gap: 16px;
  padding: 24px 32px 20px;
  border-bottom: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  position: sticky; top: 0; z-index: 10;
}

.head-icon {
  width: 48px; height: 48px;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  color: white; flex-shrink: 0;
  box-shadow: 0 8px 16px rgba(79, 70, 229, 0.2);
}

.head-icon.review-icon {
  background: linear-gradient(135deg, #10B981, #34D399);
  box-shadow: 0 8px 16px rgba(16, 185, 129, 0.2);
}

.head-titles { flex: 1; }

.modal-title { 
  font-family: 'Outfit', sans-serif;
  font-size: 20px; font-weight: 700; color: var(--text-main); 
  margin: 0 0 4px; letter-spacing: -0.02em;
}

.modal-sub { 
  font-size: 13px; color: var(--text-muted); margin: 0; 
  display: flex; align-items: center; gap: 6px;
}
.sub-name { color: var(--text-main); font-weight: 600; }
.dot { opacity: 0.5; }

.close-btn {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--background);
  color: var(--text-muted);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.close-btn:hover {
  background: #F1F5F9; color: var(--text-main); transform: rotate(90deg);
}

.modal-body { padding: 32px; overflow-y: auto; flex: 1; }

.form-section { display: flex; flex-direction: column; gap: 24px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.form-field { display: flex; flex-direction: column; gap: 8px; }

.form-field label {
  font-size: 13px; font-weight: 600; color: var(--text-main);
  display: flex; align-items: center; gap: 4px;
}
.req { color: var(--danger); }

.input-wrap { position: relative; }
.input-icon {
  position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
  color: var(--text-muted); pointer-events: none;
}

.field-input, .field-textarea {
  width: 100%; padding: 12px 16px;
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 12px;
  font-family: inherit; font-size: 14px; color: var(--text-main);
  transition: all 0.2s; box-sizing: border-box;
}
.field-input.with-icon { padding-left: 42px; }

.field-input:focus, .field-textarea:focus {
  background: white; border-color: var(--primary);
  outline: none; box-shadow: 0 0 0 4px var(--ring);
}
.field-textarea { resize: vertical; min-height: 80px; }

.field-hint { font-size: 12px; color: var(--text-muted); margin: 0; }

.stepper-wrap {
  display: flex; align-items: center;
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 12px; padding: 4px;
}
.step-btn {
  width: 36px; height: 36px;
  border-radius: 8px; border: none;
  background: white; color: var(--text-main);
  font-size: 16px; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.step-btn:hover { background: #F8FAFC; color: var(--primary); }
.step-btn:active { transform: scale(0.95); }
.step-val { flex: 1; text-align: center; font-weight: 600; font-size: 15px; color: var(--text-main); }

/* Review Questions Step */
.questions-body { background: #F8FAFC; padding: 24px 32px; }
.q-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24px;
}
.q-count { font-size: 14px; color: var(--text-muted); }
.q-count strong { color: var(--text-main); font-weight: 600; }

.btn-add-q {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px;
  background: white; color: var(--text-main);
  border: 1px solid var(--border); border-radius: 99px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.btn-add-q:hover { border-color: var(--primary); color: var(--primary); transform: translateY(-1px); }

.q-edit-card {
  background: white; border: 1px solid var(--border);
  border-radius: 16px; margin-bottom: 16px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
  transition: all 0.2s; overflow: hidden;
}
.q-edit-card:hover { border-color: #CBD5E1; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }

.q-edit-head {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 20px; background: #F8FAFC;
  border-bottom: 1px solid var(--border);
}
.q-badge {
  background: var(--text-main); color: white;
  font-size: 11px; font-weight: 700; padding: 4px 10px;
  border-radius: 6px; letter-spacing: 0.05em;
}
.q-correct-pill {
  display: flex; align-items: center; gap: 4px;
  background: rgba(16, 185, 129, 0.1); color: var(--success);
  font-size: 11px; font-weight: 600; padding: 4px 10px;
  border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.2);
}
.btn-remove-q {
  margin-left: auto; width: 28px; height: 28px;
  background: white; border: 1px solid var(--border);
  color: var(--danger); border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.btn-remove-q:hover { background: #FEF2F2; border-color: #FECACA; transform: scale(1.05); }

.q-edit-body { padding: 20px; }
.q-text-input {
  width: 100%; padding: 14px 16px;
  background: white; border: 1px solid var(--border);
  border-radius: 12px; font-family: inherit; font-size: 15px; font-weight: 500;
  color: var(--text-main); resize: vertical; margin-bottom: 16px;
  box-sizing: border-box; transition: all 0.2s;
}
.q-text-input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 4px var(--ring); }

.choices-edit { display: flex; flex-direction: column; gap: 10px; }
.choice-edit-row {
  display: flex; align-items: center; gap: 12px;
  padding: 8px; border-radius: 14px; border: 1px solid transparent;
  transition: all 0.2s;
}
.choice-edit-row:hover { background: #F8FAFC; border-color: var(--border); }
.choice-edit-row.is-correct { background: rgba(16, 185, 129, 0.05); border-color: rgba(16, 185, 129, 0.2); }

.correct-radio {
  width: 32px; height: 32px; border-radius: 10px;
  background: white; border: 1px solid var(--border);
  font-size: 13px; font-weight: 700; color: var(--text-muted);
  cursor: pointer; transition: all 0.2s; flex-shrink: 0;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.correct-radio:hover { border-color: var(--success); color: var(--success); }
.correct-radio.active {
  background: var(--success); border-color: var(--success);
  color: white; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
}

.choice-input {
  flex: 1; padding: 10px 14px;
  background: white; border: 1px solid var(--border);
  border-radius: 10px; font-family: inherit; font-size: 14px;
  color: var(--text-main); transition: all 0.2s;
}
.choice-input:focus { outline: none; border-color: var(--primary); }
.choice-edit-row.is-correct .choice-input {
  border-color: rgba(16, 185, 129, 0.3); background: white;
}

/* Footer & Buttons */
.modal-foot {
  display: flex; justify-content: flex-end; gap: 12px;
  padding: 20px 32px; border-top: 1px solid var(--border);
  background: white; position: sticky; bottom: 0; z-index: 10;
}

.btn-cancel {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 20px; background: white; border: 1px solid var(--border);
  border-radius: 12px; font-size: 14px; font-weight: 600; color: var(--text-main);
  cursor: pointer; transition: all 0.2s;
}
.btn-cancel:hover { background: #F8FAFC; border-color: #CBD5E1; }

.btn-primary {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #4F46E5, #4338CA);
  color: #FFFFFF !important; border: none; border-radius: 12px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all 0.2s; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}
.btn-primary * { color: #FFFFFF !important; }
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px); box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
}
.btn-primary:active:not(:disabled) { transform: translateY(0); }
.btn-primary:disabled { background: #E2E8F0; color: #64748B !important; border: 1px solid #CBD5E1; cursor: not-allowed; box-shadow: none; }
.btn-primary:disabled * { color: #64748B !important; }
.btn-primary.full-width { width: 100%; padding: 14px; font-size: 15px; }

/* Confirmation Step */
.step-confirm {
  display: flex; flex-direction: column; align-items: center;
  padding: 48px 40px; text-align: center;
}
.success-anim { margin-bottom: 24px; animation: bounce 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.confirm-icon-wrap {
  width: 80px; height: 80px; border-radius: 24px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(52, 211, 153, 0.2));
  color: var(--success); display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 0 10px rgba(16, 185, 129, 0.05);
}
.confirm-title { font-family: 'Outfit', sans-serif; font-size: 24px; font-weight: 700; color: var(--text-main); margin: 0 0 8px; }
.confirm-sub { font-size: 15px; color: var(--text-muted); margin: 0 0 32px; }

.confirm-card {
  width: 100%; background: #F8FAFC; border: 1px solid var(--border);
  border-radius: 16px; padding: 20px 24px; margin-bottom: 32px;
}
.detail-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 0; border-bottom: 1px dashed var(--border);
}
.detail-row:last-child { border-bottom: none; padding-bottom: 0; }
.detail-row:first-child { padding-top: 0; }
.detail-lbl { font-size: 13px; color: var(--text-muted); font-weight: 500; }
.detail-val { font-size: 14px; color: var(--text-main); font-weight: 600; }

/* Spinner */
.spin {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: white;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes bounce {
  0% { transform: scale(0.5); opacity: 0; }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}

/* Transitions */
.modal-fade-enter-active, .modal-fade-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .modal, .modal-fade-leave-to .modal { transform: scale(0.95) translateY(10px); }
</style>