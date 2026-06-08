<template>
  <div style="display:flex; min-height:100vh; background:#f8fafc;">
    <AppSidebar />

    <div v-if="!expertId" class="no-session">
      <p>Invalid session. Please log in again.</p>
    </div>

    <main v-else class="main-content">

      <!-- Header global -->
      <GlobalHeader title="Candidate Evaluation" />

      <!-- Sous-header filtres -->
      <div class="sub-header">
        <p class="page-subtitle">
          {{ filtreOffreId ? offreSelectionnee?.titre : 'All offers' }}
          <span class="sep">·</span>
          {{ candidaturesFiltrees.length }} application{{ candidaturesFiltrees.length !== 1 ? 's' : '' }}
        </p>
        <div class="header-actions">
          <div class="select-wrapper">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" class="sel-icon"><rect x="2" y="7" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2" stroke="currentColor" stroke-width="2"/></svg>
            <select v-model="filtreOffreId" @change="chargerCandidatures" class="select-filter">
              <option :value="null">All offers</option>
              <option v-for="o in offres" :key="o.offreId" :value="o.offreId">{{ o.titre }} ({{ o.nombreCandidatures }})</option>
            </select>
          </div>
          <div class="select-wrapper">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" class="sel-icon"><path d="M3 6h18M7 12h10M11 18h2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            <select v-model="filtreStatut" @change="chargerCandidatures" class="select-filter">
              <option value="">All statuses</option>
              <option value="Nouvelle">New</option>
              <option value="En cours">In Progress</option>
              <option value="Présélectionné">Shortlisted</option>
              <option value="Entretien">Interview</option>
              <option value="Acceptée">Accepted</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-bar">
        <div class="stat-card">
          <div class="stat-icon" style="background:#eff6ff;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2" stroke="#2563eb" stroke-width="1.8" stroke-linecap="round"/></svg></div>
          <div><p class="stat-val">{{ totalCandidatures }}</p><p class="stat-lbl">Total</p></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#f0fdf4;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17l-5-5" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
          <div><p class="stat-val">{{ candidaturesEvaluees }}</p><p class="stat-lbl">Evaluated</p></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#fff7ed;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#f97316" stroke-width="1.8"/><path d="M12 6v6l4 2" stroke="#f97316" stroke-width="1.8" stroke-linecap="round"/></svg></div>
          <div><p class="stat-val">{{ candidaturesFiltrees.length - candidaturesEvaluees }}</p><p class="stat-lbl">Pending</p></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#fefce8;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="#ca8a04" stroke-width="1.8" stroke-linejoin="round"/></svg></div>
          <div><p class="stat-val">{{ avgScore }}</p><p class="stat-lbl">Avg Score</p></div>
        </div>
      </div>

      <div class="content">
        <div v-if="loading" class="center-state"><div class="spinner"></div><p>Loading...</p></div>
        <div v-else-if="candidaturesFiltrees.length===0" class="center-state">
          <p class="empty-title">No applications yet</p>
        </div>
        <div v-else class="cards-grid">
          <div v-for="c in candidaturesFiltrees" :key="c.id" class="eval-card" :class="{evaluated:c.avisExpert}">
            <div class="card-top">
              <div class="card-avatar">{{ initiales(c.candidatNomComplet) }}</div>
              <div class="card-info">
                <h3 class="card-name">{{ c.candidatNomComplet }}</h3>
                <p class="card-email">{{ c.candidatEmail }}</p>
              </div>
              <div class="card-badges">
                <span class="offre-tag">{{ truncate(c.offreTitre,18) }}</span>
                <span class="statut-badge" :class="statutClass(c.statut)">{{ statutLabel(c.statut) }}</span>
              </div>
            </div>
            <div class="mini-pipeline">
              <div v-for="s in PIPELINE_STEPS" :key="s.key" class="mini-step" :class="{'mstep-active':c.statut===s.key,'mstep-done':isPipelineDone(c.statut,s.key),'mstep-danger':s.key==='Refusée'&&c.statut==='Refusée','mstep-success':s.key==='Acceptée'&&c.statut==='Acceptée'}" :title="s.label"></div>
            </div>
            <div v-if="c.tousLesAvis?.length>0" class="team-reviews-mini">
              <p class="team-reviews-label">Team reviews <span class="team-count">{{ c.tousLesAvis.length }}</span><span class="team-avg" :class="scoreBadgeClass(avgTousLesAvis(c))">avg {{ avgTousLesAvis(c).toFixed(1) }}/5</span></p>
              <div class="team-reviews-list">
                <div v-for="(av,i) in c.tousLesAvis" :key="av.id??i" class="team-review-item">
                  <div class="team-avatar" :style="{background:avatarColor(av.expertNom)}">{{ (av.expertNom||'E').charAt(0).toUpperCase() }}</div>
                  <div class="team-review-body"><span class="team-expert-nom">{{ av.expertNom||'Expert' }}</span><span class="team-score-pill" :class="scoreBadgeClass(av.score)">{{ av.score.toFixed(1) }}/5</span></div>
                </div>
              </div>
            </div>
            <div v-if="c.avisExpert" class="current-eval-banner">
              <div class="ceb-left"><span class="ceb-label">My Score</span><span class="ceb-score" :class="scoreColorClass(c.avisExpert.score)">{{ c.avisExpert.score.toFixed(1) }}<span class="ceb-of">/5</span></span></div>
              <div class="ceb-right"><span class="ceb-match" :class="scoreBadgeClass(c.avisExpert.score)">{{ Math.round(c.avisExpert.score*20) }}% Match</span><span class="evaluated-chip">✓ Evaluated</span></div>
            </div>
            <div class="doc-row">
              <button v-if="getCandidateCvUrl(c)" class="btn-cv" @click="openCandidateCv(c)">
                View CV
              </button>
              <span v-else class="no-cv-text">No CV provided</span>
            </div>
            <div class="ai-summary-box">
              <p class="ai-summary-label">AI Summary</p>
              <p class="ai-summary-text">{{ c.resumeIA || 'No AI summary available yet.' }}</p>
            </div>
            <hr class="divider"/>
            <div class="eval-block">
              <div class="eval-block-header"><p class="eval-block-title">{{ c.avisExpert?'Update My Evaluation':'Evaluate This Candidate' }}</p><span v-if="c.avisExpert" class="evaluated-chip">✓ Evaluated</span></div>
              <div class="score-block">
                <div class="score-top-row">
                  <span class="score-lbl">Score</span>
                  <span class="score-display" :class="scoreColorClass(avisForm[c.id]?.score??0)">{{ formatScore(avisForm[c.id]?.score??0) }}<span class="score-of-sm">/5.0</span></span>
                  <span class="score-pct" :class="scoreBadgeClass(avisForm[c.id]?.score??0)">{{ Math.round((avisForm[c.id]?.score??0)*20) }}% match</span>
                </div>
                <input type="range" min="0" max="5" step="0.1" :value="avisForm[c.id]?.score??0" class="score-slider" :style="{'--pct':((avisForm[c.id]?.score??0)/5*100)+'%'}" @input="setScore(c.id,parseFloat($event.target.value))"/>
                <div class="slider-labels"><span v-for="n in [0,1,2,3,4,5]" :key="n">{{ n }}</span></div>
              </div>
              <div class="comment-block">
                <label class="comment-label">Expert Assessment</label>
                <textarea v-if="avisForm[c.id]" v-model="avisForm[c.id].commentaire" placeholder="Describe the candidate's strengths, weaknesses..." class="comment-textarea" rows="4"></textarea>
              </div>
              <div class="eval-actions">
                <button class="btn-submit-eval" :disabled="submitting[c.id]" @click="soumettreAvis(c)">
                  <div v-if="submitting[c.id]" class="spinner-btn"></div>
                  <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  {{ submitting[c.id]?'Saving...':(c.avisExpert?'Update Evaluation':'Submit Evaluation') }}
                </button>
                <transition name="fade"><div v-if="successMsg[c.id]" class="success-pill">Saved!</div></transition>
              </div>
            </div>
            <p class="card-date">Applied {{ formatDate(c.creeLe) }}</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import api from '../../services/api'
