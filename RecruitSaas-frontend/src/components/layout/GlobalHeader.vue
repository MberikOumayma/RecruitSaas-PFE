<template>
  <header class="page-header">
    <div class="header-left">
      <h2 class="header-title">{{ title }}</h2>
    </div>
    <div class="header-right">
      <CandidateNotificationBell v-if="userRole === 'Candidat'" />
      <NotificationBell v-else />

      <div class="divider-v"></div>

      <div class="user-profile-container" v-click-outside="closeMenu">
        <div class="user-profile-btn" @click="toggleUserMenu">
          <div class="user-avatar">
            <img
              v-if="avatarSrc"
              :src="avatarSrc"
              :alt="username"
              class="user-avatar-img"
              @error="onAvatarError"
            />
            <span v-else class="user-avatar-initials">{{ userInitials }}</span>
          </div>
          <div class="user-info">
            <p class="user-name">{{ username }}</p>
            <p class="user-role">{{ roleLabel }}</p>
          </div>
          <ChevronsUpDownIcon :size="14" class="expand-icon" />
        </div>

        <div v-if="showUserMenu" class="user-dropdown">
          <div class="dropdown-user-header">
            <p class="dropdown-user-name">{{ username }}</p>
            <p class="dropdown-user-email">{{ userEmail }}</p>
          </div>
          <div class="dropdown-divider"></div>
          <button @click="goToSettings" class="dropdown-item">
            <SettingsIcon :size="15" />
            <span>Settings</span>
          </button>
          <div class="dropdown-divider"></div>
          <button @click="handleLogout" class="dropdown-item text-danger">
            <LogOutIcon :size="15" />
            <span>Disconnect</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import {
  ChevronsUpDownIcon, LogOutIcon, SettingsIcon
} from 'lucide-vue-next'
import { authStore } from '../../stores/auth'
import NotificationBell from '@/components/NotificationBell.vue'
import CandidateNotificationBell from '../../views/candidate/components/CandidateNotificationBell.vue'

const API_BASE = 'http://localhost:5202'

export default {
  name: 'GlobalHeader',
  components: {
    ChevronsUpDownIcon, LogOutIcon, SettingsIcon,
    NotificationBell,
    CandidateNotificationBell,
  },
  directives: {
    'click-outside': {
      mounted(el, binding) {
        el._clickOutside = (e) => { if (!el.contains(e.target)) binding.value() }
        document.addEventListener('click', el._clickOutside)
      },
      unmounted(el) {
        document.removeEventListener('click', el._clickOutside)
      },
    },
  },
  props: {
    title: { type: String, default: '' },
  },
  data() {
    return { showUserMenu: false, avatarBroken: false }
  },
  computed: {
    username() {
      const u = authStore.user
      if (!u) return 'User'
      return u.fullName || u.username || u.email || 'User'
    },
    userEmail() {
      return authStore.user?.email || localStorage.getItem('userEmail') || ''
    },
    userRole() {
      return authStore.user?.role || ''
    },
    roleLabel() {
      const labels = {
        Tenant: 'Recruiter',
        Expert: 'Expert',
        Candidat: 'Candidate',
        Admin: 'Administrator',
      }
      return labels[this.userRole] || this.userRole
    },
    avatarSrc() {
      if (this.avatarBroken) return ''
      const raw = (authStore.user?.photoUrl || '').trim()
      if (!raw) return ''
      if (raw.startsWith('http://') || raw.startsWith('https://')) return raw
      return `${API_BASE}${raw.startsWith('/') ? '' : '/'}${raw}`
    },
    userInitials() {
      const parts = this.username.split(/\s+/).filter(Boolean)
      if (!parts.length) return '?'
      return parts.map(p => p[0]).join('').toUpperCase().slice(0, 2)
    },
  },
  mounted() {
    authStore.fetchCurrentUser()
  },
  methods: {
    onAvatarError() {
      this.avatarBroken = true
    },
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu
    },
    closeMenu() {
      this.showUserMenu = false
    },
    goToSettings() {
      this.showUserMenu = false
      const routes = {
        Tenant: '/recruiter/settings',
        Expert: '/expert/settings',
        Candidat: '/profile',
        Admin: '/admin/settings',
      }
      this.$router.push(routes[this.userRole] || '/')
    },
    handleLogout() {
      authStore.logout()
      this.$router.push('/login')
    },
  },
}
</script>

<style scoped>
.page-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  background: #fff;
  border-bottom: 1px solid rgba(69, 74, 131, 0.1);
  flex-shrink: 0;
}

.header-left { display: flex; align-items: center; gap: 32px; }
.header-title { font-size: 17px; font-weight: 700; margin: 0; color: #0f172a; }

.header-right {
  display: flex; align-items: center; gap: 8px; margin-left: auto;
}

.divider-v { width: 1px; height: 32px; background: rgba(69,74,131,0.1); margin: 0 8px; }

.user-profile-container { position: relative; }

.user-profile-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 6px 10px; border-radius: 8px;
  cursor: pointer; transition: background 0.15s;
}
.user-profile-btn:hover { background: #f8fafc; }

.user-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  border: 1.5px solid rgba(69,74,131,0.12);
  background: #f1f5f9;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; overflow: hidden;
}
.user-avatar-img {
  width: 100%; height: 100%; object-fit: cover;
}
.user-avatar-initials {
  font-size: 12px; font-weight: 700; color: #1A2B4C;
}

.user-info { display: flex; flex-direction: column; min-width: 0; }
.user-name {
  font-size: 13px; font-weight: 700; color: #0f172a; margin: 0; line-height: 1.2;
  max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.user-role { font-size: 11px; color: #64748b; margin: 0; }
.expand-icon { color: #94a3b8; flex-shrink: 0; }

.user-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  width: 220px; background: #fff;
  border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 6px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  z-index: 100;
}

.dropdown-user-header { padding: 8px 10px 10px; }
.dropdown-user-name  { font-size: 13px; font-weight: 700; color: #0f172a; margin: 0 0 2px; }
.dropdown-user-email { font-size: 11px; color: #94a3b8; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.dropdown-divider { height: 1px; background: #f1f5f9; margin: 4px 0; }

.dropdown-item {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 9px 10px;
  border: none; background: none; border-radius: 7px;
  font-size: 13px; font-weight: 500;
  color: #475569; cursor: pointer;
  transition: background 0.15s; font-family: inherit;
}
.dropdown-item:hover { background: #f1f5f9; color: #0f172a; }
.text-danger { color: #ef4444; }
.text-danger:hover { background: #fef2f2 !important; color: #dc2626; }
</style>
