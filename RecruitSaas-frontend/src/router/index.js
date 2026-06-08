import { createRouter, createWebHistory } from 'vue-router'
import { authStore, isTokenExpired } from '../stores/auth'

// Auth
import WelcomePage from '../views/auth/WelcomePage.vue'
import RoleSelection from '../views/auth/RoleSelection.vue'
import RegisterCandidate from '../views/auth/RegisterCandidate.vue'
import RegisterCompany from '../views/auth/RegisterCompany.vue'
import Login from '../views/auth/Login.vue'
import AuthCallback from '../views/auth/AuthCallback.vue'

// Candidate
import OffresView from '../views/candidate/OffresView.vue'
import OffreDetailsApplyView from '../views/candidate/OffreDetailsApplyView.vue'
import CandidatDashboard from '../views/candidate/components/CandidatDashboard.vue'
import CandidatApplications from '../views/candidate/components/CandidatApplications.vue'
import ProfileView from '../views/candidate/components/ProfileView.vue'
import SavedJobsView from '../views/candidate/SavedJobsView.vue'
import ScheduleInterview from '../views/candidate/components/ScheduleInterview.vue'
import CandidatInterviews from '../views/candidate/components/CandidatInterviews.vue'
import PublicJobView from '../views/candidate/PublicJobView.vue'

// Recruiter
import TenantDashboard from '../views/recruiter/TenantDashboard.vue'
import JobOffers from '../views/recruiter/JobOffers.vue'
import Candidates from '../views/recruiter/Candidates.vue'
import TeamManagement from '../views/recruiter/TeamManagement.vue'
import OfferCandidates from '../views/recruiter/OfferCandidates.vue'
import CandidateDetails from '../views/recruiter/CandidateDetails.vue'
import TenantProfile from '../views/recruiter/TenantProfile.vue'
import Reports from '../views/recruiter/Reports.vue'
import InterviewsCalendar from '../views/recruiter/InterviewsCalendar.vue'
import Companys from '../views/recruiter/Companys.vue'

// Job creation
import CreateJobStep1 from '../views/recruiter/CreateJobStep1.vue'
import CreateJobStep2 from '../views/recruiter/CreateJobStep2.vue'
import CreateJobStep3 from '../views/recruiter/CreateJobStep3.vue'

// Admin
import TenantRequests from '../views/admin/TenantRequests.vue'
import TenantManagement from '../views/admin/TenantManagement.vue'
import AdminSettings from '../views/admin/AdminSettings.vue'

// Expert
import ExpertDashboard from '../views/expert/ExpertDashboard.vue'
import ExpertApplications from '../views/expert/ExpertApplications.vue'

// Public interview
import InterviewSchedule from '../views/candidate/components/ScheduleInterview.vue'