import AppSidebar from '../../components/layout/AppSidebar.vue'
import GlobalHeader from '../../components/layout/GlobalHeader.vue'
import { applicationStatusLabel, formatRecruiterDate, isRejectedApplicationStatus } from '../../utils/recruiterI18n'

const IMAGE_EXTS=['png','jpg','jpeg','gif','webp','bmp','tiff','tif','svg','ico','avif']
const OFFICE_EXTS=['doc','docx','ppt','pptx','xls','xlsx']
const API_BASE='http://localhost:5202/api'
const PIPELINE_STEPS=[{key:'Nouvelle',label:'Applied'},{key:'En cours',label:'In Review'},{key:'Présélectionné',label:'Shortlisted'},{key:'Entretien',label:'Interview'},{key:'Acceptée',label:'Accepted'},{key:'Refusée',label:'Declined'}]
const PIPELINE_ORDER=['Nouvelle','En cours','Présélectionné','Entretien','Acceptée','Refusée']

function isPipelineDone(cur,key){if(key==='Refusée'||key==='Acceptée')return false;const ci=PIPELINE_ORDER.indexOf(cur),si=PIPELINE_ORDER.indexOf(key);return si<ci&&ci!==-1}
function avgTousLesAvis(c){if(!c.tousLesAvis?.length)return 0;return c.tousLesAvis.reduce((a,v)=>a+v.score,0)/c.tousLesAvis.length}
function getExpertId(){const t=localStorage.getItem('token');if(!t)return null;try{return JSON.parse(atob(t.split('.')[1])).expertId??null}catch{return null}}
function getExtFromUrl(url){if(!url)return'';try{const f=url.split('?')[0].split('/').pop();const d=f.lastIndexOf('.');return d===-1?'':f.substring(d+1).toLowerCase()}catch{return''}}
function proxyUrl(u){return(!u)?'':getExtFromUrl(u)==='pdf'?`${API_BASE}/expert/proxy?url=${encodeURIComponent(u)}`:u}
function getFileType(url){const e=getExtFromUrl(url);if(e==='pdf')return'pdf';if(IMAGE_EXTS.includes(e))return'image';if(OFFICE_EXTS.includes(e))return'office';return'other'}
function getFileName(url){return url?decodeURIComponent(url.split('?')[0].split('/').pop()):'File'}
function getCandidateCvUrl(c){return c?.cvUrl||c?.cvURL||c?.CvUrl||''}
async function openCandidateCv(c){
  const cvUrl=getCandidateCvUrl(c)
  if(!cvUrl)return
  window.open(cvUrl,'_blank','noopener,noreferrer')
}

