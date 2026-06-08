<template>
  <div class="page-layout">
    <AppSidebar />

    <main class="main-content">
      <!-- Header -->
      <GlobalHeader title="Recruiter Portal" />

      <!-- Content -->
      <div class="content">
        <!-- Page heading -->
        <div class="page-heading">
          <div>
            <h2 class="page-title">Job Offers</h2>
            <p class="page-sub">
              Manage and track your active recruitment campaigns
            </p>
          </div>
          <button class="btn btn-primary" @click="createOffer">
            <PlusIcon :size="16" />
            Create Offer
          </button>
        </div>

        <!-- Filters -->
        <div class="filters-row">
          <div class="input-wrapper">
            <SearchIcon :size="15" class="input-icon" />
            <input v-model="search" type="text" class="filter-input" placeholder="Search" />
          </div>
          <div class="select-wrapper">
            <BuildingIcon :size="15" class="input-icon" />
            <select v-model="selectedCompany" class="filter-select">
              <option value="">All Companies</option>
              <option v-for="e in entreprises" :key="e.id" :value="e.id">
                {{ e.nom }}
              </option>
            </select>
            <ChevronDownIcon :size="14" class="select-caret" />
          </div>
          <div class="select-wrapper">
            <CheckCircleIcon :size="15" class="input-icon" />
            <select v-model="selectedStatus" class="filter-select">
              <option value="">All Status</option>
              <option value="published">Published</option>
              <option value="draft">Unpublished</option>
            </select>
            <ChevronDownIcon :size="14" class="select-caret" />
          </div>
        </div>

        <!-- Table -->
        <div class="table-card">
          <table class="offers-table">
            <thead>
              <tr>
                <th>Job Title</th>
                <th>Company Name</th>
                <th>Location</th>
                <th>Candidates</th>
                <th>Date created</th>
                <th>Status</th>
                <th class="col-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="offer in filteredOffers" :key="offer.id">
                <td>
                  <p class="offer-title">{{ offer.title }}</p>
                </td>
                <td class="cell-text">{{ offer.company }}</td>
                <td>
                  <span class="location-cell">
                    <MapPinIcon :size="13" />
                    {{ offer.location }}
                  </span>
                </td>
                <td>
                  <button class="candidate-count candidate-count-link" @click="viewCandidates(offer.id)">
                    <UsersIcon :size="14" class="count-icon" />
                    {{ offer.candidates }}
                  </button>
                </td>
                <td class="cell-text">{{ offer.datePosted }}</td>
                <td>
                  <span class="badge" :class="offer.status === 'published'
                      ? 'badge-green'
                      : 'badge-grey'
                    ">
                    {{ offer.status }}
                  </span>
                </td>
                <td class="col-right">
                  <div class="actions">
                    <button class="action-btn" title="Preview" @click="previewOffer(offer.id)">
                      <EyeIcon :size="18" />
                    </button>
                    <button class="action-btn" title="Edit" @click="editOffer(offer.id)">
                      <PencilIcon :size="18" />
                    </button>

                    <!-- Three dots menu -->
                    <div class="menu-container" v-click-outside="() => (activeMenuId = null)">
                      <button class="action-btn" :class="{ 'btn-active': activeMenuId === offer.id }" @click.stop="
                        activeMenuId =
                        activeMenuId === offer.id ? null : offer.id
                        ">
                        <MoreVerticalIcon :size="18" />
                      </button>

                      <transition name="menu-fade">
                        <div v-if="activeMenuId === offer.id" class="dropdown-menu">
                          <button class="menu-item" @click="toggleStatus(offer)">
                            <component :is="offer.status === 'published'
                                ? 'UnlinkIcon'
                                : 'GlobeIcon'
                              " :size="14" />
                            {{
                              offer.status === "published"
                                ? "Unpublish"
                                : "Publish"
                            }}
                          </button>

                          <button class="menu-item" @click="handleCopyLink(offer)">
                            <CopyIcon :size="14" />
                            Copy Link
                          </button>

                          <button class="menu-item" @click="openAssign(offer)">
                            <UserPlusIcon :size="14" />
                            Assign Members
                          </button>

                          <div class="menu-divider"></div>

                          <button class="menu-item danger" @click="deleteOffer(offer.id)">
                            <TrashIcon :size="14" />
                            Delete
                          </button>
                        </div>
                      </transition>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination -->
          <div class="pagination-bar">
            <p class="pagination-info">
              Showing 1 to {{ filteredOffers.length }}
            </p>
            <div class="pagination-buttons">
              <button class="page-btn">Previous</button>
              <button class="page-btn page-btn-active">1</button>
              <button class="page-btn">2</button>
              <button class="page-btn">Next</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Modals -->
    <AssignExpertsModal :is-open="showAssignModal" :offre-id="assigningOffreId" @close="showAssignModal = false"
      @saved="loadOffers" />
  </div>
