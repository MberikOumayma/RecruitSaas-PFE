<template>
  <div style="display:flex; min-height:100vh; background:#f8fafc;">
    <AppSidebar />
    <main class="settings-page">

      <!-- Header global -->
      <GlobalHeader title="Settings" />

      <!-- Contenu -->
      <div class="settings-content">
        <div class="settings-layout">

          <!-- Nav tabs -->
          <aside class="settings-nav">
            <button v-for="tab in tabs" :key="tab.id" class="settings-nav-item" :class="{active:activeTab===tab.id}" @click="activeTab=tab.id">
              <span class="nav-item-icon" v-html="tab.icon"></span>
              <span>{{ tab.label }}</span>
            </button>
          </aside>

          <!-- Panel -->
          <section class="settings-panel">

            <!-- Profile -->
            <div v-if="activeTab==='profile'">
              <div class="panel-header">
                <div class="panel-icon-wrap" style="background:#f0fdf4;"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="#16a34a" stroke-width="1.8"/><path d="M4 20c0-4 3.58-7 8-7s8 3 8 7" stroke="#16a34a" stroke-width="1.8" stroke-linecap="round"/></svg></div>
                <div><h2 class="panel-title">Profile Information</h2><p class="panel-desc">Your public profile visible to recruiters.</p></div>
              </div>
              <div class="form-body">
                <div class="field-row">
                  <div class="field-group"><label>First Name</label><div class="input-wrap"><input v-model="profile.firstName" type="text" placeholder="John"/></div></div>
                  <div class="field-group"><label>Last Name</label><div class="input-wrap"><input v-model="profile.lastName" type="text" placeholder="Doe"/></div></div>
                </div>
                <div class="field-group"><label>Email</label><div class="input-wrap"><input v-model="profile.email" type="email" placeholder="john@company.com"/></div></div>
                <div class="field-group"><label>Phone</label><div class="input-wrap"><input v-model="profile.phone" type="tel" placeholder="+1 (555) 000-0000"/></div></div>
                <div class="field-group"><label>Specialty</label><div class="input-wrap"><input v-model="profile.specialty" type="text" placeholder="e.g. Full-Stack Engineer"/></div></div>
                <div v-if="profileError" class="alert alert-error">{{ profileError }}</div>
                <div v-if="profileSuccess" class="alert alert-success">{{ profileSuccess }}</div>
                <div class="form-footer">
                  <button class="btn-submit" :disabled="profileLoading" @click="sauvegarderProfil">
                    <div v-if="profileLoading" class="spinner-sm"></div>
                    {{ profileLoading?'Saving…':'Save Changes' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Password -->
            <div v-if="activeTab==='password'">
              <div class="panel-header">
                <div class="panel-icon-wrap" style="background:#eff6ff;"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="5" y="11" width="14" height="10" rx="2" stroke="#2563eb" stroke-width="1.8"/><path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="#2563eb" stroke-width="1.8" stroke-linecap="round"/></svg></div>
                <div><h2 class="panel-title">Change Password</h2><p class="panel-desc">Update your password to keep your account secure.</p></div>
              </div>
              <div class="form-body">
                <div class="field-group"><label>Current Password</label><div class="input-wrap"><input v-model="pwd.ancien" :type="showPwd.ancien?'text':'password'" placeholder="••••••••"/><button class="eye-btn" @click="showPwd.ancien=!showPwd.ancien" type="button">👁</button></div></div>
                <div class="field-row">
                  <div class="field-group"><label>New Password</label><div class="input-wrap"><input v-model="pwd.nouveau" :type="showPwd.nouveau?'text':'password'" placeholder="••••••••"/><button class="eye-btn" @click="showPwd.nouveau=!showPwd.nouveau" type="button">👁</button></div></div>
                  <div class="field-group"><label>Confirm Password</label><div class="input-wrap"><input v-model="pwd.confirm" :type="showPwd.confirm?'text':'password'" placeholder="••••••••"/><button class="eye-btn" @click="showPwd.confirm=!showPwd.confirm" type="button">👁</button></div></div>
                </div>
                <div v-if="pwd.nouveau" class="strength-bar-wrap">
                  <div class="strength-bar"><div class="strength-fill" :class="strengthClass" :style="{width:strengthPercent+'%'}"></div></div>
                  <span class="strength-label" :class="strengthClass">{{ strengthLabel }}</span>
                </div>
                <div v-if="pwdError" class="alert alert-error">{{ pwdError }}</div>
                <div v-if="pwdSuccess" class="alert alert-success">{{ pwdSuccess }}</div>
                <div class="form-footer">
                  <button class="btn-submit" :disabled="pwdLoading" @click="changerMotDePasse">
                    <div v-if="pwdLoading" class="spinner-sm"></div>
                    {{ pwdLoading?'Saving…':'Update Password' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Notifications -->
            <div v-if="activeTab==='notifications'">
              <div class="panel-header">
                <div class="panel-icon-wrap" style="background:#fefce8;"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="#ca8a04" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="#ca8a04" stroke-width="1.8" stroke-linecap="round"/></svg></div>
                <div><h2 class="panel-title">Notification Preferences</h2><p class="panel-desc">Choose how and when you receive updates.</p></div>
              </div>
              <div class="form-body">
                <div v-for="n in notifications" :key="n.id" class="notif-row">
                  <div class="notif-text"><p class="notif-title">{{ n.title }}</p><p class="notif-desc">{{ n.desc }}</p></div>
                  <label class="toggle"><input type="checkbox" v-model="n.enabled"/><span class="toggle-track"><span class="toggle-thumb"></span></span></label>
                </div>
                <div v-if="notifError" class="alert alert-error">{{ notifError }}</div>
                <div v-if="notifSuccess" class="alert alert-success">{{ notifSuccess }}</div>
                <div class="form-footer">
                  <button class="btn-submit" :disabled="notifLoading" @click="sauvegarderNotifications">
                    <div v-if="notifLoading" class="spinner-sm"></div>
                    {{ notifLoading?'Saving…':'Save Preferences' }}
                  </button>
                </div>
              </div>
            </div>

          </section>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/services/api'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import GlobalHeader from '@/components/layout/GlobalHeader.vue'

const activeTab=ref('password')
const tabs=[
  {id:'profile',label:'Profile',icon:`<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.8"/><path d="M4 20c0-4 3.58-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>`},
  {id:'password',label:'Security',icon:`<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>`},
  {id:'notifications',label:'Notifications',icon:`<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>`}
]

function decodeToken(token){try{const base64=token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/');return JSON.parse(decodeURIComponent(atob(base64).split('').map(c=>'%'+('00'+c.charCodeAt(0).toString(16)).slice(-2)).join('')))}catch{return{}}}
const token=localStorage.getItem('token')||localStorage.getItem('authToken')||''
const decoded=decodeToken(token)
const expertId=decoded.expertId||null

const pwd=reactive({ancien:'',nouveau:'',confirm:''})
const showPwd=reactive({ancien:false,nouveau:false,confirm:false})
const pwdError=ref(''),pwdSuccess=ref(''),pwdLoading=ref(false)
const strengthPercent=computed(()=>{const p=pwd.nouveau;if(!p)return 0;let s=0;if(p.length>=8)s+=25;if(p.length>=12)s+=15;if(/[A-Z]/.test(p))s+=20;if(/[0-9]/.test(p))s+=20;if(/[^A-Za-z0-9]/.test(p))s+=20;return Math.min(s,100)})
const strengthClass=computed(()=>{const v=strengthPercent.value;if(v>=75)return'strong';if(v>=40)return'medium';return'weak'})
const strengthLabel=computed(()=>{const v=strengthPercent.value;if(v>=75)return'Strong';if(v>=40)return'Moderate';return'Weak'})
async function changerMotDePasse(){pwdError.value='';pwdSuccess.value='';if(!pwd.ancien||!pwd.nouveau||!pwd.confirm){pwdError.value='All fields are required.';return}if(pwd.nouveau!==pwd.confirm){pwdError.value='New passwords do not match.';return}if(pwd.nouveau.length<8){pwdError.value='Password must be at least 8 characters.';return}pwdLoading.value=true;try{await api.post('/auth/change-password',{ancienMotDePasse:pwd.ancien,nouveauMotDePasse:pwd.nouveau});pwdSuccess.value='Password updated successfully.';pwd.ancien='';pwd.nouveau='';pwd.confirm='';setTimeout(()=>{pwdSuccess.value=''},4000)}catch{pwdError.value='Current password is incorrect.'}finally{pwdLoading.value=false}}

const profile=reactive({firstName:'',lastName:'',email:'',phone:'',specialty:''})
const profileLoading=ref(false),profileSuccess=ref(''),profileError=ref('')
async function chargerProfil(){if(!expertId)return;try{const{data}=await api.get(`/expert/${expertId}/profil`);profile.firstName=data.firstName??'';profile.lastName=data.lastName??'';profile.email=data.email??'';profile.phone=data.phone??'';profile.specialty=data.specialty??''}catch(e){console.error(e)}}
async function sauvegarderProfil(){if(!expertId)return;profileError.value='';profileSuccess.value='';profileLoading.value=true;try{await api.put(`/expert/${expertId}/profil`,{firstName:profile.firstName,lastName:profile.lastName,email:profile.email,phone:profile.phone,specialty:profile.specialty});profileSuccess.value='Profile updated successfully.';setTimeout(()=>{profileSuccess.value=''},3000)}catch{profileError.value='Error saving profile.'}finally{profileLoading.value=false}}

const NOTIF_KEY=`notif_prefs_${expertId}`
const notifLoading=ref(false),notifSuccess=ref(''),notifError=ref('')
const notifications=reactive([
  {id:'new_application',title:'New Candidate Application',desc:'Receive an alert when a candidate applies to your assigned offer.',enabled:true},
  {id:'eval_reminder',title:'Evaluation Reminder',desc:'Get notified when a candidate is waiting for your evaluation.',enabled:true},
  {id:'status_updates',title:'Status Updates',desc:"Be informed when a recruiter changes a candidate's status.",enabled:false}
])
function applyNotifPrefs(prefs){if(!Array.isArray(prefs))return;prefs.forEach(pref=>{const n=notifications.find(n=>n.id===pref.id);if(n&&typeof pref.enabled==='boolean')n.enabled=pref.enabled})}
async function chargerNotifications(){if(expertId){try{const{data}=await api.get(`/expert/${expertId}/notifications`);if(Array.isArray(data)&&data.length){applyNotifPrefs(data);return}}catch{}}try{const saved=JSON.parse(localStorage.getItem(NOTIF_KEY)||'null');if(saved)applyNotifPrefs(saved)}catch{}}
async function sauvegarderNotifications(){notifError.value='';notifSuccess.value='';notifLoading.value=true;const payload=notifications.map(n=>({id:n.id,enabled:n.enabled}));if(expertId){try{await api.put(`/expert/${expertId}/notifications`,payload);notifSuccess.value='Preferences saved.';setTimeout(()=>{notifSuccess.value=''},3000);notifLoading.value=false;return}catch{}}try{localStorage.setItem(NOTIF_KEY,JSON.stringify(payload));notifSuccess.value='Preferences saved locally.';setTimeout(()=>{notifSuccess.value=''},3000)}catch{notifError.value='Failed to save.'}finally{notifLoading.value=false}}

onMounted(async()=>{await chargerProfil();await chargerNotifications()})
</script>

<style scoped>
*{box-sizing:border-box}
.settings-page{flex:1;min-width:0;display:flex;flex-direction:column;overflow:hidden;font-family:'Inter',system-ui,sans-serif;color:#1e293b;background:#f8fafc}
.settings-content{flex:1;overflow-y:auto;padding:28px 32px}
.settings-layout{display:flex;gap:24px;align-items:flex-start}
.settings-nav{width:200px;flex-shrink:0;background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:8px;display:flex;flex-direction:column;gap:2px;box-shadow:0 1px 3px rgba(0,0,0,0.05)}
.settings-nav-item{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:9px;font-size:0.84rem;font-weight:500;color:#475569;background:none;border:none;cursor:pointer;text-align:left;font-family:inherit;transition:background 0.13s,color 0.13s;width:100%}
.settings-nav-item:hover{background:#f1f5f9;color:#1A2B4C}
.settings-nav-item.active{background:rgba(26,43,76,0.08);color:#1A2B4C;font-weight:700}
.nav-item-icon{display:flex;align-items:center;flex-shrink:0}
.settings-panel{flex:1;min-width:0;background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:28px 32px;box-shadow:0 1px 4px rgba(0,0,0,0.06)}
.panel-header{display:flex;align-items:flex-start;gap:16px;margin-bottom:28px;padding-bottom:22px;border-bottom:1px solid #f1f5f9}
.panel-icon-wrap{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.panel-title{font-size:1.05rem;font-weight:800;color:#0f172a;margin:0 0 4px}
.panel-desc{font-size:0.82rem;color:#94a3b8;margin:0}
.form-body{display:flex;flex-direction:column;gap:0}
.field-row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.field-group{display:flex;flex-direction:column;gap:5px;margin-bottom:16px}
.field-group label{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#64748b}
.input-wrap{position:relative;display:flex;align-items:center}
.input-wrap input{width:100%;padding:10px 14px;border:1px solid #e2e8f0;border-radius:10px;font-size:0.86rem;color:#0f172a;background:#f8fafc;outline:none;font-family:inherit;transition:border-color 0.15s,background 0.15s}
.input-wrap input:focus{border-color:#1A2B4C;background:#fff;box-shadow:0 0 0 3px rgba(26,43,76,0.07)}
.input-wrap input::placeholder{color:#cbd5e1}
.eye-btn{position:absolute;right:10px;background:none;border:none;cursor:pointer;color:#94a3b8;display:flex;align-items:center;padding:4px;border-radius:5px;font-size:12px}
.strength-bar-wrap{display:flex;align-items:center;gap:10px;margin-bottom:18px}
.strength-bar{flex:1;height:5px;background:#e2e8f0;border-radius:99px;overflow:hidden}
.strength-fill{height:100%;border-radius:99px;transition:width 0.3s ease,background 0.3s ease}
.strength-fill.weak{background:#ef4444}.strength-fill.medium{background:#f59e0b}.strength-fill.strong{background:#22c55e}
.strength-label{font-size:0.7rem;font-weight:700;min-width:55px;text-align:right}
.strength-label.weak{color:#ef4444}.strength-label.medium{color:#f59e0b}.strength-label.strong{color:#22c55e}
.alert{display:flex;align-items:center;gap:8px;font-size:0.82rem;font-weight:600;padding:10px 14px;border-radius:10px;margin-bottom:18px}
.alert-error{color:#ef4444;background:#fef2f2;border:1px solid #fee2e2}
.alert-success{color:#16a34a;background:#f0fdf4;border:1px solid #dcfce7}
.form-footer{display:flex;align-items:center;gap:14px;padding-top:6px;flex-wrap:wrap}
.btn-submit{display:inline-flex;align-items:center;gap:7px;background:#1A2B4C;color:#fff;border:none;border-radius:10px;padding:10px 24px;font-size:0.84rem;font-weight:700;cursor:pointer;font-family:inherit;transition:opacity 0.15s}
.btn-submit:hover:not(:disabled){opacity:0.88}
.btn-submit:disabled{opacity:0.4;cursor:not-allowed}
.notif-row{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 0;border-bottom:1px solid #f1f5f9}
.notif-row:last-of-type{border-bottom:none}
.notif-text{flex:1;min-width:0}
.notif-title{font-size:0.88rem;font-weight:700;color:#0f172a;margin:0 0 3px}
.notif-desc{font-size:0.78rem;color:#94a3b8;margin:0;line-height:1.4}
.toggle{position:relative;display:inline-flex;cursor:pointer;flex-shrink:0}
.toggle input{position:absolute;opacity:0;width:0;height:0}
.toggle-track{width:42px;height:24px;background:#e2e8f0;border-radius:99px;position:relative;transition:background 0.2s}
.toggle input:checked+.toggle-track{background:#1A2B4C}
.toggle-thumb{position:absolute;top:3px;left:3px;width:18px;height:18px;background:#fff;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.15);transition:transform 0.2s}
.toggle input:checked+.toggle-track .toggle-thumb{transform:translateX(18px)}
.spinner-sm{width:13px;height:13px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:spin 0.65s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:900px){.settings-layout{flex-direction:column}.settings-nav{width:100%;flex-direction:row;flex-wrap:wrap}.settings-content{padding:16px}.field-row{grid-template-columns:1fr}}
</style>