const expertId=getExpertId(),offres=ref([]),candidatures=ref([]),loading=ref(false),filtreOffreId=ref(null),filtreStatut=ref(''),avisForm=reactive({}),submitting=reactive({}),successMsg=reactive({}),cvOuvert=reactive({}),pdfLoading=reactive({}),pdfError=reactive({}),pdfRendered=new Set()

let pdfjsLib=null
async function getPdfjsLib(){if(pdfjsLib)return pdfjsLib;const pdfjs=await import('pdfjs-dist');pdfjs.GlobalWorkerOptions.workerSrc=new URL('pdfjs-dist/build/pdf.worker.min.mjs',import.meta.url).toString();pdfjsLib=pdfjs;return pdfjsLib}

const totalCandidatures=computed(()=>offres.value.reduce((a,o)=>a+(o.nombreCandidatures??0),0))
const candidaturesFiltrees=computed(()=>{
  const list=(Array.isArray(candidatures.value)?candidatures.value:[]).filter(c=>!isRejectedApplicationStatus(c.statut))
  return list
})
const offreSelectionnee=computed(()=>offres.value.find(o=>o.offreId===filtreOffreId.value))
const candidaturesEvaluees=computed(()=>candidaturesFiltrees.value.filter(c=>c.avisExpert).length)
const avgScore=computed(()=>{const ev=candidaturesFiltrees.value.filter(c=>c.avisExpert);if(!ev.length)return'—';return(ev.reduce((a,c)=>a+(c.avisExpert.score??0),0)/ev.length).toFixed(1)})

onMounted(async()=>{if(!expertId)return;await chargerOffres();await chargerCandidatures()})

