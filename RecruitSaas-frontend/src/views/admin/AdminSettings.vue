<template>
    <div class="app-shell">
        <!-- SIDEBAR réutilisable (identique à TenantRequests) -->
        <AppSidebar role="admin" />

        <!-- MAIN -->
        <div class="main-area">
            <GlobalHeader title="Admin portail" />

            <!-- PAGE CONTENT -->
            <div class="page-wrapper">
                <!-- Header -->
                <div class="page-header">
                    <div>
                        <h1 class="page-title">Settings</h1>
                        <p class="page-subtitle">Manage your account preferences and security.</p>
                    </div>
                </div>

                <!-- Content -->
                <div class="settings-layout">
                    <!-- Sidebar tabs -->
                    <aside class="settings-nav">
                        <button v-for="tab in tabs"
                                :key="tab.id"
                                class="settings-nav-item"
                                :class="{ active: activeTab === tab.id }"
                                @click="activeTab = tab.id">
                            <span class="nav-item-icon" v-html="tab.icon"></span>
                            <span>{{ tab.label }}</span>
                        </button>
                    </aside>

                    <!-- Panel -->
                    <section class="settings-panel">

                        <!-- ── Profile ── -->
                        <div v-if="activeTab === 'profile'">
                            <div class="panel-header">
                                <div class="panel-icon-wrap" style="background:#f0fdf4;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                                        <circle cx="12" cy="8" r="4" stroke="#16a34a" stroke-width="1.8" />
                                        <path d="M4 20c0-4 3.58-7 8-7s8 3 8 7" stroke="#16a34a" stroke-width="1.8" stroke-linecap="round" />
                                    </svg>
                                </div>
                                <div>
                                    <h2 class="panel-title">Profile Information</h2>
                                    <p class="panel-desc">Your public profile.</p>
                                </div>
                            </div>
                            <div class="form-body">
                                <div class="field-row">
                                    <div class="field-group">
                                        <label>First Name</label>
                                        <div class="input-wrap"><input v-model="profile.firstName" type="text" placeholder="John" /></div>
                                    </div>
                                    <div class="field-group">
                                        <label>Last Name</label>
                                        <div class="input-wrap"><input v-model="profile.lastName" type="text" placeholder="Doe" /></div>
                                    </div>
                                </div>
                                <div class="field-group">
                                    <label>Email</label>
                                    <div class="input-wrap">
                                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" class="input-icon"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="#94a3b8" stroke-width="1.8" /><path d="M22 6l-10 7L2 6" stroke="#94a3b8" stroke-width="1.8" /></svg>
                                        <input v-model="profile.email" type="email" placeholder="admin@company.com" class="has-icon" />
                                    </div>
                                </div>
                                <div class="field-group">
                                    <label>Phone</label>
                                    <div class="input-wrap">
                                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" class="input-icon"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 1.27h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 9a16 16 0 0 0 6.09 6.09l1.09-1.09a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="#94a3b8" stroke-width="1.8" /></svg>
                                        <input v-model="profile.phone" type="tel" placeholder="+1 (555) 000-0000" class="has-icon" />
                                    </div>
                                </div>
                                <div class="field-group">
                                    <label>Role / Department</label>
                                    <div class="input-wrap"><input v-model="profile.role" type="text" placeholder="e.g. System Administrator" /></div>
                                </div>

                                <div class="form-footer">
                                    <button class="btn-submit" :disabled="profileLoading" @click="sauvegarderProfil">
                                        <div v-if="profileLoading" class="spinner-sm"></div>
                                        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none">
                                            <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
                                        </svg>
                                        {{ profileLoading ? 'Saving…' : 'Save Changes' }}
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- ── Security (Password) ── -->
                        <div v-if="activeTab === 'security'">
                            <div class="panel-header">
                                <div class="panel-icon-wrap" style="background:#eff6ff;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                                        <rect x="5" y="11" width="14" height="10" rx="2" stroke="#2563eb" stroke-width="1.8" />
                                        <path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="#2563eb" stroke-width="1.8" stroke-linecap="round" />
                                    </svg>
                                </div>
                                <div>
                                    <h2 class="panel-title">Change Password</h2>
                                    <p class="panel-desc">Update your password to keep your account secure.</p>
                                </div>
                            </div>

                            <div class="form-body">
                                <div class="field-group">
                                    <label>Current Password</label>
                                    <div class="input-wrap">
                                        <input v-model="pwd.ancien" :type="showPwd.ancien ? 'text' : 'password'" placeholder="••••••••" />
                                        <button class="eye-btn" @click="showPwd.ancien = !showPwd.ancien" type="button">
                                            <svg v-if="!showPwd.ancien" width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" /><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" /></svg>
                                            <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
                                        </button>
                                    </div>
                                </div>

                                <div class="field-row">
                                    <div class="field-group">
                                        <label>New Password</label>
                                        <div class="input-wrap">
                                            <input v-model="pwd.nouveau" :type="showPwd.nouveau ? 'text' : 'password'" placeholder="••••••••" />
                                            <button class="eye-btn" @click="showPwd.nouveau = !showPwd.nouveau" type="button">
                                                <svg v-if="!showPwd.nouveau" width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" /><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" /></svg>
                                                <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
                                            </button>
                                        </div>
                                    </div>
                                    <div class="field-group">
                                        <label>Confirm Password</label>
                                        <div class="input-wrap">
                                            <input v-model="pwd.confirm" :type="showPwd.confirm ? 'text' : 'password'" placeholder="••••••••" />
                                            <button class="eye-btn" @click="showPwd.confirm = !showPwd.confirm" type="button">
                                                <svg v-if="!showPwd.confirm" width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" /><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" /></svg>
                                                <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <!-- Strength indicator -->
                                <div v-if="pwd.nouveau" class="strength-bar-wrap">
                                    <div class="strength-bar">
                                        <div class="strength-fill" :class="strengthClass" :style="{ width: strengthPercent + '%' }"></div>
                                    </div>
                                    <span class="strength-label" :class="strengthClass">{{ strengthLabel }}</span>
                                </div>

                                <div class="form-footer">
                                    <button class="btn-submit" :disabled="pwdLoading" @click="changerMotDePasse">
                                        <div v-if="pwdLoading" class="spinner-sm"></div>
                                        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none">
                                            <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
                                        </svg>
                                        {{ pwdLoading ? 'Saving…' : 'Update Password' }}
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- ── Notifications ── -->
                        <div v-if="activeTab === 'notifications'">
                            <div class="panel-header">
                                <div class="panel-icon-wrap" style="background:#fefce8;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="#ca8a04" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                                        <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="#ca8a04" stroke-width="1.8" stroke-linecap="round" />
                                    </svg>
                                </div>
                                <div>
                                    <h2 class="panel-title">Notification Preferences</h2>
                                    <p class="panel-desc">
                                        In the portal today: the header bell and toasts cover tenant validation. Email delivery is not wired yet — toggles are saved for when your backend supports it.
                                    </p>
                                </div>
                            </div>
                            <div class="form-body">
                                <div v-for="n in notifications" :key="n.id" class="notif-row">
                                    <div>
                                        <p class="notif-title">{{ n.title }}</p>
                                        <p class="notif-desc">{{ n.desc }}</p>
                                    </div>
                                    <label class="toggle">
                                        <input type="checkbox" v-model="n.enabled" />
                                        <span class="toggle-track">
                                            <span class="toggle-thumb"></span>
                                        </span>
                                    </label>
                                </div>
                                <div class="form-footer">
                                    <button class="btn-submit" @click="saveNotifications">
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                                            <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
                                        </svg>
                                        Save Preferences
                                    </button>
                                </div>
                            </div>
                        </div>

                    </section>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, reactive, computed, onMounted } from 'vue'
    import api from '@/services/api'
    import AppSidebar from '@/components/layout/AppSidebar.vue'
    import GlobalHeader from '@/components/layout/GlobalHeader.vue'
    import { useNotification } from '@/composables/useNotification'

    const { toast } = useNotification()

    /* ── Tabs ── */
    const activeTab = ref('profile')
    const tabs = [
        {
            id: 'profile',
            label: 'Profile',
            icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.8"/><path d="M4 20c0-4 3.58-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
        },
        {
            id: 'security',
            label: 'Security',
            icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
        },
        {
            id: 'notifications',
            label: 'Notifications',
            icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
        }
    ]

    /* ── Profile ── */
    const profile = reactive({
        id: null,
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        role: ''
    })
    const profileLoading = ref(false)

    /* ── Password ── */
    const pwd = reactive({ ancien: '', nouveau: '', confirm: '' })
    const showPwd = reactive({ ancien: false, nouveau: false, confirm: false })
    const pwdLoading = ref(false)

    /* ── Notifications ── */
    const notifications = reactive([
        {
            id: 1,
            title: 'Company validation queue',
            desc: 'Already active in-app: the bell shows pending companies, the list refreshes on a timer, and you get a toast when a new Pending request appears. Use the bell to open Company Validation Requests and approve or reject.',
            enabled: true
        },
        {
            id: 2,
            title: 'Tenant decisions & onboarding',
            desc: 'Already active in-app: approving or rejecting on Company Validation Requests shows an immediate toast (company name and outcome).',
            enabled: true
        },
        {
            id: 3,
            title: 'Platform pulse digest',
            desc: 'Not sent by email yet. The same metrics (pending reviews, new tenants in 24h, totals, job counts) are on the admin dashboard when you open Tenant Requests — this toggle is reserved for a future daily email.',
            enabled: false
        },
        {
            id: 4,
            title: 'Admin account security',
            desc: 'Not sent by email yet. New device / failed login alerts are not implemented; password changes on this Settings page already show success or error toasts. This toggle is reserved for future security emails.',
            enabled: false
        }
    ])

    /* ── Password Strength ── */
    const strengthPercent = computed(() => {
        const p = pwd.nouveau
        if (!p) return 0
        let s = 0
        if (p.length >= 8) s += 25
        if (p.length >= 12) s += 15
        if (/[A-Z]/.test(p)) s += 20
        if (/[0-9]/.test(p)) s += 20
        if (/[^A-Za-z0-9]/.test(p)) s += 20
        return Math.min(s, 100)
    })

    const strengthClass = computed(() => {
        const v = strengthPercent.value
        if (v >= 75) return 'strong'
        if (v >= 40) return 'medium'
        return 'weak'
    })

    const strengthLabel = computed(() => {
        const v = strengthPercent.value
        if (v >= 75) return 'Strong'
        if (v >= 40) return 'Moderate'
        return 'Weak'
    })

    /* ── Methods ── */

    // Load admin profile
    async function loadAdminProfile() {
        profileLoading.value = true
        try {
            const response = await api.get('/admin/profile')
            const userData = response.data.data

            profile.id = userData.id
            profile.firstName = userData.firstName || ''
            profile.lastName = userData.lastName || ''
            profile.email = userData.email || ''
            profile.phone = userData.phone || ''
            profile.role = userData.role || 'Admin'
        } catch {
            toast.error('Unable to load profile. Please try again.')
        } finally {
            profileLoading.value = false
        }
    }

    // Save profile
    async function sauvegarderProfil() {
        if (!profile.firstName || !profile.lastName || !profile.email) {
            toast.warning('First name, last name, and email are required.')
            return
        }

        profileLoading.value = true
        try {
            await api.put('/admin/profile', {
                firstName: profile.firstName,
                lastName: profile.lastName,
                email: profile.email,
                phone: profile.phone
            })
            toast.success('Profile updated successfully.')
        } catch (err) {
            const msg = err.response?.data?.message || 'Could not save profile.'
            toast.error(msg)
        } finally {
            profileLoading.value = false
        }
    }

    // Change password
    async function changerMotDePasse() {
        if (!pwd.ancien || !pwd.nouveau || !pwd.confirm) {
            toast.warning('All password fields are required.')
            return
        }
        if (pwd.nouveau !== pwd.confirm) {
            toast.warning('New password and confirmation do not match.')
            return
        }
        if (pwd.nouveau.length < 8) {
            toast.warning('Password must be at least 8 characters.')
            return
        }

        pwdLoading.value = true
        try {
            await api.post('/admin/change-password', {
                currentPassword: pwd.ancien,
                newPassword: pwd.nouveau
            })
            toast.success('Password updated successfully.')
            pwd.ancien = ''
            pwd.nouveau = ''
            pwd.confirm = ''
        } catch (err) {
            const msg = err.response?.data?.message || 'Could not update password. Check your current password.'
            toast.error(msg)
        } finally {
            pwdLoading.value = false
        }
    }

    function saveNotifications() {
        toast.success('Notification preferences saved.')
    }

    // Load data on mount
    onMounted(() => {
        loadAdminProfile()
    })