</template>

<script>
import {
  SearchIcon,
  BellIcon,
  HelpCircleIcon,
  PlusIcon,
  FilterIcon,
  BuildingIcon,
  ChevronDownIcon,
  CheckCircleIcon,
  MapPinIcon,
  UsersIcon,
  EyeIcon,
  PencilIcon,
  Trash2Icon,
  MoreVerticalIcon,
  GlobeIcon,
  UserPlusIcon,
  UnlinkIcon,
  CopyIcon,
  TrashIcon,
} from "lucide-vue-next";
import AppSidebar from "../../components/layout/AppSidebar.vue";
import GlobalHeader from "../../components/layout/GlobalHeader.vue";
import AssignExpertsModal from "../../components/modals/AssignExpertsModal.vue";
import {
  getOffres,
  deleteOffre,
  getEntreprises,
  changePublicationStatus,
  togglePublicLink,
} from "../../services/offreService";

import { useNotification } from "../../composables/useNotification";

export default {
  name: "JobOffers",
  components: {
    AppSidebar,
    GlobalHeader,
    AssignExpertsModal,
    SearchIcon,
    BellIcon,
    HelpCircleIcon,
    PlusIcon,
    FilterIcon,
    BuildingIcon,
    ChevronDownIcon,
    CheckCircleIcon,
    MapPinIcon,
    UsersIcon,
    EyeIcon,
    PencilIcon,
    Trash2Icon,
    MoreVerticalIcon,
    GlobeIcon,
    UserPlusIcon,
    UnlinkIcon,
    CopyIcon,
    TrashIcon,
  },
  setup() {
    const { toast, confirm } = useNotification();
    return { toast, confirm };
  },
  data() {
    return {
      entreprises: [],
      search: "",
      selectedCompany: "",
      selectedStatus: "",
      offers: [],
      searchTimeout: null,
      activeMenuId: null,
      showAssignModal: false,
      assigningOffreId: null,
    };
  },
  mounted() {
    this.loadOffers();
    this.fetchEntreprises();
  },
  computed: {
    filteredOffers() {
      return this.offers;
    },
  },
  watch: {
    selectedCompany() {
      this.loadOffers();
    },
    selectedStatus() {
      this.loadOffers();
    },
    search() {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.loadOffers();
      }, 300);
    },
  },
  methods: {
    async loadOffers() {
      try {
        const companyId = this.selectedCompany || null;
        const searchQuery = this.search || null;
        const statusFilter = this.selectedStatus || null;

        const res = await getOffres(companyId, searchQuery, statusFilter);
        this.offers = (res.data || []).map((o) => ({
          id: o.id,
          title: o.titre || o.title || "Untitled Offer",
          description: o.description,
          company: o.nomEntreprise,
          location: o.localisation,
          candidates: o.nombreCandidats,
          datePosted: new Date(o.creeLe || Date.now()).toLocaleDateString(),
          status: o.estPublie ? "published" : "draft",
          publicLink: o.lienPublic,
          isPublicLinkEnabled: o.isPublicLinkEnabled,
        }));
      } catch (err) {
        console.error("Failed to load offers", err);
      }
    },
    async deleteOffer(id) {
      const confirmed = await this.confirm({
        title: "Delete Offer?",
        message:
          "Are you sure you want to delete this job offer? This action cannot be undone.",
        confirmText: "Delete",
        cancelText: "Cancel",
      });

      if (!confirmed) return;

      try {
        await deleteOffre(id);
        this.offers = this.offers.filter((o) => o.id !== id);
        this.toast.success("Offer deleted successfully.");
      } catch (err) {
        console.error("Delete failed", err);
        this.toast.error("Failed to delete offer.");
      }
    },
    async fetchEntreprises() {
      try {
        const res = await getEntreprises();
        this.entreprises = res.data || [];
      } catch (err) {
        console.error("Failed to load entreprises", err);
      }
    },
    createOffer() {
      this.$router.push("/recruiter/jobs/create/new/step1");
    },
    editOffer(id) {
      this.$router.push(`/recruiter/jobs/create/${id}/step1`);
    },
    previewOffer(id) {
      this.$router.push(`/recruiter/jobs/create/${id}/step3`);
    },
    async toggleStatus(offer) {
      this.activeMenuId = null;
      const newStatus = offer.status !== "published";
      try {
        await changePublicationStatus(offer.id, newStatus);
        offer.status = newStatus ? "published" : "draft";
        this.toast.success(
          `Offer ${newStatus ? "published" : "unpublished"} successfully.`,
        );
      } catch (err) {
        this.toast.error("Failed to change publication status.");
      }
    },
    async handleCopyLink(offer) {
      this.activeMenuId = null;
      if (!offer.publicLink) {
        const confirmed = await this.confirm({
          title: "Public Link Missing",
        message: `This offer doesn't have a public link enabled.

Do you want to generate one now?

(Public link will only work if the offer is published on the platform)`,
          cancelText: "No"
        });

        if (confirmed) {
          try {
            const res = await togglePublicLink(offer.id, true);
            offer.publicLink = res.data.lienPublic;
            offer.isPublicLinkEnabled = true;
            this.toast.success("Public link generated!");
            this.copyToClipboard(offer.publicLink);
          } catch (err) {
            this.toast.error("Failed to generate link.");
            return;
          }
        } else return;
      } else {
        this.copyToClipboard(offer.publicLink);
      }
    },
    copyToClipboard(text) {
      navigator.clipboard
        .writeText(text)
        .then(() => {
          this.toast.info("Link copied to clipboard!");
        })
        .catch(() => {
          this.toast.error("Failed to copy link.");
        });
    },
    openAssign(offer) {
      this.activeMenuId = null;
      this.assigningOffreId = offer.id;
      this.showAssignModal = true;
    },
    viewCandidates(offerId) {
      this.$router.push(`/recruiter/jobs/${offerId}/candidates`);
    },
  },
  directives: {
    "click-outside": {
      mounted(el, binding) {
        el.clickOutsideEvent = function (event) {
          if (!(el === event.target || el.contains(event.target))) {
            binding.value(event);
          }
        };
        document.body.addEventListener("click", el.clickOutsideEvent);
      },
      unmounted(el) {
        document.body.removeEventListener("click", el.clickOutsideEvent);
      },
    },
  },
};
</script>