async function chargerOffres(){try{const{data}=await api.get(`/expert/${expertId}/offres`);offres.value=Array.isArray(data)?data:[]}catch{offres.value=[]}}
async function chargerCandidatures(){loading.value=true;try{const params={};if(filtreOffreId.value)params.offreId=filtreOffreId.value;if(filtreStatut.value)params.statut=filtreStatut.value;const{data}=await api.get(`/expert/${expertId}/candidatures`,{params});candidatures.value=Array.isArray(data)?data:[];candidatures.value.forEach(c=>{if(!avisForm[c.id])avisForm[c.id]={score:c.avisExpert?.score??0,commentaire:c.avisExpert?.commentaire??''}})}catch{candidatures.value=[]}finally{loading.value=false}}
async function soumettreAvis(candidature){const form=avisForm[candidature.id];if(!form)return;submitting[candidature.id]=true;successMsg[candidature.id]='';try{await api.post(`/expert/${expertId}/avis`,{candidatureId:candidature.id,score:form.score,commentaire:form.commentaire});successMsg[candidature.id]='Saved!';await chargerCandidatures();setTimeout(()=>{successMsg[candidature.id]=''},3000)}catch{}finally{submitting[candidature.id]=false}}

function setScore(id,val){if(!avisForm[id])avisForm[id]={score:0,commentaire:''};avisForm[id].score=val}
function formatScore(val){return(typeof val==='number'?val:0).toFixed(1)}
function scoreColorClass(val){return val>=4?'score-high':val>=2.5?'score-mid':'score-low'}
function scoreBadgeClass(score){if(score==null)return'score-none';if(score>=4)return'score-high';if(score>=2.5)return'score-mid';return'score-low'}
function initiales(nom){if(!nom)return'?';return nom.split(' ').map(p=>p[0]).join('').toUpperCase().slice(0,2)}
function truncate(str,n){return str&&str.length>n?str.slice(0,n)+'…':str||'—'}
function formatDate(dateStr){if(!dateStr)return'—';return formatRecruiterDate(dateStr,{year:'numeric',month:'long',day:'numeric'})}
function avatarColor(name){if(!name)return'#1A2B4C';const c=['#1A2B4C','#0d4f8c','#1a3c2e','#3b1f4e','#7c3238','#1e4a6e','#2d4a1e'];let h=0;for(let i=0;i<name.length;i++)h=name.charCodeAt(i)+((h<<5)-h);return c[Math.abs(h)%c.length]}
function statutLabel(s){return applicationStatusLabel(s)}
function statutClass(s){return{'st-new':s==='Nouvelle','st-inprogress':s==='En cours','st-shortlisted':s==='Présélectionné','st-interview':s==='Entretien','st-accepted':s==='Acceptée','st-declined':s==='Refusée'}}
</script>

