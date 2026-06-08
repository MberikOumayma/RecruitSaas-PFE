<template>
  <div class="actions-dropdown-container" v-click-outside="closeMenu">
    <button 
      class="trigger-btn" 
      :class="{ 'is-active': isOpen }" 
      @click.stop="toggleMenu"
    >
      <MoreVerticalIcon :size="18" />
    </button>

    <Transition name="dropdown-fade">
      <div v-if="isOpen" class="dropdown-menu">
        <div class="dropdown-section">
          <p class="section-title">Core</p>
          <button class="dropdown-item" @click="handleAction('view-profile')">
            <UserIcon :size="14" class="item-icon" />
            <span>View Profile</span>
          </button>
          <button class="dropdown-item" @click="handleAction('view-cv')">
            <FileTextIcon :size="14" class="item-icon" />
            <span>View CV</span>
          </button>
          <button class="dropdown-item" @click="handleAction('download-cv')">
            <DownloadIcon :size="14" class="item-icon" />
            <span>Download CV</span>
          </button>
        </div>

        <div class="dropdown-divider"></div>

        <div class="dropdown-section">
          <p class="section-title">AI Actions</p>
          
         <button 
  class="dropdown-item" 
  @click="handleAction(candidate.scoreIA == null ? 'calculate' : 'recalculate')"
>
  <CalculatorIcon :size="14" class="item-icon text-tertiary" />
  <span>
    {{ candidate.scoreIA == null ? 'Calculate Score' : 'Recalculate Score' }}
  </span>
</button>
          
        </div>

        <div class="dropdown-divider"></div>

        <div class="dropdown-section">
          <button class="dropdown-item item-danger" @click="handleAction('reject')">
            <XCircleIcon :size="14" class="item-icon" />
            <span>Reject Candidate</span>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { 
  MoreVerticalIcon, 
  UserIcon, 
  FileTextIcon, 
  DownloadIcon, 
  TagIcon, 
  CalculatorIcon, 
  Wand2Icon, 
  SparklesIcon, 
  BriefcaseIcon,
  ArrowRightLeftIcon,
  XCircleIcon
} from 'lucide-vue-next'

export default {
  name: 'CandidateActionsDropdown',
  components: {
    MoreVerticalIcon, UserIcon, FileTextIcon, DownloadIcon, TagIcon,
    CalculatorIcon, Wand2Icon, SparklesIcon, BriefcaseIcon,
    ArrowRightLeftIcon, XCircleIcon
  },
 props: {
  candidate: {
    type: Object,
    required: true
  }
},
  data() {
    return {
      isOpen: false
    }
  },
  methods: {
    toggleMenu() {
      this.isOpen = !this.isOpen
    },
    closeMenu() {
      this.isOpen = false
    },
    handleAction(action) {
      this.$emit('action', { action, candidate: this.candidate })
      this.closeMenu()
    }
  },
  directives: {
    'click-outside': {
      mounted(el, binding) {
        el.clickOutsideEvent = function(event) {
          if (!(el === event.target || el.contains(event.target))) {
            binding.value(event)
          }
        }
        document.body.addEventListener('click', el.clickOutsideEvent)
      },
      unmounted(el) {
        document.body.removeEventListener('click', el.clickOutsideEvent)
      }
    }
  }
}
</script>

<style scoped>
.actions-dropdown-container {
  position: relative;
  display: inline-block;
}

.trigger-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #94A3B8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.trigger-btn:hover, .trigger-btn.is-active {
  background: rgba(69, 74, 131, 0.08);
  color: #454a83;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  width: 220px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  padding: 8px 0;
  z-index: 50;
  transform-origin: top right;
}

.dropdown-section {
  padding: 4px 8px;
}

.section-title {
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94A3B8;
  margin: 4px 8px;
    text-align: center;

}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: #475569;
  font-size: 13px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.dropdown-item:hover {
  background: #F8FAFC;
  color: #0F172A;
}

.item-icon {
  color: #94A3B8;
  transition: color 0.15s ease;
}

.dropdown-item:hover .item-icon {
  color: #454a83;
}

.dropdown-item:hover .text-tertiary {
  color: #0D9488;
}

.item-danger {
  color: #E11D48;
}

.item-danger:hover {
  background: #FFE4E6;
  color: #E11D48;
}

.item-danger .item-icon {
  color: #E11D48;
}

.item-danger:hover .item-icon {
  color: #BE123C;
}

.dropdown-divider {
  height: 1px;
  background: #F1F5F9;
  margin: 4px 0;
}

/* Animations */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-5px);
}
</style>