<style scoped>
/* ── Layout ── */
.page-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7f8;
  font-family: "Inter", sans-serif;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

/* ── Header CSS has been moved to GlobalHeader.vue, but we keep other structural parts. ── */

.search-wrapper {
  position: relative;
  max-width: 360px;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-input {
  width: 100%;
  height: 38px;
  padding: 0 14px 0 36px;
  background: #f5f7f8;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
  transition: box-shadow 0.15s;
}

.search-input:focus {
  box-shadow: 0 0 0 2px rgba(69, 74, 131, 0.2);
}

/* ── Header Right & icons related CSS moved to GlobalHeader.vue ── */

.divider-v {
  width: 1px;
  height: 32px;
  background: rgba(69, 74, 131, 0.1);
  margin: 0 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-text {
  text-align: right;
}

.user-name {
  font-size: 13px;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
  color: #0f172a;
}

.user-role {
  font-size: 11px;
  color: #454a83;
  font-weight: 500;
  margin: 0;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(69, 74, 131, 0.2);
}

/* ── Content ── */
.content {
  flex: 1;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

/* ── Page heading ── */
.page-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
  color: #0f172a;
}

.page-sub {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

/* ── Filters ── */
.filters-row {
  display: flex;
  gap: 14px;
}

.input-wrapper,
.select-wrapper {
  position: relative;
  max-width: 320px;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

.filter-input,
.filter-select {
  width: 100%;
  height: 44px;
  padding: 0 14px 0 36px;
  background: #fff;
  border: 1px solid rgba(69, 74, 131, 0.15);
  border-radius: 12px;
  font-size: 13px;
  outline: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  box-sizing: border-box;
  font-family: inherit;
  color: #0f172a;
  transition: box-shadow 0.15s;
}

.filter-input:focus,
.filter-select:focus {
  box-shadow: 0 0 0 3px rgba(69, 74, 131, 0.15);
}

.filter-select {
  appearance: none;
  padding-right: 32px;
  cursor: pointer;
}

.select-caret {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

/* ── Table card ── */
.table-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid rgba(69, 74, 131, 0.1);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  overflow: visible;
  /* Prevent clipping of the dropdown menu */
}

.offers-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

thead tr {
  background: #f5f7f8;
  border-bottom: 1px solid rgba(69, 74, 131, 0.1);
}

thead th {
  padding: 14px 20px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #64748b;
}

.col-right {
  text-align: right;
}

tbody tr {
  border-bottom: 1px solid rgba(69, 74, 131, 0.05);
  transition: background 0.12s;
}

tbody tr:last-child {
  border-bottom: none;
}

tbody tr:hover {
  background: rgba(69, 74, 131, 0.025);
}

tbody td {
  padding: 14px 20px;
  vertical-align: middle;
}

.offer-title {
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 2px;
  color: #0f172a;
}

.offer-sub {
  font-size: 11px;
  color: #94a3b8;
  margin: 0;
}

.cell-text {
  font-size: 13px;
  color: #475569;
}

.location-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #475569;
}

.candidate-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.candidate-count-link {
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.15s, color 0.15s;
  text-decoration: none;
}

.candidate-count-link:hover {
  background: rgba(69, 74, 131, 0.08);
  color: #454a83;
}

.candidate-count-link:hover .count-icon {
  color: #454a83;
}

.count-icon {
  color: #454a83;
}

/* ── Badges ── */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.badge-green {
  background: #dcfce7;
  color: #16a34a;
}

.badge-grey {
  background: #f1f5f9;
  color: #64748b;
}

/* ── Actions ── */
.actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 2px;
}

.action-btn {
  padding: 7px;
  border: none;
  background: none;
  color: #94a3b8;
  cursor: pointer;
  border-radius: 8px;
  display: flex;
  align-items: center;
  transition:
    color 0.15s,
    background 0.15s;
}

.action-btn:hover {
  color: #454a83;
  background: rgba(69, 74, 131, 0.08);
}

.action-btn-danger:hover {
  color: #dc2626;
  background: #fef2f2;
}

/* ── Pagination ── */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-top: 1px solid rgba(69, 74, 131, 0.1);
  background: #f5f7f8;
}

.pagination-info {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin: 0;
}

.pagination-buttons {
  display: flex;
  gap: 6px;
}

.page-btn {
  padding: 5px 12px;
  font-size: 13px;
  border: 1px solid rgba(69, 74, 131, 0.2);
  border-radius: 6px;
  background: none;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s;
  color: #0f172a;
}

.page-btn:hover {
  background: #fff;
}

.page-btn-active {
  background: #454a83;
  color: #fff;
  border-color: #454a83;
  font-weight: 700;
}

.page-btn-active:hover {
  background: #454a83;
}

/* ── Button ── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  font-family: inherit;
  transition: opacity 0.15s;
}

.btn-primary {
  background: #1A2B4C;
  color: #fff;
  box-shadow: 0 4px 12px rgba(69, 74, 131, 0.25);
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-primary:active {
  transform: scale(0.97);
}

/* ── Actions Dropdown ── */
.menu-container {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 5px;
  background: #fff;
  border: 1px solid rgba(69, 74, 131, 0.15);
  border-radius: 12px;
  box-shadow:
    0 10px 25px -5px rgba(0, 0, 0, 0.1),
    0 8px 10px -6px rgba(0, 0, 0, 0.1);
  padding: 6px;
  z-index: 50;
  min-width: 180px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  border-radius: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.menu-item:hover {
  background: #f8fafc;
  color: #454a83;
}

.menu-item svg {
  color: #94a3b8;
  transition: color 0.2s;
}

.menu-item:hover svg {
  color: #454a83;
}

.menu-item.danger {
  color: #dc2626;
}

.menu-item.danger:hover {
  background: #fef2f2;
  color: #dc2626;
}

.menu-item.danger svg {
  color: #f87171;
}

.menu-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 4px 0;
}

/* Animations */
.menu-fade-enter-active,
.menu-fade-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.btn-active {
  background: rgba(69, 74, 131, 0.1) !important;
  color: #454a83 !important;
}
</style>