<style scoped>
*{box-sizing:border-box}
.main-content{flex:1;min-width:0;display:flex;flex-direction:column;overflow:hidden;font-family:'Plus Jakarta Sans',system-ui,sans-serif;color:#1e293b;background:#f8fafc}
.no-session{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:#94a3b8;font-family:'Plus Jakarta Sans',system-ui,sans-serif}
.sub-header{display:flex;justify-content:space-between;align-items:center;padding:12px 32px;background:#fff;border-bottom:1px solid #e2e8f0;flex-shrink:0;flex-wrap:wrap;gap:10px}
.page-subtitle{font-size:0.83rem;color:#94a3b8;margin:0}.sep{margin:0 5px}
.header-actions{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.select-wrapper{position:relative;display:inline-flex;align-items:center}
.sel-icon{position:absolute;left:10px;pointer-events:none;color:#94a3b8}
.select-filter{appearance:none;background:#fff;border:1px solid #e2e8f0;color:#334155;padding:8px 14px 8px 30px;border-radius:9px;font-size:0.81rem;font-weight:500;cursor:pointer;font-family:inherit;outline:none;min-width:150px}
.stats-bar{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;padding:16px 32px;background:#f8fafc;border-bottom:1px solid #e2e8f0;flex-shrink:0}
.stat-card{background:#fff;border:1px solid #e2e8f0;border-radius:13px;padding:14px 16px;display:flex;align-items:center;gap:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05)}
.stat-icon{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.stat-val{font-size:1.3rem;font-weight:800;color:#0f172a;margin:0;line-height:1}
.stat-lbl{font-size:0.63rem;color:#94a3b8;margin:3px 0 0;font-weight:600;text-transform:uppercase;letter-spacing:0.07em}
.content{flex:1;overflow-y:auto;padding:24px 32px}
.center-state{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:72px 20px;gap:10px;color:#94a3b8}
.empty-title{font-size:0.95rem;font-weight:700;color:#475569;margin:0}
.cards-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(480px,1fr));gap:18px}
.eval-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:22px;box-shadow:0 1px 4px rgba(0,0,0,0.05);transition:box-shadow 0.2s,transform 0.15s}
.eval-card:hover{box-shadow:0 6px 24px rgba(0,0,0,0.08);transform:translateY(-1px)}
.eval-card.evaluated{border-left:3px solid #1A2B4C}
.card-top{display:flex;align-items:flex-start;gap:12px;margin-bottom:10px}
.card-avatar{width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,#1A2B4C,#4a6fa5);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.82rem;flex-shrink:0}
.card-info{flex:1;min-width:0}
.card-name{font-size:0.93rem;font-weight:700;color:#0f172a;margin:0 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card-email{font-size:0.76rem;color:#94a3b8;margin:0}
.card-badges{display:flex;flex-direction:column;align-items:flex-end;gap:4px;flex-shrink:0}
.offre-tag{background:#f1f5f9;color:#475569;font-size:0.66rem;font-weight:600;padding:3px 8px;border-radius:99px;max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.statut-badge{font-size:0.65rem;font-weight:700;padding:3px 8px;border-radius:99px;text-transform:uppercase;letter-spacing:0.05em}
.st-new{background:#eff6ff;color:#2563eb}.st-inprogress{background:#fff7ed;color:#f97316}.st-shortlisted{background:#f0fdf4;color:#16a34a}.st-interview{background:#fdf4ff;color:#a855f7}.st-accepted{background:#f0fdf4;color:#16a34a}.st-declined{background:#fef2f2;color:#ef4444}
.mini-pipeline{display:flex;gap:3px;align-items:center;margin-bottom:10px}
.mini-step{flex:1;height:5px;border-radius:99px;background:#e2e8f0;transition:background 0.2s}
.mstep-done{background:#86efac}.mstep-active{background:#1A2B4C}.mstep-danger{background:#fca5a5}.mstep-success{background:#86efac}
.team-reviews-mini{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px 12px;margin-bottom:12px}
.team-reviews-label{font-size:0.68rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.07em;margin:0 0 8px;display:flex;align-items:center;gap:6px}
.team-count{background:#1A2B4C;color:#fff;font-size:0.6rem;font-weight:700;padding:1px 6px;border-radius:99px}
.team-avg{font-size:0.68rem;font-weight:700;padding:2px 7px;border-radius:99px}
.team-avg.score-high{background:#dcfce7;color:#16a34a}.team-avg.score-mid{background:#fef9c3;color:#a16207}.team-avg.score-low{background:#fee2e2;color:#dc2626}
.team-reviews-list{display:flex;flex-direction:column;gap:6px}
.team-review-item{display:flex;align-items:center;gap:8px}
.team-avatar{width:26px;height:26px;border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.65rem;font-weight:800;flex-shrink:0}
.team-review-body{display:flex;align-items:center;gap:6px;flex:1}
.team-expert-nom{font-size:0.78rem;font-weight:600;color:#334155;flex:1}
.team-score-pill{font-size:0.68rem;font-weight:800;padding:2px 8px;border-radius:99px}
.team-score-pill.score-high{background:#dcfce7;color:#16a34a}.team-score-pill.score-mid{background:#fef9c3;color:#a16207}.team-score-pill.score-low{background:#fee2e2;color:#dc2626}
.current-eval-banner{display:flex;align-items:center;justify-content:space-between;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px 14px;margin-bottom:12px}
.ceb-left{display:flex;align-items:baseline;gap:8px}.ceb-label{font-size:0.7rem;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.07em}
.ceb-score{font-size:1.4rem;font-weight:800;line-height:1}.ceb-of{font-size:0.75rem;color:#94a3b8;font-weight:500}
.ceb-right{display:flex;align-items:center;gap:8px}
.ceb-match{font-size:0.72rem;font-weight:800;padding:3px 9px;border-radius:99px}
.score-high{color:#22c55e}.score-mid{color:#f59e0b}.score-low{color:#ef4444}
.score-high.ceb-match{background:#dcfce7}.score-mid.ceb-match{background:#fef9c3}.score-low.ceb-match{background:#fee2e2}
.evaluated-chip{display:inline-flex;align-items:center;gap:3px;background:#f0fdf4;color:#16a34a;font-size:0.66rem;font-weight:700;padding:3px 8px;border-radius:99px;border:1px solid #bbf7d0}
.doc-row{display:flex;align-items:center;justify-content:flex-start;margin-bottom:10px}
.btn-cv{display:inline-flex;align-items:center;gap:6px;background:#eff6ff;color:#1A2B4C;border:1px solid #bfdbfe;border-radius:8px;padding:6px 11px;font-size:0.74rem;font-weight:700;text-decoration:none}
.btn-cv:hover{background:#dbeafe}
.no-cv-text{font-size:0.72rem;color:#94a3b8;font-style:italic}
.ai-summary-box{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px 12px;margin-bottom:12px}
.ai-summary-label{font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin:0 0 6px}
.ai-summary-text{font-size:0.78rem;color:#334155;line-height:1.5;margin:0}
.divider{border:none;border-top:1px solid #f1f5f9;margin:16px 0}
.eval-block-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.eval-block-title{font-size:0.76rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin:0}
.score-block{margin-bottom:14px}
.score-top-row{display:flex;align-items:baseline;gap:10px;margin-bottom:10px}
.score-lbl{font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#94a3b8}
.score-display{font-size:1.4rem;font-weight:800;line-height:1}
.score-of-sm{font-size:0.74rem;font-weight:500;color:#94a3b8}
.score-pct{font-size:0.72rem;font-weight:700;padding:2px 8px;border-radius:99px;margin-left:auto}
.score-pct.score-high{background:#dcfce7;color:#16a34a}.score-pct.score-mid{background:#fef9c3;color:#a16207}.score-pct.score-low{background:#fee2e2;color:#dc2626}.score-pct.score-none{background:#f1f5f9;color:#94a3b8}
.score-slider{-webkit-appearance:none;appearance:none;width:100%;height:6px;border-radius:99px;outline:none;cursor:pointer;background:linear-gradient(to right,#1A2B4C 0%,#1A2B4C var(--pct,0%),#e2e8f0 var(--pct,0%),#e2e8f0 100%)}
.score-slider::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;border-radius:50%;background:#fff;border:2.5px solid #1A2B4C;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,0.15)}
.slider-labels{display:flex;justify-content:space-between;padding:3px 1px 0}
.slider-labels span{font-size:0.6rem;color:#cbd5e1;font-weight:600}
.comment-block{margin-bottom:14px}
.comment-label{display:block;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#64748b;margin-bottom:6px}
.comment-textarea{width:100%;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;color:#334155;padding:10px 13px;font-size:0.83rem;resize:vertical;font-family:inherit;line-height:1.6;outline:none}
.comment-textarea:focus{border-color:#1A2B4C;background:#fff}
.eval-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.btn-submit-eval{display:inline-flex;align-items:center;gap:7px;background:#1A2B4C;color:#fff;border:none;border-radius:10px;padding:10px 20px;font-size:0.83rem;font-weight:700;cursor:pointer;font-family:inherit;transition:opacity 0.15s}
.btn-submit-eval:hover:not(:disabled){opacity:0.88}
.btn-submit-eval:disabled{opacity:0.4;cursor:not-allowed}
.success-pill{display:inline-flex;align-items:center;gap:5px;background:#f0fdf4;color:#16a34a;font-size:0.78rem;font-weight:700;padding:6px 12px;border-radius:99px;border:1px solid #bbf7d0}
.card-date{font-size:0.68rem;color:#cbd5e1;margin:10px 0 0;text-align:right;font-weight:500}
.spinner{width:26px;height:26px;border:2.5px solid #e2e8f0;border-top-color:#1A2B4C;border-radius:50%;animation:spin 0.65s linear infinite}
.spinner-btn{width:13px;height:13px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:spin 0.65s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.fade-enter-active,.fade-leave-active{transition:opacity 0.3s}
.fade-enter-from,.fade-leave-to{opacity:0}
@media(max-width:1100px){.stats-bar{grid-template-columns:repeat(2,1fr)}}
@media(max-width:900px){.content{padding:16px}.cards-grid{grid-template-columns:1fr}}
</style>