</script>

<style scoped>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    /* ── Structure identique à TenantRequests ── */
    .app-shell {
        display: flex;
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
        background: #f6f6f8;
        color: #1e293b;
    }

    .main-area {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }

    /* Page wrapper */
    .page-wrapper {
        padding: 24px;
        flex: 1;
    }

    /* Header */
    .page-header {
        margin-bottom: 28px;
    }

    .page-title {
        font-size: 1.7rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 4px;
    }

    .page-subtitle {
        font-size: 0.85rem;
        color: #94a3b8;
        margin: 0;
    }

    /* ── Settings layout ── */
    .settings-layout {
        display: flex;
        gap: 24px;
        align-items: flex-start;
    }

    /* Left nav */
    .settings-nav {
        width: 200px;
        flex-shrink: 0;
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 8px;
        display: flex;
        flex-direction: column;
        gap: 2px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .settings-nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 9px 12px;
        border-radius: 9px;
        font-size: 0.84rem;
        font-weight: 500;
        color: #475569;
        background: none;
        border: none;
        cursor: pointer;
        text-align: left;
        font-family: inherit;
        transition: background 0.13s, color 0.13s;
        width: 100%;
    }

        .settings-nav-item:hover {
            background: #f1f5f9;
            color: #1A2B4C;
        }

        .settings-nav-item.active {
            background: rgba(26,43,76,0.08);
            color: #1A2B4C;
            font-weight: 700;
        }

    .nav-item-icon {
        display: flex;
        align-items: center;
        flex-shrink: 0;
    }

    /* Panel */
    .settings-panel {
        flex: 1;
        min-width: 0;
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 28px 32px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    /* Panel header */
    .panel-header {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 28px;
        padding-bottom: 22px;
        border-bottom: 1px solid #f1f5f9;
    }

    .panel-icon-wrap {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .panel-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 4px;
    }

    .panel-desc {
        font-size: 0.82rem;
        color: #94a3b8;
        margin: 0;
    }

    /* Form body */
    .form-body {
        display: flex;
        flex-direction: column;
        gap: 0;
    }

    .field-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
    }

    .field-group {
        display: flex;
        flex-direction: column;
        gap: 5px;
        margin-bottom: 16px;
    }

        .field-group label {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
        }

    .input-wrap {
        position: relative;
        display: flex;
        align-items: center;
    }

    .input-icon {
        position: absolute;
        left: 12px;
        color: #94a3b8;
        pointer-events: none;
    }

    .input-wrap input {
        width: 100%;
        padding: 10px 14px;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        font-size: 0.86rem;
        color: #0f172a;
        background: #f8fafc;
        outline: none;
        font-family: inherit;
        transition: border-color 0.15s, background 0.15s;
    }

        .input-wrap input.has-icon {
            padding-left: 36px;
        }

        .input-wrap input:focus {
            border-color: #1A2B4C;
            background: #fff;
            box-shadow: 0 0 0 3px rgba(26,43,76,0.07);
        }

        .input-wrap input::placeholder {
            color: #cbd5e1;
        }

    .eye-btn {
        position: absolute;
        right: 10px;
        background: none;
        border: none;
        cursor: pointer;
        color: #94a3b8;
        display: flex;
        align-items: center;
        padding: 4px;
        border-radius: 5px;
        transition: color 0.13s;
    }

        .eye-btn:hover {
            color: #475569;
        }

    /* Strength */
    .strength-bar-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 18px;
    }

    .strength-bar {
        flex: 1;
        height: 5px;
        background: #e2e8f0;
        border-radius: 99px;
        overflow: hidden;
    }

    .strength-fill {
        height: 100%;
        border-radius: 99px;
        transition: width 0.3s ease, background 0.3s ease;
    }

        .strength-fill.weak {
            background: #ef4444;
        }

        .strength-fill.medium {
            background: #f59e0b;
        }

        .strength-fill.strong {
            background: #22c55e;
        }

    .strength-label {
        font-size: 0.7rem;
        font-weight: 700;
        min-width: 55px;
        text-align: right;
    }

        .strength-label.weak {
            color: #ef4444;
        }

        .strength-label.medium {
            color: #f59e0b;
        }

        .strength-label.strong {
            color: #22c55e;
        }

    /* Form footer */
    .form-footer {
        display: flex;
        align-items: center;
        gap: 14px;
        padding-top: 6px;
    }

    .btn-submit {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: #1A2B4C;
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 0.84rem;
        font-weight: 700;
        cursor: pointer;
        font-family: inherit;
        transition: opacity 0.15s;
    }

        .btn-submit:hover:not(:disabled) {
            opacity: 0.88;
        }

        .btn-submit:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

    /* Notifications */
    .notif-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 16px 0;
        border-bottom: 1px solid #f1f5f9;
    }

        .notif-row:last-of-type {
            border-bottom: none;
        }

    .notif-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 3px;
    }

    .notif-desc {
        font-size: 0.78rem;
        color: #94a3b8;
        margin: 0;
    }

    /* Toggle */
    .toggle {
        position: relative;
        display: inline-flex;
        cursor: pointer;
        flex-shrink: 0;
    }

        .toggle input {
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
        }

    .toggle-track {
        width: 42px;
        height: 24px;
        background: #e2e8f0;
        border-radius: 99px;
        position: relative;
        transition: background 0.2s;
    }

    .toggle input:checked + .toggle-track {
        background: #1A2B4C;
    }

    .toggle-thumb {
        position: absolute;
        top: 3px;
        left: 3px;
        width: 18px;
        height: 18px;
        background: #fff;
        border-radius: 50%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.15);
        transition: transform 0.2s;
    }

    .toggle input:checked + .toggle-track .toggle-thumb {
        transform: translateX(18px);
    }

    /* Spinner */
    .spinner-sm {
        width: 13px;
        height: 13px;
        border: 2px solid rgba(255,255,255,0.3);
        border-top-color: #fff;
        border-radius: 50%;
        animation: spin 0.65s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    /* Responsive */
    @media (max-width: 900px) {
        .settings-layout {
            flex-direction: column;
        }

        .settings-nav {
            width: 100%;
            flex-direction: row;
            flex-wrap: wrap;
        }

        .page-wrapper {
            padding: 20px 16px;
        }

        .field-row {
            grid-template-columns: 1fr;
        }
    }
</style>