<template>
    <div class="app-shell">
        <AppSidebar role="Admin" />

        <div class="main-area">
            <GlobalHeader title="Admin portail" />
            <!-- Toolbar page -->
            <header class="topbar">
                <div class="topbar-search">
                    <span class="material-icons search-icon">search</span>
                    <input type="text"
                           v-model="searchQuery"
                           placeholder="Search by tenant name, email, company, RNE…"
                           class="topbar-input" />
                </div>
                <div class="topbar-right">
                    <span class="count-pill">{{ filteredTenants.length }} tenants</span>
                    <button class="btn-export" @click="exportToCSV">
                        <span class="material-icons" style="font-size:15px">download</span>
                        Export
                    </button>
                </div>
            </header>

            <!-- PAGE CONTENT -->
            <div class="page-wrapper">

                <!-- Page header -->
                <div class="page-header">
                    <h1 class="page-title">Tenant Management</h1>
                    <p class="page-subtitle">Approved tenants from the database, with recruiter profile data (TenantProfiles) when available.</p>
                </div>

                <!-- Stats (palette #414a84 comme maquette) -->
                <div class="stats-row">
                    <div class="stat-card">
                        <div class="stat-lbl">Approved tenants</div>
                        <div class="stat-num">{{ stats.total }}</div>
                        <span class="material-icons stat-card-ico" aria-hidden="true">bar_chart</span>
                    </div>
                    <div class="stat-card">
                        <div class="stat-lbl">Active jobs</div>
                        <div class="stat-num">{{ stats.totalJobs }}</div>
                        <span class="material-icons stat-card-ico" aria-hidden="true">bar_chart</span>
                    </div>
                    <div class="stat-card">
                        <div class="stat-lbl">Industries</div>
                        <div class="stat-num">{{ stats.industries }}</div>
                        <span class="material-icons stat-card-ico" aria-hidden="true">bar_chart</span>
                    </div>
                    <div class="stat-card">
                        <div class="stat-lbl">Joined this month</div>
                        <div class="stat-num">{{ stats.joinedThisMonth }}</div>
                        <span class="material-icons stat-card-ico" aria-hidden="true">bar_chart</span>
                    </div>
                </div>

                <!-- Filters + sort -->
                <div class="filters-bar">
                    <button v-for="f in industryFilters"
                            :key="f"
                            :class="['filter-btn', { active: activeFilter === f }]"
                            @click="activeFilter = f">
                        {{ f === 'all' ? 'All' : f }}
                    </button>

                    <div class="filter-sep"></div>

                    <select v-model="sortKey" class="sort-sel">
                        <option value="tenantDisplayName">Sort: Tenant name</option>
                        <option value="companyName">Sort: Company</option>
                        <option value="approvedAt">Sort: Date joined</option>
                        <option value="activeJobs">Sort: Active jobs</option>
                    </select>
                </div>

                <!-- Loading / Error states -->
                <div v-if="loading" class="state-center">
                    <div class="spinner"></div>
                    <span>Loading tenants...</span>
                </div>

                <div v-else-if="error" class="state-center error-state">
                    <span class="material-icons" style="font-size:2rem">error_outline</span>
                    <p>{{ error }}</p>
                    <button @click="loadTenants" class="btn-retry">Retry</button>
                </div>

                <!-- Tenant grid -->
                <div v-else class="tenant-grid">
                    <div v-for="(tenant, index) in paginatedTenants"
                         :key="tenant.tenantId || tenant.rne"
                         class="tenant-card"
                         @click="openModal(tenant)">
                        <div :class="['card-banner', `banner-${(index % 6) + 1}`]"></div>
                        <div class="card-body">
                            <div class="avatar-row">
                                <div class="avatar" :data-initial="nameInitial(tenant)">
                                    <img v-if="tenant.logoUrl"
                                         :src="getLogoUrl(tenant.logoUrl)"
                                         :alt="displayName(tenant)"
                                         class="avatar-img"
                                         @error="onImgError($event)" />
                                    <span v-else>{{ nameInitial(tenant) }}</span>
                                </div>
                                <span class="badge-approved">Approved</span>
                            </div>

                            <div class="tenant-head">
                                <div class="tenant-name">{{ displayName(tenant) }}</div>
                                <div class="tenant-job">{{ tenant.jobTitle || '—' }}</div>
                            </div>

                            <div class="tenant-contact">
                                <div class="contact-row">
                                    <span class="material-icons contact-ico">phone</span>
                                    <a v-if="tenant.phone" class="contact-link" :href="telHref(tenant.phone)">{{ tenant.phone }}</a>
                                    <span v-else class="contact-empty">—</span>
                                </div>
                                <div class="contact-row">
                                    <span class="material-icons contact-ico">language</span>
                                    <a v-if="tenant.website"
                                       class="contact-link"
                                       :href="externalUrl(tenant.website)"
                                       target="_blank"
                                       rel="noopener">{{ tenant.website }}</a>
                                    <span v-else class="contact-empty">—</span>
                                </div>
                                <div class="contact-row">
                                    <span class="material-icons contact-ico">share</span>
                                    <a v-if="tenant.linkedin"
                                       class="contact-link"
                                       :href="externalUrl(tenant.linkedin)"
                                       target="_blank"
                                       rel="noopener">{{ tenant.linkedin }}</a>
                                    <span v-else class="contact-empty">—</span>
                                </div>
                                <div class="contact-row">
                                    <span class="material-icons contact-ico">alternate_email</span>
                                    <a v-if="tenant.twitter"
                                       class="contact-link"
                                       :href="externalUrl(tenant.twitter)"
                                       target="_blank"
                                       rel="noopener">{{ tenant.twitter }}</a>
                                    <span v-else class="contact-empty">—</span>
                                </div>
                            </div>

                            <div v-if="tenant.companyName" class="org-line">
                                <span class="material-icons org-ico">business</span>
                                <span class="org-text">{{ tenant.companyName }}<template v-if="tenant.rne"><span class="org-rne mono"> · {{ tenant.rne }}</span></template></span>
                            </div>

                            <div class="divider"></div>

                            <div class="info-grid info-grid-compact">
                                <div class="info-item">
                                    <div class="info-lbl">Email</div>
                                    <div class="info-val">{{ tenant.workEmail || '—' }}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-lbl">Approved</div>
                                    <div class="info-val">{{ formatDate(tenant.approvedAt) }}</div>
                                </div>
                            </div>

                            <div class="card-footer">
                                <span class="jobs-badge">{{ tenant.activeJobs ?? 0 }} active jobs</span>
                                <div class="card-actions">
                                    <button class="btn-icon"
                                            title="View details"
                                            @click.stop="openModal(tenant)">
                                        <span class="material-icons" style="font-size:16px">visibility</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-if="filteredTenants.length === 0" class="no-results">
                        No approved tenants found.
                    </div>
                </div>

                <!-- Pagination -->
                <div v-if="!loading && !error && filteredTenants.length > 0" class="pagination-bar">
                    <span class="page-info">
                        Showing {{ ((currentPage - 1) * itemsPerPage) + 1 }}–{{ Math.min(currentPage * itemsPerPage, filteredTenants.length) }} of {{ filteredTenants.length }} tenants
                    </span>
                    <div class="page-btns">
                        <button class="pb" @click="previousPage" :disabled="currentPage === 1">
                            <span class="material-icons" style="font-size:15px">chevron_left</span>
                        </button>
                        <button v-for="page in displayedPages"
                                :key="page"
                                :class="['pb', { active: currentPage === page }]"
                                @click="goToPage(page)">
                            {{ page }}
                        </button>
                        <button class="pb" @click="nextPage" :disabled="currentPage === totalPages">
                            <span class="material-icons" style="font-size:15px">chevron_right</span>
                        </button>
                    </div>
                </div>

            </div>
        </div>

        <!-- DETAIL MODAL -->
        <div v-if="showModal" class="modal-overlay" @click="closeModal">
            <div class="modal" @click.stop>
                <div :class="['modal-banner', `banner-${modalBannerIndex}`]">
                    <button class="modal-close" @click="closeModal">
                        <span class="material-icons">close</span>
                    </button>
                </div>
                <div v-if="selectedTenant" class="modal-body">
                    <div class="modal-top-row">
                        <div class="avatar large" :data-initial="nameInitial(selectedTenant)">
                            <img v-if="selectedTenant.logoUrl"
                                 :src="getLogoUrl(selectedTenant.logoUrl)"
                                 :alt="displayName(selectedTenant)"
                                 class="avatar-img"
                                 @error="onImgError($event)" />
                            <span v-else>{{ nameInitial(selectedTenant) }}</span>
                        </div>
                        <div class="modal-tenant-head">
                            <div class="modal-tenant-name">{{ displayName(selectedTenant) }}</div>
                            <div class="modal-tenant-job">{{ selectedTenant.jobTitle || '—' }}</div>
                        </div>
                        <span class="badge-approved">Approved</span>
                    </div>

                    <div class="detail-section">
                        <div class="detail-section-title">Contact &amp; présence</div>
                        <div class="detail-row"><span class="dl">Phone</span><span class="dv">
                            <a v-if="selectedTenant.phone" class="link-out" :href="telHref(selectedTenant.phone)">{{ selectedTenant.phone }}</a>
                            <template v-else>—</template>
                        </span></div>
                        <div class="detail-row"><span class="dl">Website</span><span class="dv">
                            <a v-if="selectedTenant.website" :href="externalUrl(selectedTenant.website)" target="_blank" rel="noopener" class="link-out">{{ selectedTenant.website }}</a>
                            <template v-else>—</template>
                        </span></div>
                        <div class="detail-row"><span class="dl">LinkedIn</span><span class="dv">
                            <a v-if="selectedTenant.linkedin" :href="externalUrl(selectedTenant.linkedin)" target="_blank" rel="noopener" class="link-out">{{ selectedTenant.linkedin }}</a>
                            <template v-else>—</template>
                        </span></div>
                        <div class="detail-row"><span class="dl">Twitter / X</span><span class="dv">
                            <a v-if="selectedTenant.twitter" :href="externalUrl(selectedTenant.twitter)" target="_blank" rel="noopener" class="link-out">{{ selectedTenant.twitter }}</a>
                            <template v-else>—</template>
                        </span></div>
                        <div class="detail-row"><span class="dl">Email</span><span class="dv">{{ selectedTenant.workEmail || '—' }}</span></div>
                    </div>

                    <div class="detail-section">
                        <div class="detail-section-title">Organization</div>
                        <div class="detail-row"><span class="dl">Company</span><span class="dv">{{ selectedTenant.companyName || '—' }}</span></div>
                        <div class="detail-row"><span class="dl">RNE</span><span class="dv mono">{{ selectedTenant.rne || '—' }}</span></div>
                        <div class="detail-row"><span class="dl">Industry</span><span class="dv">{{ selectedTenant.industry || '—' }}</span></div>
                        <div class="detail-row"><span class="dl">Active jobs</span><span class="dv">{{ selectedTenant.activeJobs ?? 0 }}</span></div>
                        <div class="detail-row"><span class="dl">Approved</span><span class="dv">{{ formatDate(selectedTenant.approvedAt) }}</span></div>
                        <div class="detail-row"><span class="dl">Hiring</span><span class="dv">{{ hiringStatusLabel(selectedTenant.hiringStatus) }}</span></div>
                        <div class="detail-row detail-row-block"><span class="dl">Work types</span><span class="dv">{{ formatStringList(parseJsonStringArray(selectedTenant.workTypesJson)) }}</span></div>
                        <div class="detail-row detail-row-block"><span class="dl">Tech stack</span><span class="dv">{{ formatStringList(parseJsonStringArray(selectedTenant.techStackJson)) }}</span></div>
                        <div class="detail-row" v-if="selectedTenant.profileUpdatedAt"><span class="dl">Profile updated</span><span class="dv">{{ formatDate(selectedTenant.profileUpdatedAt) }}</span></div>
                    </div>

                    <div class="modal-actions">
                        <button class="btn-danger" @click="handleSuspend(selectedTenant)">
                            <span class="material-icons" style="font-size:15px">block</span>
                            Suspend tenant
                        </button>
                        <button
                            type="button"
                            class="btn-primary"
                            :disabled="!selectedTenant?.linkedin"
                            :title="selectedTenant?.linkedin ? 'Open LinkedIn in a new tab' : 'No LinkedIn URL on file'"
                            @click="viewFullProfile(selectedTenant)">
                            View full profile
                            <span class="material-icons" style="font-size:15px">open_in_new</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, computed, onMounted, watch } from 'vue'
    import axios from 'axios'
    import AppSidebar from '../../components/layout/AppSidebar.vue'
    import GlobalHeader from '../../components/layout/GlobalHeader.vue'

    const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5202/api'

    const api = axios.create({
        baseURL: API_BASE,
        headers: { 'Content-Type': 'application/json' }
    })

    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null
    if (token) {
        api.defaults.headers.common.Authorization = `Bearer ${token}`
    }

    // ─── State ───────────────────────────────────────────────────────────────────
    const tenants = ref([])
    const loading = ref(false)
    const error = ref(null)
    const searchQuery = ref('')
    const activeFilter = ref('all')
    const sortKey = ref('tenantDisplayName')
    const showModal = ref(false)
    const selectedTenant = ref(null)
    const modalBannerIndex = ref(1)
    const currentPage = ref(1)
    const itemsPerPage = ref(12)

    // ─── Computed ────────────────────────────────────────────────────────────────
    const industryFilters = computed(() => {
        const industries = [...new Set(tenants.value.map(t => t.industry).filter(Boolean))]
        return ['all', ...industries.slice(0, 5)]
    })

    const filteredTenants = computed(() => {
        let list = tenants.value
        if (activeFilter.value !== 'all') {
            list = list.filter(t => t.industry === activeFilter.value)
        }
        if (searchQuery.value) {
            const q = searchQuery.value.toLowerCase()
            list = list.filter(t =>
                displayName(t).toLowerCase().includes(q) ||
                t.companyName?.toLowerCase().includes(q) ||
                t.rne?.toLowerCase().includes(q) ||
                t.owner?.toLowerCase().includes(q) ||
                t.jobTitle?.toLowerCase().includes(q) ||
                t.website?.toLowerCase().includes(q) ||
                t.linkedin?.toLowerCase().includes(q) ||
                t.twitter?.toLowerCase().includes(q) ||
                t.phone?.toLowerCase().includes(q) ||
                t.workEmail?.toLowerCase().includes(q)
            )
        }
        return [...list].sort((a, b) => {
            if (sortKey.value === 'approvedAt') return new Date(b.approvedAt) - new Date(a.approvedAt)
            if (sortKey.value === 'activeJobs') return (b.activeJobs ?? 0) - (a.activeJobs ?? 0)
            if (sortKey.value === 'tenantDisplayName') return (displayName(a) || '').localeCompare(displayName(b) || '')
            return (a.companyName ?? '').localeCompare(b.companyName ?? '')
        })
    })

    const totalPages = computed(() => {
        return Math.ceil(filteredTenants.value.length / itemsPerPage.value)
    })

    const paginatedTenants = computed(() => {
        const start = (currentPage.value - 1) * itemsPerPage.value
        const end = start + itemsPerPage.value
        return filteredTenants.value.slice(start, end)
    })

    const displayedPages = computed(() => {
        const delta = 2
        const range = []
        const rangeWithDots = []
        let l

        for (let i = 1; i <= totalPages.value; i++) {
            if (i === 1 || i === totalPages.value || (i >= currentPage.value - delta && i <= currentPage.value + delta)) {
                range.push(i)
            }
        }

        range.forEach((i) => {
            if (l) {
                if (i - l === 2) {
                    rangeWithDots.push(l + 1)
                } else if (i - l !== 1) {
                    rangeWithDots.push('...')
                }
            }
            rangeWithDots.push(i)
            l = i
        })

        return rangeWithDots
    })

    const stats = computed(() => {
        const industries = new Set(tenants.value.map(t => t.industry).filter(Boolean))
        const thisMonth = new Date(); thisMonth.setDate(1); thisMonth.setHours(0, 0, 0, 0)
        return {
            total: tenants.value.length,
            totalJobs: tenants.value.reduce((s, t) => s + (t.activeJobs ?? 0), 0),
            industries: industries.size,
            joinedThisMonth: tenants.value.filter(t => t.approvedAt && new Date(t.approvedAt) >= thisMonth).length
        }
    })

    // ─── Methods ─────────────────────────────────────────────────────────────────

    async function loadTenants() {
        loading.value = true
        error.value = null
        try {
            const res = await api.get('/admin/tenants', { params: { status: 'Approved' } })
            tenants.value = res.data.data || []
        } catch (err) {
            console.error('Failed to load tenants:', err)
            error.value = err.response?.data?.message || 'Unable to load tenants. Check that the backend is accessible.'
        } finally {
            loading.value = false
        }
    }

    const apiOrigin = API_BASE.replace(/\/api\/?$/, '')

    function getLogoUrl(logoUrl) {
        if (!logoUrl) return null
        if (logoUrl.startsWith('http://') || logoUrl.startsWith('https://')) return logoUrl
        if (logoUrl.startsWith('/')) {
            return `${apiOrigin}${logoUrl}`
        }
        return `${apiOrigin}/imagesProfiles/${logoUrl}`
    }

    function parseJsonStringArray(json) {
        if (!json || typeof json !== 'string') return []
        try {
            const a = JSON.parse(json)
            return Array.isArray(a) ? a.map(String).filter(Boolean) : []
        } catch {
            return []
        }
    }

    function hiringStatusLabel(s) {
        if (!s) return '—'
        const m = { actively: 'Actively hiring', sometimes: 'Sometimes', paused: 'Paused' }
        return m[String(s).toLowerCase()] || s
    }

    function formatStringList(arr) {
        if (!arr || !arr.length) return '—'
        return arr.join(', ')
    }

    function externalUrl(url) {
        const u = String(url || '').trim()
        if (!u) return '#'
        if (/^https?:\/\//i.test(u)) return u
        return `https://${u}`
    }

    function displayName(t) {
        if (!t) return ''
        return (t.tenantDisplayName || t.workEmail || t.owner || '').trim() || '—'
    }

    function nameInitial(t) {
        const n = displayName(t)
        if (!n || n === '—') return '?'
        return n.charAt(0).toUpperCase()
    }

    function telHref(phone) {
        if (!phone) return '#'
        const d = String(phone).replace(/[^\d+]/g, '')
        return d ? `tel:${d}` : '#'
    }

    function onImgError(event) {
        event.target.style.display = 'none'
        const parent = event.target.parentElement
        if (parent && !parent.querySelector('.avatar-fallback')) {
            const span = document.createElement('span')
            span.className = 'avatar-fallback'
            span.textContent = parent.dataset.initial || '?'
            parent.appendChild(span)
        }
    }

    function openModal(tenant) {
        selectedTenant.value = tenant
        modalBannerIndex.value = (filteredTenants.value.indexOf(tenant) % 6) + 1
        showModal.value = true
    }

    function closeModal() {
        showModal.value = false
        selectedTenant.value = null
    }

    async function handleSuspend(tenant) {
        if (!confirm(`Are you sure you want to suspend ${tenant.companyName}? This will disable their account.`)) return

        try {
            await api.patch(`/admin/tenants/${encodeURIComponent(tenant.rne)}/suspend`)
            alert(`✅ ${tenant.companyName} has been suspended successfully.`)
            await loadTenants()
            closeModal()
        } catch (err) {
            console.error('Error suspending tenant:', err)
            alert(`❌ Error suspending tenant: ${err.response?.data?.message || err.message}`)
        }
    }

    function viewFullProfile(tenant) {
        if (!tenant?.linkedin?.trim()) {
            alert('Aucune URL LinkedIn renseignée pour ce tenant.')
            return
        }
        const url = externalUrl(tenant.linkedin.trim())
        window.open(url, '_blank', 'noopener,noreferrer')
    }

    function exportToCSV() {
        const headers = ['Tenant name', 'Job title', 'Company Name', 'RNE', 'Owner', 'Email', 'Phone', 'Industry', 'Hiring', 'Website', 'LinkedIn', 'Twitter', 'Work types', 'Tech stack', 'Active Jobs', 'Approved', 'Profile updated']
        const rows = filteredTenants.value.map(t => [
            `"${(displayName(t) || '').replace(/"/g, '""')}"`,
            `"${(t.jobTitle || '').replace(/"/g, '""')}"`,
            `"${(t.companyName || '').replace(/"/g, '""')}"`,
            `"${(t.rne || '').replace(/"/g, '""')}"`,
            `"${(t.owner || '').replace(/"/g, '""')}"`,
            `"${(t.workEmail || '').replace(/"/g, '""')}"`,
            `"${(t.phone || '').replace(/"/g, '""')}"`,
            `"${(t.industry || '').replace(/"/g, '""')}"`,
            `"${(t.hiringStatus || '').replace(/"/g, '""')}"`,
            `"${(t.website || '').replace(/"/g, '""')}"`,
            `"${(t.linkedin || '').replace(/"/g, '""')}"`,
            `"${(t.twitter || '').replace(/"/g, '""')}"`,
            `"${formatStringList(parseJsonStringArray(t.workTypesJson)).replace(/"/g, '""')}"`,
            `"${formatStringList(parseJsonStringArray(t.techStackJson)).replace(/"/g, '""')}"`,
            t.activeJobs || 0,
            formatDate(t.approvedAt),
            formatDate(t.profileUpdatedAt)
        ])

        const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
        const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', `tenants_export_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
    }

    function formatDate(d) {
        if (!d) return '—'
        try {
            return new Date(d).toLocaleDateString('fr-FR', {
                day: '2-digit', month: 'short', year: 'numeric'
            })
        } catch {
            return '—'
        }
    }

    function previousPage() {
        if (currentPage.value > 1) {
            currentPage.value--
        }
    }

    function nextPage() {
        if (currentPage.value < totalPages.value) {
            currentPage.value++
        }
    }

    function goToPage(page) {
        if (page !== '...') {
            currentPage.value = page
        }
    }

    function resetPagination() {
        currentPage.value = 1
    }

    watch([searchQuery, activeFilter, sortKey], () => {
        resetPagination()
    })

    onMounted(() => loadTenants())
</script>

<style scoped>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    *, *::before, *::after {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

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

    /* ── Topbar ─────────────────────────────────────────────────────────────── */
    .topbar {
        position: sticky;
        top: 0;
        z-index: 40;
        background: white;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 24px;
        gap: 16px;
    }

    .topbar-search {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
        max-width: 480px;
    }

    .search-icon {
        color: #94a3b8;
        font-size: 19px !important;
        flex-shrink: 0;
    }

    .topbar-input {
        flex: 1;
        border: none;
        outline: none;
        font-size: 13px;
        color: #334155;
        font-family: 'Inter', sans-serif;
        background: transparent;
    }

        .topbar-input::placeholder {
            color: #94a3b8;
        }

    .topbar-right {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .count-pill {
        font-size: 12px;
        font-weight: 500;
        color: #475569;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 9999px;
        padding: 4px 12px;
        white-space: nowrap;
    }

    .btn-export {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 12px;
        font-weight: 600;
        color: #144bb8;
        background: rgba(20,75,184,.06);
        border: 1px solid rgba(20,75,184,.2);
        border-radius: 8px;
        padding: 7px 14px;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        transition: background .15s;
    }

        .btn-export:hover {
            background: rgba(20,75,184,.1);
        }

        .btn-export .material-icons {
            font-size: 15px !important;
        }

    /* ── Page wrapper ───────────────────────────────────────────────────────── */
    .page-wrapper {
        padding: 24px;
        flex: 1;
    }

    .page-header {
        margin-bottom: 20px;
    }

    .page-title {
        font-size: 18px;
        font-weight: 700;
        color: #1e293b;
    }

    .page-subtitle {
        font-size: 13px;
        color: #64748b;
        margin-top: 4px;
    }

    /* ── Stats row ──────────────────────────────────────────────────────────── */
    .stats-row {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }

    .stat-card {
        position: relative;
        background: #414a84;
        border: none;
        border-radius: 10px;
        padding: 16px 20px 20px;
        flex: 1;
        min-width: 130px;
        min-height: 96px;
        box-shadow: 0 2px 8px rgba(65, 74, 132, 0.35);
    }

    .stat-lbl {
        font-size: 10px;
        font-weight: 700;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0 0 10px 0;
        line-height: 1.3;
    }

    .stat-num {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
        padding-right: 36px;
    }

    .stat-card-ico {
        position: absolute;
        right: 14px;
        bottom: 12px;
        font-size: 26px !important;
        color: #000000;
        line-height: 1;
        pointer-events: none;
        opacity: 0.95;
    }

    /* ── Filters bar ────────────────────────────────────────────────────────── */
    .filters-bar {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }

    .filter-btn {
        font-size: 12px;
        font-weight: 500;
        padding: 5px 14px;
        border-radius: 9999px;
        border: 1px solid #e2e8f0;
        background: white;
        color: #64748b;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        transition: all .15s;
    }

        .filter-btn.active {
            background: #144bb8;
            color: white;
            border-color: #144bb8;
        }

        .filter-btn:hover:not(.active) {
            border-color: #cbd5e1;
            color: #1e293b;
        }

    .filter-sep {
        width: 1px;
        height: 20px;
        background: #e2e8f0;
        margin: 0 4px;
    }

    .sort-sel {
        font-size: 12px;
        font-weight: 500;
        color: #64748b;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 6px 10px;
        outline: none;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        margin-left: auto;
    }

    /* ── Tenant grid ────────────────────────────────────────────────────────── */
    .tenant-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }

    .tenant-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
        cursor: pointer;
        transition: border-color .15s, box-shadow .15s;
    }

        .tenant-card:hover {
            border-color: #cbd5e1;
            box-shadow: 0 4px 12px rgba(0,0,0,.06);
        }

    /* Banner colors */
    .card-banner {
        height: 52px;
    }

    .banner-1 {
        background: linear-gradient(135deg, #144bb8 0%, #0e3a8f 100%);
    }

    .banner-2 {
        background: linear-gradient(135deg, #0f766e 0%, #0d6061 100%);
    }

    .banner-3 {
        background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
    }

    .banner-4 {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
    }

    .banner-5 {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
    }

    .banner-6 {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    .card-body {
        padding: 0 16px 16px;
    }

    .avatar-row {
        margin-top: -22px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }

    .avatar {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        border: 2.5px solid white;
        background: #f1f5f9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 700;
        color: #144bb8;
        overflow: hidden;
        flex-shrink: 0;
    }

        .avatar.large {
            width: 60px;
            height: 60px;
            border-radius: 12px;
            border-width: 3px;
            font-size: 22px;
        }

    .avatar-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 7px;
    }

    .avatar-fallback {
        font-weight: 700;
        font-size: 14px;
        color: #144bb8;
    }

    .badge-approved {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        background: #dcfce7;
        color: #166534;
        border-radius: 9999px;
        padding: 3px 9px;
        white-space: nowrap;
    }

    .tenant-head {
        margin-bottom: 10px;
    }

    .tenant-name {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.25;
        margin-bottom: 4px;
    }

    .tenant-job {
        font-size: 12px;
        font-weight: 500;
        color: #64748b;
        line-height: 1.35;
    }

    .tenant-contact {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 10px;
    }

    .contact-row {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        font-size: 12px;
        min-height: 20px;
    }

    .contact-ico {
        font-size: 16px !important;
        color: #94a3b8;
        flex-shrink: 0;
        margin-top: 1px;
    }

    .contact-link {
        color: #2563eb;
        text-decoration: none;
        word-break: break-all;
        line-height: 1.35;
    }

        .contact-link:hover {
            text-decoration: underline;
        }

    .contact-empty {
        color: #cbd5e1;
    }

    .org-line {
        display: flex;
        align-items: flex-start;
        gap: 6px;
        padding: 8px 10px;
        background: #f8fafc;
        border-radius: 8px;
        border: 1px solid #f1f5f9;
        margin-bottom: 4px;
    }

    .org-ico {
        font-size: 16px !important;
        color: #94a3b8;
        flex-shrink: 0;
        margin-top: 1px;
    }

    .org-text {
        font-size: 11px;
        color: #64748b;
        line-height: 1.4;
    }

    .org-rne {
        color: #94a3b8;
    }

    .info-grid-compact {
        margin-top: 2px;
    }

    .divider {
        height: 1px;
        background: #f1f5f9;
        margin: 10px 0;
    }

    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
    }

    .info-lbl {
        font-size: 9px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #94a3b8;
        margin-bottom: 2px;
    }

    .info-val {
        font-size: 12px;
        font-weight: 500;
        color: #334155;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

        .info-val.mono {
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: #64748b;
        }

    .card-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 12px;
        padding-top: 10px;
        border-top: 1px solid #f1f5f9;
    }

    .jobs-badge {
        font-size: 11px;
        font-weight: 500;
        color: #144bb8;
        background: rgba(20,75,184,.08);
        border-radius: 6px;
        padding: 3px 9px;
    }

    .card-actions {
        display: flex;
        gap: 5px;
    }

    .btn-icon {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        color: #64748b;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all .15s;
    }

        .btn-icon:hover {
            background: #144bb8;
            color: white;
            border-color: #144bb8;
        }

    /* ── Pagination ─────────────────────────────────────────────────────────── */
    .pagination-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .page-info {
        font-size: 11px;
        color: #94a3b8;
    }

    .page-btns {
        display: flex;
        gap: 4px;
    }

    .pb {
        width: 30px;
        height: 30px;
        border-radius: 5px;
        border: 1px solid #e2e8f0;
        background: white;
        color: #64748b;
        font-size: 12px;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all .15s;
    }

        .pb:hover:not(:disabled) {
            border-color: #cbd5e1;
            color: #1e293b;
        }

        .pb.active {
            background: #144bb8;
            color: white;
            border-color: #144bb8;
            font-weight: 700;
        }

        .pb:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

    /* ── States ─────────────────────────────────────────────────────────────── */
    .state-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        padding: 60px;
        font-size: 13px;
        color: #94a3b8;
    }

    .error-state {
        color: #ef4444;
    }

    .spinner {
        width: 32px;
        height: 32px;
        border: 3px solid #e2e8f0;
        border-top-color: #144bb8;
        border-radius: 50%;
        animation: spin .8s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .btn-retry {
        padding: 6px 16px;
        background: #144bb8;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 12px;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
    }

    .no-results {
        grid-column: 1 / -1;
        text-align: center;
        padding: 60px;
        color: #94a3b8;
        font-size: 13px;
    }

    /* ── Modal ──────────────────────────────────────────────────────────────── */
    .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,.5);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 20px;
        animation: fadeIn .15s ease;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
        }

        to {
            opacity: 1;
        }
    }

    .modal {
        background: white;
        border-radius: 12px;
        width: 460px;
        max-width: 100%;
        max-height: 85vh;
        overflow-y: auto;
        box-shadow: 0 25px 60px -12px rgba(0,0,0,.3);
        animation: slideUp .2s ease;
    }

    @keyframes slideUp {
        from {
            transform: translateY(16px);
            opacity: 0;
        }

        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .modal-banner {
        height: 72px;
        border-radius: 12px 12px 0 0;
        position: relative;
    }

    .modal-close {
        position: absolute;
        top: 10px;
        right: 12px;
        background: rgba(255,255,255,.15);
        border: none;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background .15s;
    }

        .modal-close:hover {
            background: rgba(255,255,255,.25);
        }

    .modal-body {
        padding: 20px 20px 24px;
        position: relative;
        z-index: 1;
        background: #fff;
        border-radius: 0 0 12px 12px;
    }

    .modal-top-row {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        margin-top: 0;
        margin-bottom: 8px;
        padding-bottom: 18px;
        border-bottom: 1px solid #f1f5f9;
    }

    .modal-top-row .avatar.large {
        flex-shrink: 0;
        margin-top: 0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
    }

    .modal-top-row .avatar-img {
        object-fit: cover;
    }

    .modal-tenant-head {
        flex: 1;
        min-width: 0;
        padding-top: 2px;
    }

    .modal-tenant-name {
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.3;
        word-break: break-word;
    }

    .modal-tenant-job {
        font-size: 13px;
        color: #64748b;
        margin-top: 6px;
        font-weight: 500;
        line-height: 1.35;
    }

    .modal-top-row .badge-approved {
        flex-shrink: 0;
        margin-top: 2px;
        margin-left: auto;
        align-self: flex-start;
    }

    .detail-section {
        margin-top: 18px;
    }

    .detail-section-title {
        font-size: 9px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #94a3b8;
        margin-bottom: 8px;
    }

    .detail-row {
        display: flex;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #f8fafc;
    }

        .detail-row:last-child {
            border-bottom: none;
        }

    .detail-row-block {
        align-items: flex-start;
    }

        .detail-row-block .dv {
            white-space: normal;
            word-break: break-word;
            line-height: 1.45;
        }

    .link-out {
        color: #2563eb;
        text-decoration: none;
    }

        .link-out:hover {
            text-decoration: underline;
        }

    .dl {
        width: 80px;
        font-size: 10px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: .05em;
        flex-shrink: 0;
    }

    .dv {
        font-size: 13px;
        color: #334155;
    }

        .dv.mono {
            font-family: 'Courier New', monospace;
        }

    .modal-actions {
        display: flex;
        gap: 10px;
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid #f1f5f9;
    }

    .btn-danger {
        display: flex;
        align-items: center;
        gap: 5px;
        flex: 1;
        padding: 9px 12px;
        justify-content: center;
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: background .15s;
    }

        .btn-danger:hover {
            background: #fecaca;
        }

    .btn-primary {
        display: flex;
        align-items: center;
        gap: 5px;
        flex: 1;
        padding: 9px 12px;
        justify-content: center;
        background: #144bb8;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: background .15s;
    }

        .btn-primary:hover:not(:disabled) {
            background: #1040a0;
        }

        .btn-primary:disabled {
            opacity: 0.45;
            cursor: not-allowed;
        }

    /* ── Responsive ─────────────────────────────────────────────────────────── */
    @media (max-width: 768px) {
        .stats-row {
            flex-direction: column;
        }

        .tenant-grid {
            grid-template-columns: 1fr;
        }

        .filters-bar {
            flex-wrap: wrap;
        }

        .sort-sel {
            margin-left: 0;
        }
    }
</style>