const routes = [
  // Auth
  { path: '/', name: 'Welcome', component: WelcomePage },
  { path: '/role-selection', name: 'RoleSelection', component: RoleSelection, meta: { guestOnly: true } },
  { path: '/register-candidate', name: 'RegisterCandidate', component: RegisterCandidate, meta: { guestOnly: true } },
  { path: '/register-company', name: 'RegisterCompany', component: RegisterCompany, meta: { guestOnly: true } },
  { path: '/login', name: 'Login', component: Login, meta: { guestOnly: true } },
  { path: '/auth/callback', name: 'AuthCallback', component: AuthCallback, meta: { guestOnly: true } },

  // Candidate
  { path: '/dashboard', name: 'CandidatDashboard', component: CandidatDashboard, meta: { requiresAuth: true } },
  { path: '/offres', name: 'Offres', component: OffresView, meta: { requiresAuth: true } },
  { path: '/offres/:id', name: 'OffreDetailsApply', component: OffreDetailsApplyView, meta: { requiresAuth: true } },
  { path: '/applications', name: 'Applications', component: CandidatApplications, meta: { requiresAuth: true } },
  {
    path: '/entretien-ia/:avatarNom?',
    name: 'EntretienIA',
    component: () => import('../views/candidate/EntretienView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/candidate/entretien-ia/:avatarNom?',
    redirect: (to) => ({
      path: `/entretien-ia${to.params.avatarNom ? `/${to.params.avatarNom}` : ''}`,
      query: to.query,
      hash: to.hash
    })
  },
  { path: '/saved', name: 'SavedJobs', component: SavedJobsView, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: ProfileView, meta: { requiresAuth: true } },
  { path: '/schedule-interview/:token', name: 'ScheduleInterview', component: ScheduleInterview, meta: { requiresAuth: true } },
  { path: '/interviews', name: 'CandidatInterviews', component: CandidatInterviews, meta: { requiresAuth: true } },

  // Recruiter
  { path: '/recruiter/dashboard', name: 'TenantDashboard', component: TenantDashboard, meta: { requiresAuth: true } },
  { path: '/recruiter/jobs', name: 'JobOffers', component: JobOffers, meta: { requiresAuth: true } },
  { path: '/recruiter/candidates', name: 'Candidates', component: Candidates, meta: { requiresAuth: true } },
  { path: '/recruiter/jobs/:id/candidates', name: 'OfferCandidates', component: OfferCandidates, meta: { requiresAuth: true } },
  { path: '/recruiter/candidates/:id', name: 'CandidateDetails', component: CandidateDetails, meta: { requiresAuth: true } },
  { path: '/recruiter/team', name: 'TeamManagement', component: TeamManagement, meta: { requiresAuth: true } },
  { path: '/recruiter/companys', name: 'CompanysManagment', component: Companys, meta: { requiresAuth: true } },
  { path: '/public/offres/:token', name: 'PublicJob', component: PublicJobView, meta: { requiresAuth: false } },
  { path: '/recruiter/settings', name: 'RecruiterSettings', component: TenantProfile, meta: { requiresAuth: true } },
  { path: '/recruiter/reports', name: 'Reports', component: Reports, meta: { requiresAuth: true } },
  { path: '/recruiter/interviews', name: 'InterviewsCalendar', component: InterviewsCalendar, meta: { requiresAuth: true } },
{
  path: '/quiz/:token',
  name: 'QuizInterface',
  component: () => import('../views/candidate/Quiz.vue'),
  meta: { requiresAuth: false }
},
  // Job creation
  { path: '/recruiter/jobs/create/:id/step1', name: 'CreateJobStep1', component: CreateJobStep1, meta: { requiresAuth: true } },
  { path: '/recruiter/jobs/create/:id/step2', name: 'CreateJobStep2', component: CreateJobStep2, meta: { requiresAuth: true } },
  { path: '/recruiter/jobs/create/:id/step3', name: 'CreateJobStep3', component: CreateJobStep3, meta: { requiresAuth: true } },

  // Admin
  { path: '/admin/dashboard', name: 'AdminDashboard', component: TenantRequests, meta: { requiresAuth: true } },
  { path: '/admin/tenants', name: 'AdminTenantManagement', component: TenantManagement, meta: { requiresAuth: true } },
  { path: '/admin/settings', name: 'AdminSettings', component: AdminSettings, meta: { requiresAuth: true } },
  { path: '/admin/requests', redirect: '/admin/dashboard' },

  // Expert
  { path: '/expert/dashboard', name: 'ExpertDashboard', component: ExpertDashboard, meta: { requiresAuth: true } },
  { path: '/expert/settings', component: () => import('@/views/expert/SettingsExpert.vue'), meta: { requiresAuth: true } },
  { path: '/expert/candidates', component: () => import('@/views/expert/CandidatesExpert.vue') },
  { path: '/expert/interviews', name: 'ExpertInterviews', component: InterviewsCalendar, meta: { requiresAuth: true } },

  // Interview public — choix créneau
  { path: '/interview/:token', name: 'InterviewSchedulePublic', component: () => import('../views/interview/InterviewSchedule.vue') },

  // ✅ Route entretien IA avec avatar — token en query param
  {
    path: '/interview/:token/rejoindre',
    name: 'InterviewLive',
    component: () => import('../views/candidate/EntretienView.vue'),
    meta: { requiresAuth: false }
  },

  // fallback
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  let token = localStorage.getItem('token')

  if (token && isTokenExpired(token)) {
    authStore.logout()
    token = null
  }

  if (to.meta.requiresAuth && !token) {
    next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
  } else if (to.meta.guestOnly && token) {
    const role = authStore.user?.role
    if (role === 'Candidat')    next('/dashboard')
    else if (role === 'Tenant') next('/recruiter/dashboard')
    else if (role === 'Admin')  next('/admin/dashboard')
    else if (role === 'Expert') next('/expert/dashboard')
    else                        next('/')
  } else {
    next()
  }
})

export default router