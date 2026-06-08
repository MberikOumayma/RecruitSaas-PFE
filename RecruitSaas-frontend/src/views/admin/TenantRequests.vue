<template>
    <div class="page-layout">
        <AppSidebar />
        <main class="main-content">
            <GlobalHeader title="Admin portail" subTitle="Manage and approve company registrations" />

            <div class="content">
                <!-- Stats Cards -->
              
                <!-- Table Card -->
                <div class="table-card">
                    <div class="table-toolbar">
                        <div>
                            <h2 class="table-title">Company Validation Requests</h2>
                            <p class="table-subtitle">Review and approve new recruitment tenant applications.</p>
                        </div>
                        <div class="toolbar-right">
                            <div class="search-wrapper">
                                <span class="material-icons search-icon-input">search</span>
                                <input type="text" v-model="searchQuery" placeholder="Search companies..." class="search-input" />
                            </div>
                            <button class="btn-filter">
                                <span class="material-icons">filter_list</span>
                                Filter List
                            </button>
                        </div>
                    </div>

                    <div v-if="loading" class="state-center">
                        <div class="spinner"></div>
                        <span>Loading requests...</span>
                    </div>

                    <div v-if="error" class="state-center error-state">
                        <span class="material-icons" style="font-size:2rem">error_outline</span>
                        <p>{{ error }}</p>
                        <button @click="loadRequests" class="btn-retry">Retry</button>
                    </div>

                    <div v-if="!loading && !error" class="table-overflow">
                        <table>
                            <thead>
                                <tr>
                                    <th @click="sortBy('companyName')" class="sortable">
                                        Company <span v-if="sortKey === 'companyName'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                                    </th>
                                    <th @click="sortBy('rne')" class="sortable">
                                        RNE <span v-if="sortKey === 'rne'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                                    </th>
                                    <th @click="sortBy('owner')" class="sortable">
                                        Owner <span v-if="sortKey === 'owner'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                                    </th>
                                    <th @click="sortBy('industry')" class="sortable">
                                        Domain <span v-if="sortKey === 'industry'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                                    </th>
                                    <th @click="sortBy('status')" class="sortable">
                                        Status <span v-if="sortKey === 'status'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                                    </th>
                                    <th class="th-center">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="request in filteredAndSortedRequests" :key="request.companyName" class="table-row">
                                    <td>
                                        <div class="company-cell">
                                            <div
                                                class="company-avatar"
                                                :class="{ 'company-avatar--logo': showCompanyLogo(request) }"
                                            >
                                                <img
                                                    v-if="showCompanyLogo(request)"
                                                    :src="getLogoUrl(request.logoUrl)"
                                                    :alt="request.companyName || ''"
                                                    class="company-logo-img"
                                                    @error="onRowLogoError(request.companyName)"
                                                />
                                                <span v-else>{{ request.companyName?.charAt(0) }}</span>
                                            </div>
                                            <span class="company-name">{{ request.companyName }}</span>
                                        </div>
                                    </td>
                                    <td><span class="rne">{{ request.rne }}</span></td>
                                    <td>
                                        <div class="owner-name">{{ request.owner }}</div>
                                        <div class="owner-email">{{ request.workEmail }}</div>
                                    </td>
                                    <td>
                                        <a href="#" class="domain-link">
                                            {{ request.industry }}
                                            <span class="material-icons" style="font-size:12px">open_in_new</span>
                                        </a>
                                    </td>
                                    <td>
                                        <span :class="['badge', getBadgeClass(request.status)]">
                                            {{ getStatusLabel(request.status) }}
                                        </span>
                                    </td>
                                    <td>
                                        <div class="action-btns">
                                            <button v-if="request.status === 'Pending'" @click="handleApprove(request.companyName)" class="btn-approve">Approve</button>
                                            <button v-if="request.status === 'Pending'" @click="handleReject(request.companyName)" class="btn-reject">Reject</button>
                                            <button @click="viewDetails(request.companyName)" class="btn-view" title="View details">
                                                <span class="material-icons" style="font-size:16px">visibility</span>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <div v-if="filteredAndSortedRequests.length === 0" class="no-results">No requests found</div>
                    </div>

                    <div v-if="!loading && !error" class="table-footer">
                        <p class="showing-text">Showing 1 to {{ filteredAndSortedRequests.length }} of {{ stats.total }} validation requests</p>
                        <div class="pagination">
                            <button class="page-btn"><span class="material-icons" style="font-size:16px">chevron_left</span></button>
                            <button class="page-btn active">1</button>
                            <button class="page-btn">2</button>
                            <button class="page-btn">3</button>
                            <button class="page-btn"><span class="material-icons" style="font-size:16px">chevron_right</span></button>
                        </div>
                    </div>
                </div>

                <!-- Bottom Row -->
                <div class="bottom-row">
                    <div class="ai-card">
                        <div class="ai-card-header">
                            <div class="ai-card-title">
                                <span class="material-icons ai-title-icon">bar_chart</span>
                                New tenant registrations (last 5 days)
                            </div>
                            <span class="live-badge"><span class="live-dot"></span>DASHBOARD</span>
                        </div>
                        <div class="tenant-activity-chart" role="img" aria-label="Tenant sign-ups per day over the last five days">
                            <div v-for="(day, i) in tenantActivitySeries" :key="i" class="tenant-activity-col">
                                <span class="tenant-activity-value">{{ formatCount(day.count) }}</span>
                                <div class="tenant-activity-bar-track">
                                    <div
                                        class="tenant-activity-bar-fill"
                                        :style="{ height: day.count === 0 ? '0%' : `${day.barPct}%` }"
                                    ></div>
                                </div>
                                <span class="tenant-activity-label">{{ day.label }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="infra-card">
                        <div class="infra-card-header">
                            <div class="infra-pulse">
                                <span class="pulse-ring"></span>
                                <span class="material-icons pulse-icon">wifi</span>
                            </div>
                            <span class="infra-title">Infrastructure Health</span>
                        </div>
                        <div class="infra-grid">
                            <div class="infra-item">
                                <p class="infra-label">REGISTERED TENANTS</p>
                                <div class="infra-value-row">
                                    <span class="infra-value">{{ formatCount(platformStats.total) }}</span>
                                    <span class="infra-dot green"></span>
                                </div>
                            </div>
                            <div class="infra-item">
                                <p class="infra-label">JOB POSTINGS</p>
                                <div class="infra-value-row">
                                    <span class="infra-value">{{ formatCount(platformStats.totalJobs) }}</span>
                                    <span class="material-icons infra-refresh">work_outline</span>
                                </div>
                            </div>
                            <div class="infra-item">
                                <p class="infra-label">PENDING REVIEWS</p>
                                <div class="infra-value-row">
                                    <span class="infra-value">{{ formatCount(platformStats.pending) }}</span>
                                    <span class="infra-dot" :class="platformStats.pending > 0 ? 'amber' : 'green'"></span>
                                </div>
                            </div>
                            <div class="infra-item">
                                <p class="infra-label">NEW TENANTS (24H)</p>
                                <div class="infra-value-row">
                                    <span class="infra-value">{{ formatCount(platformStats.newTenantsToday) }}</span>
                                    <span class="material-icons infra-refresh">person_add</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- MODAL DETAILS -->
        <div v-if="showDetailsModal" class="modal-overlay" @click="closeModal">
            <div class="modal" @click.stop>
                <div class="modal-header">
                    <h2>Company Details</h2>
                    <button class="modal-close" @click="closeModal"><span class="material-icons">close</span></button>
                </div>
                <div v-if="selectedRequest" class="modal-body">
                    <div class="modal-company-top">
                        <div
                            class="company-avatar large"
                            :class="{ 'company-avatar--logo': showModalCompanyLogo }"
                        >
                            <img
                                v-if="showModalCompanyLogo"
                                :src="getLogoUrl(selectedRequest.logoUrl)"
                                :alt="selectedRequest.companyName || ''"
                                class="company-logo-img"
                                @error="modalLogoBroken = true"
                            />
                            <span v-else>{{ selectedRequest.companyName?.charAt(0) }}</span>
                        </div>
                        <div class="modal-company-head-text">
                            <div class="modal-company-name">{{ selectedRequest.companyName }}</div>
                            <span :class="['badge', getBadgeClass(selectedRequest.status)]">{{ getStatusLabel(selectedRequest.status) }}</span>
                            <p v-if="selectedRequest.id" class="modal-company-id">ID entreprise · <span class="mono">{{ selectedRequest.id }}</span></p>
                        </div>
                    </div>


                    <div class="detail-section-title detail-section-title--after-hero">Informations</div>

                    <div class="detail-rows">
                        <div class="detail-row">
                            <span class="dl">RNE</span>
                            <span class="dv mono">{{ selectedRequest.rne || '—' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="dl">Secteur</span>
                            <span class="dv">{{ selectedRequest.industry || '—' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="dl">Responsable</span>
                            <span class="dv">{{ selectedRequest.owner || '—' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="dl">E-mail</span>
                            <span class="dv">
                                <a v-if="selectedRequest.workEmail" :href="'mailto:' + selectedRequest.workEmail" class="detail-link">{{ selectedRequest.workEmail }}</a>
                                <template v-else>—</template>
                            </span>
                        </div>
                        <div class="detail-row">
                            <span class="dl">Créée le</span>
                            <span class="dv">{{ formatDate(selectedRequest.createdAt) }}</span>
                        </div>
                    </div>

                    <div v-if="selectedRequest.status === 'Pending'" class="modal-actions">
                        <button type="button" class="btn-reject" @click="handleRejectFromModal">Reject</button>
                        <button type="button" class="btn-approve" @click="handleApproveFromModal">Approve</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template> 

<script setup>
    import { ref, computed, onMounted, reactive } from 'vue'
    import axios from 'axios'
    import AppSidebar from '../../components/layout/AppSidebar.vue'
    import GlobalHeader from '../../components/layout/GlobalHeader.vue'
    import { useNotification } from '../../composables/useNotification'

    const requests = ref([])

    /** Données agrégées (GET /admin/dashboard) — cartes du bas + jobs / nouveaux tenants. */
    const platformStats = ref({
        total: 0,
        pending: 0,
        approved: 0,
        rejected: 0,
        totalJobs: 0,
        newTenantsToday: 0,
        processed: 0,
        processingRatePercent: 0,
        tenantsCreatedLast5Days: []
    })

    const selectedRequest = ref(null)
    const showDetailsModal = ref(false)
    const loading = ref(false)
    const error = ref(null)
    const searchQuery = ref('')
    const sortKey = ref('companyName')
    const sortOrder = ref('asc')
    
    const { toast, confirm: confirmModal } = useNotification()

    const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5202/api'

    const api = axios.create({
        baseURL: API_BASE,
        headers: { 'Content-Type': 'application/json' }
    })

    /** Row keys where the logo image failed to load (fallback to initial). */
    const rowLogoFailed = reactive({})
    const modalLogoBroken = ref(false)

    function getLogoUrl(logoUrl) {
        if (!logoUrl) return null
        if (logoUrl.startsWith('http://') || logoUrl.startsWith('https://')) return logoUrl
        if (logoUrl.startsWith('/')) {
            return `${API_BASE.replace(/\/api\/?$/, '')}${logoUrl}`
        }
        return `${API_BASE.replace(/\/api\/?$/, '')}/imagesProfiles/${logoUrl}`
    }

    function showCompanyLogo(request) {
        const name = request?.companyName
        if (!name || rowLogoFailed[name]) return false
        return !!getLogoUrl(request?.logoUrl)
    }

    const showModalCompanyLogo = computed(() => {
        if (!selectedRequest.value || modalLogoBroken.value) return false
        return !!getLogoUrl(selectedRequest.value.logoUrl)
    })

    function onRowLogoError(companyName) {
        if (companyName) rowLogoFailed[companyName] = true
    }

    const stats = computed(() => ({
        total: requests.value.length,
        pending: requests.value.filter(r => r.status === 'Pending').length,
        approved: requests.value.filter(r => r.status === 'Approved').length,
        rejected: requests.value.filter(r => r.status === 'Rejected').length,
        totalJobs: platformStats.value.totalJobs ?? 0,
        newTenantsToday: platformStats.value.newTenantsToday ?? 0
    }))

    /** Aligne les libellés sur les buckets UTC du backend (AdminService.GetDashboardStatsAsync). */
    const tenantActivitySeries = computed(() => {
        const raw = platformStats.value.tenantsCreatedLast5Days
        const counts = Array.isArray(raw) ? raw.map((x) => Number(x) || 0) : []
        const slice = counts.slice(0, 5)
        while (slice.length < 5) slice.push(0)
        const max = Math.max(1, ...slice)
        const now = new Date()
        const utcMidnight = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())
        const labels = []
        for (let i = 0; i < 5; i++) {
            const dayMs = utcMidnight - (4 - i) * 86400000
            const d = new Date(dayMs)
            labels.push(
                d.toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    timeZone: 'UTC'
                })
            )
        }
        return slice.map((count, i) => ({
            count,
            label: labels[i],
            barPct: Math.round((count / max) * 100)
        }))
    })

    function formatCount(n) {
        const x = Number(n)
        if (!Number.isFinite(x)) return '0'
        return x.toLocaleString('en-US')
    }

    async function loadDashboardStats() {
        try {
            const res = await api.get('/admin/dashboard')
            const d = res.data?.data
            if (!d || typeof d !== 'object') return
            platformStats.value = {
                total: d.total ?? 0,
                pending: d.pending ?? 0,
                approved: d.approved ?? 0,
                rejected: d.rejected ?? 0,
                totalJobs: d.totalJobs ?? 0,
                newTenantsToday: d.newTenantsToday ?? 0,
                processed: d.processed ?? 0,
                processingRatePercent: d.processingRatePercent ?? 0,
                tenantsCreatedLast5Days: Array.isArray(d.tenantsCreatedLast5Days) ? d.tenantsCreatedLast5Days : []
            }
        } catch (e) {
            console.error('Dashboard stats:', e)
        }
    }

    const filteredAndSortedRequests = computed(() => {
        let filtered = requests.value
        if (searchQuery.value) {
            const q = searchQuery.value.toLowerCase()
            filtered = filtered.filter(r => r.companyName.toLowerCase().includes(q))
        }
        return [...filtered].sort((a, b) => {
            let aVal = a[sortKey.value] ?? '', bVal = b[sortKey.value] ?? ''
            if (typeof aVal === 'string') { aVal = aVal.toLowerCase(); bVal = bVal.toLowerCase() }
            return sortOrder.value === 'asc' ? (aVal > bVal ? 1 : -1) : (aVal < bVal ? 1 : -1)
        })
    })

    const getBadgeClass = s => ({ Pending: 'badge-pending', Approved: 'badge-approved', Rejected: 'badge-rejected', Verifying: 'badge-verifying' }[s] || 'badge-pending')
    const getStatusLabel = s => ({ Pending: 'Pending Review', Approved: 'Approved', Rejected: 'Rejected', Verifying: 'Verifying DNS' }[s] || s)

    async function loadRequests() {
        loading.value = true; error.value = null
        try {
            const res = await api.get('/admin/tenant-requests')
            console.log('Response:', res.data)
            requests.value = res.data.data
            Object.keys(rowLogoFailed).forEach((k) => { delete rowLogoFailed[k] })
        } catch (err){
            console.error('Error:', err.response)
            error.value = 'Unable to load requests. Check that the backend is accessible on http://localhost:5202'
        } finally {
            loading.value = false
            loadDashboardStats()
        }
    }

    async function handleApprove(name) {
        const confirmed = await confirmModal({
            title: 'Approve Request?',
            message: `Are you sure you want to approve the request from ${name}?`,
            confirmText: 'Approve',
            cancelText: 'Cancel'
        })
        if (!confirmed) return
        
        try { 
            await api.patch(`/admin/tenant-requests/by-name/${encodeURIComponent(name)}/approve`); 
            await loadRequests(); 
            toast.success(`${name} matching has been approved.`)
            if (showDetailsModal.value) closeModal() 
        }
        catch { 
            toast.error('Error approving request') 
        }
    }

    async function handleReject(name) {
        const confirmed = await confirmModal({
            title: 'Reject Request?',
            message: `Are you sure you want to reject the request from ${name}? This action cannot be undone.`,
            confirmText: 'Reject',
            cancelText: 'Cancel'
        })
        if (!confirmed) return
        
        try { 
            await api.patch(`/admin/tenant-requests/by-name/${encodeURIComponent(name)}/reject`); 
            await loadRequests(); 
            toast.warning(`${name} request has been rejected.`)
            if (showDetailsModal.value) closeModal() 
        }
        catch { 
            toast.error('Error rejecting request') 
        }
    }

    async function viewDetails(name) {
        modalLogoBroken.value = false
        try {
            const res = await api.get(`/admin/tenant-requests/by-name/${encodeURIComponent(name)}`)
            selectedRequest.value = res.data.data
            showDetailsModal.value = true
        } catch {
            toast.error('Error loading details')
        }
    }

    const closeModal = () => {
        showDetailsModal.value = false
        selectedRequest.value = null
        modalLogoBroken.value = false
    }

    async function handleApproveFromModal() {
        const name = selectedRequest.value?.companyName
        if (name) await handleApprove(name)
    }

    async function handleRejectFromModal() {
        const name = selectedRequest.value?.companyName
        if (name) await handleReject(name)
    }

    const sortBy = key => { if (sortKey.value === key) sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'; else { sortKey.value = key; sortOrder.value = 'asc' } }
    const formatDate = d => d ? new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''

    onMounted(loadRequests)
</script>

<style scoped>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    *, *::before, *::after {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    .page-layout {
        display: flex;
        height: 100vh;
        overflow: hidden;
        background: #f5f7f8;
        font-family: 'Inter', sans-serif;
    }

    .main-content {
        flex: 1;
        margin-left: 0px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .content {
        flex: 1;
        padding: 24px;
        overflow-y: auto;
    }



    .topbar-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .notif-btn {
        position: relative;
        width: 36px;
        height: 36px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: #64748b;
        transition: all 0.15s;
    }

        .notif-btn:hover {
            border-color: #144bb8;
            color: #144bb8;
        }

        .notif-btn .material-icons {
            font-size: 19px;
        }

    .notif-dot {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 7px;
        height: 7px;
        background: #ef4444;
        border-radius: 50%;
        border: 2px solid white;
    }

    .region-pill {
        display: flex;
        align-items: center;
        gap: 6px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 7px 12px;
        font-size: 12px;
        font-weight: 500;
        color: #475569;
        cursor: pointer;
        white-space: nowrap;
    }

    .page-wrapper {
        padding: 24px;
        flex: 1;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 24px;
    }

    .stat-card {
        position: relative;
        overflow: hidden;
        border-radius: 12px;
        padding: 22px;
        color: white;
        box-shadow: 0 20px 40px -12px rgba(20,75,184,0.25);
    }

    .stat-blue {
        background: #454a83;
    }

    .stat-dark {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        box-shadow: 0 20px 40px -12px rgba(0,0,0,0.3);
    }

    .stat-indigo {
        background: #5d6199;
    }

    .stat-inner {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        position: relative;
        z-index: 1;
    }

    .stat-label {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.7);
        margin-bottom: 6px;
    }

        .stat-label.muted {
            color: #94a3b8;
        }

    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
        letter-spacing: -0.02em;
    }

    .stat-trend {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 500;
        margin-top: 12px;
    }

        .stat-trend .material-icons {
            font-size: 14px;
        }

        .stat-trend.teal {
            color: #14b8a6;
        }

        .stat-trend.white-muted {
            color: rgba(255,255,255,0.65);
        }

    .stat-chart {
        width: 90px;
        height: 60px;
    }

    .donut-wrapper {
        position: relative;
        width: 80px;
        height: 80px;
        flex-shrink: 0;
    }

    .donut-label {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 700;
        color: #14b8a6;
    }

    .bar-chart {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        width: 90px;
        height: 60px;
    }

    .bars {
        display: flex;
        align-items: flex-end;
        gap: 5px;
        height: 48px;
    }

    .bar {
        width: 10px;
        border-radius: 3px 3px 0 0;
    }

    .stat-bg-icon {
        position: absolute;
        right: -14px;
        bottom: -14px;
        font-size: 7rem !important;
        opacity: 0.07;
        color: white;
    }

    .table-card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.07);
        overflow: hidden;
        margin-bottom: 24px;
    }

    .table-toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 22px;
        border-bottom: 1px solid #f1f5f9;
    }

    .table-title {
        font-size: 15px;
        font-weight: 700;
        color: #1e293b;
    }

    .table-subtitle {
        font-size: 12px;
        color: #64748b;
        margin-top: 3px;
    }

    .toolbar-right {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .search-wrapper {
        position: relative;
        display: flex;
        align-items: center;
    }

    .search-icon-input {
        position: absolute;
        left: 8px;
        color: #94a3b8;
        font-size: 17px !important;
        pointer-events: none;
    }

    .search-input {
        padding: 7px 12px 7px 32px;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        font-size: 12px;
        font-family: 'Inter', sans-serif;
        color: #334155;
        outline: none;
        width: 200px;
        transition: border-color 0.15s;
    }

        .search-input:focus {
            border-color: #144bb8;
        }

        .search-input::placeholder {
            color: #94a3b8;
        }

    .btn-filter {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        font-weight: 600;
        color: #144bb8;
        background: none;
        border: none;
        padding: 7px 12px;
        border-radius: 7px;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        transition: background 0.15s;
        white-space: nowrap;
    }

        .btn-filter .material-icons {
            font-size: 16px;
        }

        .btn-filter:hover {
            background: rgba(20,75,184,0.06);
        }

    .table-overflow {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
    }

    thead tr {
        background: #454a83;
        color: white;
    }

    th {
        padding: 12px 22px;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        white-space: nowrap;
    }

        th.sortable {
            cursor: pointer;
            user-select: none;
        }

            th.sortable:hover {
                background: rgba(255,255,255,0.1);
            }

        th.th-center {
            text-align: center;
        }

    tbody tr {
        border-bottom: 1px solid #f1f5f9;
        transition: background 0.12s;
    }

        tbody tr:last-child {
            border-bottom: none;
        }

        tbody tr:hover {
            background: #f8fafc;
        }

    td {
        padding: 14px 22px;
        font-size: 13px;
        vertical-align: middle;
    }

    .company-cell {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .company-avatar {
        width: 36px;
        height: 36px;
        border-radius: 7px;
        background: #f1f5f9;
        color: #144bb8;
        font-weight: 700;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .company-avatar--logo {
        padding: 0;
        overflow: hidden;
        background: #fff;
        border: 1px solid #e2e8f0;
    }

    .company-logo-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

        .company-avatar.large {
            width: 48px;
            height: 48px;
            font-size: 20px;
        }

    .company-name {
        font-weight: 600;
    }

    .rne {
        font-size: 12px;
        font-family: 'Courier New', monospace;
        color: #64748b;
    }

    .owner-name {
        font-weight: 500;
        color: #334155;
    }

    .owner-email {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 2px;
    }

    .domain-link {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        color: #144bb8;
        text-decoration: none;
        font-size: 12px;
    }

        .domain-link:hover {
            text-decoration: underline;
        }

    .badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 9px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: nowrap;
    }

    .badge-pending {
        background: #fef3c7;
        color: #b45309;
    }

    .badge-approved {
        background: #dcfce7;
        color: #166534;
    }

    .badge-rejected {
        background: #fee2e2;
        color: #991b1b;
    }

    .badge-verifying {
        background: #dbeafe;
        color: #1d4ed8;
    }

    .action-btns {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }

    .btn-approve {
        padding: 5px 12px;
        background: #14b8a6;
        color: white;
        border: none;
        border-radius: 7px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: background 0.15s;
    }

        .btn-approve:hover {
            background: #0d9488;
        }

    .btn-reject {
        padding: 5px 12px;
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 7px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: background 0.15s;
    }

        .btn-reject:hover {
            background: #dc2626;
        }

    .btn-view {
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        color: #64748b;
        cursor: pointer;
        transition: all 0.15s;
    }

        .btn-view:hover {
            background: #144bb8;
            color: white;
            border-color: #144bb8;
        }

    .table-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 22px;
        background: #f8fafc;
        border-top: 1px solid #f1f5f9;
    }

    .showing-text {
        font-size: 11px;
        color: #94a3b8;
    }

    .pagination {
        display: flex;
        gap: 4px;
    }

    .page-btn {
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #e2e8f0;
        border-radius: 5px;
        font-size: 12px;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        background: white;
        color: #64748b;
        cursor: pointer;
        transition: all 0.15s;
    }

        .page-btn:hover {
            border-color: #cbd5e1;
            color: #1e293b;
        }

        .page-btn.active {
            background: #144bb8;
            color: white;
            border-color: #144bb8;
            font-weight: 700;
        }

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
        animation: spin 0.8s linear infinite;
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
        text-align: center;
        padding: 40px;
        color: #94a3b8;
        font-size: 13px;
    }

    .bottom-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }

    .ai-card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    .ai-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 22px;
    }

    .ai-card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 700;
        color: #1e293b;
    }

    .ai-title-icon {
        font-size: 17px !important;
        color: #144bb8;
    }

    .live-badge {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 9px;
        font-weight: 700;
        color: #14b8a6;
        letter-spacing: 0.08em;
    }

    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #14b8a6;
        animation: pulse-live 1.5s ease-in-out infinite;
    }

    @keyframes pulse-live {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }

        50% {
            opacity: 0.5;
            transform: scale(0.8);
        }
    }

    .tenant-activity-chart {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 10px;
        min-height: 140px;
        padding-top: 4px;
    }

    .tenant-activity-col {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        min-width: 0;
    }

    .tenant-activity-value {
        font-size: 12px;
        font-weight: 700;
        color: #0f172a;
    }

    .tenant-activity-bar-track {
        width: 100%;
        max-width: 44px;
        height: 88px;
        background: #f1f5f9;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        overflow: hidden;
    }

    .tenant-activity-bar-fill {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(180deg, #144bb8, #1e40af);
        transition: height 0.45s ease;
        min-height: 0;
    }

    .tenant-activity-label {
        font-size: 9px;
        font-weight: 600;
        color: #94a3b8;
        text-align: center;
        line-height: 1.2;
        text-transform: capitalize;
    }

    .infra-card {
        background: #0f1824;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }

    .infra-card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 22px;
    }

    .infra-pulse {
        position: relative;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .pulse-ring {
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 2px solid #14b8a6;
        animation: pulse-ring 2s ease-out infinite;
    }

    @keyframes pulse-ring {
        0% {
            transform: scale(0.8);
            opacity: 1;
        }

        100% {
            transform: scale(1.4);
            opacity: 0;
        }
    }

    .pulse-icon {
        font-size: 16px !important;
        color: #14b8a6;
        position: relative;
        z-index: 1;
    }

    .infra-title {
        font-size: 13px;
        font-weight: 700;
        color: white;
    }

    .infra-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }

    .infra-item {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 8px;
        padding: 14px;
    }

    .infra-label {
        font-size: 8px;
        font-weight: 700;
        color: rgba(255,255,255,0.35);
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }

    .infra-value-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .infra-value {
        font-size: 18px;
        font-weight: 700;
        color: white;
    }

    .infra-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

        .infra-dot.green {
            background: #14b8a6;
        }

        .infra-dot.amber {
            background: #f59e0b;
        }

    .infra-refresh {
        font-size: 16px !important;
        color: rgba(255,255,255,0.3);
    }

    .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.5);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.15s ease;
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
        width: 520px;
        max-width: 90vw;
        max-height: 85vh;
        overflow-y: auto;
        box-shadow: 0 25px 60px -12px rgba(0,0,0,0.3);
        animation: slideUp 0.2s ease;
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

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 22px;
        border-bottom: 1px solid #f1f5f9;
    }

        .modal-header h2 {
            font-size: 15px;
            font-weight: 700;
            color: #1e293b;
        }

    .modal-close {
        background: none;
        border: none;
        color: #94a3b8;
        cursor: pointer;
        display: flex;
        align-items: center;
        border-radius: 6px;
        padding: 4px;
        transition: color 0.15s;
    }

        .modal-close:hover {
            color: #1e293b;
        }

    .modal-body {
        padding: 22px;
    }

    .modal-company-top {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        margin-bottom: 4px;
        padding-bottom: 20px;
        border-bottom: 1px solid #f1f5f9;
    }

    .modal-company-head-text {
        flex: 1;
        min-width: 0;
    }

    .modal-company-name {
        font-size: 16px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 6px;
    }

    .modal-company-id {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 8px;
        line-height: 1.4;
    }

    .modal-company-id .mono {
        font-family: 'Courier New', monospace;
        color: #64748b;
        word-break: break-all;
    }

    .detail-section-title {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin: 20px 0 10px;
    }

    .detail-section-title--after-hero {
        margin-top: 4px;
    }

    .detail-rows {
        display: flex;
        flex-direction: column;
    }

    .detail-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #f8fafc;
    }

    .detail-row:last-child {
        border-bottom: none;
    }

    .dl {
        width: 100px;
        font-size: 10px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        flex-shrink: 0;
        padding-top: 2px;
    }

    .dv {
        font-size: 13px;
        color: #334155;
        line-height: 1.45;
        flex: 1;
        min-width: 0;
        word-break: break-word;
    }

        .dv.mono {
            font-family: 'Courier New', monospace;
        }

    .detail-link {
        color: #144bb8;
        text-decoration: none;
        font-weight: 500;
    }

    .detail-link:hover {
        text-decoration: underline;
    }

    .modal-actions {
        display: flex;
        gap: 10px;
        justify-content: flex-end;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #f1f5f9;
    }

    @media (max-width: 768px) {
        .main-area {
            margin-left: 0;
        }

        .stats-grid {
            grid-template-columns: 1fr;
        }

        .bottom-row {
            grid-template-columns: 1fr;
        }

        .table-toolbar {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
        }

        .toolbar-right {
            flex-wrap: wrap;
        }

        .search-input {
            width: 160px;
        }
    }
</style>