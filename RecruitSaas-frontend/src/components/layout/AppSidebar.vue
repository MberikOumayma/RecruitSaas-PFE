<template>
  <aside class="sidebar">
    <div class="sidebar-logo">
      <img src="/appli-logo.png" alt="TalentFlow" class="sidebar-brand-logo" />
      <p class="logo-sub">{{ planName }}</p>
    </div>

    <nav class="sidebar-nav">
      <!-- Tenant Nav -->
      <template v-if="userRole === 'Tenant'">
        <router-link to="/recruiter/dashboard" class="nav-item"><LayoutDashboardIcon :size="18" /><span>Dashboard</span></router-link>
        <router-link to="/recruiter/companys"  class="nav-item"><Building :size="18" /><span>Companies</span></router-link>
        <router-link to="/recruiter/jobs"      class="nav-item"><BriefcaseIcon :size="18" /><span>Jobs</span></router-link>
        <router-link to="/recruiter/candidates" class="nav-item"><UsersIcon :size="18" /><span>Candidates</span></router-link>
        <router-link to="/recruiter/team"      class="nav-item"><UserIcon :size="18" /><span>Team</span></router-link>
        <router-link to="/recruiter/reports"   class="nav-item"><BarChart2Icon :size="18" /><span>Reports</span></router-link>
        <router-link to="/recruiter/interviews" class="nav-item"><VideoIcon :size="18" /><span>Interviews</span></router-link>
        <router-link to="/recruiter/settings"  class="nav-item"><SettingsIcon :size="18" /><span>Settings</span></router-link>
      </template>

      <!-- Candidat Nav -->
      <template v-else-if="userRole === 'Candidat'">
        <p class="nav-section-label">MAIN MENU</p>
        <router-link to="/dashboard"    class="nav-item" exact><LayoutDashboardIcon :size="18" /><span>Dashboard</span></router-link>
        <router-link to="/offres"       class="nav-item" exact><SearchIcon :size="18" /><span>Job Exploration</span></router-link>
        <router-link to="/applications" class="nav-item" exact><FileTextIcon :size="18" /><span>Applications</span></router-link>
        <router-link to="/saved"        class="nav-item" exact>
          <BookmarkIcon :size="18" /><span>Saved</span>
          <span v-if="savedCount > 0" class="nav-badge">{{ savedCount }}</span>
        </router-link>
        <p class="nav-section-label">PREFERENCES</p>
        <router-link to="/profile" class="nav-item" exact><UserIcon :size="18" /><span>Profile</span></router-link>
        <router-link to="/interviews" class="nav-item"><VideoIcon :size="18" /><span>Interviews</span></router-link>
      </template>

      <!-- Admin Nav -->
      <template v-else-if="userRole === 'Admin'">
        <p class="nav-section-label">MAIN MENU</p>
        <router-link to="/admin/dashboard" class="nav-item"><LayoutDashboardIcon :size="18" /><span>Dashboard</span></router-link>
        <router-link to="/admin/tenants"   class="nav-item"><BuildingIcon :size="18" /><span>Tenant Management</span></router-link>
        <router-link to="/admin/settings"  class="nav-item"><SettingsIcon :size="18" /><span>Settings</span></router-link>
      </template>

      <!-- Expert Nav -->
      <template v-else-if="userRole === 'Expert'">
        <router-link to="/expert/dashboard"    class="nav-item"><LayoutDashboardIcon :size="18" /><span>Dashboard</span></router-link>
        
        <router-link to="/expert/candidates"   class="nav-item"><UsersIcon :size="18" /><span>Applications</span></router-link>
        <router-link to="/expert/interviews"   class="nav-item"><VideoIcon :size="18" /><span>Interviews</span></router-link>
        <router-link to="/expert/settings"     class="nav-item"><SettingsIcon :size="18" /><span>Settings</span></router-link>
      </template>
    </nav>
  </aside>
</template>

<script>
import {
  LayoutDashboardIcon, BriefcaseIcon, UsersIcon,
  UserIcon, SearchIcon, FileTextIcon, SettingsIcon,
  Building, BuildingIcon,
  BookmarkIcon, BarChart2Icon, VideoIcon
} from 'lucide-vue-next'
import { authStore } from '../../stores/auth'
import { getSavedCount } from '../../utils/savedOffres'

export default {
  name: 'AppSidebar',
  components: {
    LayoutDashboardIcon, BriefcaseIcon, UsersIcon,
    UserIcon, SearchIcon, FileTextIcon, SettingsIcon,
    Building, BuildingIcon,
    BookmarkIcon, BarChart2Icon, VideoIcon
  },
  data() {
    return { savedCount: 0 }
  },
  mounted() {
    this.savedCount = getSavedCount()
    window.addEventListener('saved-offres-changed', this.onSavedOffresChanged)
  },
  beforeUnmount() {
    window.removeEventListener('saved-offres-changed', this.onSavedOffresChanged)
  },
  computed: {
    userRole() { return authStore.user?.role || 'Tenant' },
    planName() {
      if (this.userRole === 'Admin')    return 'Admin Portal'
      if (this.userRole === 'Tenant')   return 'Enterprise Plan'
      if (this.userRole === 'Expert')   return 'Expert Plan'
      if (this.userRole === 'Candidat') return 'Candidate Portal'
      return 'Free Plan'
    }
  },
  methods: {
    onSavedOffresChanged() { this.savedCount = getSavedCount() }
  }
}
</script>

<style scoped>
.sidebar {
  width: 232px;
  min-width: 232px;
  max-width: 232px;
  display: flex; flex-direction: column;
  flex-shrink: 0; height: 100vh; background: #ffffff;
  border-right: 1px solid #e2e8f0; position: sticky; top: 0;
}
.sidebar-logo {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: clamp(8px, 1.4vw, 14px);
  padding: 16px 10px 14px;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
}
.sidebar-brand-logo {
  width: 88%;
  height: auto;
  max-height: clamp(52px, 20vw, 110px);
  object-fit: contain;
  object-position:  center;
  display: block;
}
.logo-sub {
  font-size: clamp(10px, 1.1vw, 12px);
  color: #94a3b8;
  margin: 0;
  line-height: 1.35;
  
}
.sidebar-nav { flex:1; padding:0 8px; display:flex; flex-direction:column; gap:2px; overflow-y:auto; }
.nav-item {
  display:flex; align-items:center; gap:8px;
  padding:7px 10px; border-radius:8px;
  font-size:12.5px; font-weight:500;
  color:#475569; text-decoration:none;
  transition:background 0.15s, color 0.15s;
}
.nav-item:hover { background:#f1f5f9; color:#1A2B4C; }
.nav-item.router-link-active { background:rgba(26,43,76,0.1); color:#1A2B4C; font-weight:700; }
.nav-section-label {
  font-size:10px; font-weight:700; text-transform:uppercase;
  letter-spacing:0.08em; color:#94a3b8;
  padding:14px 12px 4px; margin:0;
}
.nav-badge {
  margin-left:auto; background:#1A2B4C; color:#fff;
  font-size:10px; font-weight:700;
  padding:1px 6px; border-radius:99px;
}

@media (max-height: 700px) {
  .sidebar-brand-logo { max-height: clamp(44px, 9vh, 88px); }
  .sidebar-logo { padding-top: 12px; gap: 8px; }
}
</style>